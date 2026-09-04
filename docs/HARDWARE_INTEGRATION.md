# Hardware Integration Guide

**Where the physical system connects, and how a reviewer can trace sensor → feature → engine → action.**

HOMES is designed **synthetic-first**: the entire loop runs today on deterministic fake data (labeled `FAKE DATA`), and every real-hardware branch is gated behind a clean interface. This means a reviewer can run the whole system *right now* with no hardware, and can see precisely where each physical sensor plugs in.

---

## 1. The plug-in philosophy

Three rules keep the hardware boundary clean and honest:

1. **A single interface per sensor.** Each physical device maps to one capture module that yields a typed, provenance-bearing window. Downstream code never touches the device directly.
2. **Real is gated, never faked.** The real-hardware branch (`mock=False`) raises `PolarUnavailable` until the device is present. It does **not** silently substitute synthetic data or fabricate a "real" result.
3. **Identical downstream.** The feature → engine → gap → provenance chain is **byte-identical** for real and synthetic windows. Hardware only changes the *source* of the RR stream, never the pipeline that consumes it.

---

## 2. The Stage-A hardware plug-in (M1: EM8 interoception)

This is the **first and primary** hardware integration. It is the keystone gate of the entire program.

```
   Polar H10 HRV strap (BLE, ECG-grade)
              │  1 kHz ECG
              ▼
   polar_capture.py  ──►  RR intervals (ms)  +  provenance  (T8)
              │
              ▼
   hrv_pipeline.py  ──►  RMSSD/SDNN/LFHF/pNN50 via neurokit2  (T9)
              │
              ▼
   em_theory_bayes.py  ──►  P(EM8 | features) → voice predictions  (T10)
              │
              ▼
   reconciliation_gap(predicted, self-reported)  (primary DV)
              │
              ▼
   storage/store.py  ──►  provenance-tagged logbook row (M1 write target)
```

### The interface (concrete)

```python
# polar_capture.py
from polar_capture import CaptureWindow, capture_rr_window, is_polar_present

window: CaptureWindow = capture_rr_window(
    n=300,          # ~4-5 min of beats
    mock=True,      # False once the Polar H10 is present
    seed=7,         # deterministic synthetic stream (FAKE DATA)
)
# window.rr_intervals_ms : list[float]  (heartbeats, ms)
# window.as_provenance() : Provenance   (source/timestamp/version/confidence/actor)
```

The **only** change to go live is `mock=False`. When the strap is present:

```bash
python polar_capture.py        # prints detection + a real/synthetic window
```

### Bill of materials (Stage A)

| Part | Purpose |
|------|---------|
| Raspberry Pi 5 | local compute node (or a dev machine until M1) |
| Polar H10 HRV strap | ECG-grade BLE heart rate + RR stream |
| (optional) BLE USB dongle | A6 class — range/stability for the Pi's BLE |

Full BOM with Stage B–D sensors in [`HARDWARE_BUILD_SPEC.md`](docs/HARDWARE_BUILD_SPEC.md).

---

## 3. The later-stage plug-ins (M3/M4)

These follow the same pattern; the capture modules are staged in `leg3_manifest.csv` and wired as their measurement models land.

| Stage | Hardware | Corner | Plugs into | Gate |
|-------|----------|--------|------------|------|
| **B** | Zigbee/USB hub: ambient light, sound, temperature | EM10 sensation | (Stage B feature wiring) | M3 |
| **C** | Disciplined webcam (on-device, default-off, **no frames stored**) | EM4 perception | (Stage C) | M4 |
| **D** | Derived: D1/D2 state + log history | EM2 latent | (Stage D) | M4 |

The webcam stage is **disciplined by design**: on-device inference only, physical off by default, no frame storage — it must *earn its place* by beating the no-camera baseline, or it is pruned (an honest negative).

---

## 4. Data flow with retention governance (OC-4)

Once hardware flows, biometric data is governed, not hoarded:

```
   Polar H10 ──► capture/raw/          (Class A: raw RR, 30-day default purge)
        │
        ▼
   features store                     (Class B: RMSSD/SDNN/LFHF, 90-day default)
        │
        ▼
   logbook (storage/schema.sql)       (Class C: reconciled state — NEVER purged)
                                      (Class D: provenance — append-only)
```

`retention_purge.py` enforces this:
- Class A raw signals: **hard-deleted** after 30 days (irreversible), erasure *fact* logged to an audit ledger.
- Class B features: purged after 90 days (extension via documented sign-off for study duration).
- **The purge never touches the logbook** (keystone-governed Class C/D).
- H4-trip acceleration: an ease-off shortens the effective raw window to 7 days.

```bash
python retention_purge.py              # dry-run (default)
python retention_purge.py --apply      # enforce retention
python retention_purge.py --apply --h4-trip   # accelerated ease-off purge
```

---

## 5. How to verify the integration works

```bash
# 1. Install pinned deps
pip install -r requirements.txt

# 2. Run the full gate suite (91 tests) — all synthetic-first, no hardware needed
python -m pytest gates/ -q            # expect: 91 passed

# 3. Run the capture module (mock path)
python polar_capture.py               # prints a synthetic window + detection probe

# 4. When the Polar H10 arrives:
python polar_capture.py               # confirm detection (mock=False path)
python -m pytest gates/test_m1_real_path.py -v   # real-loop gate
```

The M1 gate is **already closed on the synthetic baseline**. The real-HRV run is the remaining step, pending Stage-A hardware arrival.

---

## 6. Review checklist for hardware-minded reviewers

If you're reviewing the physical-instrumentation side, the highest-value questions are:

1. **EM8 estimability** — Can a Polar H10 (or similar HRV strap) plausibly recover an "interoception" signal robustly enough to beat a no-sensor baseline? (This is the program's entire keystone premise — Leg 3.)
2. **Motion/caffeine/exercise confounds** — the manifest flags these as the key EM8 failure modes. How would you design them out?
3. **Webcam discipline** — is the "on-device, default-off, no-frame-storage" posture sufficient, or is any camera still too surveillant for this project's H4 values?
4. **The synthetic-first boundary** — is the mock/real gating sound? Could a reviewer be misled into thinking synthetic results are real?

---

*The instrumentation is designed to be a reviewer's-first-class citizen: traceable, gated, and honest about exactly what is synthetic today and what awaits hardware.*
