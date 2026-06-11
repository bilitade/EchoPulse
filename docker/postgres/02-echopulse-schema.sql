CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    raw_text TEXT NOT NULL,
    rating SMALLINT CHECK (rating BETWEEN 1 AND 5),
    summary TEXT,
    category TEXT,
    severity TEXT CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    sentiment TEXT CHECK (sentiment IN ('positive', 'negative', 'neutral')),
    product_area TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE feedback ADD COLUMN IF NOT EXISTS rating SMALLINT;
ALTER TABLE feedback ADD COLUMN IF NOT EXISTS product_area TEXT;
ALTER TABLE feedback ADD COLUMN IF NOT EXISTS resolved BOOLEAN DEFAULT FALSE;
ALTER TABLE feedback ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMPTZ;

CREATE INDEX IF NOT EXISTS idx_feedback_created_at ON feedback (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_feedback_category ON feedback (category);
CREATE INDEX IF NOT EXISTS idx_feedback_severity ON feedback (severity);
CREATE INDEX IF NOT EXISTS idx_feedback_resolved ON feedback (resolved) WHERE resolved = FALSE;

CREATE INDEX IF NOT EXISTS idx_feedback_fts ON feedback
    USING GIN (to_tsvector('english', raw_text || ' ' || COALESCE(summary, '')));
