#!/usr/bin/env python3
"""hrv_pipeline.py — feature extraction -> engine posterior -> gap -> provenance
(implementation plan T9/T10).

Turns a CaptureWindow (from polar_capture.py) into the reconciled engine
output, closing the EM8 loop. This is the real, hardware-agnostic wiring
the M1 smoke test exercises end-to-end on synthetic data (and will run
identically on real RR once the strap arrives).

Pipeline (matches the M1 gate contract, 09_implementation_plan.md §4):
  1. FEATURES  (T9): neurokit2 field-standard HRV on the RR stream
     (intervals_to_peaks -> hrv). Produces RMSSD/SDNN/LFHF/pNN50.
  2. MEASUREMENT MODEL: feature -> P(EM8 interoception active). At M1
     this uses the annotated mapping (low RMSSD => higher arousal =>
     higher P(EM8)); M2 learns the real measurement model. Marked as the
     M1 provisional estimate, NOT the M2-learned posterior.
  3. ENGINE (T10): substrate posterior -> voice predictions -> gap vs a
     supplied self-report. All arithmetic in em_theory_bayes.py.
  4. PROVENANCE: every durable record carries the engine-minimum fields;
     the caller writes to the logbook (storage/store.py) per OC-4 class
     rules.
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import numpy as np

from em_theory_bayes import (  # noqa: E402
    EmTheoryBayes, Provenance, SubstratePosterior, VoicePrediction,
    SelfReport, ReconciliationGap, SUBSTRATE_CORNERS, VOICE_CORNERS,
)
from polar_capture import CaptureWindow  # noqa: E402

import neurokit2 as nk  # noqa: E402


@dataclass(frozen=True)
class Em8Features:
    """Derived HRV features (Class B data)."""

    rmssd: float
    sdnn: float
    lfhf: float
    pnn50: float

    def as_dict(self) -> Dict[str, float]:
        return {
            "RMSSD": round(self.rmssd, 3),
            "SDNN": round(self.sdnn, 3),
            "LFHF": round(self.lfhf, 3),
            "pNN50": round(self.pnn50, 3),
        }


def extract_hrv_features(rr_intervals_ms: Sequence[float]) -> Em8Features:
    """Field-standard neurokit2 HRV extraction (T9).

    RR intervals (ms) -> peaks -> time+frequency HRV, mirroring the M1
    smoke test's _hrv_features. pNN50 added as a 4th standard feature.
    """
    peaks = nk.intervals_to_peaks(np.asarray(rr_intervals_ms, dtype=float))
    hrv = nk.hrv(peaks, sampling_rate=1000, show=False)
    def g(col: str, default: float) -> float:
        return float(hrv[col].iloc[0]) if col in hrv.columns and not math.isnan(float(hrv[col].iloc[0])) else default
    return Em8Features(
        rmssd=g("HRV_RMSSD", float("nan")),
        sdnn=g("HRV_SDNN", float("nan")),
        lfhf=g("HRV_LFHF", float("nan")),
        pnn50=g("HRV_pNN50", float("nan")),
    )


def feature_to_posterior(features: Em8Features, others: Optional[Dict[str, float]] = None) -> Dict[str, float]:
    """Measurement model (M1 provisional): feature -> P(substrate corners).

    EM8 interoception: low RMSSD => higher autonomic arousal => higher
    P(EM8 active). Annotated mapping (same as the M1 smoke test). The
    other substrate corners (EM2/EM4/EM10) are held at neutral until their
    measurement models land (M3/M4 per leg3_manifest). This is the M1
    PROVISIONAL estimate — M2 learns the real measurement model.
    """
    rmssd = features.rmssd if not math.isnan(features.rmssd) else 60.0
    arousal = max(0.0, min(1.0, (80.0 - rmssd) / 65.0))
    base = others or {}
    return {
        "EM2": base.get("EM2", 0.5),
        "EM4": base.get("EM4", 0.5),
        "EM8": arousal,
        "EM10": base.get("EM10", 0.5),
    }


@dataclass(frozen=True)
class PipelineResult:
    """The full M1 pipeline output for one capture window."""

    features: Em8Features
    posterior: SubstratePosterior
    prediction: VoicePrediction
    gap: ReconciliationGap
    source: str
    timestamp: str


def run_pipeline(
    window: CaptureWindow,
    engine: EmTheoryBayes,
    self_report: Optional[Dict[str, float]] = None,
    others: Optional[Dict[str, float]] = None,
    prov_confidence: float = 0.9,
) -> PipelineResult:
    """Close the EM8 loop for one capture window (T9 + T10).

    window: CaptureWindow from polar_capture (synthetic or real).
    engine: the situating-bridge engine (mock=True OK for M1).
    self_report: participant voice ratings (default all 0.5 neutral).
    """
    features = extract_hrv_features(window.rr_intervals_ms)
    substrate = feature_to_posterior(features, others=others)

    prov = Provenance(
        source=window.source, timestamp=window.timestamp,
        schema_version=window.schema_version, confidence=prov_confidence,
        actor="capture",
    )
    posterior = SubstratePosterior(probabilities=substrate, provenance=prov)
    prediction = engine.predict_voices(posterior)

    ratings = self_report or {v: 0.5 for v in VOICE_CORNERS}
    report = SelfReport(
        ratings=ratings,
        provenance=Provenance(window.source, window.timestamp,
                              window.schema_version, 1.0, "participant"),
    )
    gap = engine.reconciliation_gap(prediction, report)

    return PipelineResult(
        features=features, posterior=posterior, prediction=prediction,
        gap=gap, source=window.source, timestamp=window.timestamp,
    )


if __name__ == "__main__":
    import em_theory_bayes as eb
    engine = eb.EmTheoryBayes(mock=True)
    win = CaptureWindow(
        rr_intervals_ms=[850.0 + 20.0 * ((i % 5) - 2) for i in range(300)],
        source="synthetic.capture", timestamp=datetime.now(timezone.utc).isoformat(),
        schema_version="0.1", confidence=0.9,
    )
    r = run_pipeline(win, engine)
    print("features:", r.features.as_dict())
    print("P(EM8):", round(r.posterior.probabilities["EM8"], 3))
    print("gap:", round(r.gap.value, 3))
    print("source:", r.source)
