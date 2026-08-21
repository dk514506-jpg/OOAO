# DAEMON MANOR — IMPLEMENTATION PLAN
## Task-Level Build Plan: Companion Files, Repo Layout, Milestone Gates
Version 1.0 · 2026-08-18 · Author: Pip · Owner chain: Pip → Coder seat → Locus (validation)
Baseline: Raspberry Pi 5 + Polar H10 (Stage A) · Data: SYNTHETIC until M1 hardware (Dallas directive 2026-08-18)
Companions: 08_build_spec_sheet.md (BOM) · bp_c_em.yaml (governed contract) · leg3_manifest.csv ·
em_theory_bayes.py (engine skeleton, M0 verified) · synthetic_manor_data.py (fake-data harness, verified)

---

## 1. What this plan covers

The keystone spec's B.8 quality bar: *a solo home-lab builder can read the spec
on a Friday and order Stage-A parts by Saturday.* The build spec sheet answers
the ordering question; this plan answers the building question: what tasks, in
what order, with what dependencies, gated by which milestones, owned by whom.

Scope: Leg 3 (substrate estimability) executed FIRST per the corpus and v4.1 §6
— the go/no-go that decides whether the keystone stands. Downstream (D4
worldview position, D6 Talker expression) are separately gated blueprints
outside this plan.

## 2. Repository layout (one home for the Manor)

```
~/manor/                         # the home-lab node (Pi 5, or dev machine until M1)
├── bp_c_em.yaml                 # governed contract (DRAFT v0.1 — this workspace)
├── leg3_manifest.csv            # sensor/estimability map (DRAFT — this workspace)
├── em_theory_bayes.py           # engine (SKELETON v0.1, M0 verified — this workspace)
├── synthetic_manor_data.py      # fake-data generator (verified — this workspace)
├── capture/                     # BLE ingestion (polar-h10), HERMES P/C/P pattern
│   └── polar_capture.py
├── features/                    # neurokit2 wrappers (RMSSD/SDNN/LFHF/pNN50)
│   └── hrv_features.py
├── engine/                      # em_theory_bayes.py lives at repo root (reference path)
├── storage/                     # SQLite schema + provenance columns; Data Steward audit
│   ├── schema.sql
│   └── store.py
├── gates/                       # milestone gates M0-M5 (E5 mock-first tests)
│   ├── test_m0_mock_loop.py     # M0 reference (synthetic loop)
│   ├── test_m1_capture_smoke.py # M1 EM8 loop: capture, features, engine, gap, provenance
│   ├── test_engine_negative.py  # fail-closed negatives (contract, posterior, confidence, trust gate)
│   └── test_m2_sufficiency.py   # M2 (downstream)
├── data/                        # synthetic (now) → real (M1+) — NEVER committed
│   └── manifest.json            # provenance: what was generated, when, by what
├── requirements.txt             # pinned deps (see §5)
└── README.md                    # runbook: how to run each gate
```

## 3. Task graph (dependency-ordered)

```
T1 scaffold repo + venv + pinned deps            (Pip)
  └─ T2 draft bp_c_em.yaml contract              (Pip — DONE in this workspace)
  └─ T3 draft leg3_manifest.csv                  (Pip — DONE)
  └─ T4 engine skeleton em_theory_bayes.py       (Pip — DONE, M0 verified)
  └─ T5 synthetic data harness                   (Pip — DONE, verified)
T2..T5 are DONE as drafts; the tasks below BUILD on them.

T6 storage schema + store.py (SQLite, provenance columns)      (Coder seat)
T7 gates/ harness: test_provenance.py, test_m0_mock_loop.py    (Coder seat)
T8 capture smoke: polar-h10 BLE scan + RR stream → SQLite      (Coder seat)  [M1 hardware]
T9 features: neurokit2 RMSSD/SDNN/LFHF from RR stream          (Coder seat)  [M1]
T10 wire features → engine posterior → gap → provenance log    (Coder seat)  [M1]
── M1 GATE: loop closes on REAL or SYNTHETIC HRV; provenance writes ──
T11 sufficiency harness: fit/hold-out/calibrate vs baseline     (Coder seat)
T12 self-report instrument: Talker prompts + rating capture     (Coder seat)  [M2]
── M2 GATE: GO/NO-GO #1 — does EM8 beat no-sensor baseline? ──
T13 EM10 sensors (Zigbee/USB hub) + feature wiring              (Coder seat)  [M3]
T14 re-run sufficiency on {EM8, EM10}                           (Coder seat)  [M3]
── M3 GATE: does adding sensory-load help? ──
T15 webcam (disciplined) + EM2 derived features                 (Coder seat)  [M4]
T16 pruning decisions (EM4 weak? EM2 near-blind?)                (Pip + Locus) [M4]
── M4 GATE: camera earns its place? EM2 pruned? ──
T17 fidelity map (good/partial/weak/blind per corner) — spec     (Pip)         [M4]
    B.7: M4 delivers the honest fidelity map
T18 keystone go/no-go documented; graph pruned or promoted      (Locus)       [M5]
── M5 GATE: keystone stands, or honest negative ──
```

Owners: Pip (design/adjacency), Coder seat (implementation), Locus (validation
gates M2/M5), Data Steward (storage/provenance audit), Dallas (G-015 sign-off
on any durable change; final go/no-go).

## 4. Milestone gates (the contract for each)

| Gate | Test | Pass condition | Decision |
|---|---|---|---|
| M0 | test_m0_mock_loop.py | engine runs on synthetic data; gap computable; provenance validated | DONE (reference) |
| M1 | test_m1_capture_smoke.py | RR intervals arrive (real or synthetic); timestamps monotonic; features in physiological range; provenance rows non-empty | loop closes |
| M2 | test_m2_sufficiency.py | EM8 model beats no-sensor baseline at matching self-report (calibration, not point accuracy) | GO/NO-GO #1 |
| M3 | re-run sufficiency {EM8, EM10} | adding EM10 improves or ties; not worse | continue / prune |
| M4 | corner tests | webcam beats no-camera baseline; EM2 worth keeping | keep / prune |
| M5 | fidelity map + decision doc | map produced (delivered M4 per spec B.7); keystone promoted or pruned honestly | keystone stands / honest negative |

## 5. Pinned dependencies (requirements.txt — industry practice: pin, don't float)

```
python>=3.11
pyyaml==6.0.*        # contract parsing
polar-h10==0.5.*     # BLE HRV (or the newer fork pin)
neurokit2==0.2.*     # HRV/EDA features
pgmpy==0.1.*         # Bayesian engine arithmetic (or numpy backend for v1)
numpy<2.0            # pin per pgmpy/neurokit2 compatibility
pytest==8.*          # gate tests
```

LLM (encode/decode only, G-003): llama.cpp + Qwen2.5-7B-Instruct Q4_K_M —
NOT a python dep; runs as a sidecar process; the engine never calls it for math.

## 6. Testing discipline (E5, mock-first — industry practice)

- Every gate test runs against mock/synthetic data first; real hardware
  replaces mocks at M1 but the synthetic path stays as the regression suite.
- Negative tests are first-class and SUITE-BACKED (all four verified in code,
  per OC-18 Locus REVISE): engine refuses to run without the contract
  (EngineError), empty provenance raises, incomplete posterior raises,
  confidence out of range raises — see gates/test_engine_negative.py +
  test_m1_capture_smoke.py::test_provenance_fields_nonempty.
- Trust-gate discipline (spec A.3, harmonized OC-18): personalize_update is
  gated by trust = f(CSI, tier), not bare CSI — covered by
  test_engine_negative.py::test_trust_gate_harmonized_with_spec_a3.
- CI-friendly: `pytest gates/` must pass before any milestone is declared.
- No secrets in configs (Vault/zero-trust lesson, S33): the H10 pairing is a
  device-local secret; store per the storage schema, never in bp_c_em.yaml.

## 7. Data policy (per Dallas directive 2026-08-18)

- Synthetic data is the DEFAULT until M1 hardware arrives. The harness
  (synthetic_manor_data.py) is deterministic (seed), generates both arms
  (with_substrate + baseline for the M2 comparison), and its ground truth is
  KNOWN — so reconstruction quality can be scored today, with no sensors.
- Every synthetic dataset carries a manifest.json labeled FAKE DATA — do not
  treat as measured (the Meng/A3/A4 lesson applied to our own outputs).
- Real data begins at M1; the synthetic harness remains as the regression
  baseline and the M2 no-sensor comparison.

## 8. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Pi 5 BLE range/stability with H10 | A6 USB dongle in the BOM; capture smoke test gates M1 |
| 7B Q4 LLM too slow on Pi 5 | encode/decode-only contract tolerates it; else move LLM to RTX 3060 PC (E1/E11) |
| M2 sufficiency ambiguous at n small | B.6 protocol: calibration curves + held-out split; synthetic-first lets us power-test the gate before real data |
| Engine drift from contract | bp_c_em.yaml is the single source; engine refuses to run without it |
| Over-claiming from synthetic results | manifest.json FAKE DATA labels + §7 policy; fidelity map only from real data |

## 9. Definition of done (this plan)

- All T1–T18 tasks have owners and are either done or scheduled.
- The three companion files exist, are versioned beside the docs (OC-5 closed),
  and the engine + synthetic harness run and pass their negative tests.
- The Friday test is answered: order A1–A5 from the build spec, run T6–T10,
  close M1 on synthetic data today, on real HRV when the strap arrives.
