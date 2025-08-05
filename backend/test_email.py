#!/usr/bin/env python3
"""
Email Test Script
Test the email verification functionality
"""

import smtplib
import sys
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from config import settings

def test_smtp_connection():
    """Test SMTP connection and authentication"""
    try:
        print("🔍 Testing SMTP connection...")
        print(f"Host: {settings.smtp_host}")
        print(f"Port: {settings.smtp_port}")
        print(f"Username: {settings.smtp_username}")
        print(f"TLS: {settings.smtp_use_tls}")
        
        # Test connection
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            if settings.smtp_use_tls:
                print("🔒 Starting TLS...")
                server.starttls()
            
            print("🔐 Logging in...")
            server.login(settings.smtp_username, settings.smtp_password)
            print("✅ SMTP connection successful!")
            return True
            
    except Exception as e:
        print(f"❌ SMTP connection failed: {e}")
        return False

def send_test_email():
    """Send a test email"""
    try:
        test_email = settings.smtp_username  # Send to self for testing
        
        subject = "Test Email - Scientific Text Annotator"
        html_body = """
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Test Email</h2>
            <p>This is a test email to verify SMTP configuration is working.</p>
            <p>If you received this, your email setup is working correctly!</p>
        </body>
        </html>
        """
        
        text_body = """
        Test Email
        
        This is a test email to verify SMTP configuration is working.
        If you received this, your email setup is working correctly!
        """
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{settings.smtp_from_name} <{settings.smtp_from_email or settings.smtp_username}>"
        msg['To'] = test_email
        
        # Attach both text and HTML versions
        text_part = MIMEText(text_body, 'plain')
        html_part = MIMEText(html_body, 'html')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        # Send email
        print(f"📧 Sending test email to {test_email}...")
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            if settings.smtp_use_tls:
                server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(msg)
        
        print("✅ Test email sent successfully!")
        print(f"📫 Check your inbox at {test_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send test email: {e}")
        return False

def main():
    print("=" * 50)
    print("🧪 Email Configuration Test")
    print("=" * 50)
    
    # Test SMTP connection
    if test_smtp_connection():
        print("\n" + "=" * 50)
        # Test sending email
        if send_test_email():
            print("\n✅ All email tests passed!")
            print("If you don't receive the test email, check:")
            print("1. Your spam/junk folder")
            print("2. Gmail App Password is correct")
            print("3. Gmail 2FA is enabled")
            print("4. 'Less secure app access' is disabled (should be)")
        else:
            print("\n❌ Email sending failed")
    else:
        print("\n❌ SMTP connection failed")
        print("\nTroubleshooting steps:")
        print("1. Verify Gmail App Password")
        print("2. Enable 2-Factor Authentication on Gmail")
        print("3. Generate a new App Password")
        print("4. Update .env file with the new password")

if __name__ == "__main__":
    main()
