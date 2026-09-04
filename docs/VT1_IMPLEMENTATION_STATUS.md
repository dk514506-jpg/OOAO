# VT-1 Phase 0 Implementation Status — the ledger behind the synthesis package

Status: LANDED AND VERIFIED · 25 August 2026
Companion to: `HOMES_VT1_Sublation_Synthesis_Package_v1_0` (§5 architecture,
§6 phase ladder, §8 database schematics, §9 governance deltas).

This file exists because G-VT-2 (executable validation) demands that every
PASS cite a runnable check. The synthesis package's own §8 verification
transcript could not be reproduced end-to-end at review time — migration 001
was missing from the canon and nothing had been committed. This ledger records
what now actually exists, with the real numbers. Every claim below was
re-executed on this repository on 25 Aug 2026.

## What was landed

| Artifact | Role | Verified by |
|---|---|---|
| `storage/001_vertical_time.sql` | Vertical-time layer: logbook `layer` (3-value CHECK), `mono_ns` single-clock discipline, `clock_skew_ns`, `coverage_gaps` (cause CHECK, PK gap_start+source) | full-chain negative tests (below) |
| `storage/002_vt_synthesis.sql` | Epistemic wrapper columns (`epistemic_status` 13-value CHECK, `boundary_id`, `valid_until`), `observations` (missingness 8-state, value-NULL-iff-not-observed), `sediment_manifest` (write-only destination lock) | shipped artifact, byte-identical; chain tests |
| `storage/store.py` | Migration chain applied once per DB via `PRAGMA user_version` (0.1→1→2→3), atomic per migration, reopen-safe; `LogbookRow` carries the VT fields with fail-closed validation | suite + store smoke |
| `vt_recoverability.py` | The certification module the synthesis crosswalk names (§5.3): entropy (bits), JSD, ΔBrier, Certify(c), stability, discriminability; fail-closed contract load; R-5 non-binding machinery | 15 gates |
| `vt_recoverability_contract.yaml` | Phase-0 contract, `registered: false` (R-5): numbers may calibrate, never adjudicate | fail-closed tests |
| `vt_estimate.py` | Phase-1 epistemic wrapper: Estimate(τ) = (status, posterior), the §5.2 resolution order, expiry sweep, missingness→status classifier | 15 gates |
| `gates/test_vt_recoverability.py` | 15 recoverability gates (the synthesis's "13 vertical-time tests", exceeded) | suite |
| `gates/test_vt_estimate.py` | 15 wrapper gates incl. the R-2 invariant (posterior never surfaces when status ≠ estimable) | suite |

## The verification transcript (re-run 25 Aug 2026)

### Migration chain (SQL level): `schema.sql → 001 → 002`

```
OK: invalid epistemic_status rejected                    (CHECK fires)
OK: observed-with-NULL-value rejected (missingness modeled)
OK: declined SELF observation round-trips with no value
OK: sediment manifest write-only destination enforced   (nas_write_only only)
OK: invalid layer rejected                              (3-value CHECK)
OK: symbolic layer admitted (quarantined downstream)
OK: coverage_gaps cause CHECK enforced
OK: coverage_gaps PK (gap_start, source) enforced
MIGRATION CHAIN 0.1 -> 001 -> 002 VERIFIED
```

### Store level (python)

```
fresh DB user_version: 3
round-trip: layer/status/boundary/mono_ns persist through write+read
bad layer rejected at write (LogbookError, fail-closed)
reopen: user_version stays 3, no ALTER re-run, rows survive
```

### Gate suite (python3.13 -m pytest gates/ -q)

```
91 passed  (was 53 on 8/20)
  = 53 legacy (untouched, all green)
  + 15 vt_recoverability gates
  + 15 vt_estimate gates (one parametrized ×9)
```

## Corrections to the synthesis package's claims

The synthesis package (v1.0, §8 + header) claimed "66 tests: 53 legacy + 13
vertical-time" and "applied and negatively tested against the real schema
chain." As reviewed, the executable canon held neither the 13 tests nor
migration 001; the chain was not applied to anything. After this landing:

- **66 → 91**: the honest count is 91 passing, 53 legacy + 38 vertical-time
  (15 recoverability + 15 wrapper, one parametrized).
- **"applied against the real schema chain" → now literally true**: the chain
  exists in the canon, applies atomically via user_version, and is re-verified
  by this file's own transcript.
- **`vt_recoverability` "coded, tested" → now true**: module + contract + 15
  gates landed.
- **R-5 deferral honored**: the shipped contract is `registered: false`; the
  machinery refuses to bind until the Phase-4 ε ceremony. Numbers below are
  calibration-reference only.

## What this does NOT claim

- No real-sensor data: everything runs on synthetic fixtures (M1 hardware
  still pending — Polar H10).
- No ε ceremony: `registered: true` + git tag + change freeze is Phase 4.
- The epistemic wrapper is landed as a module; the Phase-2 write-path
  extension (store.py populating observations + coverage_gaps from capture)
  and Phase-3 runtime admission (Admit(•) with H4 outermost) remain on the
  ladder.
- Sediment Archive stays QUARANTINED behind BP-O; Reverie/symbolic stays
  quarantined per both tracks.

## Next ladder rungs (per §6)

1. Phase 1 exit: wrapper statuses exercised against real store rows (write
   path extension — Phase 2).
2. Phase 2: capture → observations/coverage_gaps write path; skew quarantine
   fixture (skewed clock → T1).
3. Phase 3: Admit(•) with the H4 sovereignty test.
4. Phase 4: ε ceremony → M1 real capture → honest M2 verdict (NO-GO
   acceptable and files to the fidelity map).
