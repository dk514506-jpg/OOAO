# DAEMON MANOR
## A Person-Centric Digital Service Ecosystem Twin — Renovated HOMES Architecture v4.1

Version 1.1 · 2026-08-18 · Amended: v4.1 (2026-09-04)
v4.1 amendments: all verified findings from the architecture review applied (see §9).
Companion to: HOMES Architecture v3.0 (Governance Edition), BP-C-EM + Leg 3 Spec,
Research Prospectus v2.0, and the Extraction Register (03_extraction_register_old_plan.md)
Formal spine: Kabashkin, I. (2026). From Assets and Processes to Service Ecosystems
(MAKE 8(7), 210; DOI 10.3390/make8070210) — the APS/DSET hierarchy, transposed person-ward.

---

## 0. The Vision

The old plan asked: *what is HOMES and what does it feel like to build?*
The governance corpus asked: *under what rules is it permitted to sense, reason, act?*
This architecture asks the third question: **what is HOMES a model OF?**

Answer: **one person — Dallas — in his home, understood as a living ecosystem.**
Not a city of meters and grids. A person. And the digital twin of that person is not a
dashboard; it is a **manor** — a household of personas, daemons, and services that
together constitute a *world to remember in*.

Kabashkin's framework formalizes digital twins as a four-level hierarchy:
assets → processes → services → ecosystem. His case study was a smart-city electricity
ecosystem. This architecture performs the transposition his framework was built to
support: **city → person; grid → body and home; utility services → personas;
service ecosystem → Daemon Manor.** The formal skeleton is preserved; the
instantiation is contentful — the actor set, the value structure, and the keystone's
transduction role all change materially. That is the renovation, stated plainly.

> The city's power plant becomes the body's heart-rate variability.
> The city's distribution grid becomes the room's ambient light, sound, and presence.
> The city's billing and forecasting services become the personas: Silvey, Pip, Locus,
> the Council — each a service the Manor delivers to its sole citizen.
> The city's ecosystem of actors and value becomes the Manor itself: the household of
> daemons and personas whose value-generation is *situated self-legibility*.

---

## 1. The Reconceptualized Graphical Abstract

The original (Kabashkin Fig. 4 + graphical abstract): an UPRIGHT four-layer pyramid —
orange Asset-Centric DT (power plants, lines, meters) as the widest base → green
Process-Centric DT (generation, transmission, billing workflows) → blue Service-Centric
DT (energy services, demand response) → yellow DSET (ecosystem of actors, services,
value) at the apex — with a physical-city banner beneath and side panels detailing
the service layer and the ecosystem twin. (Orientation and color-coding verified
against the source's rendered figures; note: Fig. 4 itself is a monochrome
two-column diagram, not a pyramid — the pyramid is the graphical abstract.)

The transposed abstract:

```
                    ┌─────────────────────────────────────────┐
                    │   DSET  —  DAEMON MANOR (yellow)        │
                    │   the whole household of personas,       │
                    │   daemons, memory, and value:            │
                    │   situated self-legibility, ontological  │
                    │   security, continuity of self           │
                    │   e = (S, U, E_PS, E_SS, E_US, V)        │
                    └───────────────────┬─────────────────────┘
                    ┌───────────────────▼─────────────────────┐
                    │   SCDT  —  PERSONA LAYER (blue)         │
                    │   Silvey · Pip · Locus · Council seats  │
                    │   Talker · Envoy                         │
                    │   each a service twin with role,        │
                    │   authority ceiling, trust tier,        │
                    │   provenance, and enablement by the      │
                    │   processes below                        │
                    └───────────────────┬─────────────────────┘
                    ┌───────────────────▼─────────────────────┐
                    │   PCDT  —  PROCESS LAYER (green)        │
                    │   ingestion · feature extraction ·      │
                    │   measurement models · reconciliation   │
                    │   engine · consolidation workflows ·    │
                    │   event monitoring · blueprint pipeline │
                    └───────────────────┬─────────────────────┘
                    ┌───────────────────▼─────────────────────┐
                    │   ACDT  —  ASSET LAYER (orange)         │
                    │   the body: HRV, EDA, breathing         │
                    │   the home: light, sound, temperature   │
                    │   the hardware: RTX 3060, Pi cluster,   │
                    │   ESP32 nodes, sensors                  │
                    └───────────────────┬─────────────────────┘
        ┌──────────────────────────────┴──────────────────────────────┐
        │  PHYSICAL BANNER: a person at a desk in a room, wearing an  │
        │  HRV strap, surrounded by ambient sensors, a small cluster  │
        │  of computers humming — the "smart city" reduced to its     │
        │  proper scale: one human life, one home                     │
        └─────────────────────────────────────────────────────────────┘
```

Side panel (left) — **Service-Centric Digital Twins = the personas.** Where Kabashkin
drew cloud services, operators, and smartphones, this panel draws the Manor's
personas as service twins. Each persona is a *service delivered to the sole actor*,
Dallas, and is instantiated with the attributes the corpus requires of a service
twin (role, authority ceiling, trust tier, governance law set, enabling processes,
quality indicators):

| Persona | Role | Authority ceiling | Trust tier | Enabling processes (Γ_S) | Quality indicators |
|---|---|---|---|---|---|
| Silvey | Steward of the whole; host persona | A5 (propose + implement within law) | T2 | capture, blueprint pipeline, reconciliation | gap trend, law-adherence rate |
| Pip | Designer; ass-witness to Dallas | A4 (propose, implement pending gate) | T2 | blueprint pipeline, consolidation | blueprint acceptance, def rate |
| Locus | Validator-steward (7-check) | A4 (adjudicate, not act) | T2 | validation-gate workflow, BP pipeline | verdict fidelity, false-accept rate |
| Council seats (Coder, Data Steward, Safety Reviewer) | Advisory review body | A4 (critique, recommend) | T2 | design review workflow | review coverage, finding validity |
| Talker | First-person expression | A5 (speak) | T1-T2 (CSI-gated) | measurement models, reconciliation, narrative rebuild | narrative-gap agreement (H4), interruption |
| Envoy | Externally-facing persona (Kovari [15] Talker/Envoy pattern) | A2 (communicate only; no internal action) | T1 | event monitoring, message assembly | delivery rate, disclosure compliance |

Per-persona attribute table: v4.1 deliverable per the OC-8 review (Locus check 6);
the CSI-modulated authority mechanism is pending OC-14 (Chow-style rejection
thresholds).

Side panel (right) — **DSET = Daemon Manor.** Where Kabashkin drew service hubs, user
segments, and providers, this panel draws the Manor's structure: the personas as
services in dependency (E_SS), Dallas as the sole actor/participant (U), the
value-generation structure V = {gap reduction, self-legibility, memory continuity,
routine stability, ontological security}, and the orchestration hub that is the
Shared Trans-Domain State.

The pyramid is upright because the asset layer is the broadest and most concrete,
and each higher layer is narrower, more abstract, and composed from the one below —
exactly as in the original. **What changed is the referent: one person's life
instead of a city's grid — and the instantiation, which is contentful (actor set,
value structure, keystone transduction).**

---

## 2. Formal Mapping onto Kabashkin's Framework

### 2.1 The four mappings

| Kabashkin formal | HOMES instantiation |
|---|---|
| DTA : A → DA (asset twin) | The Somatic + Environment twins (D1, D2): body-state vectors (HRV, EDA, breathing, arousal proxies) and room-state vectors (light, sound, temperature, presence). Each asset a_i ∈ A has observable state x_a(t). |
| DTP : P → DP (process twin) | The process layer: ingestion (HERMES-style capture), feature extraction (neurokit2), measurement models (feature → P(substrate)), the reconciliation engine (em_theory_bayes.py), consolidation workflows, event monitoring, blueprint pipeline execution. Each process p ∈ P has Γ_P(p) = participating assets. |
| DTS : S → DS (service twin) | The persona layer: Silvey, Pip, Locus, Council seats (Coder, Data Steward, Safety Reviewer), Talker, Envoy. Each persona s ∈ S is a service with role, authority ceiling, trust tier, quality indicators, and Γ_S(s) = enabling processes. |
| DTE : E → DE (ecosystem twin) | Daemon Manor: e = (S, U, E_PS, E_SS, E_US, V) where U = {Dallas} ∪ {personas}, V = the value-generation structure (gap reduction, self-legibility, memory continuity, routine stability, ontological security). |

### 2.2 Cross-layer dependencies (the Manor's connective tissue)

- E_AP ⊆ A×P: asset participates in process (HRV stream feeds the arousal feature
  extractor; light sensor feeds the environmental-load model).
- E_PS ⊆ P×S: process enables persona (the reconciliation engine enables Locus's
  validation; the measurement model enables the Talker's state-indexed voice).
- E_SS ⊆ S×S: persona depends on persona (Talker depends on Locus's gate; Pip's
  blueprints are validated by Locus; Council reviews Pip's designs).
- E_US ⊆ U×S: the sole actor Dallas provides, regulates, consumes every persona
  service; personas also serve one another (Council seats are both services and
  quasi-actors within the Manor).

**Quasi-actor extension (owned, not hidden):** a persona p ∈ S is also an actor
u ∈ U when it provides, regulates, or gates another persona's service (e.g.,
Council reviewing Pip's blueprint; Locus gating Talker's expression). This S∩U
overlap is an explicit extension beyond Kabashkin's city case (where U is
external actors only), compatible with his Assumption 3 (services "may be
connected with one or more actors"), and is what lets a self-governing household
of personas be expressed in the framework. It is a structural novelty of the
person-ward instantiation — not a relabeling of the city case.

### 2.3 Layered embedding and traceability

The hierarchy holds: **DTA ≼ DTP ≼ DTS ≼ DTE**, with projection operators:

- π_P→A(process) = {asset twins participating in that process} — e.g., projecting the
  reconciliation engine down to the HRV + EDA streams that feed it.
- π_S→P(persona) = {process twins enabling that persona} — e.g., projecting Locus
  down to the validation-gate workflow and the blueprint pipeline.
- π_E→S(Manor) = {persona twins composing the Manor}.

**Theorem 1 applied (Daemon Manor corollary, v4.1 — traceability vs grounding
disambiguated):** every persona utterance, every validation verdict, every Talker
response is cross-layer *traceable* to the assets that grounded it, through the
composed projection π_E→A = π_P→A* ∘ π_S→P* ∘ π_E→S. This is the formal statement of
the corpus's APS traceability chain (G-005) and its Provenance Law (G-012): the
Manor's provenance chain holds structurally — every claim carries its asset-level
lineage.

Traceability is an audit property, not a truth property. Theorem 1 in the source
guarantees the *recoverability of references*, not the *correctness of claims*: a
fabricated utterance that nonetheless cites real assets (e.g., an HRV stream that
did not behave as claimed) passes the projection chain intact. **Groundedness is a
separate property, measured by the reconciliation gap (the keystone's actual
measurement) and enforced by the OCI/CAI/CSI write-time gates at the projection
leaves** (per-utterance provenance contract per the interTwin yProv pattern;
milestone test: an ungrounded-claim injection probe — see §9). "The failure is
visible" therefore holds for the *audit chain*; whether an utterance is grounded
is a gate-enforced question, not a corollary.

### 2.4 The non-reducibility proposition, read person-ward

**Proposition 1 (conditional non-reducibility of service-centric twins), transposed:**
Under Assumptions 4-5, *a persona is not reconstructively reducible to its enabling
processes and underlying assets alone.* Two Manors could share identical sensors and
identical pipelines yet differ in personas — in actor roles (authority ceilings),
service dependencies (who may gate whom), and value-generation (what the Manor is
*for*). The persona layer is ontologically distinct.

This is the formal justification for something the project has always held
intuitively — carried conditionally, as the source requires. **Under Assumptions 4-5
— and for the Manor foundational only on the value-generation dimension (roles and
dependencies are by-design in this architecture; see below) — a persona is not its
pipeline, a designer is not the script they run, a validator is not the checklist
they apply.**

Honesty note (v4.1, per OC-8 review): Assumption 4 (service-twin attributes not
fully determined by asset+process layers) is only partially true for the engineered
parts of the Manor — §4 fixes authority ceilings *by role*, §2.5 makes service
dependencies designed blueprint rows, and trust tiers come from data quality. Those
are design choices (already justified as such in Architecture v3), not mathematical
consequences. What is genuinely undetermined is the value-generation dimension: the
gap trajectory and the felt experience. **The non-reducibility claim therefore
collapses to the keystone's estimability premise — it is a Leg-3-testable
hypothesis, not an achieved result.** Pre-registered probe (OC-17): two Manor
configurations sharing identical assets+processes, differing only in governance/
value settings — does the service layer differ observably?

### 2.5 The APS-matrix as the Blueprint Registry

Kabashkin's APS-matrix M_APS : A×P → S — which asset/process combinations enable
which services — is, in the Manor, **the Blueprint Registry itself.** Each blueprint
row is a typed dependency path:

- BP-C-001 (D1 fatigue suppresses D6 interruption): assets {HRV, EDA} → process
  {fatigue measurement model} → service {Talker interruption policy}.
- BP-C-002 (D5 security degradation raises D4 memory uncertainty): assets {sensor
  identity, session state} → process {trust-tier monitor} → service {Memory/Worldview
  gate}.
- BP-C-EM (the keystone): assets {sensors} → process {substrate estimation,
  reconciliation engine} → service {situated-state candidate for the personas}.

The registry IS the graph schema G_APS = (V_A ∪ V_P ∪ V_S, E_AP ∪ E_PS ∪ E_SS) —
a heterogeneous graph where nodes are assets, processes, personas and edges are the
dependency paths. This unifies the corpus's two artifacts (Blueprint Registry +
hypergraph) into one structure: **the hypergraph stores the APS graph; hyperedges are
the reified dependency paths with provenance.**

**RCC-8 spatial grounding (v4.1 — placed, per OC-8 review R6):** the extraction
register's E3 keeps RCC-8 spatial relations as CORE; they now have a formal home.
Add a spatial edge type E_SPATIAL ⊆ V_A × V_A over the asset-layer nodes — room-region
vs body-region relations on the D2 room-state vectors (e.g., "desk is inside room",
"body is at desk", "light-source left of body") — expressed in the RCC-8 relation
set (DC/EC/PO/EQ/TPP/NTPP and inverses) with time-validity intervals. These edges
anchor the asset layer's geometry, which the physical banner ("a person at a desk in
a room") presupposes, and give the projection chain spatial grounding at its leaves.

### 2.6 ML placement (where learning lives in the Manor)

Per Kabashkin §4.7, each level fixes its own learning problem:

- Asset level: per-corner condition monitoring — "is this sensor stream trustworthy
  right now?" (feeds trust tiers, data-quality fields).
- Process level: relational learning over the process graph — workflow classification,
  event detection, bottleneck/anomaly detection in the daemon pipelines.
- Service level: value-oriented learning — the reconciliation gap as a
  service-outcome variable, forecast/trend of gap and CSI, coordination of persona
  responses (when may Talker speak = f(state, gap, CSI)).

The keystone's rule — LLM does encode/decode only, the engine does arithmetic —
fits naturally: the LLM lives at the service layer (persona expression), the engine
lives at the process layer (probability math), and sensors live at the asset layer.
**The hierarchy gives a principled home to the encode/math/decode split; it does not
enforce it** (v4.1, per OC-8 review: the source fixes learning *problems* per level,
not model roles — the split is the keystone's own design stipulation).

Per-level ML placement, with the ACTUAL learners (v4.1 — resolves OC-6's CDT
labeling at the placement level):

| Level | Kabashkin §4.7 learning problem | Manor's actual learner | CDT label |
|---|---|---|---|
| Asset | per-component condition monitoring, anomaly, RUL | per-stream trust/quality classifier → feeds T0-T3 tiers | CDT-0 |
| Process | relational learning over process graph (workflow class., bottleneck/event detection, forecasting) | CPT learning in the bridge (the only genuinely learned component) + relational anomaly detection on daemon pipelines | CDT-1 |
| Service | value forecasting, coordination over Γ | NONE initially — personas are configured, not learned; deferred: OC-14 (learned Chow-style rejection thresholds / coordination policy) | CDT-0 → CDT-1 deferred |

---

## 3. What the Extracted Elements Become (Crosswalk from the Extraction Register)

| Extracted element | Home in Daemon Manor |
|---|---|
| E1 three-tier gloss | The felt description of the APS stack |
| E2 bounded-window narrative + MIRROR | D4→D6 expression path; narrative indexed to (state, gap, CSI); rebuilt asynchronously by the reconciliation loop; local-only; bounded by window, not literally O(1) |
| E3 reified hyperedges + RCC-8 | G_APS heterogeneous graph; hyperedges = dependency paths + provenance; RCC-8 as E_SPATIAL on asset-layer nodes (§2.5) |
| E4 error isolation | Default fallback for every persona (G-016): last-good narrative, last-good CPT, no-action |
| E5 test-before-hardware | Every milestone M1-M5 ships with mock engine + synthetic data gates |
| E6 phase gates | M-ladder verification steps |
| E7 BOM | Stage A-D parts per substrate corner (Leg 3) |
| E8 Zenoh/Neo4j/GreptimeDB | Physical transport + graph store + telemetry store (with fixed schemas) |
| E9 Talker/Thinker | Archetype of the persona layer: every persona is a service twin |
| E10 STL temporal rules | Coupling triggers + gap-floor watch + H4 monitor (non-vacuous semantics) |
| E11 cheap-model loop | Local 8B encode/decode; consolidation on triggers only |
| E12 gap-as-measure | The keystone (BP-C-EM); primary DV of the research program |

Excluded elements (X1-X10) are deliberately not carried: unearned claims, unrealistic
timelines, privacy leaks, vacuous logic, broken tests, and the conversation-dump
format itself.

---

## 4. Governance in the Manor (integration with Architecture v3)

The 16 laws, trust tiers, authority codes, and blueprint pipeline all carry over
unchanged — the Manor does not re-litigate governance. Three additions clarify
the person-centric structure:

**Enforcement statement (OC-7, closed):** governance in the Manor is enforced
by REVIEW, not by kernel — the laws bind the personas, the blueprint pipeline,
and the Council's validation gates, but nothing in the runtime kernel
automatically enforces them. Every law's enforcement point is a review process
(Locus 7-check, Council critique, blueprint gates, participant sign-off G-015),
and the audit trail (G-012) makes enforcement failures visible. This is stated
explicitly because the alternative — claiming kernel-enforced governance — is
false and would be a premature-coherence failure.

1. **G-017 (proposed) — Person-Indexing Law.** Every service in the Manor must be
   indexable to the sole subject: a persona service that cannot be traced (via the
   projection chain) to Dallas's state, report, or authority is not a Manor service.
   (This makes the keystone's "about THIS person" property a constitutional rule.)

2. **The gap-floor rule is a Manor-wide watch.** The iatrogenic gate (H4) applies to
   the ecosystem, not just the bridge: if gap → 0 with rising "felt watched", the
   Manor eases off everywhere (HALT personalization, surface to participant).

3. **Persona trust tiers map to service quality.** A persona's authority ceiling is
   fixed by role; its effective reach is modulated by the current CSI of the state
   object it consumes. A low-CSI reading downgrades every persona that would act on
   it — the Manor cannot act confidently on noise, whatever any persona's nominal
   authority.

   Evidence for confidence-gated adaptivity (v4.1, per OC-8 review R10 — the
   best-supported governance element now carries its citations, with analogy
   labels): A1 (Mirza et al. 2026, peer-reviewed, L4, simulated inventory domain —
   adaptive policies beat fixed policies increasingly under uncertainty: 92%→88%
   at low, 60%→38% at high variability + disruption; *analogy*, not direct
   evidence for personalization); Bethapuri et al. 2026 (L4 — transfer-based
   control allocation = Chow's rejection rule: act iff confidence ≥ 1−t, where t
   IS the Triple-Index gate; *direct structural fit*); D1 (Huq 2026, L2
   self-labeled — scenario-adaptive strategy shifts under rising uncertainty).
   The mechanism (Chow-style rejection thresholds) is pending OC-14; the H4
   iatrogenic cost calibrates the thresholds (θ_Talker > θ_Locus, since Talker's
   speech carries interruption cost).

---

## 5. The Keystone in the Manor

The EM-Theory Bayesian bridge (BP-C-EM) is not a fifth layer; it is the **transduction
between layers** — the coupling that makes the whole hierarchy about one person:

- Sensors (assets) estimate the substrate P(EM2,4,8,10 | sensors) — asset→process.
- The engine predicts the voices; the participant reports them; the gap is computed —
  process-level arithmetic.
- The gap enters the personas' context (Talker's state-indexed voice, Locus's gates,
  the weekly debrief) — process→service.
- The gap's trajectory is the Manor's primary observable INDICATOR of ecosystem
  value V — service→ecosystem. (v4.1, per OC-8 review R3: V is a structure, not a
  scalar — see §9.1.)

Without the bridge, the Manor is a mirror: an accurate model with no point of view.
With it, the Manor is a perspective: **state indexed to one person, position supplied
by worldview orchestration (D4), expression supplied by the personas (D6)** — the
STATE × POSITION × EXPRESSION composition from the Keystone Note, now with a formal
home in the hierarchy.

---

## 6. Build Sequencing (unchanged from the corpus, restated)

Leg 3 executes first — it is the substrate-estimability go/no-go, staged cheap-first,
camera-free early, milestone-gated (M0-M5), with the extraction register's BOM as the
Stage A-D parts list. If Sufficiency fails, the graph is pruned honestly and the
fidelity map is the contribution. The Manor is built from the ground up: assets
(Stage A: capture + feature extraction + mock engine; the real engine enters at the
measurement-model milestone per E5's mock-first gates — the engine consumes
measurement-model outputs, so it cannot precede them) → processes (measurement
models) → personas (the keystone's A4-capped candidate service) → ecosystem (full
Manor with Talker expression and worldview position, each downstream blueprint
separately gated). The two-week timeline is gone; the honest ladder is in.

---

## 7. Status and Honesty Labels

- This document: L2 (architectural) — design specified, no runtime evidence.
- The formal transposition (Section 2): L2, with the skeleton directly inherited
  from a peer-reviewed L1-L2 conceptual-mathematical source (Kabashkin 2026 —
  low-TRL per its own §1.3/§3.8: conceptual and architectural validation, no
  empirical ML pipeline; peer review is a quality marker, not an evidence level).
  No empirical weight is inherited (v4.1, per OC-8 review).
- The extraction register: L2, post-frame-check (OC-8 verdict: REVISE light; all
  items applied in v4.1).
- EM-Theory and the keystone: L1-L2 as before; Leg 3 will earn L3+ only with data.
- OCI/CAI/CSI: concept-for-formula until the published Kabashkin 2026b formulas are
  instantiated (OC-1, D10); registry floats are placeholders.

---

## 8. Open Items Introduced by This Document

- OC-8 (CLOSED 2026-08-18): three-body review complete — Locus REVISE (light) +
  Council KERNEL PRESERVED; all verified findings applied in v4.1 (see §9).
- OC-9 (new): produce the Daemon Manor graphical abstract as a rendered figure
  (SVG/HTML) from the ASCII in Section 1, for inclusion in the grant package.
  Figure fidelity precondition: diff the ASCII against the actual source images
  (already partially verified — orientation/colors confirmed; Fig. 4 is a
  monochrome two-column diagram, not a pyramid). Give Dallas (U) visible presence
  in the rendered figure.
- OC-10 (new): draft G-017 (Person-Indexing Law) as a formal law with failure mode
  and source citation, for Architecture v3 amendment.
- OC-16 (new, per review R1): ungrounded-claim injection test — milestone-gated
  probe that forces a fabricated utterance citing real assets and asserts the
  OCI/CAI/CSI write-time gates reject it while traceability still holds.
- OC-17 (new, per review R2/C2): pre-registered Assumption-4 probe — two Manor
  configurations sharing identical assets+processes, differing only in
  governance/value settings; does the service layer differ observably?

---

## 9. Amendment Log (v4.1)

Three-body review (Locus + Council Design + Council Evidence) on the v4.0 text;
verdict files in Household/reviews/. Every finding below was verified against the
artifacts before application.

### 9.1 Value structure disambiguated (R3, both Councils)
V is a STRUCTURE, not a scalar: V = ⟨{gap-reduction, self-legibility, memory
continuity, routine stability, ontological security}, g(t)⟩ where g(t) = the
reconciliation-gap trajectory is the primary OBSERVABLE INDICATOR of V (the
program's DV) — not V itself. Each of the five dimensions gets its own indicator:
gap-reduction = gap magnitude/trend; self-legibility = narrative-vs-report
agreement; memory continuity = hypergraph retention + revocation integrity;
routine stability = H4/instrument data; ontological security =
felt-understood-vs-felt-watched. Pre-registered at Leg 3: which dimensions the
gap indexes (per Council-2 R7).

### 9.2 Applied findings (all verified)
1. Pyramid orientation corrected: UPRIGHT (not inverted) — vision-verified against
   the source graphical abstract; Fig. 4 is a monochrome diagram, not a pyramid.
2. Evidence ladder: Kabashkin relabeled peer-reviewed L1-L2 (not L6).
3. Theorem-1 corollary: traceability (audit) split from groundedness (gate-enforced,
   gap-measured); ungrounded-claim injection test added (OC-16).
4. "Hierarchy enforces the split" → "hierarchy gives a principled home";
   per-level ML placement table with actual learners (resolves OC-6 at placement
   level).
5. Proposition 1 carried conditionally; non-reducibility collapsed to the
   keystone's estimability premise; Assumption-4 probe pre-registered (OC-17).
6. S∩U quasi-actor extension owned as an explicit novelty (not "only the referent
   changed").
7. Envoy instantiated (role, ceiling A2, trust T1, enabling processes); per-persona
   attribute table added (Locus check 6).
8. RCC-8 placed as E_SPATIAL on asset-layer nodes (§2.5) — register and architecture
   now agree.
9. E2 renamed bounded-window narrative (register + Manor crosswalk);
   register E5 aligned to all of M1-M5.
10. Governance addition 3 now cites its evidence (A1 analogy, Bethapuri Chow
    rejection, D1 scenario-adaptive) with mechanism pending OC-14.
11. Stage A ordering fixed (capture + features + mock engine; real engine at the
    measurement-model milestone).
12. Ecosystem-tuple note: source Construction 4 writes e=(A,U,...) but its prose and
    Algorithm 1 give (S,U,Γ) — the Manor's S reading is the defensible variant
    (source typo; footnote for future reviewers).

### 9.3 Carry-forward (not applied, tracked)
- OC-9 figure render must diff against source images (partially done) + give
  Dallas visible presence.
- OC-14/OC-15/OC-16/OC-17 opened (see §8 and Household/open_charges.md).
- Secrets-lifecycle × E2 interaction (Council-2 T4): the MIRROR rebuild must be
  revocation-safe — revoked memories must not re-enter the narrative; added to
  OC-11's spec (OC-15).

---

*This architecture is provisional, like everything in this program: the composition
argument is strong, the estimability premise is open, and the claim that a
well-grounded model of situatedness constitutes genuine perspective is held lightly.
What is not provisional is the structure: assets → processes → personas → Manor,
one person at the center, and every claim traceable down the projection chain to the
sensors that earned it.*
