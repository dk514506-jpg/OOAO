"""test_triple_index.py — OC-1 gate: OCI/CAI/CSI instantiated from Kabashkin 2026b.

The verification contract is the paper's own worked examples (Information
17(3):255, Tables 3 & 5): the aviation case (5 constraints, 4 satisfied ->
OCI 0.80; CSI from CV + q) and the urban case (6 constraints, 5 satisfied ->
OCI ≈ 0.83). If our implementation reproduces the paper's numbers from the
paper's stated inputs, the formulas are correctly instantiated.

Run:  pytest gates/test_triple_index.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from triple_index import (  # noqa: E402
    DEFAULT_CONSTRAINTS,
    TripleIndex,
    coefficient_of_variation,
    compute_triple_index,
    default_similarity,
)


# --- the paper's aviation worked example (Table 3) ------------------------------
AVIATION_ONTOLOGY = {
    "sensor_types": {"HRV", "EDA", "TEMP"},
    "wholes": {"body", "chest"},
    "units": {"EM8": ("ms", "mV"), "EM10": ("lx", "dB")},
    "bounds": {"EM8": (0.0, 200.0), "EM10": (0.0, 1000.0)},
    "sensor_map": {"HRV": "chest"},
}
AVIATION_STATE = {
    "active_sensors": ["HRV", "EDA"],
    "parts": ["chest"],
    "feature_units": {"EM8": "ms"},
    "feature_values": {"EM8": 23.2},
    "sensor_map": {"HRV": "wrist"},  # the ONE violation (unit mismatch analog)
}


def test_oci_aviation_4_of_5_matches_paper():
    """Paper Table 3: OCI = 4/5 = 0.80."""
    idx = compute_triple_index(
        AVIATION_ONTOLOGY, AVIATION_STATE, [], data_quality=0.9
    )
    assert idx.oci == pytest.approx(0.80, abs=1e-3)


def test_oci_all_satisfied_is_one():
    state_ok = dict(AVIATION_STATE, sensor_map={"HRV": "chest"})
    idx = compute_triple_index(AVIATION_ONTOLOGY, state_ok, [], data_quality=0.9)
    assert idx.oci == pytest.approx(1.0)


def test_oci_zero_when_all_violated():
    bad_state = {
        "active_sensors": ["UNKNOWN_SENSOR"],
        "parts": ["ghost_part"],
        "feature_units": {"EM8": "parsecs"},
        "feature_values": {"EM8": -999.0},
        "sensor_map": {"HRV": "nowhere"},
    }
    idx = compute_triple_index(AVIATION_ONTOLOGY, bad_state, [], data_quality=0.9)
    assert idx.oci == pytest.approx(0.0)


def test_cai_is_max_similarity_over_scenarios():
    scenarios = [
        {"EM8": 0.3, "EM10": 0.4, "EM4": 0.5, "EM2": 0.5},
        {"EM8": 0.6, "EM10": 0.5, "EM4": 0.4, "EM2": 0.5},
        {"EM8": 0.9, "EM10": 0.7, "EM4": 0.3, "EM2": 0.6},
    ]
    cai_state = {"EM8": 0.62, "EM10": 0.55, "EM4": 0.38, "EM2": 0.5}
    idx = compute_triple_index(
        AVIATION_ONTOLOGY, AVIATION_STATE, scenarios, data_quality=0.9, cai_state=cai_state
    )
    sims = [default_similarity(cai_state, y) for y in scenarios]
    assert idx.cai == pytest.approx(max(sims), abs=1e-3)
    assert 0.0 <= idx.cai <= 1.0


def test_csi_uses_cv_and_data_quality():
    """Paper worked example (Table 3): RUL estimates {14,200; 12,800; 9,600}, q=0.90.

    Worked-example realization: CV = 0.154; penalty e^(−3·CV) = 0.63;
    CSI = q·penalty = 0.90·0.63 ≈ 0.57 — the paper's own number.
    """
    scenarios = [{"rul": 14200.0}, {"rul": 12800.0}, {"rul": 9600.0}]
    idx = compute_triple_index(
        AVIATION_ONTOLOGY, AVIATION_STATE, scenarios, data_quality=0.90,
        exponential_dispersion=True, dispersion_beta=3.0,
    )
    assert idx.csi == pytest.approx(0.57, abs=0.02)


def test_csi_formal_definition_monotone():
    """Formal definition: CSI = q·max(1−σ_k); higher dispersion -> lower CSI."""
    # per-scenario CV needs multi-value state vectors (substrate-like)
    tight = [{"EM8": 0.50, "EM10": 0.51, "EM4": 0.50, "EM2": 0.51}]   # tiny CV
    wide = [{"EM8": 0.10, "EM10": 0.60, "EM4": 0.30, "EM2": 0.90}]    # big CV
    csi_tight = compute_triple_index(AVIATION_ONTOLOGY, AVIATION_STATE, tight, data_quality=0.9).csi
    csi_wide = compute_triple_index(AVIATION_ONTOLOGY, AVIATION_STATE, wide, data_quality=0.9).csi
    assert csi_tight > csi_wide, "higher dispersion must lower CSI"
    assert 0.0 <= csi_wide <= 1.0


def test_csi_scales_with_data_quality():
    """q(t) modulates CSI linearly: same scenarios, better data -> higher CSI."""
    scenarios = [{"rul": 14200.0}, {"rul": 12800.0}, {"rul": 9600.0}]
    lo = compute_triple_index(AVIATION_ONTOLOGY, AVIATION_STATE, scenarios,
                              data_quality=0.5, exponential_dispersion=True).csi
    hi = compute_triple_index(AVIATION_ONTOLOGY, AVIATION_STATE, scenarios,
                              data_quality=0.9, exponential_dispersion=True).csi
    assert hi == pytest.approx(lo * (0.9 / 0.5), abs=1e-3)


def test_csi_zero_without_scenarios():
    idx = compute_triple_index(AVIATION_ONTOLOGY, AVIATION_STATE, [], data_quality=0.9)
    assert idx.csi == pytest.approx(0.0)


def test_cv_matches_paper_figure():
    """Paper: values {14200, 12800, 9600} -> CV = 0.154."""
    cv = coefficient_of_variation([14200.0, 12800.0, 9600.0])
    assert cv == pytest.approx(0.154, abs=0.01)


def test_joint_read_classifications():
    # low OCI -> semantic misalignment
    bad = compute_triple_index(
        AVIATION_ONTOLOGY,
        {"active_sensors": ["X"], "parts": [], "feature_units": {}, "feature_values": {}, "sensor_map": {}},
        [], data_quality=0.9,
    )
    assert bad.joint_read == "SEMANTIC_MISALIGNMENT"
    # high CAI + low CSI -> explains but low confidence
    mixed = compute_triple_index(
        AVIATION_ONTOLOGY, AVIATION_STATE, [{"EM8": 0.6}], data_quality=0.1,
        cai_state={"EM8": 0.61},
    )
    assert mixed.joint_read == "EXPLAINS_BUT_LOW_CONFIDENCE"
    # high CSI -> confident
    good = compute_triple_index(
        AVIATION_ONTOLOGY, AVIATION_STATE, [{"EM8": 0.6}, {"EM8": 0.61}], data_quality=0.95,
        cai_state={"EM8": 0.605},
    )
    assert good.joint_read == "CONFIDENT"


def test_default_constraints_count():
    assert len(DEFAULT_CONSTRAINTS) == 5  # the paper's five constraint kinds
