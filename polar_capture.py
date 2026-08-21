#!/usr/bin/env python3
"""polar_capture.py — Polar H10 BLE HRV capture (implementation plan T8).

Bridges the M1 capture step from SYNTHETIC to REAL hardware. The M1 gate
(test_m1_capture_smoke.py) currently feeds the pipeline a synthetic RR
stream (Polar H10 stand-in). This module provides the REAL capture path
so that, when the strap arrives, the same downstream pipeline (features
-> engine -> gap -> provenance) runs on live RR intervals.

Field standard: the Polar H10 streams ECG-grade data over BLE; the
polar-h10 library (or its fork) yields RR intervals in milliseconds from
a 1 kHz ECG. The RR interval (ms) is the canonical input to neurokit2's
HRV feature extraction (intervals_to_peaks -> hrv), exactly as the M1
smoke test's _hrv_features does.

Design (E5 mock-first, synthetic until M1 hardware):
- `capture_forever(...)`: generator yielding RR intervals from the
  strap. Until hardware is present this raises PolarUnavailable.
- `capture_rr_window(...)`: collect a bounded window (default ~300 beats,
  ~4-5 min) -> list[float] RR ms, matching the smoke test's stream shape.
- `is_polar_present() -> bool`: detect whether a strap is reachable via
  bluetooth, so callers can route synthetic vs real without guessing.

Mock mode: pass mock=True (default) to get a deterministic synthetic
stream via SyntheticManorData (regression-safe, FAKE-DATA labeled). This
keeps the module testable WITHOUT hardware and preserves the synthetic
regression baseline.

Provenance: every returned window carries a capture provenance object
(source='polar.capture' real | 'synthetic.capture' mock, timestamp,
schema_version, confidence, actor='capture').

No raw signal is ever written here; this module only produces the RR
window and its provenance. Storage/retention is the logbook's + the
OC-4 purge job's concern (see OC4_BIOMETRIC_RETENTION_POLICY.md).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterator, List, Optional

logger = logging.getLogger("polar_capture")


class PolarUnavailable(RuntimeError):
    """Raised when real capture is requested but no Polar H10 is reachable."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class CaptureWindow:
    """A bounded RR-interval window (ms) plus provenance."""

    rr_intervals_ms: List[float]
    source: str            # 'polar.capture' (real) | 'synthetic.capture' (mock)
    timestamp: str
    schema_version: str
    confidence: float      # 0..1
    actor: str = "capture"

    def as_provenance(self):
        from em_theory_bayes import Provenance
        return Provenance(self.source, self.timestamp, self.schema_version,
                          self.confidence, self.actor)


def is_polar_present() -> bool:
    """Detect whether a Polar H10 strap is reachable over Bluetooth.

    Returns False when no device is paired/visible. Until hardware
    arrives this is False; callers should route to mock. Not a guarantee
    of a working stream — just a reachability probe.
    """
    try:
        import subprocess
        out = subprocess.run(
            ["bluetoothctl", "devices"], capture_output=True, text=True, timeout=8
        )
        return "Polar" in (out.stdout or "")
    except Exception as e:  # bluetoothctl missing / timeout / no BT stack
        logger.debug("polar presence probe failed: %s", e)
        return False


def _synthetic_stream(n: int = 300, seed: int = 7) -> List[float]:
    """Deterministic synthetic RR stream (Polar H10 stand-in), FAKE-DATA.

    Mirrors the M1 smoke test fixture: ~60-80 bpm resting baseline with
    respiratory sinus arrhythmia, RR 600-1200 ms.
    """
    import math
    import random
    rng = random.Random(seed)
    base = rng.uniform(800.0, 950.0)
    stream = []
    for i in range(n):
        rr = base + rng.gauss(0, 18) + 25.0 * math.sin(i / 20.0)
        stream.append(round(max(600.0, min(1200.0, rr)), 1))
    return stream


def capture_rr_window(n: int = 300, mock: bool = True, seed: int = 7) -> CaptureWindow:
    """Collect a bounded RR window (ms).

    mock=True (default): deterministic synthetic stream, FAKE-DATA
    labeled (source='synthetic.capture'). Regression-safe, works now.
    mock=False: REAL Polar H10 BLE capture. Raises PolarUnavailable if no
    strap is present. Requires the polar-h10 library (pinned in
    requirements.txt at M1).
    """
    if mock:
        rr = _synthetic_stream(n=n, seed=seed)
        return CaptureWindow(
            rr_intervals_ms=rr, source="synthetic.capture",
            timestamp=_now(), schema_version="0.1", confidence=0.9,
        )

    if not is_polar_present():
        raise PolarUnavailable(
            "no Polar H10 reachable; capture_rr_window(mock=False) needs the strap "
            "(M1 hardware not yet present)"
        )

    # --- real capture path (enabled when hardware + polar-h10 arrive) ---
    try:
        import polar_h10  # noqa: F401  (pinned at M1)
    except ImportError as e:
        raise PolarUnavailable(
            "polar-h10 library not installed; run M1 setup to pin it"
        ) from e
    # TODO(M1): instantiate the strap, subscribe to the RR stream, collect
    # n RR intervals in ms. This is the hardware-gated branch; it cannot
    # be exercised until the device arrives. The synthetic branch above is
    # the verified, regression-safe path.
    raise PolarUnavailable(
        "real capture branch is stubbed until the Polar H10 is present "
        "(synthetic-first discipline; see 09_implementation_plan.md §7)"
    )


def capture_forever(mock: bool = True, **kw) -> Iterator[CaptureWindow]:
    """Stream windows indefinitely (mock default). Each iteration yields
    one bounded CaptureWindow; use for live M1 loop before M1 hardware."""
    while True:
        yield capture_rr_window(mock=mock, **kw)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    win = capture_rr_window(mock=True)
    prov = win.as_provenance()
    prov.validate()
    mean_rr = sum(win.rr_intervals_ms) / len(win.rr_intervals_ms)
    hr = 60_000 / mean_rr
    print(f"capture (mock) OK: n={len(win.rr_intervals_ms)} mean_RR={mean_rr:.1f}ms "
          f"implied_HR={hr:.1f}bpm source={win.source}")
    print("Polar present:", is_polar_present())
