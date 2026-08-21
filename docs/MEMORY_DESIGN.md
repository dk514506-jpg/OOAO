# DAEMON MANOR — AGENTIC MEMORY DESIGN NOTE
## The D4 Memory/Worldview Twin, per the Agent-Memory Survey (Huang et al., TMLR 2026)

Version 0.1 (draft for Locus frame-check) · 2026-08-18 · Designer: Pip
Source: Huang, W.-C. et al. (2026). A Survey of Agent Memory in the Second Half:
Towards Self-Evolving and Long-Horizon Agents. TMLR 07/2026; arXiv:2602.06052v4.
This note translates the survey's taxonomy and system-design findings into a
concrete memory architecture for Daemon Manor, consistent with Architecture v3
governance, the APS hierarchy (v4), and the keystone (BP-C-EM).

---

## 1. Why This Survey Matters to the Manor

The survey's opening claim is the Manor's claim: the field has moved from the
"first half" (architecture and scaling) to the "second half" (utility in
long-horizon, user-dependent, real environments) — where memory is not an
interface to history but **the substrate of agent self-evolution**. The Manor is
an n=1, long-horizon, always-on, deeply user-dependent system; every design
lesson in the survey applies directly, and the survey's three-dimensional
taxonomy gives the D4 Twin a complete design language it did not previously have.

## 2. The Three-Dimensional Taxonomy, Instantiated

### 2.1 Memory Substrate — what form
- **External (primary):** the Neo4j G_APS hypergraph (reified dependency paths
  with provenance), GreptimeDB telemetry, text records, the Blueprint Registry.
  Per the survey, external storage should be **structure-aware**: expose only
  reasoning-critical spans at retrieval (precision-oriented retrieval), not
  ever-growing context injection. This is a direct upgrade to the old plan's
  "dump last 15 min of hyperedges" approach.
- **Internal (secondary):** the fine-tuned 8B Talker's weights; latent state
  carried by the engine's posterior distributions (P(EM2,4,8,10|sensors)).
  Internal memory is bounded and NOT the store of record — provenance requires
  the external layer (G-012).

### 2.2 Cognitive Mechanism — how it functions
| Mechanism | Manor instantiation | Governed by |
|---|---|---|
| Sensory | Raw sensor buffers (HERMES capture), transient by design | G-009 (fast loop only) |
| Working | Shared Trans-Domain State (the Manor's "working memory": domain states, uncertainty, constraints, objectives) | G-001 (grounding), G-009 |
| Episodic | Reified hyperedges — state-at-encoding with full provenance | G-012; BP-C-EM logbook |
| Semantic | Ontology + worldview (D4); APS schema; distilled facts | G-005 (APS traceability), G-006 (Triple Index) |
| Procedural | Blueprints, workflows, skills — the registry's BP-W/BP-R types; persona operating procedures | G-003 (Blueprint Law), G-011 (Reflection) |

The survey's key consolidation loop — "episodic records distill into semantic
facts and procedural skills" — is exactly the Manor's slow-loop translation
(G-013): hyperedges → weekly debrief → worldview calibration.

### 2.3 Memory Subject — who it serves
- **User-centric memory (Dallas):** biographical facts, preferences, self-reports
  (the voices), evolving goals, gap history. THIS is the keystone's home: the
  reconciliation gap is a user-centric memory signal of the highest order — it
  indexes all other memory to the person.
- **Agent-centric memory (the personas):** validation verdicts, blueprint
  history, council decisions, failed/gained trajectories — the Manor's own
  lessons, kept separate from the participant's data. This split is the survey's
  and the corpus's simultaneously: personas accumulate experience; the
  participant's data is never conflated with it.

## 3. Multi-Agent Memory Architecture: Hybrid + Orchestrated

The survey catalogs four multi-agent memory architectures. The Manor is
deliberately **hybrid + orchestrated**:

- **Private layer per persona:** each persona (Silvey, Pip, Locus, Council seats)
  keeps its own working notes and role-specific experience (survey: MetaAgents —
  "role stays stable and consistent, information from dialogue written back
  locally"). Prevents role bleed and preserves authority boundaries.
- **Shared layer:** the Shared Trans-Domain State + hypergraph as the common
  workspace (survey: shared-workspace pattern), with **filtering and
  coordination** to prevent noise (MetaGPT's role-profile filtering).
- **Orchestrator:** the blueprint pipeline + Locus's validation gate act as the
  controller (survey: MIRIX's Meta Memory Manager; LEGOMem's orchestrator) —
  deciding who may read/write what, with **write control**: only the governed
  memory path (candidate → Triple-Index → BP-M gate → durable) may mutate
  durable memory. This is Memory-R1's ADD/UPDATE/DELETE/NOOP pattern, governed:
  - ADD → A4 candidate creation (logbook entry)
  - UPDATE → BP-M revision path with provenance (never silent overwrite)
  - DELETE → BP-O/BP-M retirement path (never hard-delete; Deprecated/Retired)
  - NOOP → the Triple-Index gate declines (log only, no write)

Survey finding honored: "the memory manager agent is the only agent allowed to
mutate memory" — in the Manor, that manager is the governed pipeline itself,
not any single persona. No persona writes durable memory directly; every write
passes the gate. This makes the A4/A5 authority codes an actual memory-write
control mechanism, not just a policy statement.

## 4. Memory Evolution: From Prompt-Driven to Learned

The survey's evolution-policy ladder (prompting → fine-tuning → RL) maps onto a
sensible Manor roadmap:

1. **Now (prompt-driven):** static, governed rules — blueprint pipeline, trust
   tiers, Triple-Index gates, gap-floor watch. Fully interpretable; matches L2
   evidence level.
2. **Leg 3 data (fine-tuning-ready):** the trust-weighted CPT learning in
   BP-C-EM is exactly "personalize_update" — a small, governed parameter
   evolution (survey: continual learning for user adaptation). The CPTs are the
   Manor's first learned memory policy.
3. **Later (RL — explicitly out of scope for now):** the survey's MEM1/Mem-α
   train agents to consolidate/discard memory via RL. For n=1 with an 8B local
   model this is a research project in itself; the corpus already tags CDT-1 as
   the ceiling — a learned memory controller is a CDT-2-level ambition. Recorded
   as a future direction, not a commitment.

## 5. Trustworthy Memory (Survey §9.4 — the non-negotiable)

The survey's trustworthy-memory findings are mandatory reading for the Manor:

- **Privacy leakage via memory extraction** (Wang et al., 2025a): memory modules
  are vulnerable to targeted extraction even black-box. Mitigation: local-only,
  no cloud, provenance-tagged stores, trust tiers gate what can even be read.
- **Memory poisoning and adversarial manipulation**: an attacker who can write
  the shared store can poison every downstream persona. Mitigation: write control
  (only governed path mutates), T0/T1 sources log-only (Watanabe/G-008).
- **User-controllable inspection, editing, revocation**: the survey demands the
  participant be able to inspect, edit, and revoke stored memories. The Manor
  MUST implement this as a first-class feature: Dallas can query what the Manor
  remembers about him, correct it (G-015 human-correction path), and delete it.
  This is a new requirement surfaced by the survey — added to Open Charges as
  OC-11 (user memory inspection/revocation console).
- **Blinded reports to prevent anchoring** (prospectus §8): the survey's
  "conflicting signals, partial observability" finding supports the blinded
  self-report design.

## 6. What This Changes in the Architecture

1. **Precision-oriented retrieval** replaces "last 15 min of hyperedges": the
   context query becomes structure-aware (fetch reasoning-critical spans via
   APS paths, not time-window dumps). Aligns with G-009 and the O(1) narrative.
2. **The A4/A5 codes become a memory-write control mechanism** (Memory-R1
   pattern), not just policy: no persona mutates durable memory; the governed
   path does.
3. **Persona private memory is a first-class layer**: role-stability memory per
   persona, kept distinct from shared state and from participant data.
4. **OC-11 added**: user memory inspection/editing/revocation console (survey
   §9.4 requirement; also closes the corpus's biometric-retention gap partially).
5. **The survey's six open challenges** map onto the Manor's open charges: 9.1 →
   self-evolution via CPTs (bounded); 9.2 → persona collaboration memory
   (hybrid+orchestrated); 9.3 → structure-aware retrieval; 9.4 → trustworthy
   memory (OC-11); 9.5 → multimodal/world-model (future, aligns with
   world-model research hunt); 9.6 → real-world benchmarking (the n=1 design
   IS a real-world benchmark; the fidelity map is the benchmark result).

## 7. Status

- This note: L2 (architectural design, pending Locus frame-check).
- The survey: L6 (peer-reviewed synthesis; 218 papers).
- Confidence: high on the taxonomy mapping; medium on RL evolution (future).
- Open charges added: OC-11 (memory inspection/revocation console); OC-12
  (structure-aware retrieval design replacing time-window context query).
