"""test_vt_estimate.py — Phase 1 epistemic wrapper gates (R-2).

Covers vt_estimate.py: every status in the §5.2 resolution order reachable by
fixture, the invariant that a numeric posterior NEVER surfaces when status !=
estimable, the expiry sweep (Formalization Part XI), and the missingness ->
epistemic classifier.

Run:  pytest gates/test_vt_estimate.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from em_theory_bayes import VOICE_CORNERS  # noqa: E402
import vt_estimate as ve  # noqa: E402

SIG = {c: 0.5 for c in VOICE_CORNERS}
POST = {"EM2": 0.4, "EM4": 0.5, "EM8": 0.6, "EM10": 0.7}

# --- the §5.2 resolution order, status by status ---------------------------------


def test_unknown_when_no_data():
    e = ve.estimate(ve.EstimateContext(data_present=False))
    assert e.status == "unknown"
    assert e.posterior is None


def test_unknown_when_expired():
    e = ve.estimate(ve.EstimateContext(data_present=True, expired=True))
    assert e.status == "unknown"
    assert "expired" in e.reason


def test_indeterminate_when_provenance_inadmissible():
    e = ve.estimate(ve.EstimateContext(data_present=True, provenance_admissible=False))
    assert e.status == "indeterminate"


def test_indeterminate_when_cai_inadmissible():
    e = ve.estimate(ve.EstimateContext(data_present=True, cai_admissible=False))
    assert e.status == "indeterminate"


def test_declined_self_authority_absolute():
    e = ve.estimate(ve.EstimateContext(data_present=True, participant_state="declined"))
    assert e.status == "declined"


def test_withdrawn_self_authority_absolute():
    e = ve.estimate(ve.EstimateContext(data_present=True, participant_state="withdrawn"))
    assert e.status == "withdrawn"


def test_contested_when_prediction_deviates_beyond_delta():
    e = ve.estimate(ve.EstimateContext(
        data_present=True, prediction={v: 0.9 for v in VOICE_CORNERS},
        self_report={v: 0.1 for v in VOICE_CORNERS}, delta=0.20))
    assert e.status == "contested"
    assert "δ" in e.reason


def test_indeterminate_when_entropy_over_epsilon():
    e = ve.estimate(ve.EstimateContext(
        data_present=True, entropy=0.8, epsilon=0.30,
        prediction=SIG, self_report=SIG))
    assert e.status == "indeterminate"
    assert "ε" in e.reason


def test_contested_gap_floor_halts_personalization():
    # the gap-floor rule sits ABOVE the entropy check: even a perfect entropy
    # resolves to contested when gap→0 while felt-watched rises
    e = ve.estimate(ve.EstimateContext(
        data_present=True, entropy=0.05, epsilon=0.30,
        prediction=SIG, self_report=SIG,
        gap_trend_down=True, felt_watched_rising=True))
    assert e.status == "contested"
    assert "gap-floor" in e.reason


def test_estimable_emits_posterior():
    e = ve.estimate(ve.EstimateContext(
        data_present=True, prediction=SIG, self_report=SIG,
        entropy=0.1, epsilon=0.30, posterior=POST))
    assert e.status == "estimable"
    assert e.posterior == POST
    assert e.surfaces_number is True


# --- the R-2 invariant: no number outside estimable ------------------------------

@pytest.mark.parametrize("ctx", [
    ve.EstimateContext(data_present=False, posterior=POST),
    ve.EstimateContext(data_present=True, expired=True, posterior=POST),
    ve.EstimateContext(data_present=True, provenance_admissible=False, posterior=POST),
    ve.EstimateContext(data_present=True, cai_admissible=False, posterior=POST),
    ve.EstimateContext(data_present=True, participant_state="declined", posterior=POST),
    ve.EstimateContext(data_present=True, participant_state="withdrawn", posterior=POST),
    ve.EstimateContext(data_present=True, gap_trend_down=True, felt_watched_rising=True, posterior=POST),
    ve.EstimateContext(data_present=True, prediction={v: 0.9 for v in VOICE_CORNERS},
                       self_report={v: 0.1 for v in VOICE_CORNERS}, posterior=POST),
    ve.EstimateContext(data_present=True, entropy=0.9, prediction=SIG, self_report=SIG, posterior=POST),
])
def test_no_posterior_surfaces_under_any_non_estimable_status(ctx):
    e = ve.estimate(ctx)
    assert e.status != "estimable"
    assert e.posterior is None
    assert e.surfaces_number is False


def test_estimate_rejects_unknown_status_and_smuggled_posterior():
    with pytest.raises(ValueError, match="unknown epistemic status"):
        ve.Estimate("bogus", None, "x")
    with pytest.raises(ValueError, match="forbidden"):
        ve.Estimate("unknown", POST, "x")


# --- expiry sweep (Formalization Part XI) -----------------------------------------

def test_expiry_sweep_roundtrip():
    rows = [
        {"window_id": "w1", "valid_until": "2026-08-01T00:00:00Z", "epistemic_status": "estimable"},
        {"window_id": "w2", "valid_until": "2026-09-01T00:00:00Z", "epistemic_status": "estimable"},
        {"window_id": "w3", "valid_until": None, "epistemic_status": "estimable"},
    ]
    now = "2026-08-25T12:00:00Z"
    updates = ve.sweep_expired(rows, now)
    ids = {u["window_id"] for u in updates}
    assert ids == {"w1"}                      # only the stale row resolves to expired
    assert updates[0]["epistemic_status"] == "expired"
    assert len(updates) == 1


# --- missingness classifier (observations table -> 13-status vocabulary) -----------

def test_classify_missingness_mapping():
    assert ve.classify_missingness("observed") == "estimable"
    assert ve.classify_missingness("declined") == "declined"
    assert ve.classify_missingness("private") == "private"
    assert ve.classify_missingness("expired") == "expired"
    assert ve.classify_missingness("sensor_failure") == "indeterminate"
    assert ve.classify_missingness("intentionally_unrecorded") == "intentionally-unrecorded"
    assert ve.classify_missingness("not_applicable") == "not-presently-interpretable"


def test_classify_missingness_unknown_value_raises():
    with pytest.raises(ValueError, match="unknown missingness"):
        ve.classify_missingness("fabricated")
