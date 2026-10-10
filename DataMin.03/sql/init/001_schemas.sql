CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS mart;
CREATE SCHEMA IF NOT EXISTS audit;

CREATE TABLE IF NOT EXISTS audit.source_file (
    source_key text PRIMARY KEY,
    filename text NOT NULL,
    sha256 text NOT NULL CHECK (length(sha256) = 64),
    bytes bigint NOT NULL CHECK (bytes > 0),
    source_url text NOT NULL
);
