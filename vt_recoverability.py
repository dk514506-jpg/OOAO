#!/usr/bin/env python3
"""vt_recoverability.py — VT-1 recoverability certification (R-3, certification-ε).

Implements the keystone's certification checkpoint (HOMES_VT1_Sublation_Synthesis
§5.3)::

    Certify(c) = [ΔBrier ≥ margin] ∧ [median_W H ≤ ε_c ∧ coverage ≥ θ]

Pure computation over window metrics: entropy (bits), Jensen–Shannon
divergence, Brier deltas, stability, and discriminability. No inference, no
text output, and — by contract — identical behavior on synthetic and real
data: every threshold comes from the contract file, never from the data and
never from this module (fail-closed load).

R-5 deferral: the shipped contract (vt_recoverability_contract.yaml) carries
``registered: false``. Until the ε ceremony (Phase 4) flips it, ``certify()``
computes and returns the metrics but refuses to bind — ``certified`` is False
and ``binding`` is False. Provisional numbers may calibrate; they never
adjudicate. The gates exercise the full machinery on registered fixtures.

Convention note: the engine's posteriors are per-corner activations, not a
normalized distribution, so every distribution entering this module is
normalized defensively before entropy/JSD are computed. Documented, not
silent.

Industry best-practices observed (mirrors m2_sufficiency.py):
  - dataclass results with gate-style reads, deterministic, no hidden state
  - fail-closed contract loading (missing key = refuse to run, never default)
  - thresholds only from contract; unit-tested on fixtures, identical path
    for synthetic and real evaluation sets
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence

import numpy as np
import yaml  # PyYAML; pinned in requirements.txt

logger = logging.getLogger("vt_recoverability")


class RecoverabilityError(RuntimeError):
    """Raised when the certification contract or inputs violate invariants
    (fail-closed)."""


# --- result types -------------------------------------------------------------

@dataclass(frozen=True)
class WindowMetrics:
    """One evaluation window's recoverability-relevant metrics (evaluation set W)."""

    window_id: str
    entropy: float                # H(Ω|D,L) for this window, bits (0 = certain)
    has_data: bool                # usable observation present (coverage numerator)
    brier_improvement: float      # baseline − model Brier (>0 = model helps)


@dataclass(frozen=True)
class CertificationResult:
    """The Certify(c) decision. ``binding`` is False until the ε ceremony
    (R-5): an unregistered contract may report metrics, never a verdict."""

    certified: bool
    binding: bool
    median_entropy: float         # median_W H (bits)
    coverage: float               # usable windows / all windows in W
    delta_brier: float            # mean ΔBrier over W
    reasons: List[str] = field(default_factory=list)

    @property
    def gate_read(self) -> str:
        if not self.binding:
            return "NON-BINDING (contract not registered — R-5): metrics only, no verdict"
        if self.certified:
            return "CERTIFIED: recoverability holds on evaluation set W"
        return "NOT CERTIFIED: " + "; ".join(self.reasons)


@dataclass(frozen=True)
class StabilityResult:
    """Repeated-measurement stability of one subject's embodied signature."""

    stable: bool
    max_jsd: float                # max pairwise JSD across measurements
    n_measurements: int


@dataclass(frozen=True)
class DiscriminabilityResult:
    """Between-subject separation of two embodied signatures."""

    separated: bool
    jsd: float


# --- contract loading (fail-closed) --------------------------------------------

_REQUIRED_THRESHOLDS = (
    "epsilon_c", "coverage_theta", "brier_margin",
    "stability_max_jsd", "discriminability_min_jsd",
)


def load_contract(path: Optional[Path | str] = None) -> dict:
    """Load and validate the recoverability contract.

    Fail-closed: a missing file, a missing ``registered`` flag, or any
    missing threshold key raises RecoverabilityError — the certification
    refuses to run ungoverned.
    """
    p = Path(path) if path else Path(__file__).parent / "vt_recoverability_contract.yaml"
    if not p.exists():
        raise RecoverabilityError(f"contract file missing: {p}")
    with open(p) as fh:
        contract = yaml.safe_load(fh)
    _validate_contract(contract)
    return contract


def _validate_contract(contract: dict) -> None:
    if not isinstance(contract, dict) or "registered" not in contract:
        raise RecoverabilityError("contract must declare 'registered' (bool)")
    if "thresholds" not in contract or not isinstance(contract["thresholds"], dict):
        raise RecoverabilityError("contract must declare 'thresholds'")
    missing = [k for k in _REQUIRED_THRESHOLDS if k not in contract["thresholds"]]
    if missing:
        raise RecoverabilityError(f"contract missing threshold(s): {missing}")
    for k in _REQUIRED_THRESHOLDS:
        if not isinstance(contract["thresholds"][k], (int, float)):
            raise RecoverabilityError(f"threshold '{k}' must be numeric")


# --- information-theoretic primitives (bits) -----------------------------------

def _normalize(probs: Mapping[str, float] | np.ndarray) -> np.ndarray:
    """Engine posteriors are per-corner activations, not distributions:
    normalize defensively before any entropy/JSD computation. Accepts either
    a corner->probability mapping or an already-vectorized array."""
    if isinstance(probs, np.ndarray):
        p = np.asarray(probs, dtype=float)
    elif isinstance(probs, Mapping):
        p = np.asarray([max(0.0, float(v)) for v in probs.values()], dtype=float)
    else:
        raise RecoverabilityError(f"cannot normalize input of type {type(probs).__name__}")
    total = float(p.sum())
    if total <= 0.0:
        raise RecoverabilityError("distribution has non-positive mass")
    return p / total


def entropy(probs: Mapping[str, float], base: float = 2.0) -> float:
    """Shannon entropy of a (possibly unnormalized) probability mapping, in
    the given base (default bits). Uniform over n → log2(n); point mass → 0."""
    p = _normalize(probs)
    p = p[p > 0.0]
    if p.size == 0:
        return 0.0
    return float(-np.sum(p * np.log(p)) / np.log(base))


def _kl(p: np.ndarray, q: np.ndarray) -> float:
    eps = 1e-12
    return float(np.sum(p * np.log((p + eps) / (q + eps)) / np.log(2.0)))


def jsd(p: Mapping[str, float], q: Mapping[str, float]) -> float:
    """Jensen–Shannon divergence in bits: symmetric, bounded [0, 1].
    0 = identical distributions; 1 = disjoint supports."""
    pn, qn = _normalize(p), _normalize(q)
    m = 0.5 * (pn + qn)
    return float(0.5 * _kl(pn, m) + 0.5 * _kl(qn, m))


def brier_delta(baseline_brier: float, model_brier: float) -> float:
    """ΔBrier = baseline − model. Positive = the model beats the no-sensor
    baseline at matching outcome (calibration error, lower is better)."""
    return float(baseline_brier - model_brier)


# --- the Certify(c) checkpoint --------------------------------------------------

def certify(contract: dict, windows: Sequence[WindowMetrics]) -> CertificationResult:
    """The keystone's certification checkpoint (synthesis §5.3).

    Fail-closed: empty evaluation set raises; an unregistered contract can
    never certify (metrics are still returned, calibration-reference only).
    """
    _validate_contract(contract)
    if not windows:
        raise RecoverabilityError("certify: empty evaluation set W")
    usable = [w for w in windows if w.has_data]
    median_h = float(np.median([w.entropy for w in usable])) if usable else float("inf")
    coverage = len(usable) / len(windows)
    delta_brier = float(np.mean([w.brier_improvement for w in windows]))
    t = contract["thresholds"]

    reasons: List[str] = []
    if delta_brier < t["brier_margin"]:
        reasons.append(f"ΔBrier {delta_brier:.3f} below margin {t['brier_margin']}")
    if median_h > t["epsilon_c"]:
        reasons.append(f"median_W H {median_h:.3f} above ε_c {t['epsilon_c']}")
    if coverage < t["coverage_theta"]:
        reasons.append(f"coverage {coverage:.3f} below θ {t['coverage_theta']}")

    binding = bool(contract.get("registered", False))
    if not binding:
        reasons.append("contract not registered — R-5: numbers bind only at the ε ceremony")
    certified = bool(not reasons and binding)

    return CertificationResult(
        certified=certified,
        binding=binding,
        median_entropy=round(median_h, 6),
        coverage=round(coverage, 6),
        delta_brier=round(delta_brier, 6),
        reasons=reasons,
    )


# --- stability and discriminability (paper §21) ---------------------------------

def stability(measurements: Sequence[Mapping[str, float]], contract: dict) -> StabilityResult:
    """Repeated-measurement stability of one subject's signature (paper §21):
    max pairwise JSD over the repeated estimates ≤ stability_max_jsd."""
    _validate_contract(contract)
    if len(measurements) < 2:
        raise RecoverabilityError("stability requires ≥ 2 repeated measurements")
    sigs = [_normalize(m) for m in measurements]
    max_jsd = max(jsd(sigs[i], sigs[j]) for i in range(len(sigs)) for j in range(i + 1, len(sigs)))
    stable = max_jsd <= contract["thresholds"]["stability_max_jsd"]
    return StabilityResult(stable=stable, max_jsd=round(float(max_jsd), 6), n_measurements=len(measurements))


def discriminability(sig_a: Mapping[str, float], sig_b: Mapping[str, float], contract: dict) -> DiscriminabilityResult:
    """Between-subject separation (paper §21): JSD ≥ discriminability_min_jsd."""
    _validate_contract(contract)
    d = jsd(sig_a, sig_b)
    separated = d >= contract["thresholds"]["discriminability_min_jsd"]
    return DiscriminabilityResult(separated=separated, jsd=round(float(d), 6))


# --- CLI: synthetic self-check (FAKE DATA label, same discipline as m2) ---------

def main() -> int:
    import argparse

    logging.basicConfig(level=logging.INFO)
    ap = argparse.ArgumentParser(description="VT-1 recoverability certification self-check (synthetic).")
    ap.add_argument("--contract", type=Path, default=None)
    args = ap.parse_args()

    contract = load_contract(args.contract)
    # synthetic evaluation set: 40 windows, low entropy, full coverage, small
    # but positive ΔBrier — machinery demo, NOT a measurement.
    rng = np.random.RandomState(7)
    windows = [
        WindowMetrics(
            window_id=f"syn-{i:03d}",
            entropy=float(rng.uniform(0.05, 0.25)),
            has_data=True,
            brier_improvement=float(rng.uniform(0.03, 0.08)),
        )
        for i in range(40)
    ]
    result = certify(contract, windows)
    print(f"=== VT-1 RECOVERABILITY CERTIFICATION (SYNTHETIC — machinery demo) ===")
    print(f"median_W H    : {result.median_entropy:.4f} bits")
    print(f"coverage      : {result.coverage:.3f} (θ={contract['thresholds']['coverage_theta']})")
    print(f"ΔBrier (mean) : {result.delta_brier:+.4f} (margin={contract['thresholds']['brier_margin']})")
    print(f"gate read     : {result.gate_read}")
    print("REMEMBER: synthetic results validate the machinery, not the hypothesis.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
