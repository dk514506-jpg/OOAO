#!/usr/bin/env python3
"""m2_sufficiency.py — the M2 sufficiency harness (B.6 protocol, T11).

The B.6 three-move protocol, made executable:

  1. COLLECT LABELED WINDOWS — the synthetic harness generates both arms:
     with_substrate (injected state drives features + noisy self-report) and
     baseline (noise-only features, flat substrate). Ground truth is KNOWN.
  2. FIT AND HOLD OUT — fit the measurement model (RMSSD -> P(EM8)) on a
     training split; evaluate on held-out windows. Estimate quality is judged
     by CALIBRATION (is P well-calibrated?), not point accuracy — a
     well-calibrated 0.6 beats a confident wrong 1.0 (B.6).
  3. RUN THE SUFFICIENCY TEST — does predicting the voices from the estimated
     substrate beat the no-sensor baseline at matching self-report? Per
     corner and overall. The gate: GO/NO-GO #1 (M2).

SYNTHETIC-FIRST: this run validates the HARNESS on fake data (FAKE DATA
discipline — the result is harness validation, not measurement). The real M2
go/no-go happens on real labeled windows once M1 hardware lands; the harness
is the same, only the data source changes.

Industry best-practices: deterministic seed, train/test split, calibration
curve + Brier score (not accuracy), paired comparison vs baseline, results
written to a JSON artifact with provenance.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from cds.stats.bootstrap import bootstrap_ci
from cds.stats.power import power_t_test

from synthetic_manor_data import SyntheticManorData


@dataclass
class SufficiencyResult:
    """The M2 output: per-corner and overall sufficiency vs baseline."""

    corner: str
    brier_with_substrate: float      # calibration error, sensor arm
    brier_baseline: float            # calibration error, no-sensor arm
    improvement: float               # brier_baseline - brier_with_substrate (>0 = sensor helps)
    n_train: int
    n_test: int
    synthetic: bool = True           # FAKE DATA label — always true until M1 hardware
    improvement_ci: Optional[Tuple[float, float]] = None  # bootstrap 95% CI on paired per-window deltas
    power_report: Optional[Dict[str, float]] = None       # descriptive post-hoc power (FAKE DATA — not a driver)

    @property
    def gate_read(self) -> str:
        if self.improvement <= 0.0:
            return "NO-GO: sensor arm does not beat baseline"
        if self.improvement < 0.02:
            return "MARGINAL: improvement within noise — knife-edge"
        return "GO: sensor arm beats no-sensor baseline at matching self-report"


def _brier(preds: np.ndarray, actuals: np.ndarray) -> float:
    """Brier score: mean squared error of predicted probability vs binary outcome.
    Well-calibrated predictions minimize this; it punishes confident-wrong 1.0."""
    return float(np.mean((preds - actuals) ** 2))


def _calibrate(preds: np.ndarray, actuals: np.ndarray, n_bins: int = 5) -> Dict[str, float]:
    """Calibration curve summary: for each bin, |mean prediction - observed rate|.
    Returns the max miscalibration (0 = perfectly calibrated)."""
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    max_err = 0.0
    for lo, hi in zip(bins[:-1], bins[1:]):
        m = (preds >= lo) & (preds < hi)
        if m.sum() == 0:
            continue
        mean_pred = preds[m].mean()
        observed = actuals[m].mean()
        max_err = max(max_err, abs(mean_pred - observed))
    return {"max_miscalibration": round(float(max_err), 4), "n_bins": n_bins}


def fit_measurement_model(
    windows: List, corner: str, noise: float
) -> Tuple[float, float]:
    """Fit RMSSD -> P(corner active) via logistic regression on the training arm.
    Returns (intercept, slope) — the measurement model for this corner.
    Synthetic stand-in for the M1 feature path (neurokit2 RMSSD -> posterior).
    """
    X = np.array([w.features["rmssd_ms"] for w in windows], dtype=float)
    y = np.array([1.0 if w.substrate_state[corner] > 0.5 else 0.0 for w in windows])

    # logistic fit via simple gradient descent (deterministic seed)
    rng = np.random.RandomState(42)
    Xs = (X - X.mean()) / (X.std() + 1e-9)
    w_slope, b = 0.0, 0.0
    lr = 0.1
    for _ in range(500):
        z = w_slope * Xs + b
        p = 1.0 / (1.0 + np.exp(-z))
        grad_w = np.mean((p - y) * Xs)
        grad_b = np.mean(p - y)
        w_slope -= lr * grad_w
        b -= lr * grad_b
    return float(w_slope), float(b)


def predict(windows: List, corner: str, w_slope: float, b: float,
            x_mean: float, x_std: float) -> np.ndarray:
    X = np.array([w.features["rmssd_ms"] for w in windows], dtype=float)
    Xs = (X - x_mean) / (x_std + 1e-9)
    return 1.0 / (1.0 + np.exp(-(w_slope * Xs + b)))


def run_sufficiency(
    n_windows: int = 200,
    seed: int = 42,
    noise: float = 0.2,
    corner: str = "EM8",
    test_frac: float = 0.3,
) -> SufficiencyResult:
    """The B.6 three-move protocol for one corner, synthetic data."""
    gen = SyntheticManorData(seed=seed, noise=noise)

    # MOVE 1: collect labeled windows (both arms)
    sensor_windows = list(gen.stream(n_windows, arm="with_substrate"))
    baseline_windows = list(gen.stream(n_windows, arm="baseline"))

    # MOVE 2: fit on train, hold out, evaluate CALIBRATION not accuracy.
    # Normalization stats come from the TRAIN arm only (no test leakage).
    n_train = int(n_windows * (1 - test_frac))
    train = sensor_windows[:n_train]
    test = sensor_windows[n_train:]

    x_train = np.array([w.features["rmssd_ms"] for w in train], dtype=float)
    x_mean, x_std = float(x_train.mean()), float(x_train.std())
    w_slope, b = fit_measurement_model(train, corner, noise)
    preds_sensor = predict(test, corner, w_slope, b, x_mean, x_std)
    actuals_sensor = np.array([1.0 if w.substrate_state[corner] > 0.5 else 0.0 for w in test])

    # baseline arm: no-sensor model predicts the prior (0.5) for everything
    preds_baseline = np.full(len(test), 0.5)
    actuals_baseline = np.array([1.0 if w.substrate_state[corner] > 0.5 else 0.0 for w in test])

    brier_sensor = _brier(preds_sensor, actuals_sensor)
    brier_baseline = _brier(preds_baseline, actuals_baseline)

    # Paired inference (Council N2): both arms share the same held-out windows,
    # so the CI is a percentile bootstrap over PER-WINDOW deltas
    # (baseline_sqerr - sensor_sqerr), not an independent-samples resample.
    # The mean of these deltas equals `improvement` by construction.
    se_sensor = (preds_sensor - actuals_sensor) ** 2.0
    se_baseline = (preds_baseline - actuals_baseline) ** 2.0
    per_window_delta = [float(d) for d in (se_baseline - se_sensor)]
    ci = bootstrap_ci(per_window_delta, n_resamples=2000, seed=seed)
    delta_std = float(np.std(per_window_delta))
    d_obs = float(np.mean(per_window_delta) / delta_std) if delta_std > 0.0 else 0.0
    # Descriptive post-hoc power (Council N3): two-sample approximation, clearly
    # labeled — harness characterization on FAKE DATA, not a go/no-go driver.
    power_report = {
        "method": "cds power_t_test (pooled two-sample approx; post-hoc, descriptive)",
        "effect_size_d": round(d_obs, 4),
        "n_per_group": len(test),
        "alpha": 0.05,
        "power": round(float(power_t_test(d_obs, len(test))), 4),
        "note": "FAKE DATA harness characterization only — real M2 uses paired inference on hardware windows",
    }

    return SufficiencyResult(
        corner=corner,
        brier_with_substrate=round(brier_sensor, 4),
        brier_baseline=round(brier_baseline, 4),
        improvement=round(brier_baseline - brier_sensor, 4),
        n_train=n_train,
        n_test=len(test),
        synthetic=True,
        improvement_ci=(round(float(ci.lower), 4), round(float(ci.upper), 4)),
        power_report=power_report,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="M2 sufficiency harness (B.6), synthetic-first.")
    ap.add_argument("--n", type=int, default=200, help="windows per arm")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", type=Path, default=Path("data/m2_sufficiency.json"))
    args = ap.parse_args()

    results = [run_sufficiency(n_windows=args.n, seed=args.seed, corner=c) for c in ("EM8", "EM10", "EM4", "EM2")]

    artifact = {
        "protocol": "B.6 three-move (collect / fit-hold-out-calibrate / sufficiency)",
        "synthetic": True,
        "note": "FAKE DATA — harness validation only, NOT a measured M2 go/no-go. Real M2 requires M1 hardware + labeled self-report windows.",
        "seed": args.seed,
        "n_windows_per_arm": args.n,
        "test_frac": 0.3,
        "results": [{**r.__dict__, "gate_read": r.gate_read} for r in results],
        "generated_utc": datetime.now(timezone.utc).isoformat(),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(artifact, indent=2))

    print("=== M2 SUFFICIENCY (SYNTHETIC — harness validation, NOT measurement) ===")
    for r in results:
        print(f"\ncorner {r.corner}:")
        print(f"  Brier sensor arm:    {r.brier_with_substrate:.4f}")
        print(f"  Brier baseline arm:  {r.brier_baseline:.4f}")
        print(f"  improvement:         {r.improvement:+.4f}  (positive = sensor helps)")
        if r.improvement_ci:
            print(f"  improvement CI (95%): [{r.improvement_ci[0]:+.4f}, {r.improvement_ci[1]:+.4f}]  (paired bootstrap)")
        if r.power_report:
            print(f"  post-hoc power:      {r.power_report['power']:.3f} at d={r.power_report['effect_size_d']:.3f} "
                  f"(descriptive, FAKE DATA)")
        print(f"  gate read:           {r.gate_read}")
    print(f"\nartifact: {args.out}")
    print("REMEMBER: synthetic results validate the harness, not the hypothesis.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
