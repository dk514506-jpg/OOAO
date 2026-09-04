# DAEMON MANOR — SYSTEM LIFECYCLE & ROADMAP
## The Fused Plan: Three Legs × Phases × Gates × Decision Points
Version 1.0 · 2026-08-18
Fuses: prospectus v2 §6/§9 (legs, phases), BP-C-EM Leg3 Spec B.7 (milestones),
Architecture v4.1 §6 (sequencing), 09_implementation_plan.md (tasks)

---

## 1. The lifecycle in one paragraph

HOMES is a research program with an engineering spine: **Leg 3 first** (can
home-grade sensors recover EM-Theory substrate corners? — the go/no-go), then
**Leg 2** (does the reconciliation loop close and the gap behave? — the
keystone), then **Leg 1** (do the outcomes co-move and no harm is done? — the
program's purpose). The Manor architecture (v4.1) is the container; the
milestone ladder M0–M5 is the Leg-3 execution; each subsequent leg is a
separately-gated blueprint. Everything is provisional until data; nothing is
provisional about the governance.

## 2. The three legs (prospectus §6, execution order)

| Leg | What it is | Executed | Success criterion |
|---|---|---|---|
| Leg 3 — Substrate Estimability | The engineering foundation: can home-grade sensors recover P(EM2,4,8,10)? | FIRST (go/no-go) | Honest fidelity map; observable subset beats no-sensor baseline |
| Leg 2 — Situating Bridge | The keystone: reconciliation loop live; gap as primary measure | SECOND | Gap declines to a non-zero floor; passes authenticity tests |
| Leg 1 — Outcomes | Awe/wonder/recognition/felt-knowing primary (H-P1–H-P4), system timing (H-S1–H-S2), coupling (H-Loop), anti-iatrogenic (H4) | THIRD | Primary outcomes co-move with the gap; no iatrogenic harm (H4) |

> RE-CAST (R1, 20 Aug 2026): the 8/20 prospectus v4.1 reverses the retired
> purpose framing. Leg 1 previously named "memory, routine stability,
> ontological security (H1–H3)" — those are SUPERSEDED. The engine, gates,
> and storage are purpose-agnostic (gap = substrate→voices), so the build
> is unchanged; only the Leg-1 outcome hypotheses are re-cast to the 8/20
> set (H-P1–H-P4, H-S1–H-S2, H-Loop, H4). This is a documentation-level
> re-cast (data/pipeline labels), not a code change. See Silvey's_day3/.

## 3. The roadmap (calendar view, milestone-gated)

```
NOW ─────────────────────────────────────────────────────────────────────────▶
│ Leg 3 (go/no-go)                        │ Leg 2      │ Leg 1
│                                         │            │
│ M0 DONE (engine on synthetic)           │            │
│ M1 [Stage A hw] loop closes             │            │
│ M2 GO/NO-GO #1: EM8 vs baseline         │            │
│ M3 add EM10                             │            │
│ M4 webcam + EM2, pruning + fidelity map (spec B.7) │            │
│ M5 keystone stands / pruned ──────────────────────┤            │
│                                         │ BP-C-EM    │
│                                         │ validated  │
│                                         │ → Leg 2:   │
│                                         │ gap floor, │
│                                         │ H4 monitor │
│                                         │ → Leg 1:   │
│                                         │ outcomes   │
│                                         │ H-P1-H-P4, │
│                                         │ H-S1-H-S2, │
│                                         │ H-Loop, H4 │
```

Milestone schedule (solo builder, synthetic-first until hardware):
- M1: ~1–2 weekends of wiring + capture smoke (synthetic TODAY, real on strap arrival)
- M2: 1–2 weeks of labeled windows (self-report cadence) → sufficiency test
- M3: +1–2 weeks (EM10 sensors)
- M4: +2–4 weeks (webcam discipline + EM2 derived)
- M5: decision documented; fidelity map already produced at M4 (spec B.7)
Total Leg-3 span: ~6–10 weeks of calendar time for a solo builder, cheap-first,
no cloud. This REPLACES the old plan's two-week timeline (excluded as X2 —
unrealistic).

## 4. Decision points (the gates that matter)

1. **M2 GO/NO-GO #1** — does EM8 alone beat the no-sensor baseline at matching
   self-report? If NO: the keystone's estimability premise is weakened; the
   graph is pruned honestly and the fidelity map IS the contribution (B.8).
2. **M3** — does adding EM10 help or merely add noise? Continue or prune.
3. **M4** — does the webcam earn its place (beat no-camera baseline)? Is EM2
   worth keeping (derived features)? Pruning decisions documented.
4. **M5** — keystone stands (GO → Leg 2) or pruned (honest negative write-up).
5. **Leg-2 authenticity** — the four authenticity tests (prospectus §8):
   the perspective is real, not performed. Gap floor + H4 monitor (iatrogenic
   gate) are the decision instruments.
6. **Leg-1 outcome** — the 8/20 outcome set (H-P1–H-P4, H-S1–H-S2, H-Loop) co-moves with the gap; no felt-watched harm (H4). [Re-cast per R1; the retired H1–H3 set is superseded.]

Every decision point is preregistered before its data collection (the program's
discipline: prereg-first, honest negatives).

## 5. Phase structure (prospectus §9, folded into the legs)

The prospectus's phases are relationships-to-observe, not calendar boxes. The
signature phase is **Phase 7 — instrument-as-cause**: before concluding HOMES
helps or fails, ask whether the instrument itself became a cause in the system
it measures. That is the H4 iatrogenic gate, and it is a Manor-wide watch
(v4.1 §4.2), not a one-time check: if gap → 0 with rising felt-watched, the
Manor eases off everywhere and reports the ease-off.

## 6. What comes after M5 (separately gated, deliberately NOT in this plan)

- **D4 Worldview 'position' layer** — its own blueprint (BP-W), gated by the
  keystone standing; adds worldview orchestration to the state.
- **D6 Talker 'expression' layer** — its own blueprint, gated after D4;
  the state-indexed first-person voice (E2 bounded-window narrative).
- **OC-9** rendered graphical abstract (grant package, not a build gate).
- **OC-10** G-017 Person-Indexing Law formalization (governance amendment).
- **OC-14/15** persona-authority appendix + memory console spec (design, not
  build; the console's implementation is gated by the memory design note §3).

## 7. Lifecycle governance (who decides what, when)

| Role | Decides |
|---|---|
| Dallas | Sole sign-off (G-015) on durable-memory/worldview changes; final GO/NO-GO on M2/M5; participant self-report |
| Pip | Design, sequencing, blueprint drafting; ass-witness record |
| Locus | Validation gates (M2/M5), 7-check on every phase's artifacts |
| Council (Coder/Data Steward/Safety) | Implementation, provenance audit, safety review of gates |
| Phase 7 (H4) | The iatrogenic monitor — can halt personalization program-wide |

## 8. Lifecycle states (the system's own maturity ladder)

```
DRAFT → VALIDATED (Locus A.6.1) → OPERATIONAL → MONITORED → RETIRED/PRUNED
```

- Every blueprint (BP-C-EM first) moves through these states; the registry
  template tracks it.
- RETIRED/PRUNED is an honest state, not a failure: the fidelity map's
  weak/blind corners and the M4 pruning decisions retire components with
  documented reasons.
- The system as a whole is Stage 2–3 of 7 (self-tagged, prospectus); the
  ladder is CDT-0 personas → CDT-1 bridge CPTs (v4.1 ML-placement table).

## 9. Roadmap risks (honest)

- Solo-builder timeline assumes no hardware delays (Pi 5 + H10 supply);
  synthetic-first decouples progress from hardware arrival — a deliberate
  property of the E5 discipline.
- n=1 participant: every result is a single-subject result by design (the
  program's stated frame); external validity is NOT claimed; the fidelity map
  and governance grammar are the generalizable outputs.
- Self-report burden (voice corners) is the bottleneck at M2 — capped, opt-in,
  H4-watched calibration sessions (B.6) mitigate.
- The estimability premise may fail at M2: that is the planned honest-negative
  branch, not a contingency.

---

*The roadmap is the corpus's build order made explicit: Leg 3 first because it
is the cheapest falsification; M0–M5 as the gates; synthetic data now, real
data at M1; and every decision point preregistered with an honest-negative
branch. The Manor is designed. The build is specified. The roadmap is gated.
The next step is a Saturday.*
