-- 002_vt_synthesis.sql — VT-1 Synthesis migration (applies after 001_vertical_time.sql)
-- Sublates: Design Memo v0.2 §3-4 (epistemic states, observation contract, missingness),
-- Formalization v1.1 Part II (twelve epistemic resolutions) + Part XV (Sediment, write-only),
-- and the BP-C-007 coded baseline. Wrap in a transaction at apply time.

-- (1) Epistemic-status wrapper on the estimate (Formalization Part II / Estimate(tau)):
-- the engine's numeric posterior is emitted ONLY when status = 'estimable'; every
-- other status is a first-class, honest resolution — never a fabricated number.
ALTER TABLE logbook ADD COLUMN epistemic_status TEXT NOT NULL DEFAULT 'estimable'
    CHECK (epistemic_status IN (
        'estimable','unknown','indeterminate','contested',
        'not-presently-interpretable','declined','withdrawn','private',
        'intentionally-unrecorded','expired','overridden',
        'not-attributable','meaningful-but-not-classifiable'));

-- (2) Bounded inquiry jurisdiction (Design Memo §3.2): B is an inquiry boundary,
-- not the person. NULL = legacy/pre-boundary rows.
ALTER TABLE logbook ADD COLUMN boundary_id TEXT;

-- (3) Freshness/expiry (Formalization Part XI): estimates expire; stale reads
-- must resolve to 'expired', never silently reused.
ALTER TABLE logbook ADD COLUMN valid_until TEXT;

-- (4) Observation registry table (Design Memo §4.3 schema, O-01 contract).
-- One row per admissible observation; SELF/AUTO never merged pre-provenance.
CREATE TABLE IF NOT EXISTS observations (
    observation_id   TEXT NOT NULL,
    boundary_id      TEXT,
    event_time_t     TEXT NOT NULL,               -- raw coordinate time (t, never tau)
    mono_ns          INTEGER,                     -- single-clock discipline (R-VT-1)
    aligned_index_k  INTEGER,                     -- discrete estimation window k
    source_class     TEXT NOT NULL CHECK (source_class IN ('SELF','AUTO','SYSTEM')),
    domain           TEXT NOT NULL,               -- crosswalk: EM corner or D-twin id
    variable_id      TEXT NOT NULL,               -- Phase-B registry id (V-xx)
    value            TEXT,                        -- NULL permitted iff missingness != 'observed'
    units_or_scale   TEXT,
    trust_level      TEXT NOT NULL,
    retention_class  TEXT NOT NULL,
    valid_from       TEXT NOT NULL,
    valid_until      TEXT,
    missingness      TEXT NOT NULL DEFAULT 'observed'
        CHECK (missingness IN ('observed','unavailable','declined','private',
               'expired','sensor_failure','not_applicable','intentionally_unrecorded')),
    transformation_version TEXT NOT NULL,
    layer            TEXT NOT NULL DEFAULT 'psychophysiological'
        CHECK (layer IN ('physical','psychophysiological','symbolic')),
    source           TEXT NOT NULL,               -- engine-minimum provenance
    actor            TEXT NOT NULL,
    confidence       REAL NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    schema_version   TEXT NOT NULL,
    created_at       TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    PRIMARY KEY (observation_id),
    CHECK (value IS NOT NULL OR missingness != 'observed')   -- missing is modeled, never zero-filled
);
CREATE INDEX IF NOT EXISTS idx_obs_k ON observations (aligned_index_k);
CREATE INDEX IF NOT EXISTS idx_obs_var ON observations (variable_id);

-- (5) Sediment compilation manifest (Formalization Part XV): bookkeeping for the
-- write-only export to the NAS-hosted archive. The archive itself lives OFF this
-- database; no table here holds sediment content, no view reads it back, and no
-- foreign key can ever point from live tables into it. QUARANTINED; BP-O pending.
CREATE TABLE IF NOT EXISTS sediment_manifest (
    export_id        TEXT NOT NULL,
    exported_through TEXT NOT NULL,               -- watermark: last tau included
    destination      TEXT NOT NULL CHECK (destination = 'nas_write_only'),
    checksum         TEXT NOT NULL,
    row_counts       TEXT NOT NULL,               -- JSON {logbook: n, observations: n, gaps: n}
    source           TEXT NOT NULL,
    actor            TEXT NOT NULL,
    created_at       TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    PRIMARY KEY (export_id)
);
