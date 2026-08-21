CREATE TABLE IF NOT EXISTS raw_api_football.leagues (
    source_file VARCHAR NOT NULL,
    ingested_at TIMESTAMP NOT NULL,
    payload JSONB NOT NULL
);
