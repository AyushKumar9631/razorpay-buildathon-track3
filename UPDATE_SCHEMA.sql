-- Update database schema to rename metadata columns to extra_data
-- Run this in Supabase SQL Editor

-- 1. Rename metadata column in customers table
ALTER TABLE customers
RENAME COLUMN metadata TO extra_data;

-- 2. Rename metadata column in transactions table
ALTER TABLE transactions
RENAME COLUMN metadata TO extra_data;

-- 3. Rename metadata column in interventions table
ALTER TABLE interventions
RENAME COLUMN metadata TO extra_data;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'All metadata columns renamed to extra_data successfully!';
END $$;
