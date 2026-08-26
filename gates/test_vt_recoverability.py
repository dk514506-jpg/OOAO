"""test_vt_recoverability.py — the 13 vertical-time certification gates.

Covers vt_recoverability.py: entropy (bits), JSD, Brier deltas, the Certify(c)
checkpoint (pass / ε / coverage / margin failures), the R-5 non-binding rule,
fail-closed contract loading, and the paper §21 stability/discriminability
pair. Thresholds come only from (registered) fixtures — the shipped contract
stays unregistered, exactly as R-5 intends.

Run:  pytest gates/test_vt_recoverability.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import vt_recoverability as vr  # noqa: E402

# --- fixtures ------------------------------------------------------------------


def _contract(registered: bool = True, **threshold_overrides) -> dict:
    thresholds = {
        "epsilon_c": 0.30,
        "coverage_theta": 0.80,
        "brier_margin": 0.02,
        "stability_max_jsd": 0.10,
        "discriminability_min_jsd": 0.20,
    }
    thresholds.update(threshold_overrides)
    return {"registered": registered, "entropy_units": "bits", "thresholds": thresholds}


def _windows(
    entropies=(0.10, 0.15, 0.12, 0.20),
    has_data=(True, True, True, True),
    briers=(0.05, 0.05, 0.05, 0.05),
) -> list:
    return [
        vr.WindowMetrics(window_id=f"w{i:02d}", entropy=e, has_data=h, brier_improvement=b)
        for i, (e, h, b) in enumerate(zip(entropies, has_data, briers))
    ]


def _sig(a=0.9, b=0.05, c=0.03, d=0.02):
    return {"EM2": a, "EM4": b, "EM8": c, "EM10": d}


# --- 1. entropy ----------------------------------------------------------------

def test_entropy_uniform_is_max_bits():
    # uniform over 4 outcomes = exactly 2 bits of uncertainty
    assert vr.entropy({"a": 0.25, "b": 0.25, "c": 0.25, "d": 0.25}) == pytest.approx(2.0)


def test_entropy_point_mass_is_zero():
    assert vr.entropy({"a": 1.0}) == pytest.approx(0.0)


def test_entropy_normalizes_engine_style_posteriors_defensively():
    # engine posteriors are per-corner activations, not distributions;
    # entropy must be invariant to the (missing) normalization step
    raw = {"EM2": 0.4, "EM4": 0.5, "EM8": 0.6, "EM10": 0.7}
    total = sum(raw.values())
    norm = {k: v / total for k, v in raw.items()}
    assert vr.entropy(raw) == pytest.approx(vr.entropy(norm))


# --- 2. Jensen–Shannon divergence ------------------------------------------------

def test_jsd_bounds_and_identity():
    p, q = _sig(), {"EM2": 0.02, "EM4": 0.03, "EM8": 0.05, "EM10": 0.9}
    d = vr.jsd(p, q)
    assert 0.0 <= d <= 1.0
    assert vr.jsd(p, p) == pytest.approx(0.0)


def test_jsd_symmetric():
    p, q = _sig(), {"EM2": 0.02, "EM4": 0.03, "EM8": 0.05, "EM10": 0.9}
    assert vr.jsd(p, q) == pytest.approx(vr.jsd(q, p))


# --- 3. Brier delta --------------------------------------------------------------

def test_brier_delta_positive_when_model_beats_baseline():
    assert vr.brier_delta(baseline_brier=0.25, model_brier=0.15) == pytest.approx(0.10)
    assert vr.brier_delta(baseline_brier=0.20, model_brier=0.30) == pytest.approx(-0.10)


# --- 4. the Certify(c) checkpoint -------------------------------------------------

def test_certify_passes_on_registered_fixture():
    result = vr.certify(_contract(registered=True), _windows())
    assert result.binding is True
    assert result.certified is True
    assert result.reasons == []
    assert result.gate_read.startswith("CERTIFIED")


def test_certify_fails_high_entropy():
    result = vr.certify(_contract(registered=True), _windows(entropies=(0.6, 0.7, 0.65, 0.8)))
    assert result.certified is False
    assert any("ε_c" in r for r in result.reasons)


def test_certify_fails_low_coverage():
    result = vr.certify(
        _contract(registered=True),
        _windows(entropies=(0.1,) * 5, has_data=(True, False, False, False, False), briers=(0.05,) * 5),
    )
    assert result.certified is False
    assert any("coverage" in r for r in result.reasons)
    assert result.coverage == pytest.approx(0.2)


def test_certify_fails_brier_margin():
    result = vr.certify(
        _contract(registered=True, brier_margin=0.05),
        _windows(briers=(0.01, 0.02, 0.01, 0.03)),
    )
    assert result.certified is False
    assert any("ΔBrier" in r for r in result.reasons)


def test_certify_unregistered_never_binds():
    # R-5: the shipped contract is registered: false — the machinery computes
    # the metrics but must refuse a verdict, whatever the numbers say.
    result = vr.certify(_contract(registered=False), _windows())
    assert result.binding is False
    assert result.certified is False
    assert any("R-5" in r or "ceremony" in r for r in result.reasons)
    # metrics still reported (calibration-reference only)
    assert result.median_entropy == pytest.approx(0.135)


def test_certify_empty_evaluation_set_raises():
    with pytest.raises(vr.RecoverabilityError, match="empty evaluation set"):
        vr.certify(_contract(registered=True), [])


# --- 5. fail-closed contract loading ----------------------------------------------

def test_contract_load_fail_closed(tmp_path):
    import yaml

    broken = {"registered": True, "thresholds": {"epsilon_c": 0.3}}  # missing 4 keys
    p = tmp_path / "broken.yaml"
    p.write_text(yaml.safe_dump(broken))
    with pytest.raises(vr.RecoverabilityError, match="missing threshold"):
        vr.load_contract(p)
    with pytest.raises(vr.RecoverabilityError, match="missing"):
        vr.load_contract(tmp_path / "does_not_exist.yaml")


# --- 6. stability and discriminability (paper §21) ----------------------------------

def test_stability_and_discriminability():
    # same subject, three near-identical repeated measurements -> stable
    near = [_sig(0.88, 0.06, 0.04, 0.02), _sig(0.90, 0.05, 0.03, 0.02), _sig(0.89, 0.06, 0.03, 0.02)]
    stab = vr.stability(near, _contract())
    assert stab.stable is True
    assert stab.n_measurements == 3

    # two clearly distinct subjects -> separated
    sep = vr.discriminability(_sig(0.9, 0.03, 0.03, 0.04), {"EM2": 0.02, "EM4": 0.03, "EM8": 0.05, "EM10": 0.9}, _contract())
    assert sep.separated is True

    # near-identical pair -> not separated
    same = vr.discriminability(_sig(0.9, 0.03, 0.03, 0.04), _sig(0.89, 0.04, 0.03, 0.04), _contract())
    assert same.separated is False


def test_stability_requires_two_measurements():
    with pytest.raises(vr.RecoverabilityError, match="≥ 2"):
        vr.stability([_sig()], _contract())
