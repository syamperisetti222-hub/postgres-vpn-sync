-- PostgreSQL Master Setup Script
-- This script initializes the master database for VPN sync

-- Create necessary schemas if they don't exist
CREATE SCHEMA IF NOT EXISTS public;

-- Create sync metadata tables
CREATE TABLE IF NOT EXISTS public.sync_metadata (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(255),
    last_sync_time TIMESTAMP,
    record_count BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create sync logs table
CREATE TABLE IF NOT EXISTS public.sync_logs (
    id SERIAL PRIMARY KEY,
    sync_type VARCHAR(50),
    status VARCHAR(50),
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
