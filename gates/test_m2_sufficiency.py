"""test_m2_sufficiency.py — M2 gate: harness validity + synthetic GO/NO-GO.

Two layers of assertion:
  1. HARNESS VALIDITY (the meta-gate): on synthetic data with KNOWN ground
     truth, the harness must recover the injected signal structure — RMSSD
     tracks EM8 (generator: arousal -> low RMSSD) so EM8 must show GO; the
     no-sensor baseline must sit near Brier 0.25 (coin-flip ceiling) because
     the injected EM8>0.5 rate is ~0.5.
  2. DISCIPLINE: the result must be labeled synthetic and the artifact must
     carry the FAKE DATA note — synthetic results validate the harness, not
     the hypothesis (the Meng/A3/A4 lesson applied to our own outputs).

Run:  pytest gates/test_m2_sufficiency.py -v
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from m2_sufficiency import _brier, run_sufficiency  # noqa: E402


def test_baseline_brier_near_coinflip():
    """No-sensor baseline predicting 0.5 against ~50% rate => Brier ~0.25."""
    res = run_sufficiency(n_windows=200, seed=42, corner="EM8")
    assert res.brier_baseline == pytest.approx(0.25, abs=0.02)


def test_em8_go_because_rmssd_tracks_it():
    """The generator injects arousal -> low RMSSD, so the sensor arm must beat
    baseline for EM8 on synthetic data. If this fails, the HARNESS is broken
    (it failed to recover known structure), not the hypothesis."""
    res = run_sufficiency(n_windows=200, seed=42, corner="EM8")
    assert res.improvement > 0.05, f"harness failed to recover injected EM8 signal: {res.improvement}"
    assert res.gate_read.startswith("GO")


def test_em4_marginal_because_rmssd_does_not_carry_it():
    """EM4 is driven by load in the generator, not RMSSD — the sensor arm
    should NOT strongly beat baseline for EM4 (the harness correctly detects
    that RMSSD does not measure perception)."""
    res = run_sufficiency(n_windows=200, seed=42, corner="EM4")
    assert res.improvement < 0.05, f"harness overclaims RMSSD->EM4: {res.improvement}"


def test_brier_bounds():
    res = run_sufficiency(n_windows=200, seed=42, corner="EM8")
    assert 0.0 <= res.brier_with_substrate <= 0.25
    assert 0.0 <= res.brier_baseline <= 0.25


def test_artifact_is_labeled_synthetic(tmp_path, monkeypatch):
    """FAKE DATA discipline: the artifact must say synthetic and carry the note."""
    import sys as _sys
    from m2_sufficiency import main as m2_main

    out = tmp_path / "m2.json"
    monkeypatch.setattr(_sys, "argv", ["m2_sufficiency.py", "--n", "50", "--out", str(out)])
    m2_main()
    artifact = json.loads(out.read_text())
    assert artifact["synthetic"] is True
    assert artifact["note"].startswith("FAKE DATA")
    assert artifact["protocol"].startswith("B.6")
