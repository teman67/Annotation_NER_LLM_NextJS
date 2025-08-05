# Email Setup Guide for Verification Emails

## Quick Setup Options

### Option 1: Gmail (Recommended for Testing)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password:**
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Select "Mail" and generate a password
3. **Update your `.env` file:**

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-character-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=Scientific Text Annotator
SMTP_USE_TLS=True
```

### Option 2: Outlook/Hotmail

```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
SMTP_FROM_EMAIL=your-email@outlook.com
SMTP_FROM_NAME=Scientific Text Annotator
SMTP_USE_TLS=True
```

### Option 3: Custom SMTP Server

```env
SMTP_HOST=your-smtp-server.com
SMTP_PORT=587
SMTP_USERNAME=your-username
SMTP_PASSWORD=your-password
SMTP_FROM_EMAIL=noreply@yourdomain.com
SMTP_FROM_NAME=Scientific Text Annotator
SMTP_USE_TLS=True
```

## Testing the Setup

1. Update your `.env` file with the appropriate SMTP settings
2. Restart the backend server (the FastAPI server will auto-reload)
3. Register a new user or resend verification for an existing user
4. Check your email inbox (and spam folder)

## Troubleshooting

- **Gmail "Less secure app access"**: Use App Passwords instead
- **Connection timeout**: Check firewall settings
- **Authentication failed**: Verify username/password
- **Emails in spam**: This is normal for development; production needs proper domain setup

## Production Recommendations

For production, consider using dedicated email services:

- **SendGrid** (free tier: 100 emails/day)
- **AWS SES** (very affordable)
- **MailGun** (good for developers)
- **Resend** (modern alternative)

These services provide better deliverability and don't trigger spam filters.
