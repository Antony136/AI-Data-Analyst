-- Create a dedicated read-only role for AI Data Analyst.

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM pg_roles
        WHERE rolname = 'ai_analyst_readonly'
    ) THEN
        CREATE ROLE ai_analyst_readonly
        LOGIN
        PASSWORD 'CHANGE_THIS_PASSWORD';
    END IF;
END
$$;


-- Allow the role to connect to the analytics database.

GRANT CONNECT
ON DATABASE ai_data_analyst
TO ai_analyst_readonly;


-- Allow access to the public schema.

GRANT USAGE
ON SCHEMA public
TO ai_analyst_readonly;


-- Allow reading existing tables.

GRANT SELECT
ON ALL TABLES IN SCHEMA public
TO ai_analyst_readonly;


-- Automatically grant SELECT on future tables.

ALTER DEFAULT PRIVILEGES
IN SCHEMA public
GRANT SELECT
ON TABLES
TO ai_analyst_readonly;


-- Explicitly prevent table creation.

REVOKE CREATE
ON SCHEMA public
FROM ai_analyst_readonly;
