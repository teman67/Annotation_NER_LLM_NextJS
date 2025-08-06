-- Fix database schema to match backend expectations

-- 1. Add missing columns to usage_stats table
ALTER TABLE public.usage_stats 
ADD COLUMN IF NOT EXISTS tokens_used INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS input_tokens INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS output_tokens INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS cost DECIMAL(10, 6) DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS operation_type VARCHAR(50);

-- 2. Add missing columns to annotations table and rename if needed
ALTER TABLE public.annotations 
ADD COLUMN IF NOT EXISTS entities JSONB,
ADD COLUMN IF NOT EXISTS processing_params JSONB,
ADD COLUMN IF NOT EXISTS statistics JSONB;

-- 3. Update existing annotations to copy data from annotations to entities column if needed
-- (This is safe to run even if no data exists)
UPDATE public.annotations 
SET entities = annotations 
WHERE entities IS NULL AND annotations IS NOT NULL;

-- 4. Create index on new columns for better performance
CREATE INDEX IF NOT EXISTS idx_usage_stats_operation_type ON public.usage_stats(operation_type);
CREATE INDEX IF NOT EXISTS idx_usage_stats_cost ON public.usage_stats(cost);
CREATE INDEX IF NOT EXISTS idx_annotations_entities ON public.annotations USING GIN(entities);
