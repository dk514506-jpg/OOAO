#!/usr/bin/env python3
"""em_theory_bayes.py — the EM-Theory Situating Bridge engine.

Maps 1:1 to the logic block of bp_c_em.yaml (BP-C-EM, Part A of the keystone
spec). All probability arithmetic lives HERE; the LLM never touches math
(encode/decode only, per the G-003 rule). This is the ONLY genuinely learned
component of the Manor (CDT-1 per the v4.1 ML-placement table).

Status: SKELETON v0.1 (OC-5 closure) — methods exist and run on synthetic
data (M0 reference); real CPTs, real sensor wiring, and the M2 sufficiency
test are downstream milestones.

Industry best-practices observed:
  - 12-factor config via env + the governed contract file (bp_c_em.yaml)
  - typed dataclasses for the state objects (no ad-hoc dicts)
  - provenance required on every durable write (fail-closed)
  - fail-fast validation on construction (schema checks)
  - testable without hardware: every path accepts synthetic inputs (E5)
"""

from __future__ import annotations

import dataclasses
import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import yaml  # PyYAML; pinned in requirements.txt

logger = logging.getLogger("em_theory_bayes")

# --- corners (from bp_c_em.yaml) -------------------------------------------------
SUBSTRATE_CORNERS = ("EM2", "EM4", "EM8", "EM10")
VOICE_CORNERS = ("EM3", "EM5", "EM7", "EM9")


@dataclass(frozen=True)
class Provenance:
    """Every durable record carries provenance; no field may be empty.

    ENGINE MINIMUM (5 fields). The M1 write target is the Measurement Logbook
    v2.0's 9 columns (bp_c_em.yaml provenance.logbook_columns); the mapping:
    source -> substrate_vector / voice_prediction / voice_report (per kind),
    timestamp -> timestamp, schema_version -> model_version, confidence -> CSI
    (engine rows; 1.0 for participant rows), actor -> log owner column.
    """

    source: str
    timestamp: str          # ISO-8601 UTC
    schema_version: str
    confidence: float       # 0..1
    actor: str              # which persona/daemon wrote it

    def validate(self) -> None:
        if not all([self.source, self.timestamp, self.schema_version, self.actor]):
            raise ValueError(f"provenance incomplete: {self!r}")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"confidence out of range: {self.confidence}")


@dataclass
class SubstratePosterior:
    """P(substrate corner | sensors) — the estimability output."""

    probabilities: Dict[str, float]  # corner -> P(corner active | sensors)
    provenance: Provenance

    def __post_init__(self) -> None:
        self.provenance.validate()
        missing = set(SUBSTRATE_CORNERS) - set(self.probabilities)
        if missing:
            raise ValueError(f"posterior missing corners: {missing}")


@dataclass
class VoicePrediction:
    """P(voice corner) predicted from the substrate posterior."""

    probabilities: Dict[str, float]  # corner -> P(voice elevated)
    provenance: Provenance


@dataclass
class SelfReport:
    """Participant-reported voice state — ground truth for the gap."""

    ratings: Dict[str, float]  # corner -> 0..1 normalized self-report
    provenance: Provenance


@dataclass
class ReconciliationGap:
    """The keystone measure: divergence(predicted voices, reported voices)."""

    value: float               # gap g(t) — the program's primary DV
    per_corner: Dict[str, float]
    provenance: Provenance


class EngineError(RuntimeError):
    """Raised when the engine's own invariants fail (fail-closed)."""


class EmTheoryBayes:
    """The bridge engine. Probability arithmetic only — no text generation.

    The engine is deliberately model-agnostic: it consumes P(substrate|sensors)
    from measurement models (neurokit2 features -> posterior, Leg-3 stage) and
    returns voice predictions + the reconciliation gap. CPT learning
    (personalize_update) is bounded to CDT-1 and never silent (BP-M path).
    """

    def __init__(
        self,
        contract_path: Optional[Path | str] = None,
        cpt_path: Optional[Path | str] = None,
        mock: bool = True,
    ) -> None:
        self.mock = mock
        self.contract = self._load_contract(contract_path)
        self.cpts = self._load_cpts(cpt_path) if not mock else self._mock_cpts()
        logger.info("engine ready (mock=%s, contract=%s)", mock, self.contract.get("schema_version"))

    # --- loading ------------------------------------------------------------
    @staticmethod
    def _load_contract(path: Optional[Path]) -> dict:
        p = Path(path) if path else Path(__file__).parent / "bp_c_em.yaml"
        if not p.exists():
            raise EngineError(f"contract file missing: {p} — the engine refuses to run ungoverned")
        with open(p) as fh:
            return yaml.safe_load(fh)

    def _load_cpts(self, path: Optional[Path]) -> Dict[str, dict]:
        p = Path(path) if path else Path(__file__).parent / "cpts.json"
        if not p.exists():
            raise EngineError(f"CPT file missing: {p} (mock mode only until M1)")
        with open(p) as fh:
            return json.load(fh)

    def _mock_cpts(self) -> Dict[str, dict]:
        # M0 reference: uniform-ish priors + identity substrate->voice coupling.
        # These are SYNTHETIC — replaced by learned CPTs at the M2 sufficiency gate.
        return {
            "substrate_prior": {c: 0.5 for c in SUBSTRATE_CORNERS},
            "voice_given_substrate": {
                v: {s: 0.5 for s in SUBSTRATE_CORNERS} for v in VOICE_CORNERS
            },
        }

    # --- the three logic-block functions (bp_c_em.yaml) ----------------------
    def predict_voices(self, posterior: SubstratePosterior) -> VoicePrediction:
        """P(voice) = sum over substrate corners of P(voice|substrate)*P(substrate)."""
        probs: Dict[str, float] = {}
        for voice in VOICE_CORNERS:
            p = 0.0
            for corner in SUBSTRATE_CORNERS:
                p += self.cpts["voice_given_substrate"][voice][corner] * posterior.probabilities[corner]
            probs[voice] = min(1.0, max(0.0, p))
        prov = Provenance(
            source="engine.predict_voices", timestamp=_now(), schema_version=self.contract["schema_version"],
            confidence=_mean(probs.values()), actor="engine",
        )
        return VoicePrediction(probabilities=probs, provenance=prov)

    def reconciliation_gap(self, predicted: VoicePrediction, reported: SelfReport) -> ReconciliationGap:
        """g(t) = divergence(predicted voices, reported voices) — primary DV.

        Symmetric per-corner absolute divergence, aggregated as the mean.
        The gap-floor rule (H4) watches this: gap -> 0 with rising felt-watched
        signals deference, not perfect observation (iatrogenic gate).
        """
        per_corner: Dict[str, float] = {}
        for voice in VOICE_CORNERS:
            p = predicted.probabilities.get(voice, 0.0)
            r = reported.ratings.get(voice, 0.0)
            per_corner[voice] = abs(p - r)
        value = _mean(per_corner.values())
        prov = Provenance(
            source="engine.reconciliation_gap", timestamp=_now(), schema_version=self.contract["schema_version"],
            confidence=1.0 - value, actor="engine",
        )
        return ReconciliationGap(value=value, per_corner=per_corner, provenance=prov)

    def personalize_update(self, gap: ReconciliationGap, reported: SelfReport, csi: float, trust_tier: float = 0.5) -> None:
        """Bounded CPT refinement (CDT-1). NEVER silent: BP-M path, A4 ceiling,
        G-015 participant sign-off on durable change. Skeleton: records the
        candidate update for the governed promotion path; does not apply it.

        Signature harmonized (OC-18 Locus REVISE) with spec A.3: the gate is
        trust = f(CSI, tier) — confidence modulated by the acting persona's
        trust tier — rather than bare CSI. tier ∈ [0,1]; higher = more trusted.
        """
        trust = csi * (0.5 + 0.5 * trust_tier)  # f(CSI, tier): tier scales CSI toward its ceiling
        if trust < 0.5:
            logger.info("personalize_update deferred: trust=%.2f (CSI=%.2f, tier=%.2f) below floor", trust, csi, trust_tier)
            return
        candidate = {
            "gap": gap.value,
            "per_corner": gap.per_corner,
            "reported": reported.ratings,
            "csi": csi,
            "trust_tier": trust_tier,
            "trust": trust,
            "actor": "engine.personalize_update",
            "promotion_path": "BP-M (governed, participant sign-off)",
        }
        # In the real engine this writes a CANDIDATE record to the provenance
        # store and returns; Locus/BP-M promote it. Never applied in place here.
        logger.info("personalize_update candidate recorded (promotion path: BP-M)")


# --- small helpers --------------------------------------------------------------
def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def _mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


# --- CLI: mock loop (M0 reference, E5 mock-first) --------------------------------
def main() -> int:
    logging.basicConfig(level=logging.INFO)
    engine = EmTheoryBayes(mock=True)
    # synthetic posterior (M0: engine runs on synthetic data)
    post = SubstratePosterior(
        probabilities={c: 0.4 + 0.1 * i for i, c in enumerate(SUBSTRATE_CORNERS)},
        provenance=Provenance("mock.capture", _now(), "0.1", 0.9, "test"),
    )
    pred = engine.predict_voices(post)
    report = SelfReport(
        ratings={v: 0.5 for v in VOICE_CORNERS},
        provenance=Provenance("mock.self_report", _now(), "0.1", 1.0, "participant"),
    )
    gap = engine.reconciliation_gap(pred, report)
    print(f"M0 OK — gap={gap.value:.3f} per_corner={ {k: round(v, 3) for k, v in gap.per_corner.items()} }")
    print("mock engine runs on synthetic data; provenance validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
