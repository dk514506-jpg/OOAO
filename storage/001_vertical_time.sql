-- 001_vertical_time.sql — VT-1 vertical-time layer (applies after schema.sql v0.1)
-- Sublates: Design Memo v0.2 §2 (temporal alignment, single clock, windows),
--           Formalization v1.1 Part XI (freshness). Adds the layer tag, the
--           monotonic-clock discipline (R-VT-1), skew accounting, and
--           first-class gap records. Applied atomically by storage/store.py,
--           gated by PRAGMA user_version (0.1 -> 1, +001 -> 2, +002 -> 3).

-- (1) Layer separation (L_phys != L_psycho != L_symbolic):
-- every logbook row is tagged to exactly one layer; symbolic rows can never
-- be read into inference (enforced at the query layer, Phase 1).
ALTER TABLE logbook ADD COLUMN layer TEXT NOT NULL DEFAULT 'psychophysiological'
    CHECK (layer IN ('physical','psychophysiological','symbolic'));

-- (2) Single monotonic clock (R-VT-1): mono_ns is the process-wide monotonic
-- reading at write time — the only clock trusted for ordering. tau (proper
-- time) is NEVER stored here: it is an alignment index computed at read time
-- as phi(t, episode, horizon); the discrete window index k lives on
-- observations (002).
ALTER TABLE logbook ADD COLUMN mono_ns INTEGER;

-- (3) Clock-skew discipline: measured deviation of the capture clock from the
-- reference monotonic clock, in ns. NULL = no skew detected. A capture whose
-- |skew| exceeds tolerance is quarantined to coverage_gaps
-- (cause='clock_skew') by the Phase 2 write path — never silently deleted,
-- never promoted into a logbook row.
ALTER TABLE logbook ADD COLUMN clock_skew_ns INTEGER;

-- (4) coverage_gaps — capture absence as a first-class record (continuity
-- accounting). Missing capture is DATA about the inquiry, never silence:
-- declined, sensor-offline, and skew-quarantined intervals all leave a row.
CREATE TABLE IF NOT EXISTS coverage_gaps (
    gap_start   TEXT NOT NULL,                -- ISO-8601 start of the gap
    gap_end     TEXT,                         -- NULL = open-ended
    source      TEXT NOT NULL,                -- provenance: what was absent
    actor       TEXT NOT NULL,                -- provenance: recording agent
    cause       TEXT NOT NULL CHECK (cause IN (
                    'sensor_offline','clock_skew','declined',
                    'unavailable','not_applicable','other')),
    detail      TEXT,                         -- human-readable context, optional
    mono_ns     INTEGER,                      -- monotonic reading at record time
    created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    PRIMARY KEY (gap_start, source)
);
CREATE INDEX IF NOT EXISTS idx_gaps_source ON coverage_gaps (source);
