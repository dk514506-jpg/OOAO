-- Daemon Manor — Measurement Logbook schema (spec A.6 / bp_c_em.yaml)
-- The M1 write target: the 9 logbook columns + engine-minimum provenance.
-- Local, file-based, provenance-tagged (keystone spec B.5). No cloud.
-- Fail-closed discipline: NOT NULL on every provenance field; CHECK on ranges.

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS logbook (
    -- --- the 9 Measurement Logbook v2.0 columns (spec A.6) ---
    substrate_vector  TEXT    NOT NULL,  -- JSON: P(EM2,4,8,10 | sensors)
    voice_prediction  TEXT    NOT NULL,  -- JSON: P(EM3,5,7,9) predicted
    voice_report      TEXT    NOT NULL,  -- JSON: participant self-report
    gap_per_voice     TEXT    NOT NULL,  -- JSON: {EM3: g, EM5: g, ...}
    gap_mean          REAL    NOT NULL,  -- scalar primary DV
    CSI               REAL    NOT NULL CHECK (CSI >= 0.0 AND CSI <= 1.0),
    model_version     TEXT    NOT NULL,  -- schema/engine version (from provenance)
    timestamp         TEXT    NOT NULL,  -- ISO-8601 UTC (from provenance)
    human_correction_flag INTEGER NOT NULL DEFAULT 0 CHECK (human_correction_flag IN (0,1)),

    -- --- engine-minimum provenance (bp_c_em.yaml required_fields) ---
    source            TEXT    NOT NULL,  -- who wrote it (capture/engine/participant)
    actor             TEXT    NOT NULL,  -- persona/daemon that caused the write
    confidence        REAL    NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    arm               TEXT,              -- with_substrate | baseline | NULL (real)

    -- --- integrity ---
    window_id         TEXT,              -- capture window identifier (if any)
    created_at        TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),

    PRIMARY KEY (timestamp, source, window_id)
);

-- Fast read-back for the sufficiency harness (M2): by window, by arm.
CREATE INDEX IF NOT EXISTS idx_logbook_timestamp ON logbook (timestamp);
CREATE INDEX IF NOT EXISTS idx_logbook_arm ON logbook (arm);
