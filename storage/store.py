#!/usr/bin/env python3
"""storage/store.py — the Measurement Logbook writer (spec A.6 / bp_c_em.yaml).

Fail-closed at WRITE time, not just construction: every row must carry the
engine-minimum provenance (source, timestamp, schema_version, confidence,
actor) and the 9 logbook columns; empty/missing fields raise. The engine
Provenance dataclass fields map onto the schema as documented in the yaml.

Industry best-practices: schema applied idempotently on connect, WAL mode,
parameterized inserts only (no string-built SQL), explicit transaction
semantics, read-back helpers for the M2 sufficiency harness.

Usage:
    from storage.store import Logbook
    store = Logbook(Path("data/logbook.sqlite3"))
    store.write_row(...)          # fail-closed
    rows = store.read_windows(arm="with_substrate")
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from vt_estimate import EPISTEMIC_STATUSES  # the 13-status vocabulary (R-2)

_SCHEMA = Path(__file__).parent / "schema.sql"

# migration chain (VT-1): schema.sql (v0.1) -> 001_vertical_time.sql -> 002_vt_synthesis.sql
# PRAGMA user_version: 0 (fresh) -> 1 -> 2 -> 3. The ALTER-based migrations are
# applied ONCE per database, each in its own transaction (atomic), and gated by
# user_version so reopening an existing database is always safe.
_MIGRATION_SCRIPTS = ("001_vertical_time.sql", "002_vt_synthesis.sql")

LOGBOOK_COLUMNS = [
    "substrate_vector", "voice_prediction", "voice_report", "gap_per_voice",
    "gap_mean", "CSI", "model_version", "timestamp", "human_correction_flag",
    "source", "actor", "confidence", "arm", "window_id",
    # --- VT-1 (001 + 002) ---
    "layer", "mono_ns", "clock_skew_ns", "epistemic_status", "valid_until", "boundary_id",
]

_LAYERS = ("physical", "psychophysiological", "symbolic")


class LogbookError(RuntimeError):
    """Raised when a write violates the provenance contract (fail-closed)."""


@dataclass(frozen=True)
class LogbookRow:
    """One logbook row — the M1 write target, mirroring schema.sql."""

    substrate_vector: Dict[str, float]
    voice_prediction: Dict[str, float]
    voice_report: Dict[str, float]
    gap_per_voice: Dict[str, float]
    gap_mean: float
    csi: float
    model_version: str
    timestamp: str
    human_correction_flag: int = 0
    source: str = ""
    actor: str = ""
    confidence: float = 1.0
    arm: Optional[str] = None
    window_id: Optional[str] = None
    # --- VT-1 (001 + 002): layer tag, monotonic clock, two-field estimate ---
    layer: str = "psychophysiological"
    mono_ns: Optional[int] = None
    clock_skew_ns: Optional[int] = None
    epistemic_status: str = "estimable"
    valid_until: Optional[str] = None
    boundary_id: Optional[str] = None

    def validate(self) -> None:
        """Fail-closed: every required field present and in range."""
        for name, val in {
            "substrate_vector": self.substrate_vector,
            "voice_prediction": self.voice_prediction,
            "voice_report": self.voice_report,
            "gap_per_voice": self.gap_per_voice,
            "model_version": self.model_version,
            "timestamp": self.timestamp,
            "source": self.source,
            "actor": self.actor,
        }.items():
            if not val:
                raise LogbookError(f"logbook write rejected: empty field '{name}'")
        if not (0.0 <= self.gap_mean <= 1.0):
            raise LogbookError(f"gap_mean out of range: {self.gap_mean}")
        if not (0.0 <= self.csi <= 1.0):
            raise LogbookError(f"csi out of range: {self.csi}")
        if not (0.0 <= self.confidence <= 1.0):
            raise LogbookError(f"confidence out of range: {self.confidence}")
        if self.human_correction_flag not in (0, 1):
            raise LogbookError(f"human_correction_flag must be 0/1: {self.human_correction_flag}")
        if self.layer not in _LAYERS:
            raise LogbookError(f"layer must be one of {_LAYERS}: {self.layer}")
        if self.epistemic_status not in EPISTEMIC_STATUSES:
            raise LogbookError(f"epistemic_status must be one of the 13: {self.epistemic_status}")

    def as_sql_tuple(self) -> tuple:
        self.validate()
        return (
            json.dumps(self.substrate_vector, sort_keys=True),
            json.dumps(self.voice_prediction, sort_keys=True),
            json.dumps(self.voice_report, sort_keys=True),
            json.dumps(self.gap_per_voice, sort_keys=True),
            self.gap_mean,
            self.csi,
            self.model_version,
            self.timestamp,
            self.human_correction_flag,
            self.source,
            self.actor,
            self.confidence,
            self.arm,
            self.window_id,
            self.layer,
            self.mono_ns,
            self.clock_skew_ns,
            self.epistemic_status,
            self.valid_until,
            self.boundary_id,
        )


class Logbook:
    """SQLite-backed Measurement Logbook with fail-closed writes."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.path))
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._apply_schema()

    def _apply_schema(self) -> None:
        """Apply the VT-1 migration chain, once per database.

        schema.sql is idempotent DDL (IF NOT EXISTS) and safe to re-run;
        the ALTER-based 001/002 migrations are gated by PRAGMA user_version
        and each applied atomically in its own transaction, so reopening an
        existing database never re-runs (or half-runs) an ALTER.
        """
        version = int(self._conn.execute("PRAGMA user_version").fetchone()[0])
        if version < 1:
            self._conn.executescript(_SCHEMA.read_text())
            self._conn.execute("PRAGMA user_version = 1")
        for step, name in enumerate(_MIGRATION_SCRIPTS, start=2):
            if version >= step:
                continue
            script = (Path(__file__).parent / name).read_text()
            statements = _split_sql_statements(script)
            with self._conn:  # one transaction per migration — atomic
                for stmt in statements:
                    self._conn.execute(stmt)
            self._conn.execute(f"PRAGMA user_version = {step}")

    # --- writes (fail-closed) -------------------------------------------------
    def write_row(self, row: LogbookRow) -> None:
        """Insert one logbook row; raises LogbookError on any contract violation."""
        cols = ", ".join(LOGBOOK_COLUMNS)
        marks = ", ".join("?" * len(LOGBOOK_COLUMNS))
        with self._conn:  # atomic transaction
            self._conn.execute(
                f"INSERT INTO logbook ({cols}) VALUES ({marks})", row.as_sql_tuple()
            )

    def write_many(self, rows: List[LogbookRow]) -> int:
        """Batch insert; all-or-nothing (atomic)."""
        with self._conn:
            self._conn.executemany(
                f"INSERT INTO logbook ({', '.join(LOGBOOK_COLUMNS)}) "
                f"VALUES ({', '.join('?' * len(LOGBOOK_COLUMNS))})",
                [r.as_sql_tuple() for r in rows],
            )
        return len(rows)

    # --- reads (for the M2 sufficiency harness) --------------------------------
    def read_windows(self, arm: Optional[str] = None, limit: int = 1000) -> List[Dict[str, Any]]:
        q = "SELECT * FROM logbook"
        args: tuple = ()
        if arm is not None:
            q += " WHERE arm = ?"
            args = (arm,)
        q += " ORDER BY timestamp LIMIT ?"
        cur = self._conn.execute(q, args + (limit,))
        rows = []
        for r in cur.fetchall():
            d = dict(r)
            for k in ("substrate_vector", "voice_prediction", "voice_report", "gap_per_voice"):
                if d.get(k):
                    d[k] = json.loads(d[k])
            rows.append(d)
        return rows

    def count(self) -> int:
        return int(self._conn.execute("SELECT COUNT(*) FROM logbook").fetchone()[0])

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "Logbook":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()


def _split_sql_statements(script: str) -> List[str]:
    """Split a SQL script on statement terminators, ignoring ';' inside '--'
    line comments. (The migration scripts contain no multi-line string
    literals; CHECK constraints use single quotes only.)"""
    statements: List[str] = []
    buf: List[str] = []
    for line in script.splitlines():
        code = line.split("--", 1)[0]  # strip the line comment, if any
        parts = code.split(";")
        buf.append(parts[0])
        for extra in parts[1:]:        # remainder after ';' starts the next statement
            statements.append("\n".join(buf))
            buf = [extra]
    if buf:
        statements.append("\n".join(buf))
    return [s.strip() for s in statements if s.strip()]
