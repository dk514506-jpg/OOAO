"""test_m0_mock_loop.py — M0 reference gate.

The plan (§2/§4) names this file. M0 = the engine runs on synthetic data:
posterior -> predict_voices -> reconciliation_gap, with provenance validated.
Standalone (builds its own engine) so it runs independently of the M1 file.

Run:  pytest gates/test_m0_mock_loop.py -v
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import em_theory_bayes as eb  # noqa: E402


@pytest.fixture(scope="module")
def engine() -> eb.EmTheoryBayes:
    return eb.EmTheoryBayes(mock=True)


def test_m0_mock_loop_still_runs(engine):
    post = eb.SubstratePosterior(
        probabilities={c: 0.5 for c in eb.SUBSTRATE_CORNERS},
        provenance=eb.Provenance("mock.capture", _now(), "0.1", 0.9, "test"),
    )
    pred = engine.predict_voices(post)
    assert set(pred.probabilities) == set(eb.VOICE_CORNERS)
    rep = eb.SelfReport(
        ratings={v: 0.5 for v in eb.VOICE_CORNERS},
        provenance=eb.Provenance("mock.self_report", _now(), "0.1", 1.0, "participant"),
    )
    gap = engine.reconciliation_gap(pred, rep)
    assert 0.0 <= gap.value <= 1.0
    assert set(gap.per_corner) == set(eb.VOICE_CORNERS)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
