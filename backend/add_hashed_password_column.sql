-- Migration to add hashed_password column to existing users table
-- Run this in your Supabase SQL editor

ALTER TABLE public.users 
ADD COLUMN IF NOT EXISTS hashed_password VARCHAR(255);

-- If you want to make it NOT NULL later, first add default values:
-- UPDATE public.users SET hashed_password = 'temp_hash' WHERE hashed_password IS NULL;
-- ALTER TABLE public.users ALTER COLUMN hashed_password SET NOT NULL;
