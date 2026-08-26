#!/usr/bin/env python3
"""vt_estimate.py — Phase 1 epistemic wrapper (R-2, two-field estimate).

Estimate(τ) = (status, posterior) — the Formalization's Estimate(τ) resolution
order (HOMES_VT1_Sublation_Synthesis §5.2, first match wins) as a thin module
over the engine. The engine's arithmetic is untouched; this wrapper decides
when a number may be surfaced. A numeric posterior is emitted ONLY when
status == 'estimable'; every other status is a first-class, honest resolution
— never a fabricated number.

Resolution order (first match wins):
  1. data empty or expired                    -> unknown
  2. provenance or CAI inadmissible           -> indeterminate
  3. participant declined / withdrew          -> declined / withdrawn (SELF authority absolute)
  4. |prediction − SELF-report| > δ           -> contested
  5. runtime H(Ω|D,L) > ε                     -> indeterminate
  6. gap-floor: gap→0 while felt-watched↑     -> contested (deference, not accuracy)
  7. otherwise                                -> estimable

The gap-floor rule sits ABOVE the entropy check in spirit (§5.2): gap trending
to zero while felt-watched rises resolves to contested and halts
personalization, whatever the entropy says.

Also carries the observation-level classifier (8 missingness states -> the
13-status epistemic vocabulary) and the expiry sweep that resolves stale
logbook reads to 'expired' (Formalization Part XI).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Sequence

from em_theory_bayes import VOICE_CORNERS

logger = logging.getLogger("vt_estimate")

# the 13-status epistemic vocabulary (Formalization Part II / migration 002)
EPISTEMIC_STATUSES = frozenset({
    "estimable", "unknown", "indeterminate", "contested",
    "not-presently-interpretable", "declined", "withdrawn", "private",
    "intentionally-unrecorded", "expired", "overridden",
    "not-attributable", "meaningful-but-not-classifiable",
})

# observation missingness -> epistemic status (observations table, migration 002)
_MISSINGNESS_TO_STATUS = {
    "observed": "estimable",
    "unavailable": "unknown",
    "declined": "declined",
    "private": "private",
    "expired": "expired",
    "sensor_failure": "indeterminate",
    "not_applicable": "not-presently-interpretable",
    "intentionally_unrecorded": "intentionally-unrecorded",
}


@dataclass(frozen=True)
class EstimateContext:
    """Everything the wrapper needs to resolve one window's Estimate(τ)."""

    data_present: bool = False
    expired: bool = False
    provenance_admissible: bool = True
    cai_admissible: bool = True
    participant_state: str = "ok"                 # ok | declined | withdrawn
    prediction: Optional[Dict[str, float]] = None  # engine voice predictions
    self_report: Optional[Dict[str, float]] = None  # participant ratings
    delta: float = 0.20                            # contested threshold δ (provisional)
    entropy: float = 0.0                           # H(Ω|D,L) this window, bits
    epsilon: float = 0.30                          # admission-ε (provisional; Phase 3)
    gap_trend_down: bool = False                   # gap → 0
    felt_watched_rising: bool = False              # felt-watched ↑
    posterior: Optional[Dict[str, float]] = None   # emitted ONLY when estimable


@dataclass(frozen=True)
class Estimate:
    """The two-field estimate: (status, posterior). Posterior is None for
    every status except estimable — numbers never surface otherwise."""

    status: str
    posterior: Optional[Dict[str, float]]
    reason: str

    def __post_init__(self) -> None:
        if self.status not in EPISTEMIC_STATUSES:
            raise ValueError(f"unknown epistemic status: {self.status}")
        if self.status != "estimable" and self.posterior is not None:
            raise ValueError(f"posterior surfaced under status '{self.status}' — forbidden (R-2)")

    @property
    def surfaces_number(self) -> bool:
        return self.status == "estimable" and self.posterior is not None


def estimate(ctx: EstimateContext) -> Estimate:
    """Resolve Estimate(τ) per the §5.2 order (first match wins)."""

    # 1. data empty or expired -> unknown
    if not ctx.data_present or ctx.expired:
        return Estimate("unknown", None, "no fresh data: window empty or expired")

    # 2. provenance or CAI inadmissible -> indeterminate
    if not ctx.provenance_admissible or not ctx.cai_admissible:
        return Estimate("indeterminate", None, "provenance or CAI inadmissible")

    # 3. participant authority absolute (SELF)
    if ctx.participant_state == "declined":
        return Estimate("declined", None, "SELF authority: participant declined this window")
    if ctx.participant_state == "withdrawn":
        return Estimate("withdrawn", None, "SELF authority: participant withdrew")

    # gap-floor rule sits above the numeric checks: deference, not accuracy
    if ctx.gap_trend_down and ctx.felt_watched_rising:
        return Estimate("contested", None, "gap-floor rule: gap→0 with felt-watched↑ = deference, not accuracy — personalization halted")

    # 4. prediction vs SELF-report deviates beyond δ -> contested
    if ctx.prediction is None or ctx.self_report is None:
        return Estimate("indeterminate", None, "cannot reconcile: prediction or SELF-report missing")
    max_dev = max(abs(ctx.prediction.get(v, 0.0) - ctx.self_report.get(v, 0.0)) for v in VOICE_CORNERS)
    if max_dev > ctx.delta:
        return Estimate("contested", None, f"prediction vs SELF-report deviates {max_dev:.3f} > δ={ctx.delta}")

    # 5. runtime H(Ω|D,L) > ε -> indeterminate
    if ctx.entropy > ctx.epsilon:
        return Estimate("indeterminate", None, f"runtime H={ctx.entropy:.3f} > ε={ctx.epsilon}")

    # 7. otherwise -> estimable
    return Estimate("estimable", ctx.posterior, "estimable")


def classify_missingness(missingness: str) -> str:
    """Map an observations-table missingness state to the epistemic vocabulary
    (migration 002 -> Formalization Part II). Raises on unknown states."""
    try:
        return _MISSINGNESS_TO_STATUS[missingness]
    except KeyError:
        raise ValueError(f"unknown missingness state: {missingness!r}") from None


def sweep_expired(rows: Sequence[Mapping[str, Any]], now_iso: str) -> List[Dict[str, Any]]:
    """Resolve stale reads to 'expired' (Formalization Part XI): any row whose
    valid_until < now is returned with epistemic_status='expired'. Rows with
    no valid_until declare no expiry and are untouched. Caller persists."""
    updates: List[Dict[str, Any]] = []
    for r in rows:
        valid_until = r.get("valid_until")
        if valid_until and str(valid_until) < now_iso:
            updated = dict(r)
            updated["epistemic_status"] = "expired"
            updates.append(updated)
    return updates


def main() -> int:
    """Demo: resolve one window each way down the §5.2 order (synthetic)."""
    base = EstimateContext(data_present=True, prediction={v: 0.5 for v in VOICE_CORNERS},
                           self_report={v: 0.5 for v in VOICE_CORNERS}, entropy=0.1,
                           posterior={c: 0.5 for c in ("EM2", "EM4", "EM8", "EM10")})
    cases = [
        ("estimable", base),
        ("unknown (no data)", EstimateContext(data_present=False)),
        ("unknown (expired)", EstimateContext(data_present=True, expired=True)),
        ("indeterminate (CAI)", EstimateContext(data_present=True, cai_admissible=False)),
        ("declined", EstimateContext(data_present=True, participant_state="declined")),
        ("contested (δ)", EstimateContext(data_present=True, prediction={v: 0.9 for v in VOICE_CORNERS},
                                          self_report={v: 0.1 for v in VOICE_CORNERS})),
        ("indeterminate (H>ε)", EstimateContext(data_present=True, entropy=0.8,
                                                prediction={v: 0.5 for v in VOICE_CORNERS},
                                                self_report={v: 0.5 for v in VOICE_CORNERS})),
        ("contested (gap-floor)", EstimateContext(data_present=True, gap_trend_down=True,
                                                  felt_watched_rising=True,
                                                  prediction={v: 0.5 for v in VOICE_CORNERS},
                                                  self_report={v: 0.5 for v in VOICE_CORNERS})),
    ]
    print("=== VT-1 ESTIMATE(τ) RESOLUTION (synthetic demo) ===")
    for label, ctx in cases:
        e = estimate(ctx)
        print(f"{label:<24} -> {e.status:<12} posterior={'YES' if e.surfaces_number else 'no '}  ({e.reason})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
