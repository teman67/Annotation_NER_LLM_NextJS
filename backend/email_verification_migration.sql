-- Email verification columns migration
ALTER TABLE public.users 
ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS verification_token TEXT,
ADD COLUMN IF NOT EXISTS verification_token_expires_at TIMESTAMP WITH TIME ZONE;

-- Update existing users to have email_verified = true (optional, for development)
-- UPDATE public.users SET email_verified = true WHERE email_verified IS NULL;
