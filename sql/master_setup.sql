-- PostgreSQL Master Setup Script
-- Creates sync metadata and audit tables

CREATE SCHEMA IF NOT EXISTS sync_metadata;

-- Sync history table
CREATE TABLE IF NOT EXISTS sync_metadata.sync_history
(
    sync_id BIGSERIAL PRIMARY KEY,
    laptop_id VARCHAR(100) NOT NULL,
    schema_name VARCHAR(100) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    records_inserted BIGINT DEFAULT 0,
    records_updated BIGINT DEFAULT 0,
    records_deleted BIGINT DEFAULT 0,
    sync_status VARCHAR(20) NOT NULL,
    sync_start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sync_end_time TIMESTAMP,
    error_message TEXT
);

-- Audit log table
CREATE TABLE IF NOT EXISTS sync_metadata.audit_log
(
    audit_id BIGSERIAL PRIMARY KEY,
    schema_name VARCHAR(100) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    operation VARCHAR(20) NOT NULL,
    record_id TEXT,
    old_values JSONB,
    new_values JSONB,
    operation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table sync status
CREATE TABLE IF NOT EXISTS sync_metadata.table_sync_status
(
    table_sync_id BIGSERIAL PRIMARY KEY,
    schema_name VARCHAR(100) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    last_sync_time TIMESTAMP,
    total_records BIGINT,
    status VARCHAR(20),
    UNIQUE (schema_name, table_name)
);
