"""test_numerical_oracles.py — adopted-reference oracles for OOAO math kernels.

`cds` (Furox-Art, scientific-computing-system) is the pinned, audited reference
for commodity math in this repo: MIT, pure-Python, zero-dependency. Audited
2026-09-02 at commit 02931a8 (2395 tests, machine-precision oracles vs
scipy/numpy). NOTE ON PROVENANCE: line anchors and behavior in this file refer
to that AUDITED COMMIT, which is what requirements.txt git-pins — PyPI 1.7.0
lags it (missing cds/infotheory and cds/stats/power).

These gates check OOAO's own kernels against the reference so the repo's
hand-written code is never trusted on faith. vt_recoverability's entropy/jsd
delegate to cds (defensive normalization preserved — cds requires distributions
summing to 1); the engine-posterior contract (unnormalized, scale-invariant
input) is pinned here via test_vt_entropy_accepts_unnormalized_engine_posteriors.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # noqa: E402

import numpy as np  # noqa: E402
import pytest  # noqa: E402

import vt_recoverability as vr  # noqa: E402
from cds.infotheory.measures import entropy as cds_entropy  # noqa: E402
from cds.infotheory.measures import js_divergence as cds_js  # noqa: E402
from cds.signals.processing import power_spectrum  # noqa: E402
from m2_sufficiency import run_sufficiency  # noqa: E402


def _norm(mapping):
    total = sum(mapping.values())
    return {k: v / total for k, v in mapping.items()}


def _to_list(mapping):
    return [float(v) for v in mapping.values()]


# --- 1. entropy parity ---------------------------------------------------------

def test_vt_entropy_matches_cds_reference():
    for mapping in ({"a": 0.25, "b": 0.25, "c": 0.25, "d": 0.25},
                    {"a": 1.0},
                    {"a": 0.7, "b": 0.3}):
        ref = cds_entropy(_to_list(_norm(mapping)), base=2.0)
        assert vr.entropy(mapping) == pytest.approx(ref, abs=1e-9)


def test_vt_entropy_accepts_unnormalized_engine_posteriors():
    # Engine posteriors are per-corner activations, not distributions; entropy
    # must be scale-invariant AND match the cds reference on the normalized form.
    raw = {"EM2": 0.4, "EM4": 0.5, "EM8": 0.6, "EM10": 0.7}
    ref = cds_entropy(_to_list(_norm(raw)), base=2.0)
    assert vr.entropy(raw) == pytest.approx(ref, abs=1e-9)
    assert vr.entropy(raw) == pytest.approx(vr.entropy(_norm(raw)), abs=1e-12)


# --- 2. Jensen-Shannon divergence parity ---------------------------------------

def test_vt_jsd_matches_cds_reference():
    p = {"EM2": 0.6, "EM4": 0.2, "EM8": 0.1, "EM10": 0.1}
    q = {"EM2": 0.1, "EM4": 0.2, "EM8": 0.3, "EM10": 0.4}
    ref = cds_js(_to_list(p), _to_list(q), base=2.0)
    assert vr.jsd(p, q) == pytest.approx(ref, abs=1e-9)
    assert vr.jsd(p, p) == pytest.approx(0.0, abs=1e-12)
    assert 0.0 <= vr.jsd(p, q) <= 1.0


def test_vt_jsd_dynamic_range_near_zero_entries():
    # Characterization pin across dynamic range: near-zero entries (~1e-6) must
    # agree with the reference at oracle tolerance. The former hand-rolled _kl
    # blurred eps INSIDE the log, violating 0*log0 := 0; adoption removes the
    # class regardless of magnitude.
    p = {"a": 1e-6, "b": 1.0 - 1e-6}
    q = {"a": 0.5, "b": 0.5}
    ref = cds_js(_to_list(p), _to_list(q), base=2.0)
    assert vr.jsd(p, q) == pytest.approx(ref, abs=1e-9)


# --- 3. M2 sufficiency CI + power (paired bootstrap, descriptive) --------------

def test_m2_improvement_ci_and_power_present():
    res = run_sufficiency(n_windows=120, seed=42)
    assert res.improvement_ci is not None
    lo, hi = res.improvement_ci
    assert lo <= hi
    assert hi - lo > 0.0
    assert res.power_report is not None
    assert 0.0 <= res.power_report["power"] <= 1.0
    # descriptive-only discipline: the CI must NOT be asserted to exclude 0 on
    # synthetic data (Council N2) — presence and sanity are the contract here.


# --- 4. adopted spectral kernel works in-env (deterministic parity) ------------

def test_cds_spectral_kernel_matches_numpy():
    # cds power_spectrum == |FFT|^2/N. Deterministic smoke that the adopted
    # kernel integrates in this environment (future HRV LF/HF cross-check
    # harness builds on it; neurokit2 remains the runtime HRV source).
    t = np.linspace(0.0, 10.0, 128, endpoint=False)
    sig = np.sin(2 * np.pi * 2.0 * t) + 0.5 * np.sin(2 * np.pi * 5.0 * t)
    ps = np.array(power_spectrum([float(x) for x in sig]))
    ref = np.abs(np.fft.fft(sig)) ** 2.0 / len(sig)
    assert np.max(np.abs(ps - ref)) == pytest.approx(0.0, abs=1e-9)
