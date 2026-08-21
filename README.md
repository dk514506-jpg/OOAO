# HOMES — Home-Lab Operational Multi-domain Ecological System

**A governed, single-case research instrument for cultivating everyday awe, wonder, and felt knowing — built as a cognitive-and-spatial digital twin of one home and one person.**

> *"The promise of HOMES is not that it is elegant, nor that it proves awe can be engineered. It is that a person and a governed system can improve together, each supplying what the other needs, without that improvement costing the person the trust the whole project depends on."*

HOMES is an autistic-led, **n = 1**, local-first research program. It investigates whether a carefully governed technical ecology — sensors, a Bayesian inference engine, a set of bounded AI "personas," and a blueprint-governed action layer — can help establish favorable conditions for **everyday awe, wonder, recognition, and durable felt knowing**, without turning a home into a surveillance environment.

This repository is the **engine + governance + hardware-integration** core. It is structured so that a reviewer can trace the full chain: *sensor → feature → substrate estimate → voice prediction → reconciliation gap → governed action*, and see exactly where physical hardware plugs in.

---

## Why this exists

Most cognitive-support AI is a black box that optimizes task completion. HOMES is the opposite: an **instrument** whose central measure is a **reconciliation gap** — the divergence between what a machine predicts about a person's internal state from sensors, and what the person actually reports feeling.

The thesis: a well-grounded system and a well-practiced person can improve together, in a loop, *without* the system defining the person's internal state back to them (the H4 anti-iatrogenic gate guards this). Memory and routine are **enabling infrastructure, not the outcome**. The outcome is wonder — and its returnability.

---

## Repository map

```
├── README.md                 ← you are here
├── LICENSE
├── requirements.txt          ← pinned dependencies (Python 3.11+, verified)
│
├── ARCHITECTURE.md           ← the full system architecture (Daemon Manor v4.1)
├── ROADMAP.md                ← three legs × phases × gates × decision points
├── IMPLEMENTATION_PLAN.md    ← task graph (T1–T18), milestone gates M0–M5
├── HARDWARE_BUILD_SPEC.md    ← Stage A–D bill of materials + wiring order
├── MEMORY_DESIGN.md          ← the D4 memory/worldview layer
│
├── em_theory_bayes.py        ← ★ the situating-bridge inference engine (no math in LLM)
├── triple_index.py           ← OCI/CAI/CSI gate, instantiated from Kabashkin (2026)
├── grounding_gate.py         ← write-time provenance+traceability+groundedness gate
├── m2_sufficiency.py         ← the Leg-3 sufficiency test (GO/NO-GO #1) harness
├── synthetic_manor_data.py   ← deterministic fake-data generator (FAKE-DATA labeled)
├── polar_capture.py          ← ★ POLAR H10 BLE capture — the real-hardware plug-in
├── hrv_pipeline.py           ← feature extraction → engine posterior → gap
├── retention_purge.py        ← biometric retention/erasure enforcement (OC-4)
│
├── bp_c_em.yaml              ← governed contract for the situating bridge (1:1 to code)
├── leg3_manifest.csv         ← corner/sensor/estimability map
│
├── storage/
│   ├── schema.sql            ← fail-closed logbook schema (WAL, provenance-tagged)
│   └── store.py              ← fail-closed SQLite writer
│
└── gates/                    ← the M0–M5 test gates (currently 53 tests, all passing)
    ├── test_m0_mock_loop.py
    ├── test_m1_capture_smoke.py
    ├── test_m1_real_path.py
    ├── test_m2_sufficiency.py
    ├── test_engine_negative.py
    ├── test_grounding_gate.py
    ├── test_triple_index.py
    └── test_storage.py
```

---

## The core idea in one diagram

```
   SENSORS                 ENGINE                    PERSON
─────────────────   ──────────────────────   ─────────────────────
  HRV strap   ──►   P(EM8 | features)   ──►   predicts "voices"
  ambient     ──►   P(EM10| ... )       ──►   (worry, rumination,
  webcam*     ──►   P(EM4 | ... )            emotion, vigilance)
  context     ──►   P(EM2 | ... )                  │
        │                                       self-report (ground truth)
        ▼                                           │
   SUBSTRATE ESTIMATE (machine)                     │
        └──────────────► divergence ◄───────────────┘
                    = THE RECONCILIATION GAP (primary dependent variable)
```

- **4 substrate corners** (estimated by machine, non-reportable): EM2 latent state, EM4 perception, EM8 interoception, EM10 sensation.
- **4 voice corners** (self-reported): EM3 worry, EM5 rumination, EM7 emotion, EM9 vigilance.
- The **gap** between predicted and reported voices is simultaneously: (a) the primary research measure, (b) the active-inference prediction error that personalizes the model, and (c) the anti-drift force keeping the system about *this one person*.
- The **LLM never does arithmetic.** It encodes (report → structured evidence) and decodes (posteriors → language). All probability math lives in `em_theory_bayes.py`.

---

## Where the hardware plugs in ★

The most common question a reviewer asks is *"where does the physical system connect?"* The answer is deliberately clean and **synthetic-first**: every real-hardware branch is gated behind a clear interface, so the whole loop runs today on synthetic data (FAKE-DATA labeled) and switches to real signals the moment hardware is present.

| Stage | Hardware | Sensor | Plugs into | Gate |
|-------|----------|--------|------------|------|
| **A** | Raspberry Pi 5 + **Polar H10** HRV strap (BLE) | EM8 interoception | `polar_capture.py` → `hrv_pipeline.py` | **M1** |
| **B** | Zigbee/USB hub: ambient light, sound, temperature | EM10 sensation | (feature wiring, Stage B) | **M3** |
| **C** | Disciplined webcam (on-device, default-off, no frames stored) | EM4 perception | (Stage C) | **M4** |
| **D** | Derived (D1/D2 state + log history) | EM2 latent | (Stage D) | **M4** |

### The M1 hardware plug-in, concretely

```python
# polar_capture.py — the real-hardware entry point
from polar_capture import capture_rr_window, is_polar_present

if is_polar_present():                      # BLE reachability probe
    window = capture_rr_window(mock=False)  # ★ REAL Polar H10 RR stream (ms)
else:
    window = capture_rr_window(mock=True)   # deterministic synthetic stand-in
```

`capture_rr_window(mock=False)` raises `PolarUnavailable` until the strap is present — it **never fabricates** a real result. The downstream pipeline (`hrv_pipeline.py` → engine → gap → provenance) is **identical** for real and synthetic windows, so the loop closes on real data the moment the device arrives.

### The measurement chain (traceable end-to-end)

```
polar_capture.py:      BLE → RR intervals (ms) + provenance
        │
hrv_pipeline.py:       neurokit2 → RMSSD/SDNN/LFHF/pNN50   (T9)
        │
em_theory_bayes.py:    feature → P(EM8) → voice prediction  (T10)
        │
reconciliation_gap:    predicted vs self-report → gap g(t)  ★ primary DV
        │
storage/store.py:      fail-closed provenance-tagged logbook row (M1 write target)
```

Every durable record carries the engine-minimum provenance (`source, timestamp, schema_version, confidence, actor`); an empty field **rejects the write** (fail-closed).

---

## Governance — what makes this safe, not just clever

HOMES is **blueprint-governed**: no material change to the system goes live without passing through a governed lifecycle (`Draft → Designed → Coded → Validated → Approved → Active`). Three code families keep inference bounded:

- **Authority ceilings (A0–A6):** A6 (autonomous action) is *reserved and unauthorized*. The situating bridge is capped at **A4** (state candidate only); the invitation it gates is capped at **A2** (recommend). No model reading may write durable memory, change the room, or speak unbounded — each is a separate gated blueprint requiring explicit sign-off.
- **Trust tiers (T0–T3):** unverified sources log only; only cross-verified state reaches durable memory.
- **Triple-Index gate (OCI/CAI/CSI):** `triple_index.py` computes ontology consistency, cognitive adequacy, and confidence from Kabashkin (2026) — before any memory write, recommendation, or action, all three must clear their thresholds.

### The H4 anti-iatrogenic gate (the soul of the project)

Any benefit that arises from **increased self-surveillance** rather than genuine support is counted as a **failure**, not a win. The gate watches `felt-watched`, `tracking anxiety`, and `experiential flattening`; if the reconciliation gap collapses toward zero *while felt-watched rises*, that signals **deference, not perfect observation** — and the system **halts personalization** and eases off. This is encoded in `grounding_gate.py` and the H4 safety review.

### Biometric data is governed, not hoarded (OC-4)

`retention_purge.py` enforces a tiered retention policy: raw biosignals (Class A) are purged after 30 days by default; derived features (Class B) after 90; the purge **never touches** the keystone-governed reconciled logbook. Erasure is irreversible **and** provable — content hard-deleted, the *fact* of erasure appended to an audit ledger. Raw signals never leave the local store (no cloud, no egress).

---

## Verification & test discipline

The repository ships with a **53-test gate suite** that must pass before any milestone is declared. It follows a strict **mock-first (E5) discipline**: every gate runs against deterministic synthetic data first; real hardware replaces mocks at M1 but the synthetic path remains as the regression baseline. Negative tests are first-class — the engine **refuses to run without its contract file**, empty provenance raises, out-of-range confidence raises, and an ungrounded claim that cites real assets is **rejected** by the write-time gate.

```bash
pip install -r requirements.txt
python -m pytest gates/ -q        # expect: 53 passed
```

All synthetic data is labeled `FAKE DATA` in its manifest — the project refuses to let its own test fixtures masquerade as measurements.

---

## Research design (the honest frame)

- **n = 1 single-case experimental design (SCED)** toward What Works Clearinghouse standards.
- **Seven phases** (Phase 0 baseline → Phase 6 system refinement), with multiple-baseline logic staggered across practices/rooms so any effect is attributable to HOMES, not time.
- **Four authenticity tests** falsify the timing claim: Barnum dissociation, counterfactual state-sensitivity, grounding-in-fiction, and iatrogenic gap-collapse.
- **Leg 3 executes first** — the substrate-estimability go/no-go. An honest negative result (the fidelity map) is a *contribution*, not a failure.
- **No neuro or diagnostic claims.** The system measures behavior, self-report, and the human–machine gap — never brain states. EM-Theory's clinical and cosmological apparatus is explicitly out of scope.

---

## Status & roadmap

| Milestone | Status |
|-----------|--------|
| M0 — engine on synthetic data | ✅ complete (reference implementation) |
| M1 — EM8 loop closes (HRV) | ✅ closed on **synthetic** baseline; **real-HRV run pending Polar H10 arrival** |
| M2 — EM8 sufficiency (GO/NO-GO #1) | 🟡 harness validated on synthetic; real go/no-go waits for M1 hardware |
| M3–M4 — add EM10, EM4, EM2 + fidelity map | ⏳ downstream |
| M5 — keystone stands / honest negative | ⏳ gated on M2 |

The build is specified to the level of a **bill of materials and a task graph** (`HARDWARE_BUILD_SPEC.md`, `IMPLEMENTATION_PLAN.md`) — a capable solo builder can read the spec on a Friday and order Stage-A parts by Saturday.

---

## How to engage / contribute

This is a living research instrument, not a finished product. The most valuable contributions are:

- **Review of the measurement chain** — especially whether home-grade sensors can plausibly recover the EM8 interoception corner (the Leg-3 keystone question).
- **Critique of the governance grammar** — the A0–A6 ceilings, trust tiers, Triple-Index gate, and the H4 anti-iatrogenic logic.
- **Single-case (SCED) methodological co-authorship** — randomization/replication structure, visual analysis, Tau-U reporting.
- **Hardware partnership** — the Polar H10/Stage-A integration and the disciplined webcam stage.
- **An external ethics perspective** — precisely valuable because participant and investigator coincide.

If you're reading this and something strikes you as overclaimed, under-specified, or wrong: that is the *most* useful thing you can send back. The project's integrity depends on it.

---

## License

[Licensed under the MIT License](LICENSE). See the LICENSE file for the full text.

*Local-first · Autistic-led · n = 1 · Blueprint-governed · Anti-surveillant · Phenomenologically preserving*
