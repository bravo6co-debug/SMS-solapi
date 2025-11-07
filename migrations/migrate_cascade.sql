-- Migration: Change company_id foreign key constraint to CASCADE
-- Purpose: Allow company deletion to cascade delete send_history records
-- Date: 2025-11-07

BEGIN;

-- Step 1: Check existing constraint
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    rc.delete_rule
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.referential_constraints rc
    ON tc.constraint_name = rc.constraint_name
WHERE tc.table_name = 'send_history'
    AND kcu.column_name = 'company_id';

-- Step 2: Drop existing foreign key constraint
ALTER TABLE send_history
DROP CONSTRAINT IF EXISTS send_history_company_id_fkey;

-- Step 3: Add new foreign key constraint with CASCADE
ALTER TABLE send_history
ADD CONSTRAINT send_history_company_id_fkey
    FOREIGN KEY (company_id)
    REFERENCES companies(id)
    ON DELETE CASCADE;

-- Step 4: Verify the change
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    rc.delete_rule
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.referential_constraints rc
    ON tc.constraint_name = rc.constraint_name
WHERE tc.table_name = 'send_history'
    AND kcu.column_name = 'company_id';

COMMIT;
