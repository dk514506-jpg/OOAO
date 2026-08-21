"""test_storage.py — M1 "provenance logs write" gate.

End-to-end: synthetic HRV -> engine (predict_voices + reconciliation_gap) ->
Logbook.write_row -> read back -> assert all 9 A.6 logbook columns populated
and provenance intact. Plus the fail-closed write paths (empty field rejected,
out-of-range rejected).

Run:  pytest gates/test_storage.py -v
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "storage"))

import em_theory_bayes as eb  # noqa: E402
from storage.store import Logbook, LogbookError, LogbookRow  # noqa: E402

LOGBOOK_COLUMNS = [
    "substrate_vector", "voice_prediction", "voice_report", "gap_per_voice",
    "gap_mean", "CSI", "model_version", "timestamp", "human_correction_flag",
]


@pytest.fixture()
def store(tmp_path):
    s = Logbook(tmp_path / "logbook.sqlite3")
    yield s
    s.close()


@pytest.fixture()
def engine() -> eb.EmTheoryBayes:
    return eb.EmTheoryBayes(mock=True)


def _row_from_engine(engine: eb.EmTheoryBayes, ts: str) -> LogbookRow:
    """One synthetic window through the engine, shaped into a logbook row."""
    post = eb.SubstratePosterior(
        probabilities={"EM2": 0.5, "EM4": 0.5, "EM8": 0.6, "EM10": 0.5},
        provenance=eb.Provenance("synthetic.capture", ts, "0.1", 0.9, "test"),
    )
    pred = engine.predict_voices(post)
    rep = eb.SelfReport(
        ratings={v: 0.5 for v in eb.VOICE_CORNERS},
        provenance=eb.Provenance("synthetic.self_report", ts, "0.1", 1.0, "participant"),
    )
    gap = engine.reconciliation_gap(pred, rep)
    return LogbookRow(
        substrate_vector=post.probabilities,
        voice_prediction=pred.probabilities,
        voice_report=rep.ratings,
        gap_per_voice=gap.per_corner,
        gap_mean=gap.value,
        csi=0.8,
        model_version="0.1",
        timestamp=ts,
        source="engine.reconciliation_gap",
        actor="test",
        confidence=0.9,
        arm="with_substrate",
        window_id="win-0001",
    )


def test_write_and_readback_all_9_logbook_columns(store, engine):
    ts = _now()
    store.write_row(_row_from_engine(engine, ts))
    assert store.count() == 1
    rows = store.read_windows(arm="with_substrate")
    assert len(rows) == 1
    row = rows[0]
    for col in LOGBOOK_COLUMNS:
        assert row.get(col) not in (None, ""), f"logbook column '{col}' empty"
    # the JSON columns round-trip as dicts
    assert set(row["substrate_vector"]) == set(eb.SUBSTRATE_CORNERS)
    assert set(row["voice_prediction"]) == set(eb.VOICE_CORNERS)
    assert set(row["voice_report"]) == set(eb.VOICE_CORNERS)
    assert set(row["gap_per_voice"]) == set(eb.VOICE_CORNERS)
    assert 0.0 <= row["gap_mean"] <= 1.0
    assert 0.0 <= row["CSI"] <= 1.0
    assert row["timestamp"] == ts


def test_write_batch_atomic(store, engine):
    ts = _now()
    rows = [_row_from_engine(engine, f"{ts}-{i:03d}") for i in range(3)]
    n = store.write_many(rows)
    assert n == 3
    assert store.count() == 3


def test_write_rejects_empty_provenance_field(store):
    with pytest.raises(LogbookError, match="empty field"):
        store.write_row(LogbookRow(
            substrate_vector={"EM8": 0.5}, voice_prediction={"EM3": 0.5},
            voice_report={"EM3": 0.5}, gap_per_voice={"EM3": 0.0},
            gap_mean=0.5, csi=0.8, model_version="0.1", timestamp=_now(),
            source="", actor="test",  # source empty -> rejected
        ))


def test_write_rejects_out_of_range_csi(store):
    with pytest.raises(LogbookError, match="out of range"):
        store.write_row(LogbookRow(
            substrate_vector={"EM8": 0.5}, voice_prediction={"EM3": 0.5},
            voice_report={"EM3": 0.5}, gap_per_voice={"EM3": 0.0},
            gap_mean=0.5, csi=1.7, model_version="0.1", timestamp=_now(),
            source="engine", actor="test",
        ))


def test_schema_idempotent_reopen(tmp_path):
    """Reopening the same path re-applies schema without error (WAL-safe)."""
    p = tmp_path / "logbook.sqlite3"
    s1 = Logbook(p)
    s1.close()
    s2 = Logbook(p)  # second open applies schema again — must not fail
    s2.close()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
