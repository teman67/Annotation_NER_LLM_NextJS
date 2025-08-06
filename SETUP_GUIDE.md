# Setup Guide for Annotation NER LLM Application

## Issues Fixed

### 1. API Key Management

- **Problem**: No way for users to configure their OpenAI or Claude API keys
- **Solution**: Added API key management in user profile with encryption

### 2. Authentication Integration

- **Problem**: Authentication wasn't properly integrated with API calls
- **Solution**: Updated all API endpoints to use user-specific authentication

### 3. Project Management

- **Problem**: Projects page was showing dummy data
- **Solution**: Connected to backend with proper CRUD operations

## Setup Instructions

### 1. Database Setup

Run the SQL migration to add the user API keys table:

```bash
# From the backend directory
psql -h your-supabase-host -U your-user -d your-database -f add_user_api_keys_table.sql
```

Or run the SQL commands manually in your Supabase SQL editor:

```sql
-- Add table for storing encrypted user API keys
CREATE TABLE IF NOT EXISTS public.user_api_keys (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    openai_api_key_encrypted TEXT,
    anthropic_api_key_encrypted TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create unique index on user_id
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_api_keys_user_id ON public.user_api_keys(user_id);

-- Enable RLS
ALTER TABLE public.user_api_keys ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their own API keys
CREATE POLICY "Users can manage own API keys" ON public.user_api_keys
    FOR ALL USING (auth.uid() = user_id);
```

### 2. Backend Dependencies

Install the new cryptography dependency:

```bash
cd backend
pip install cryptography>=41.0.0
```

### 3. Environment Variables

Add these optional environment variables to your `.env` file:

```env
# Optional: Custom encryption key for API keys (recommended for production)
API_KEY_ENCRYPTION_KEY=your-32-character-base64-key

# System-wide API keys (fallback if users don't have their own)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

### 4. Usage Instructions

#### For Users:

1. **Configure API Keys**:

   - Go to Profile page
   - Add your OpenAI API key (get from https://platform.openai.com/api-keys)
   - Add your Anthropic API key (get from https://console.anthropic.com/)
   - Save the keys

2. **Create Projects**:

   - Go to Projects page
   - Click "New Project"
   - Fill in project details

3. **Run Annotations**:
   - Go to Annotation page
   - Upload or paste your text
   - Define or upload annotation tags
   - Select a model (only models with valid API keys will be available)
   - Run annotation

#### For Administrators:

1. **Monitor Usage**:

   - User statistics are tracked in the `usage_stats` table
   - Cost tracking is implemented per user

2. **API Key Security**:
   - API keys are encrypted using Fernet (symmetric encryption)
   - Keys are never stored in plain text
   - Each user can only access their own keys

## Key Features Added

### 1. API Key Management

- Secure encrypted storage of API keys
- Per-user API key configuration
- Masked display for security
- Validation of API key formats

### 2. Model Availability

- Dynamic model list based on configured API keys
- Clear error messages when API keys are missing
- Fallback to system-wide keys if available

### 3. Enhanced Error Handling

- Better error messages for API key issues
- User-friendly guidance to configure keys
- Proper authentication error handling

### 4. Cost Tracking

- Per-user cost tracking
- Token usage statistics
- Real-time cost estimation

### 5. Project Management

- Full CRUD operations for projects
- Project-based organization
- Annotation counting per project

## Troubleshooting

### 1. "API key not configured" error

- Go to Profile → API Keys section
- Add the appropriate API key for the model you're trying to use
- Ensure the key format is correct (sk-... for OpenAI, sk-ant-... for Anthropic)

### 2. Authentication errors

- Ensure you're logged in
- Check that your session hasn't expired
- Try logging out and back in

### 3. Database connection issues

- Verify Supabase credentials are correct
- Check that RLS policies are properly configured
- Ensure the new table was created successfully

### 4. Encryption errors

- Check that the cryptography package is installed
- Verify that the encryption key is properly set
- Try regenerating the API key encryption key

## Security Notes

1. **API Key Encryption**: All API keys are encrypted using Fernet symmetric encryption before storage
2. **Row Level Security**: Database policies ensure users can only access their own data
3. **No Plain Text Storage**: API keys are never stored in plain text
4. **Secure Display**: API keys are masked when displayed in the UI
5. **Authentication Required**: All endpoints require proper authentication

## Next Steps

1. **Test the Setup**:

   - Register a new user account
   - Configure API keys in profile
   - Create a project
   - Run an annotation

2. **Monitor Usage**:

   - Check the `usage_stats` table for tracking
   - Monitor costs and token usage
   - Review user activities

3. **Scale Considerations**:
   - Consider implementing rate limiting
   - Add user quotas or billing
   - Monitor API key usage patterns
