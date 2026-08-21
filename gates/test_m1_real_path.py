"""test_m1_real_path.py — M1 hardware-ready integration (T8-T10/T19 wiring).

Covers the NEW modules built for the real-M1 path (polar_capture.py,
hrv_pipeline.py, retention_purge.py) so M1 is READY the moment hardware
arrives. All tests run on the synthetic path (mock-first, E5) — the real
BLE branch is gated behind PolarUnavailable until the strap is present.

Run:  pytest gates/test_m1_real_path.py -v
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import polar_capture as pc  # noqa: E402
import hrv_pipeline as hp  # noqa: E402
import retention_purge as rp  # noqa: E402
import em_theory_bayes as eb  # noqa: E402


# --- polar_capture ------------------------------------------------------------

def test_mock_capture_returns_valid_window():
    win = pc.capture_rr_window(mock=True, n=300, seed=7)
    assert len(win.rr_intervals_ms) == 300
    assert all(600.0 <= rr <= 1200.0 for rr in win.rr_intervals_ms)
    prov = win.as_provenance()
    prov.validate()  # provenance complete
    assert win.source == "synthetic.capture"  # FAKE-DATA labeled


def test_real_capture_gated_when_no_hardware():
    # No strap present in this environment -> real capture must raise
    # PolarUnavailable, never fabricate data.
    with pytest.raises(pc.PolarUnavailable):
        pc.capture_rr_window(mock=False)


def test_polar_present_probe_returns_bool():
    assert isinstance(pc.is_polar_present(), bool)


# --- hrv_pipeline (T9/T10 wiring) ---------------------------------------------

@pytest.fixture(scope="module")
def engine():
    return eb.EmTheoryBayes(mock=True)


def test_pipeline_closes_loop(engine):
    win = pc.capture_rr_window(mock=True, n=300, seed=7)
    r = hp.run_pipeline(win, engine)
    assert r.features.rmssd > 0
    assert 0.0 <= r.posterior.probabilities["EM8"] <= 1.0
    assert all(0.0 <= v <= 1.0 for v in r.prediction.probabilities.values())
    assert 0.0 <= r.gap.value <= 1.0
    assert r.source == "synthetic.capture"


def test_pipeline_posterior_covers_all_substrate_corners(engine):
    win = pc.capture_rr_window(mock=True, n=300, seed=7)
    r = hp.run_pipeline(win, engine)
    assert set(r.posterior.probabilities) == set(eb.SUBSTRATE_CORNERS)


def test_feature_extraction_field_standard(engine):
    win = pc.capture_rr_window(mock=True, n=300, seed=7)
    f = hp.extract_hrv_features(win.rr_intervals_ms)
    assert 5.0 <= f.rmssd <= 120.0
    assert 5.0 <= f.sdnn <= 150.0
    assert f.pnn50 >= 0.0


# --- retention_purge (T19 / OC-4) ----------------------------------------------

def test_dry_run_purges_nothing(tmp_path):
    # an empty (or absent) raw dir, dry-run, must delete nothing
    rp.RAW_DIR = tmp_path / "raw"  # redirect for test isolation
    res = rp.purge_expired_raw(datetime.now(timezone.utc))
    assert res.raw_purged == 0


def test_raw_window_older_than_30d_is_purged(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir(parents=True)
    # create an old raw window + sidecar
    old_ts = (datetime.now(timezone.utc) - timedelta(days=40)).isoformat()
    (raw / "win1.json").write_text("{}")
    (raw / "win1.meta.json").write_text(
        f'{{"captured_at": "{old_ts}"}}')
    rp.RAW_DIR = raw
    rp.ERASURE_LEDGER = raw / ".erasure_ledger.jsonl"
    res = rp.purge_expired_raw(datetime.now(timezone.utc))
    assert res.raw_purged == 1
    # content hard-deleted (irreversible)
    assert not (raw / "win1.json").exists()
    # fact of erasure logged (provable, auditable)
    ledger = (raw / ".erasure_ledger.jsonl").read_text()
    assert "biometric_erasure" in ledger
    assert "win1.json" in ledger


def test_fresh_raw_window_not_purged(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir(parents=True)
    fresh_ts = datetime.now(timezone.utc).isoformat()
    (raw / "win2.json").write_text("{}")
    (raw / "win2.meta.json").write_text(f'{{"captured_at": "{fresh_ts}"}}')
    rp.RAW_DIR = raw
    rp.ERASURE_LEDGER = raw / ".erasure_ledger.jsonl"
    res = rp.purge_expired_raw(datetime.now(timezone.utc))
    assert res.raw_purged == 0
    assert (raw / "win2.json").exists()


def test_feature_rows_older_than_90d_purged_from_features_store(tmp_path):
    fs = tmp_path / "features"
    fs.mkdir(parents=True)
    old_ts = (datetime.now(timezone.utc) - timedelta(days=100)).isoformat()
    (fs / "feat1.json").write_text("{}")
    (fs / "feat1.meta.json").write_text(f'{{"captured_at": "{old_ts}"}}')
    res = rp.purge_feature_rows(fs, datetime.now(timezone.utc))
    assert res.feature_rows_purged == 1
    assert not (fs / "feat1.json").exists()


def test_fresh_feature_rows_not_purged(tmp_path):
    fs = tmp_path / "features"
    fs.mkdir(parents=True)
    fresh_ts = datetime.now(timezone.utc).isoformat()
    (fs / "feat2.json").write_text("{}")
    (fs / "feat2.meta.json").write_text(f'{{"captured_at": "{fresh_ts}"}}')
    res = rp.purge_feature_rows(fs, datetime.now(timezone.utc))
    assert res.feature_rows_purged == 0
    assert (fs / "feat2.json").exists()


def test_purge_never_touches_logbook(tmp_path):
    # The purge functions must NOT scan the logbook (Class C/D). Verify the
    # features-store purge ignores a sqlite logbook file placed alongside.
    fs = tmp_path / "features"
    fs.mkdir(parents=True)
    # simulate a logbook sqlite in the same dir — purge must ignore it
    lb = fs / "logbook.sqlite3"
    lb.write_bytes(b"not-a-json")
    res = rp.purge_feature_rows(fs, datetime.now(timezone.utc))
    assert lb.exists(), "logbook must never be purged by the features-store purge"


def test_mirror_invalidation_hook_called(tmp_path):
    # placeholder that must not crash on empty set
    rp.mirror_invalidation_hook([])
    rp.mirror_invalidation_hook(["win1.json"])
