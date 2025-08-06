-- Add table for storing encrypted user API keys
CREATE TABLE IF NOT EXISTS public.user_api_keys (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    openai_api_key_encrypted TEXT,
    anthropic_api_key_encrypted TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create unique index on user_id to ensure one record per user
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_api_keys_user_id ON public.user_api_keys(user_id);

-- Enable RLS
ALTER TABLE public.user_api_keys ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their own API keys
CREATE POLICY "Users can manage own API keys" ON public.user_api_keys
    FOR ALL USING (auth.uid() = user_id);

-- Update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_api_keys_updated_at 
    BEFORE UPDATE ON public.user_api_keys
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
