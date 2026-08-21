#!/usr/bin/env python3
"""grounding_gate.py — the write-time groundedness gate (v4.1 §2.3, OC-16).

The OC-8 review's R1 finding: traceability (audit) is NOT groundedness (truth).
A fabricated utterance that cites real assets passes the projection chain
intact. The fix, operationalized here: every durable claim passes through a
WRITE-TIME gate combining:

  1. PROVENANCE   — complete (source/timestamp/version/confidence/actor)
  2. TRACEABILITY — the claim's asset path exists in the G_APS asset set
                    (the projection chain is computable)
  3. GROUNDEDNESS — the claim's state assertions match the logbook's recorded
                    state within tolerance (the reconciliation gap at write
                    time); a claim about assets that "did not behave as
                    claimed" fails here even though its asset path is real.

The gate is intentionally SEPARATE from traceability: both must pass. This is
the "failure is visible" property made mechanical — the OC-16 injection test
proves a fabricated utterance citing real assets is rejected.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from storage.store import Logbook, LogbookError, LogbookRow  # noqa: E402


@dataclass(frozen=True)
class Claim:
    """A persona utterance (or durable record) to be gated at write time."""

    text: str                                   # the utterance
    actor: str                                  # who claims it
    asset_paths: List[str]                      # the G_APS asset ids it cites
    state_assertions: Dict[str, float]          # corner -> claimed value
    provenance: Dict[str, str]                  # source/timestamp/schema_version/actor


class GroundingGateError(RuntimeError):
    """The gate rejects the claim; the rejection reason is the message."""


class GroundingGate:
    """Write-time gate: provenance + traceability + groundedness, all required."""

    def __init__(
        self,
        known_assets: Sequence[str],
        tolerance: float = 0.15,
        logbook: Optional[Logbook] = None,
    ) -> None:
        self.known_assets = set(known_assets)   # G_APS asset layer (V_A)
        self.tolerance = tolerance              # max |claimed - recorded| per corner
        self.logbook = logbook                  # the recorded-truth store

    # --- 1. provenance ---------------------------------------------------------
    def _check_provenance(self, claim: Claim) -> None:
        required = {"source", "timestamp", "schema_version", "confidence", "actor"}
        missing = required - set(claim.provenance)
        if missing:
            raise GroundingGateError(f"provenance incomplete: {sorted(missing)}")

    # --- 2. traceability (the projection chain is computable) ------------------
    def _check_traceability(self, claim: Claim) -> None:
        unknown = [a for a in claim.asset_paths if a not in self.known_assets]
        if unknown:
            raise GroundingGateError(
                f"traceability FAILED: asset path not in G_APS: {unknown}"
            )

    # --- 3. groundedness (the assets behaved as claimed) -----------------------
    def _check_groundedness(self, claim: Claim, recorded: Dict[str, float]) -> None:
        for corner, claimed_val in claim.state_assertions.items():
            if corner not in recorded:
                raise GroundingGateError(
                    f"groundedness FAILED: no recorded state for corner '{corner}'"
                )
            if abs(claimed_val - recorded[corner]) > self.tolerance:
                raise GroundingGateError(
                    f"groundedness FAILED: corner '{corner}' claimed {claimed_val:.2f} "
                    f"but recorded {recorded[corner]:.2f} (|Δ|={abs(claimed_val - recorded[corner]):.2f} > tol {self.tolerance})"
                )

    # --- the gate --------------------------------------------------------------
    def admit(self, claim: Claim, recorded_state: Optional[Dict[str, float]] = None) -> str:
        """Admit or reject. Returns the admission token on success, raises on rejection.

        recorded_state: the logbook's latest recorded substrate state for the
        claim's corners (the "ground truth" the claim is checked against). In
        the full pipeline this is read from the logbook; the injection test
        supplies it explicitly.
        """
        self._check_provenance(claim)
        self._check_traceability(claim)
        if recorded_state is None:
            recorded_state = self._read_recorded_state(claim)
        self._check_groundedness(claim, recorded_state)
        # all three passed — the claim is admissible
        return f"ADMITTED:{claim.actor}:{hash(claim.text) & 0xFFFFFF:06x}"

    def _read_recorded_state(self, claim: Claim) -> Dict[str, float]:
        """Pull the latest recorded substrate state from the logbook, if present."""
        if self.logbook is None:
            raise GroundingGateError("groundedness FAILED: no logbook and no recorded_state supplied")
        rows = self.logbook.read_windows(limit=1)
        if not rows:
            raise GroundingGateError("groundedness FAILED: logbook empty, nothing recorded")
        return rows[0]["substrate_vector"]
