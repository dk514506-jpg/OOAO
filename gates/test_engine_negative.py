"""test_engine_negative.py — fail-closed negative gate tests (OC-18 Locus REVISE #3).

Plan §6 claims "negative tests are first-class." These make that suite-backed:
  1. engine refuses to run without the governed contract (EngineError)
  2. incomplete posterior rejected (ValueError)
  3. confidence out of range rejected (ValueError)
(Empty-provenance rejection is covered in test_m1_capture_smoke.py:
test_provenance_fields_nonempty.)

Run:  pytest gates/test_engine_negative.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import em_theory_bayes as eb  # noqa: E402


def test_engine_refuses_to_run_without_contract():
    """Fail-closed: no governed contract, no engine."""
    with pytest.raises(eb.EngineError, match="refuses to run ungoverned"):
        eb.EmTheoryBayes(contract_path="/tmp/definitely_missing_contract.yaml", mock=True)


def test_incomplete_posterior_rejected():
    """A posterior missing corners is not a posterior (data-quality gate)."""
    with pytest.raises(ValueError, match="missing corners"):
        eb.SubstratePosterior(
            probabilities={"EM8": 0.5},  # only 1 of 4 corners
            provenance=eb.Provenance("t", _now(), "0.1", 0.9, "test"),
        )


def test_confidence_out_of_range_rejected():
    """Confidence must be in [0,1] — a 1.7 is a corrupted record, not high trust."""
    with pytest.raises(ValueError, match="out of range"):
        eb.Provenance("t", _now(), "0.1", 1.7, "engine").validate()


def test_trust_gate_harmonized_with_spec_a3():
    """OC-18 REVISE #4: personalize_update gate is trust=f(CSI,tier), not bare CSI.

    A low-CSI high-tier record passes where bare CSI would defer; a high-CSI
    low-tier record defers where bare CSI would pass. The tier modulates.
    """
    engine = eb.EmTheoryBayes(mock=True)
    gap = eb.ReconciliationGap(
        value=0.3, per_corner={v: 0.3 for v in eb.VOICE_CORNERS},
        provenance=eb.Provenance("t", _now(), "0.1", 0.7, "engine"),
    )
    report = eb.SelfReport(
        ratings={v: 0.5 for v in eb.VOICE_CORNERS},
        provenance=eb.Provenance("t", _now(), "0.1", 1.0, "participant"),
    )
    # CSI 0.6, tier 0.9 -> trust 0.57 >= 0.5: proceeds (no raise)
    engine.personalize_update(gap, report, csi=0.6, trust_tier=0.9)
    # CSI 0.6, tier 0.1 -> trust 0.33 < 0.5: deferred (no raise)
    engine.personalize_update(gap, report, csi=0.6, trust_tier=0.1)


def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
