# DAEMON MANOR — BUILD SPEC SHEET
## Stage A–D Hardware & Software, Pinned and Orderable
Version 1.0 · 2026-08-18 · Author: Pip · Baseline: Raspberry Pi 5 node + Polar H10 (Dallas-confirmed)
Source of truth: BP-C-EM and Leg3 Spec (B.4 hardware staging, B.5 software pipeline, B.7 milestone ladder)

---

## 0. The Friday Test

The B.8 quality bar: *a solo home-lab builder can read Part B on a Friday and
order the Stage-A parts by Saturday, knowing exactly what milestone M1 requires
and how M2 decides go/no-go.* This sheet is the answer to that test.

Stage A = the EM8 loop end-to-end: HRV strap → BLE → feature extraction →
engine (mock, then real) → provenance log → milestone M1 closes. M2 then asks
the sufficiency question: does one corner (EM8/interoception) beat a no-sensor
baseline at matching self-report?

---

## 1. Stage A Hardware BOM (order on Saturday)

| # | Item | Purpose | Est. price (USD) | Notes |
|---|---|---|---|---|
| A1 | Polar H10 heart-rate strap | ECG-grade HRV source (EM8) | ~$90 | Bluetooth (BLE) + ANT+; 1 kHz ECG sampling; the de-facto HRV research standard; official Polar app for sensor firmware updates |
| A2 | Raspberry Pi 5 (8 GB) | The Manor node: capture + engine + storage | ~$80 | 8 GB model (not 4 GB) — headroom for the engine + SQLite + a small quantized LLM |
| A3 | Official 27W USB-C PSU | Pi power | ~$12 | Pi 5 needs 5V/5A; third-party PSUs cause under-voltage warnings that corrupt capture timing |
| A4 | Raspberry Pi case (official or aluminum passive) | Enclosure | ~$10 | Passive cooling recommended (no fan noise near sensors; the room is the instrument) |
| A5 | 32 GB microSD (A2-class) | Boot + OS | ~$10 | Or NVMe HAT + 128 GB SSD if you want the log store off flash (Stage B option) |
| A6 | Bluetooth 5 dongle (if Pi's onboard BLE underperforms) | H10 link | ~$10 | Pi 5's onboard BLE works, but a USB dongle improves range/stability — order only if M1 shows drops |
| A7 | (Optional) USB-C cable + power bank | Wearable-capture mobility for calibration sessions | ~$20 | Only if you want the strap paired to a phone running the Polar app as a relay during self-anchored calibration (B.6) |

**Stage A subtotal: ~$115–135** (strap + Pi 5 + PSU + case + SD). If you already
own a Pi 5 or an H10, Stage A is ~$90 for the other half.

## 2. Stage B–D Hardware (deferred, for the roadmap)

| Stage | Corner | Candidate | Est. price | Gate to enter | Honest fidelity expectation (spec B.3) |
|---|---|---|---|---|---|
| B | EM10 sensation (light/sound/temp) | Aqara/Home Assistant Zigbee sensors (temp, lux, presence) OR a single USB sensor hub (e.g., AirGradient) + USB microphone for ambient | ~$40–120 | M3: after {EM8, EM10} sufficiency re-run | PARTIAL (load yes, felt no) |
| C | EM4 perception (webcam) | USB webcam (e.g., Logitech C920-class) | ~$50 | M4, under the B.4 webcam discipline (on-device inference, no frames stored, default-off) | WEAK — camera earns its place only if it beats the no-camera baseline |
| D | EM2 beliefs (context) | No new hardware — derived from D1/D2 state + log history | $0 | M4 (EM2 pruning decision) | NEAR-BLIND — the honest expectation; pruning decision at M4 |
| D2 | EDA (optional later arm) | Grove GSR + ADC, or a research-grade wearable | $10–1500 | Post-M5, only if the fidelity map says EDA would add a corner | — |

## 3. Software Stack (pinned; reuse, don't reinvent — B.5)

| Layer | Choice | Why | Install |
|---|---|---|---|
| OS | Raspberry Pi OS Lite (bookworm, 64-bit) | Debian base, headless, low overhead | rpi-imager |
| Runtime | Python 3.11+ in a venv | Engine + capture | apt + venv |
| BLE capture | `polar-h10` (Python, asyncio) | Mature H10 BLE client; streams HR + RR intervals | pip |
| HRV features | `neurokit2` | Community standard for HRV/EDA feature extraction (RMSSD, SDNN, LF/HF, pNN50) | pip |
| Engine | `em_theory_bayes.py` (self-contained; probability arithmetic verified against cds kernels) | The "all arithmetic lives here" layer; CPTs, inference, gap | pip |
| Storage | SQLite, file-based, provenance columns | Local-first per B.5; no cloud; Data Steward seat audits | stdlib |
| LLM (encode/decode) | llama.cpp (or Ollama) + Qwen2.5-7B-Instruct Q4_K_M | Local open-weight ~8B-class with structured output | llama.cpp build |
| Scheduler | systemd timers (capture every N min; consolidation on triggers) | The daemon-community heartbeat | systemd |
| Telemetry | Prometheus node_exporter (optional Stage B) | Old-plan GreptimeDB analog, but only if M3 needs it | pip/apt |

LLM placement note: the Pi 5 (8 GB) can run a 7B Q4 (~4–5 GB) at a few tokens/sec —
fine for decode-only persona expression, sluggish for anything else. The B.5
contract (LLM = encode/decode ONLY) makes this acceptable. If it proves too slow
at M1, move the LLM to the existing RTX 3060 PC and keep the Pi as the sensor +
engine node (the architecture is hardware-agnostic per corner; this is the E1/E11
discipline).

## 4. Wire-Up Order (physical, one Saturday)

1. Flash Pi OS Lite; boot headless; `apt update && apt upgrade`.
2. Pair the H10 via the Polar Flow app ONCE (firmware + pairing state), then
   verify BLE visibility from the Pi (`hcitool lescan` or the polar-h10 lib's scan).
3. Create `~/manor/` venv; install the pinned stack.
4. Run the capture smoke test: 5 minutes of RR intervals logged to SQLite with
   provenance columns (source=device, timestamp, raw).
5. Compute one HRV feature (RMSSD) from the captured window with neurokit2.
6. Wire the mock engine: `em_theory_bayes.py` in MOCK mode (synthetic CPTs,
   synthetic observations) — the M0 reference, already DONE per B.7.
7. Close M1: real HRV → features → mock-engine posterior → provenance log writes.

## 5. Milestone Gates (what M1–M2 require, from B.7)

- M0 (DONE): engine runs on synthetic data — the reference implementation.
- M1: EM8 loop end-to-end on real HRV — one corner. Gate: the loop closes;
  provenance logs write (source, timestamp, version, confidence).
- M2: Sufficiency test on EM8 alone vs no-sensor baseline. Gate: GO/NO-GO #1 —
  does one corner beat baseline at matching self-report? (B.6 protocol: fit,
  hold out, calibrate — well-calibrated 0.6 beats confident-wrong 1.0.)
- M3: add EM10; re-run sufficiency on {EM8, EM10}.
- M4: attempt EM4 (webcam, under discipline) + EM2 (context, derived); pruning
  decisions.
- M5: go/no-go documented; keystone stands or the graph is pruned honestly.

## 6. Verification per build step

Every step ships with its test (E5, mock-first): capture smoke test (assert RR
intervals arrive, timestamp monotonic), feature test (RMSSD within physiological
range), engine test (posterior sums to 1, gap computable), provenance test (every
row has source/version/confidence, none empty), and the M2 sufficiency test
(mock-labeled windows, held-out split, calibration curve).

## 7. Honest cost notes

- Prices are mid-2026 street estimates; verify at order time. The H10 is the
  single biggest line item and is worth the money (research-standard sensor).
- No cloud spend anywhere in Stage A. The only recurring cost is electricity
  (~5 W for the Pi).
- The old plan's BOM (ESP32 nodes, cluster, docker-compose) is deliberately NOT
  carried into Stage A — the register's E7 keeps the parts concept, not the
  unearned hardware list. Stage B adds sensors only if M3's sufficiency says they
  earn their place.

---

*The Friday test, answered: read this sheet + the Leg3 spec's B.6/B.7, order
A1–A5, and M1 is a Saturday of wiring away. The gate discipline is in the
milestone ladder; the provenance discipline is in the engine spec (A.4–A.6 of
the keystone blueprint).*
