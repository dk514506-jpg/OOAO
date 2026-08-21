# Research Overview

**What HOMES studies, how it's designed, and what counts as success or failure.**

This is a concise companion to the full research design. The authoritative statement is the **Research Prospectus v4.1** (see `docs/RESEARCH_PROSPECTUS_v4.1.docx`); this document orients a first-time reader.

---

## 1. The research question

> Can a governed technical ecology — sensors, a Bayesian inference engine, and a blueprint-governed action layer — help establish favorable conditions for everyday **awe, wonder, recognition, and durable felt knowing**, without turning a home into a surveillance environment?

Two co-equal tracks, joined by a practice loop:

- **Track P (Participant):** does supported practice measurably increase awe, wonder, recognition, and felt knowing, and become more returnable and durable — without increasing self-surveillance or flattening experience?
- **Track S (System):** can the system identify useful room/time/practice patterns while preserving SELF/AUTO separation and graceful degradation — and can the situating bridge time its practice invitations well, evidenced by rising invitation-appropriateness and a reconciliation gap that declines to a stable non-zero floor?

A foundational engineering question underlies both: *can home-grade sensors recover enough of the EM substrate to beat a no-sensor baseline in timing invitations?* This is **Leg 3**, executed first.

---

## 2. The hypothesis set

| ID | Hypothesis | Falsified by |
|----|-----------|--------------|
| H-P1 · Frequency | Supported periods show more awe/wonder/recognition than baseline | no phase-linked difference |
| H-P2 · Felt knowing | Repeated practice raises felt knowing and coherence | no consistent before/after gain |
| H-P3 · Returnability | Practices become easier to return to | flat/declining returnability |
| H-P4 · Durability | Recognition events leave durable traces | traces fail to recur / trend to zero |
| H-S1 · Pattern detection | Patterns detected without flattening experience | confidence rises while richness declines |
| H-S2 · Invitation timing | Appropriateness improves; gap declines to non-zero floor | ratings don't improve, or gap collapses with felt-watched |
| H-Loop · Coupling | The two tracks co-move | persistent decoupling |
| **H4** · Anti-iatrogenic (overriding) | Any benefit co-occurs with reduced surveillance-feeling | felt-watched rises → **ease off, regardless of gains** |

---

## 3. The situating bridge (the keystone)

The EM-Theory Bayesian bridge (`em_theory_bayes.py`, contract `bp_c_em.yaml`) is the sole producer of **situated state**. It:

1. Estimates 4 non-reportable substrate corners from sensors (EM2/EM4/EM8/EM10).
2. Predicts 4 reportable "voices" (EM3 worry / EM5 rumination / EM7 emotion / EM9 vigilance).
3. Compares prediction to the participant's self-report → **reconciliation gap**.
4. Times **at most one** bounded practice invitation per eligible window.

It is capped at A4 (state candidate only); its invitation is capped at A2. The LLM is encode/decode only — it never does arithmetic.

---

## 4. Study design (n = 1, WWC-compliant)

- **Single-case experimental design (SCED)** toward What Works Clearinghouse standards.
- **Seven phases:** Phase 0 baseline → Phase 6 system refinement; multiple-baseline logic staggered across practices/rooms.
- **Measurement substrate** (SELF/AUTO kept distinct): Daily_Awe_Log, Practice_Pattern_Log, Recognition_Register, Weekly_Wonder_Reflection, Pattern_Map, Reconciliation_Log, H4_Safety_Log, Dashboard.
- **Four authenticity tests** (falsification for the timing claim): Barnum dissociation, counterfactual state-sensitivity, grounding-in-fiction, iatrogenic gap-collapse.
- **Analysis:** visual analysis primary; descriptive contrasts; Tau-U reported descriptively. No population inference claimed.

---

## 5. Leg 3 — the substrate-estimability go/no-go

Executed **first**, because the whole program depends on it:

| Corner | Sensors | Expected fidelity | Gate |
|--------|---------|-------------------|------|
| EM8 interoception | HRV strap | **good** | M1 |
| EM10 sensation | ambient light/sound/temp | partial (load yes, felt no) | M3 |
| EM4 perception | disciplined webcam | weak | M4 |
| EM2 latent state | derived | near-blind | M4 |

**Graceful degradation:** if Leg 3 prunes the substrate toward near-blindness, the program still proceeds — practice invitations timed by simple heuristics, and the fidelity map reported as the (honest) finding. A pruned graph is a *contribution*, not a failure.

---

## 6. What success and failure look like

**Success:** a local-first, blueprint-governed cognitive-and-spatial digital twin and the person who builds it improve together — each supplying what the other needs — without that improvement becoming surveillance, and without the act of measuring flattening the very wonder it sets out to notice.

**Failure (and it's the honest, valid kind):** an n=1 fidelity map showing the substrate cannot be recovered to a useful degree — reported plainly, alongside the governance grammar that generalizes beyond this single case.

---

*The contribution is method, instance, and fidelity map — not effect size. n=1 is a feature of the honesty, not a limitation to be excused.*
