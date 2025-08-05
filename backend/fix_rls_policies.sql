-- RLS Policy fix for users table
-- Run this in your Supabase SQL editor

-- Option 1: Disable RLS for users table (simpler for development)
ALTER TABLE public.users DISABLE ROW LEVEL SECURITY;

-- Option 2: Or create proper RLS policies (more secure)
-- ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
-- 
-- -- Allow service role to insert/update/delete users
-- CREATE POLICY "Service role can manage users" ON public.users
--   FOR ALL USING (auth.role() = 'service_role');
-- 
-- -- Allow users to read their own data
-- CREATE POLICY "Users can read own data" ON public.users
--   FOR SELECT USING (auth.uid()::text = id::text);
-- 
-- -- Allow users to update their own data
-- CREATE POLICY "Users can update own data" ON public.users
--   FOR UPDATE USING (auth.uid()::text = id::text);
