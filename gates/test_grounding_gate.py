"""test_grounding_gate.py — OC-16: the ungrounded-claim injection test.

The OC-8 R1 contract, made a milestone gate: force a FABRICATED utterance that
cites REAL assets (an HRV stream that did not behave as claimed) and assert:

  (a) the gate REJECTS it (groundedness fails even though traceability holds);
  (b) a GENUINE claim citing the same real assets is ADMITTED (the gate is not
      a false-positive machine — traceability still works);
  (c) traceability is checked independently: a claim citing a NON-EXISTENT
      asset is rejected on the projection chain, before groundedness matters;
  (d) provenance is checked first: an incomplete record is rejected outright.

"Traceability is an audit property, not a truth property" (v4.1 §2.3) — this
test proves the separation mechanically.

Run:  pytest gates/test_grounding_gate.py -v
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from grounding_gate import Claim, GroundingGate, GroundingGateError  # noqa: E402

# the G_APS asset layer: the HRV stream is REAL (in the asset set)
KNOWN_ASSETS = ["HRV_stream_01", "EDA_stream_01", "TEMP_sensor_02"]
# the logbook's recorded truth: HRV implies LOW arousal (high RMSSD)
RECORDED_TRUTH = {"EM8": 0.25, "EM10": 0.40, "EM4": 0.50, "EM2": 0.50}


def _prov(actor: str = "talker", confidence: str = "0.9") -> dict:
    return {
        "source": "talker.utterance",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "schema_version": "0.1",
        "confidence": confidence,
        "actor": actor,
    }


@pytest.fixture()
def gate() -> GroundingGate:
    return GroundingGate(known_assets=KNOWN_ASSETS, tolerance=0.15)


# --- (a) the core injection: fabricated claim, real assets, REJECTED ----------

def test_fabricated_claim_citing_real_assets_is_rejected(gate):
    """The OC-16 scenario: the utterance cites real assets but asserts a state
    the assets did not produce (claims high arousal from a calm HRV stream)."""
    claim = Claim(
        text="My HRV was off the charts — I was extremely aroused.",
        actor="talker",
        asset_paths=["HRV_stream_01"],            # a REAL asset
        state_assertions={"EM8": 0.95},           # but the recorded truth is 0.25
        provenance=_prov(),
    )
    with pytest.raises(GroundingGateError, match="groundedness FAILED"):
        gate.admit(claim, recorded_state=RECORDED_TRUTH)


# --- (b) genuine claim, same assets, ADMITTED ---------------------------------

def test_genuine_claim_citing_same_assets_is_admitted(gate):
    """The same real asset with a truthful assertion passes — the gate is not
    a false-positive machine; traceability still works."""
    claim = Claim(
        text="My HRV was calm — low arousal this window.",
        actor="talker",
        asset_paths=["HRV_stream_01"],
        state_assertions={"EM8": 0.25},
        provenance=_prov(),
    )
    token = gate.admit(claim, recorded_state=RECORDED_TRUTH)
    assert token.startswith("ADMITTED:talker:")


# --- (c) traceability checked independently -----------------------------------

def test_claim_citing_nonexistent_asset_rejected_on_chain(gate):
    """A claim citing an asset NOT in G_APS fails traceability — before
    groundedness even matters."""
    claim = Claim(
        text="The kitchen camera saw me pacing.",
        actor="talker",
        asset_paths=["kitchen_camera_99"],        # not in G_APS
        state_assertions={"EM4": 0.9},
        provenance=_prov(),
    )
    with pytest.raises(GroundingGateError, match="traceability FAILED"):
        gate.admit(claim, recorded_state=RECORDED_TRUTH)


# --- (d) provenance checked first ---------------------------------------------

def test_incomplete_provenance_rejected_first(gate):
    claim = Claim(
        text="Anything at all.",
        actor="talker",
        asset_paths=["HRV_stream_01"],
        state_assertions={"EM8": 0.25},
        provenance={"source": "talker"},          # missing timestamp/version/etc.
    )
    with pytest.raises(GroundingGateError, match="provenance incomplete"):
        gate.admit(claim, recorded_state=RECORDED_TRUTH)


# --- the property the review demanded: traceability holds while groundedness
# --- fails on the SAME claim (the separation, demonstrated atomically) --------

def test_traceability_holds_while_groundedness_fails(gate):
    """The v4.1 §2.3 corollary made mechanical: the fabricated claim's asset
    path IS traceable (the chain computes) — groundedness is what rejects it.
    Both properties are evaluated; the failure is on the truth property, and
    the audit path (asset_paths) survives intact for the record."""
    claim = Claim(
        text="Extreme arousal from the HRV strap.",
        actor="talker",
        asset_paths=["HRV_stream_01"],
        state_assertions={"EM8": 0.95},
        provenance=_prov(),
    )
    # traceability passes (asset is known)...
    assert claim.asset_paths[0] in gate.known_assets
    # ...but the admission fails on groundedness
    with pytest.raises(GroundingGateError, match="groundedness FAILED"):
        gate.admit(claim, recorded_state=RECORDED_TRUTH)
    # the audit trail is not destroyed by the rejection: the claim record
    # (with its asset path) is intact — rejection logs, not erases.
    assert claim.asset_paths == ["HRV_stream_01"]
    assert claim.state_assertions == {"EM8": 0.95}


# --- tolerance boundary -------------------------------------------------------

def test_within_tolerance_admitted(gate):
    claim = Claim(
        text="Mildly elevated, roughly as recorded.",
        actor="talker",
        asset_paths=["HRV_stream_01"],
        state_assertions={"EM8": 0.30},           # |0.30-0.25| = 0.05 <= 0.15
        provenance=_prov(),
    )
    token = gate.admit(claim, recorded_state=RECORDED_TRUTH)
    assert token.startswith("ADMITTED:")


def test_beyond_tolerance_rejected(gate):
    claim = Claim(
        text="Wildly elevated.",
        actor="talker",
        asset_paths=["HRV_stream_01"],
        state_assertions={"EM8": 0.60},           # |0.60-0.25| = 0.35 > 0.15
        provenance=_prov(),
    )
    with pytest.raises(GroundingGateError, match="groundedness FAILED"):
        gate.admit(claim, recorded_state=RECORDED_TRUTH)
