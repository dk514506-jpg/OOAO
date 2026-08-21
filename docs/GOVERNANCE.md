# Governance & Safety Architecture

**Why a bounded AI system can be trusted to touch a person's home and inner life — the principled answer.**

HOMES is not "an AI that lives in a home." It is a **governed order** in which bounded AI capabilities operate under explicit, auditable rules. The governance layer is not an afterthought bolted on for ethics compliance — it is the load-bearing structure that makes the system safe enough to run *at all*.

---

## 1. The three nested orders

The architecture prevents the technical control loop from becoming the metaphysical center of the project:

| Order | Contents | Governing relation |
|-------|----------|--------------------|
| **Experiential** | House, rooms, light, practice, silence, embodiment, awe, wonder, recognition, ambiguity | Grants relevance; judges lived consequence |
| **Interpretive** | SELF reports, situated-state candidates, patterns, worldview, dialogue | Makes experience cautiously legible without claiming possession |
| **Operational** | Sensors, twins, blueprints, policy, capabilities, assurance, provenance, fallback | May alter bounded conditions; **subordinate** to the orders above |

The operational order may adjust the room's lighting. It may never decide what an experience *means*.

---

## 2. Authority ceilings (A0–A6)

Every capability is capped. The most important property: **A6 (autonomous action) is reserved and unauthorized.**

| Code | Meaning | HOMES use |
|------|---------|-----------|
| A0 | Log only | sensor onboarding before trust assignment |
| A1 | Ask user | ambiguous inference surfaced as a question |
| A2 | Recommend | weekly reflection; bounded practice invitations |
| A3 | Reversible environmental adjustment | lighting, under a separately approved blueprint |
| A4 | Memory/state candidate | **the situating bridge's ceiling** (produces state, cannot act on it) |
| A5 | Durable memory/worldview update | **requires explicit participant sign-off** |
| A6 | Autonomous action | **reserved and unauthorized** |

The keystone's central safety property is containment at A4: a fluent reading of a person's state **cannot, by itself**, write memory, change the room, or speak beyond one bounded invitation per window.

---

## 3. Trust tiers (T0–T3) + typed evidence

Every sensor event carries a trust tier and a visible source type.

- **T0** unverified → log only.
- **T1** verified but degraded → temporary state only.
- **T2** verified, high quality → candidate state / bounded action.
- **T3** cross-verified or human-confirmed → durable memory / action.

Every value is also visibly typed **SELF** (participant-entered, authority-bearing) vs **AUTO** (system-generated, with source + confidence). This keeps a confident inference from being mistaken for a fact — the project's "a confident inference is never a lived fact" invariant.

---

## 4. The Triple-Index gate (OCI / CAI / CSI)

Before any memory write, recommendation, or environmental action, three indices are evaluated jointly (`triple_index.py`, instantiated from Kabashkin 2026):

- **OCI** — ontology consistency (does the reading violate declared constraints?)
- **CAI** — cognitive adequacy (is there an admissible interpretation?)
- **CSI** — confidence sufficient for the proposed use

The joint rule: high CAI + low CSI → **log or ask, not act**. The situating bridge applies this gate to every situated-state reading before it may gate an invitation.

---

## 5. The blueprint pipeline

No material change to HOMES goes live without a **Blueprint** — the mandatory intermediate artifact between an AI proposal and its execution. Lifecycle: `Draft → Designed → Coded → Validated → Approved → Active → Deprecated → Retired`. A Blueprint that fails validation returns to Draft; it is **never partially deployed**. Durable-memory and worldview blueprints additionally require the participant's explicit sign-off before activation.

---

## 6. The H4 anti-iatrogenic gate (the soul of the project)

H4 is the safety override that **outranks every other outcome**. It rests on a specific, non-generic stake: being *defined by another's perception* is the original injury this project exists to help recover from — so HOMES itself must never become a second instance of that dynamic.

- **Weekly gate:** tracks felt-understood, felt-watched, tracking anxiety, and whether recording deepened or flattened the week's experience.
- **Gap-collapse rule:** if the reconciliation gap trends to zero *while felt-watched rises*, that is **deference, not perfect observation** → halt personalization, iatrogenic review.
- **Ease-off procedure:** on a trip, pause proactive prompts; keep only minimal free-text logging; restart requires two consecutive calm weekly readings.
- **Human authority is absolute (G-015):** the participant holds sole sign-off over any durable change and may halt any process at any time.

Any apparent improvement driven by increased surveillance rather than genuine support is a **failure of the design** — on both research tracks.

---

## 7. Governance is enforced by review, not by kernel

This is stated plainly because the alternative (claiming kernel-enforced governance) would be false. The laws bind the personas, the blueprint pipeline, and the validation gates; enforcement is by **review** — Locus's 7-check validation, Council critique, blueprint gates, and participant sign-off. The audit trail (provenance) makes enforcement *failures visible*. Nothing in the runtime kernel automatically enforces a law; the discipline is structural, auditable, and honest about being so.

---

## 8. Biometric data governance (OC-4)

Raw physiological data (HRV/EDA/ECG) is governed by a ratified retention policy:
- **Class A** (raw signals): 30-day default purge, irreversible hard-delete, erasure *fact* logged.
- **Class B** (derived features): 90-day default.
- **Class C** (inferred state): keystone-governed, never touched by routine purge.
- **Class D** (provenance): append-only.
- No cloud, no egress (D3); H4-trip accelerates raw purges.

Enforced by `retention_purge.py`. See the OC-4 policy for the full text.

---

*The governance grammar — authority ceilings, trust tiers, the Triple-Index gate, the blueprint pipeline, and the H4 override — is offered as a transferable pattern for any language-model-mediated self-support system. It is the reason this project can touch a person's home and inner life without becoming surveillance.*
