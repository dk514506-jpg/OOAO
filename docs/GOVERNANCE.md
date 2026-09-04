# Governance & Safety Architecture

**Why a bounded AI system can be trusted to touch a person's home and inner life — the principled answer.**

HOMES is not "an AI that lives in a home." It is a **governed order** in which bounded AI capabilities operate under explicit, auditable rules. The governance layer is not an afterthought bolted on for ethics compliance — it is the core structure that makes the system safe enough to run *at all*.

**Scope and status (September 2026).** HOMES is in pre-deployment development: the engine runs on synthetic data (milestones M0–M1), and no hardware is installed in a home. This document governs the *design*. Where a mechanism is enforced in code, a review procedure, or still a scaffold, the section says so — the code repository (`github.com/dk514506-jpg/OOAO`) is the source of truth for what actually runs. Nothing here describes a system that is live in a home today.

---

## 1. The three nested orders

The architecture prevents the technical control loop from becoming the metaphysical center of the project:

| Order | Contents | Governing relation |
|-------|----------|--------------------|
| **Experiential** | House, rooms, light, practice, silence, embodiment, awe, wonder, recognition, ambiguity | Grants relevance; judges lived consequence |
| **Interpretive** | SELF reports, situated-state candidates, patterns, worldview, dialogue | Makes experience cautiously legible without claiming possession |
| **Operational** | Sensors, twins, blueprints, policy, capabilities, assurance, provenance, fallback | May alter bounded conditions; **subordinate** to the orders above |

The operational order may adjust the room's lighting. It may never decide what an experience *means*.

*Enforcement: conceptual architecture; the orders are the frame every other rule sits inside. No code enforces a hierarchy of meaning — by design, none could.*

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

The keystone's central safety property is containment, and it is two caps, not one: the bridge's state readings are capped at **A4** (candidate only — they cannot write memory, change the room, or act on themselves); the bridge's single permitted action — one bounded practice invitation per window — is separately capped at **A2** (recommend). A fluent reading of a person's state therefore cannot, by itself, write memory, change the room, or speak beyond that one bounded invitation.

*Enforcement: the ceilings are declared in the engine's governed contract (`bp_c_em.yaml`) and in module docstrings. No code branch enforces A0–A6 today — there is no A5/A6 action path to enforce, because the engine's only would-be write (`personalize_update`) is a skeleton that records a candidate and never applies it. Enforcement at present is therefore by absence of implementation plus contract declaration. The participant's absolute authority (declined / withdrawn states) IS enforced in code in `vt_estimate.py` and exercised by its gate tests.*

---

## 3. Trust tiers (T0–T3) + typed evidence

Every sensor event carries a trust tier and a visible source type.

- **T0** unverified → log only.
- **T1** verified but degraded → temporary state only.
- **T2** verified, high quality → candidate state / bounded action.
- **T3** cross-verified or human-confirmed → eligible for durable memory (storage requires A5 sign-off).

Every value is also visibly typed **SELF** (participant-entered, authority-bearing) vs **AUTO** (system-generated, with source + confidence). This keeps a confident inference from being mistaken for a fact — the project's "a confident inference is never a lived fact" invariant.

**Two-stage rule — qualification is not authorization.** A trust tier decides whether a record *may* be proposed for durable storage (T3 = eligible). Whether it *is* stored is decided by the authority ceiling: durable memory and worldview updates require **A5** and the participant's explicit sign-off (G-015 — the participant's absolute veto, §6). Machine cross-verification qualifies a record; only the participant authorizes its landing. These two rules govern the same transition, and they have different actors by design.

*Enforcement: provenance completeness and confidence bounds are enforced in code (fail-closed — an empty field or out-of-range confidence raises, and the engine refuses to run without its contract file). The T0–T3 tiers and the SELF/AUTO type distinction are design vocabulary, not yet machine-enforced: no tier enum or type field exists in the code; the participant's SELF authority is partially enforced via the declined/withdrawn states in `vt_estimate.py`. Machine tier-typing is a build milestone, not a current property.*

---

## 4. The Triple-Index gate (OCI / CAI / CSI)

Before any memory write, recommendation, or environmental action, three indices are evaluated jointly (`triple_index.py`, instantiated from Kabashkin 2026):

- **OCI** — ontology consistency (does the reading violate declared constraints?)
- **CAI** — cognitive adequacy (is there an admissible interpretation?)
- **CSI** — confidence sufficient for the proposed use

The joint rule: high CAI + low CSI → **log or ask, not act**. The situating bridge applies this gate to every situated-state reading before it may gate an invitation.

*Implementation status — computed, not yet wired:* the OCI/CAI/CSI computation itself is implemented (`compute_triple_index`, Kabashkin's formulas with the five Manor constraints, cosine-similarity CAI, CV-based CSI, and a worked-example self-check reproducing the paper's numbers) and covered by its own gate tests. What does not yet exist is any *wiring*: no module calls the gate, and there is no write/recommendation path in the running (synthetic) system for it to guard. The gate's activation on a live decision path is a tracked build milestone — until then, no write, recommendation, or action is gated by this index.*

---

## 5. The blueprint pipeline

No material change to HOMES goes live without a **Blueprint** — the mandatory intermediate artifact between an AI proposal and its execution. Lifecycle: `Draft → Designed → Coded → Validated → Approved → Active → Deprecated → Retired`. A Blueprint that fails validation returns to Draft; it is **never partially deployed**. Durable-memory and worldview blueprints additionally require the participant's explicit sign-off before activation (the A5 authorization of §2–§3).

*Enforcement: review procedure, not kernel (see §7). The lifecycle is tracked in the project's change ledger, and every transition leaves an audit record.*

---

## 6. The H4 anti-iatrogenic gate (the project's core safety guard)

H4 is the safety override that **outranks every other outcome**. It rests on a specific, non-generic stake: being *defined by another's perception* is the original injury this project exists to help recover from — so HOMES itself must never become a second instance of that dynamic.

- **Weekly gate:** tracks felt-understood, felt-watched, tracking anxiety, and whether recording deepened or flattened the week's experience.
- **Gap-collapse rule:** if the reconciliation gap trends to zero *while felt-watched rises*, that is **deference, not perfect observation** → halt personalization, iatrogenic review.
- **Ease-off procedure:** on a trip, pause proactive prompts; keep only minimal free-text logging; restart requires two consecutive weekly readings with no H4 trip (no rising felt-watched, no gap collapse).
- **Human authority is absolute (G-015):** the participant holds sole sign-off over any durable change and may halt any process at any time.

Any apparent improvement driven by increased surveillance rather than genuine support is a **failure of the design** — on both research tracks.

*Enforcement: the gap-floor rule (gap → 0 while felt-watched rises ⇒ status "contested", personalization halted) is implemented in `vt_estimate.py` and exercised by its gate tests (`test_vt_estimate.py`); an H4-trip flag accelerates raw-data purge in `retention_purge.py`. The weekly reading-and-review cadence and the ease-off procedure are review procedures that begin at deployment.*

---

## 7. Governance is enforced by review, not by kernel

This is stated plainly because the alternative (claiming kernel-enforced governance) would be false. The laws bind the personas, the blueprint pipeline, and the validation gates; enforcement is by **review** — structured validation and adversarial critique of every blueprint and change, performed by named reviewer roles in the project's authoring practice (validated against explicit checklists; no reviewer reviews its own work). The audit trail (provenance) makes enforcement *failures visible*. Nothing in the runtime kernel automatically enforces a law; the discipline is structural, auditable, and honest about being so.

**Who the reviewers are — stated, not hidden.** The reviewer roles are performed by language-model agents under the participant's direction and oversight, not by independent humans. This is a stated limitation, and it is handled as one: every review is logged to the audit trail, a reviewer's BLOCKED or REVISE verdict returns the blueprint to Draft rather than proceeding, disputes and disagreements escalate to the participant as final authority, and the audit trail exists precisely so that an external human reviewer can check the work. The participant may halt any review process at any time. The governance pattern's transferable claim does not depend on the reviewers being human — it depends on their work being visible, replayable, and subordinate.

**External review.** Any external reviewer may inspect the audit trail and the public code at any time; the participant responds to external findings under the same final-authority rule. The repository is public for exactly this reason.

---

## 8. Biometric data governance

Raw physiological data (HRV/EDA/ECG) is governed by a ratified retention policy:
- **Class A** (raw signals): 30-day default purge, irreversible hard-delete of the primary store, erasure *fact* logged.
- **Class B** (derived features): 90-day default.
- **Class C** (inferred state): keystone-governed, never touched by routine purge.
- **Class D** (provenance): append-only.
- No cloud, no egress (a locked design constraint); an H4 trip accelerates raw purges.

Enforced by `retention_purge.py`. **Erasure, scoped honestly:** primary-store deletion is implemented and audited, but cache/mirror copy invalidation is a recorded open item in the code — "erased" today means the primary store's hard-delete with the fact appended to the audit ledger, and full copy-level erasure lands when that open item closes. The policy text should be read against the code, which is the source of truth.

---

*The governance grammar — authority ceilings, trust tiers, the Triple-Index gate, the blueprint pipeline, and the H4 override — is offered as a transferable pattern for any language-model-mediated self-support system. It is the reason this project can touch a person's home and inner life without becoming surveillance.*
