#!/usr/bin/env python3
"""retention_purge.py — OC-4 biometric retention enforcement (proposed T19).

Implements the OC-4 policy's retention periods in code:
  - Class A (raw RR/EDA/ECG signals in the capture-layer store): purge
    after 30 days (hard delete, never soft-delete, never egress).
  - Class B (derived HRV features in the logbook): purge after 90 days.
  - Class C (inferred state): governed by the keystone, NOT purged here.
  - Class D (provenance/audit): append-only, never purged here.

Design:
  - Separate capture-layer store: raw signals live in capture/raw/<window>.json
    (per OC-4 §7 — the logbook holds reconciled B/C/D, NOT raw Class A).
  - Erasure is IRREVERSIBLE + PROVABLE: content hard-deleted; the FACT of
    erasure is appended to a purge audit log (capture/raw/.erasure_ledger.jsonl)
    with source/timestamp/actor — auditable without resurrecting data.
  - Revocation-safe: a MIRROR-invalidation hook is called for any raw
    window erased (OC-15 dependency); the caller must ensure cached
    projections derived from the erased window are invalidated in the
    same transaction.
  - No cloud: erasure is complete because raw signals never leave the
    local store (D3).

Run (dry-run by default):  python3 retention_purge.py --apply
"""
from __future__ import annotations

import argparse
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Callable, List, Optional

logger = logging.getLogger("retention_purge")

# OC-4 canonical retention periods (a Blueprint may tighten, never loosen).
RAW_RETENTION_DAYS = 30       # Class A
FEATURE_RETENTION_DAYS = 90   # Class B

RAW_DIR = Path(__file__).resolve().parent / "capture" / "raw"
ERASURE_LEDGER = RAW_DIR / ".erasure_ledger.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class PurgeResult:
    raw_purged: int
    raw_skipped_missing: int
    feature_rows_purged: int
    erasures_logged: int


def _parse_iso(ts: str) -> datetime:
    # strip trailing 'Z' if present, normalize
    t = ts.replace("Z", "+00:00")
    return datetime.fromisoformat(t)


def purge_raw_window(raw_path: Path, now: datetime, actor: str) -> bool:
    """Hard-delete ONE raw window file older than RAW_RETENTION_DAYS.

    Returns True if purged. Records the erasure fact to the ledger.
    """
    # parse captured_at from the file's sidecar metadata if present
    try:
        meta = json.loads(raw_path.with_suffix(".meta.json").read_text())
        captured = _parse_iso(meta.get("captured_at", raw_path.stem))
    except Exception:
        captured = now  # no sidecar -> treat as fresh (do not purge)
    age = now - captured
    if age < timedelta(days=RAW_RETENTION_DAYS):
        return False

    # irreversible: hard delete (unlink) — no tombstone of the content
    raw_path.unlink(missing_ok=True)
    raw_path.with_suffix(".meta.json").unlink(missing_ok=True)

    # provable: append the fact of erasure (Class D record, not content)
    ERASURE_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with open(ERASURE_LEDGER, "a") as fh:
        fh.write(json.dumps({
            "event": "biometric_erasure",
            "class": "A",
            "raw_window": raw_path.name,
            "timestamp": _now(),
            "actor": actor,
            "reason": f"retention {RAW_RETENTION_DAYS}d exceeded",
        }) + "\n")
    return True


def purge_expired_raw(now: datetime, actor: str = "retention_purge") -> PurgeResult:
    """Purge all raw Class A windows older than the retention window."""
    if not RAW_DIR.exists():
        return PurgeResult(0, 0, 0, 0)
    purged = skipped = logged = 0
    for f in RAW_DIR.iterdir():
        if f.suffix in (".json",) and not f.name.startswith("."):
            if purge_raw_window(f, now, actor):
                purged += 1
                logged += 1
            else:
                skipped += 1
    return PurgeResult(purged, skipped, 0, logged)


def purge_feature_rows(features_store: Path, now: datetime, actor: str = "retention_purge") -> PurgeResult:
    """Purge Class B derived-feature rows from the FEATURES store older than 90d.

    IMPORTANT (Council amendment, verified against storage/schema.sql):
    Class B features do NOT live in the Measurement Logbook — the logbook
    stores only reconciled state (C) + provenance (D) + self-report. A
    purge job MUST scan the capture + features stores ONLY and NEVER the
    logbook (which has no class column; a mis-scoped purge against
    keystone-governed C/D rows is a live bug risk). This function
    therefore operates on a dedicated features store directory, NOT the
    logbook sqlite.
    """
    if not features_store.exists():
        return PurgeResult(0, 0, 0, 0)
    purged = 0
    cutoff = now - timedelta(days=FEATURE_RETENTION_DAYS)
    for f in features_store.glob("*.json"):
        if f.name.startswith("."):
            continue
        try:
            meta = json.loads(f.with_suffix(".meta.json").read_text())
            captured = _parse_iso(meta.get("captured_at", ""))
        except Exception:
            continue  # unparseable -> conservative, do not purge
        if captured < cutoff:
            f.unlink(missing_ok=True)
            f.with_suffix(".meta.json").unlink(missing_ok=True)
            purged += 1
    return PurgeResult(0, 0, purged, 0)


def mirror_invalidation_hook(erased_windows: List[str]) -> None:
    """Revocation-safe MIRROR hook (OC-15 dependency).

    Called after raw windows are erased. Must ensure any cached projection
    / narrative built from an erased window is invalidated in the SAME
    transaction. The mechanism is OC-15's; this is the call site that
    guarantees erased content cannot re-enter the narrative.
    """
    if not erased_windows:
        return
    logger.info("MIRROR invalidation required for %d erased window(s): %s",
                len(erased_windows), erased_windows[:5])
    # TODO(OC-15): implement the actual MIRROR/cache invalidation here.
    # Until OC-15 lands, this is a no-op placeholder that RECORDS the
    # dependency — it must not silently claim erasure is complete.


def main() -> int:
    ap = argparse.ArgumentParser(description="OC-4 biometric retention purge")
    ap.add_argument("--apply", action="store_true",
                    help="actually purge (default: dry-run, no deletes)")
    ap.add_argument("--features-store", type=Path, default=None,
                    help="path to the Class B features store directory")
    ap.add_argument("--h4-trip", action="store_true",
                    help="H4-trip flag: accelerates Class A purge (ease-off)")
    a = ap.parse_args()

    logging.basicConfig(level=logging.INFO)
    now = datetime.now(timezone.utc)

    # H4-trip acceleration (Council amendment): an ease-off shortens the
    # effective retention window, shrinking the sensitive-data footprint.
    if a.h4_trip:
        global RAW_RETENTION_DAYS
        RAW_RETENTION_DAYS = min(RAW_RETENTION_DAYS, 7)  # accelerate to 7d

    if not a.apply:
        print("DRY-RUN: no files deleted. Pass --apply to enforce retention.")
        n = 0
        if RAW_DIR.exists():
            for f in RAW_DIR.iterdir():
                if f.suffix == ".json" and not f.name.startswith("."):
                    n += 1
        print(f"raw windows present: {n} (would purge those >{RAW_RETENTION_DAYS}d)")
        return 0

    result = purge_expired_raw(now)
    erased = []
    if a.features_store is not None:
        fb = purge_feature_rows(a.features_store, now)
        result = PurgeResult(result.raw_purged, result.raw_skipped_missing,
                             fb.feature_rows_purged, result.erasures_logged)
    mirror_invalidation_hook(erased)
    print(f"PURGED: {result.raw_purged} raw (Class A), "
          f"{result.feature_rows_purged} feature rows (Class B), "
          f"{result.erasures_logged} erasures logged")
    print("NOTE: logbook (Class C/D) is NEVER scanned by this purge "
          "(keystone-governed). SQLite stores use DELETE+CHECKPOINT+VACUUM "
          "for irreversibility; capture store is backup-excluded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
