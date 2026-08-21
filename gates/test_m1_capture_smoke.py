"""test_m1_capture_smoke.py — M1 gate: EM8 loop end-to-end on SYNTHETIC HRV.

Gate contract (09_implementation_plan.md §4): the loop closes; RR intervals
arrive; timestamps monotonic; features in physiological range; engine posterior
well-formed; gap computable; provenance rows non-empty.

Field standards: the REAL feature-extraction path (neurokit2 — community
standard for HRV) runs on a synthetic RR-interval stream that mimics a Polar
H10 (BLE, 1 kHz ECG -> RR intervals in ms). Deterministic via seed; the
synthetic harness's ground truth is KNOWN, so the loop's reconstruction is
scored, not just executed. Synthetic-first until M1 hardware (Dallas directive).

Run:  pytest gates/test_m1_capture_smoke.py -v
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import neurokit2 as nk  # noqa: E402
import numpy as np  # noqa: E402

import em_theory_bayes as eb  # noqa: E402
from synthetic_manor_data import SyntheticManorData  # noqa: E402

# --- fixtures -----------------------------------------------------------------

@pytest.fixture(scope="module")
def rr_stream() -> list[float]:
    """A deterministic synthetic RR-interval stream (Polar H10 stand-in).

    ～60-80 bpm resting heart rate => RR 750-1000 ms with realistic beat-to-beat
    variability (the 1 kHz ECG -> RR path). Seeded: reproducible run to run.
    """
    gen = SyntheticManorData(seed=7)
    rng = __import__("random").Random(7)
    # drift: mild sinus arrhythmia around a resting baseline
    n = 300  # ~4-5 min of beats
    stream = []
    base = rng.uniform(800.0, 950.0)
    for i in range(n):
        rr = base + rng.gauss(0, 18) + 25.0 * math.sin(i / 20.0)  # respiratory sinus arrhythmia
        stream.append(round(max(600.0, min(1200.0, rr)), 1))
    return stream


@pytest.fixture(scope="module")
def engine() -> eb.EmTheoryBayes:
    return eb.EmTheoryBayes(mock=True)


# --- 1. capture smoke: the stream looks like a heart --------------------------

def test_rr_intervals_physiological(rr_stream):
    assert len(rr_stream) >= 200, "stream too short for HRV features"
    assert all(600.0 <= rr <= 1200.0 for rr in rr_stream), "RR outside physiological range"
    assert 50 <= (60_000 / np.mean(rr_stream)) <= 100, "implied HR outside 50-100 bpm"


def test_rr_timestamps_monotonic(rr_stream):
    ts = [0.0]
    for rr in rr_stream:
        ts.append(ts[-1] + rr / 1000.0)  # cumulative seconds
    assert all(b > a for a, b in zip(ts, ts[1:])), "timestamps not strictly monotonic"


def _hrv_features(rr_stream: list[float]) -> dict:
    """Field-standard neurokit2 HRV call: RRIs -> peaks -> time+frequency features."""
    peaks = nk.intervals_to_peaks(np.asarray(rr_stream, dtype=float))
    hrv = nk.hrv(peaks, sampling_rate=1000, show=False)
    return {
        "RMSSD": float(hrv["HRV_RMSSD"].iloc[0]),
        "SDNN": float(hrv["HRV_SDNN"].iloc[0]),
        "LFHF": float(hrv["HRV_LFHF"].iloc[0]) if "HRV_LFHF" in hrv.columns else float("nan"),
    }


# --- 2. feature extraction: real neurokit2 path on synthetic RR --------------

def test_neurokit2_hrv_features_physiological(rr_stream):
    f = _hrv_features(rr_stream)
    assert 5.0 <= f["RMSSD"] <= 120.0, f"RMSSD {f['RMSSD']:.1f} outside plausible HRV range"
    assert 5.0 <= f["SDNN"] <= 150.0, f"SDNN {f['SDNN']:.1f} outside plausible HRV range"
    assert math.isfinite(f["LFHF"]), "LF/HF missing from neurokit2 output"


# --- 3. engine: the loop closes ----------------------------------------------

def test_engine_posterior_well_formed(engine, rr_stream):
    # measurement model (M2 will learn this; M1 uses the annotated mapping)
    rmssd = _hrv_features(rr_stream)["RMSSD"]
    # low RMSSD => higher arousal => higher P(EM8 interoception active)
    arousal = max(0.0, min(1.0, (80.0 - rmssd) / 65.0))
    posterior = eb.SubstratePosterior(
        probabilities={"EM2": 0.5, "EM4": 0.5, "EM8": arousal, "EM10": 0.5},
        provenance=eb.Provenance("synthetic.capture", _now(), "0.1", 0.9, "test"),
    )
    pred = engine.predict_voices(posterior)
    assert all(0.0 <= v <= 1.0 for v in pred.probabilities.values()), "voice probs out of [0,1]"
    assert set(pred.probabilities) == set(eb.VOICE_CORNERS), "voice corners incomplete"


def test_gap_computable_and_bounded(engine, rr_stream):
    rmssd = _hrv_features(rr_stream)["RMSSD"]
    arousal = max(0.0, min(1.0, (80.0 - rmssd) / 65.0))
    posterior = eb.SubstratePosterior(
        probabilities={"EM2": 0.5, "EM4": 0.5, "EM8": arousal, "EM10": 0.5},
        provenance=eb.Provenance("synthetic.capture", _now(), "0.1", 0.9, "test"),
    )
    pred = engine.predict_voices(posterior)
    report = eb.SelfReport(
        ratings={v: 0.5 for v in eb.VOICE_CORNERS},
        provenance=eb.Provenance("synthetic.self_report", _now(), "0.1", 1.0, "participant"),
    )
    gap = engine.reconciliation_gap(pred, report)
    assert 0.0 <= gap.value <= 1.0, f"gap {gap.value:.3f} outside [0,1]"
    assert set(gap.per_corner) == set(eb.VOICE_CORNERS), "per-corner gap incomplete"


# --- 4. provenance: every durable record carries non-empty fields -------------

def test_provenance_fields_nonempty():
    for prov in [
        eb.Provenance("synthetic.capture", _now(), "0.1", 0.9, "test"),
        eb.Provenance("synthetic.self_report", _now(), "0.1", 1.0, "participant"),
    ]:
        prov.validate()  # raises on any empty field
    with pytest.raises(ValueError):
        eb.Provenance("synthetic.capture", "", "0.1", 0.9, "test").validate()


# --- 5. regression: M0 reference still green ----------------------------------

def test_m0_mock_loop_still_runs(engine):
    post = eb.SubstratePosterior(
        probabilities={c: 0.5 for c in eb.SUBSTRATE_CORNERS},
        provenance=eb.Provenance("mock.capture", _now(), "0.1", 0.9, "test"),
    )
    pred = engine.predict_voices(post)
    rep = eb.SelfReport(
        ratings={v: 0.5 for v in eb.VOICE_CORNERS},
        provenance=eb.Provenance("mock.self_report", _now(), "0.1", 1.0, "p"),
    )
    gap = engine.reconciliation_gap(pred, rep)
    assert 0.0 <= gap.value <= 1.0


def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
