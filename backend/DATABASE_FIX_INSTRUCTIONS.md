# Database Schema Fix

## Issue Summary

The backend was expecting different table names than what existed in the database:

- Backend expects: `files`, `tags`, `project_members`, `usage_stats`
- Database had: `uploaded_files`, `tag_sets`, `project_collaborators`, `usage_analytics`

Additionally, there was a policy recursion error in the `projects` table.

## Solution

Updated the schema to match backend expectations and simplified the policies.

## How to Apply the Fix

### Option 1: Via Supabase Dashboard (Recommended)

1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Copy the contents of `backend/supabase_schema.sql`
4. Paste and run the SQL

### Option 2: Via Terminal (if you have psql)

```bash
# From the backend directory
cd backend
psql -h your-supabase-host -U postgres -d postgres -f supabase_schema.sql
```

## Changes Made

1. **Table name alignment**: Renamed tables to match backend expectations
2. **Policy simplification**: Removed recursive policies that were causing issues
3. **Sample data**: Added test data for immediate testing
4. **Schema cleanup**: Drops existing tables before recreating to avoid conflicts

## After Running the Schema

Restart your backend server to see the connection success messages:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

All tables should now show as "✅ Table 'tablename' exists"
