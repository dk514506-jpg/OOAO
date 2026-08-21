#!/usr/bin/env python3
"""synthetic_manor_data.py — fake-data generator for the Manor pipeline.

Until real sensors arrive (M1 hardware), the ENTIRE pipeline runs on synthetic
data: capture -> features -> engine -> gap -> provenance. This module is the
E5 mock-first discipline made concrete — every milestone gate (M0..M5) ships
with a synthetic-data path, and the M2 sufficiency test is defined against a
synthetic no-sensor baseline.

Design notes (industry best-practices):
  - Deterministic with a seed: every run reproducible (CI-friendly).
  - Ground truth is KNOWN (the injected "real" state), so the pipeline's
    reconstruction can be scored — the whole point of a synthetic harness.
  - Physiologically plausible ranges (RR intervals 600-1200ms, RMSSD 15-80ms)
    so downstream feature code sees realistic inputs.
  - Two arms: WITH-substrate (injected state drives features) and BASELINE
    (noise-only) — the M2 sufficiency comparison.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Iterator, List

# --- physiological ranges (plausible, not measured) -----------------------------
RR_MIN_MS, RR_MAX_MS = 600.0, 1200.0
RMSSD_RANGE = (15.0, 80.0)


@dataclass
class SyntheticWindow:
    """One labeled capture window: features + ground-truth state + self-report."""

    window_id: str
    timestamp: str
    features: Dict[str, float]     # e.g. rmssd_ms, sdnn_ms, lf_hf, pnn50
    substrate_state: Dict[str, float]  # INJECTED ground truth P(EM2/4/8/10 active)
    self_report: Dict[str, float]      # participant report (noisy version of truth)
    arm: str                          # "with_substrate" | "baseline"


class SyntheticManorData:
    """Generates labeled windows for mock capture + the sufficiency harness."""

    def __init__(self, seed: int = 42, noise: float = 0.2) -> None:
        self.rng = random.Random(seed)
        self.noise = noise

    def _rr_interval(self) -> float:
        return self.rng.uniform(RR_MIN_MS, RR_MAX_MS)

    def _rmssd(self, arousal: float) -> float:
        # higher arousal -> lower HRV (lower RMSSD); clamped to physiological range
        base = RMSSD_RANGE[1] - arousal * (RMSSD_RANGE[1] - RMSSD_RANGE[0])
        return max(RMSSD_RANGE[0], min(RMSSD_RANGE[1], base + self.rng.gauss(0, 6)))

    def window(self, window_id: str, ts: datetime, arm: str) -> SyntheticWindow:
        """One window. In the with-substrate arm, injected state drives the
        features and the (noisy) self-report; in the baseline arm, features are
        noise-only — the M2 no-sensor comparison."""
        if arm == "with_substrate":
            arousal = self.rng.uniform(0.1, 0.9)                 # injected truth
            load = self.rng.uniform(0.1, 0.9)
            # substrate corners: interoception (EM8) tracks arousal, sensation
            # (EM10) tracks load, perception (EM4)/beliefs (EM2) weaker ties
            substrate_state = {
                "EM8": arousal,
                "EM10": load,
                "EM4": 0.3 + 0.4 * load,
                "EM2": 0.3 + 0.3 * arousal,
            }
            features = {
                "rmssd_ms": self._rmssd(arousal),
                "sdnn_ms": self._rmssd(arousal) * self.rng.uniform(1.1, 1.5),
                "lf_hf": self.rng.uniform(0.5, 3.0) * (2.0 - arousal),
                "pnn50": max(0.0, min(60.0, 60.0 * (1.0 - arousal) + self.rng.gauss(0, 5))),
            }
        else:  # baseline: noise-only features, flat substrate
            substrate_state = {c: 0.5 for c in ("EM2", "EM4", "EM8", "EM10")}
            features = {
                "rmssd_ms": self.rng.uniform(*RMSSD_RANGE),
                "sdnn_ms": self.rng.uniform(20.0, 90.0),
                "lf_hf": self.rng.uniform(0.5, 3.0),
                "pnn50": self.rng.uniform(5.0, 55.0),
            }

        # voice self-report: noisy read of the substrate state (per-corner leak)
        self_report = {
            "EM3": _clip(substrate_state["EM8"] * 0.8 + self.rng.gauss(0, self.noise)),
            "EM5": _clip(substrate_state["EM2"] * 0.7 + self.rng.gauss(0, self.noise)),
            "EM7": _clip(substrate_state["EM4"] * 0.6 + self.rng.gauss(0, self.noise)),
            "EM9": _clip(substrate_state["EM10"] * 0.7 + self.rng.gauss(0, self.noise)),
        }
        return SyntheticWindow(
            window_id=window_id,
            timestamp=ts.isoformat(),
            features=features,
            substrate_state=substrate_state,
            self_report=self_report,
            arm=arm,
        )

    def stream(self, n: int, arm: str = "with_substrate", start: datetime | None = None) -> Iterator[SyntheticWindow]:
        """n windows at 5-minute cadence (the capture schedule)."""
        ts = start or datetime.now(timezone.utc)
        for i in range(n):
            yield self.window(f"{arm}-{i:04d}", ts + timedelta(minutes=5 * i), arm)

    def write_csv(self, path: Path, n: int, arm: str) -> None:
        with open(path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["window_id", "timestamp", "arm",
                                               "rmssd_ms", "sdnn_ms", "lf_hf", "pnn50",
                                               "EM2", "EM4", "EM8", "EM10",
                                               "EM3", "EM5", "EM7", "EM9"])
            w.writeheader()
            for win in self.stream(n, arm):
                w.writerow({
                    "window_id": win.window_id, "timestamp": win.timestamp, "arm": win.arm,
                    **win.features, **win.substrate_state, **win.self_report,
                })


def _clip(x: float) -> float:
    return max(0.0, min(1.0, x))


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate synthetic Manor capture data (E5 mock-first).")
    ap.add_argument("--out", type=Path, default=Path("synthetic_data"), help="output dir")
    ap.add_argument("--n", type=int, default=288, help="windows per arm (288 = 24h at 5min)")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    gen = SyntheticManorData(seed=args.seed)
    args.out.mkdir(parents=True, exist_ok=True)
    gen.write_csv(args.out / "with_substrate.csv", args.n, "with_substrate")
    gen.write_csv(args.out / "baseline.csv", args.n, "baseline")

    # manifest for provenance
    manifest = {
        "generator": "synthetic_manor_data.py",
        "seed": args.seed,
        "windows_per_arm": args.n,
        "cadence_minutes": 5,
        "arms": ["with_substrate", "baseline"],
        "note": "FAKE DATA — placeholder until M1 real-sensor capture. Do not treat as measured.",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
    }
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"synthetic data written to {args.out}/ (with_substrate.csv, baseline.csv, manifest.json)")
    print("GROUND TRUTH IS KNOWN in this harness — reconstruction can be scored (the point).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
