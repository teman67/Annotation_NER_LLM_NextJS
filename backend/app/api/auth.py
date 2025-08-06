from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Optional
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

from app.config import settings
from app.database import get_db

# Simple in-memory rate limiting for verification attempts (only for failed attempts)
verification_failed_attempts = {}

def is_rate_limited(token: str) -> bool:
    """Check if a token verification attempt should be rate limited (only applies to failed attempts)"""
    current_time = time.time()
    
    # Clean old failed attempts (older than 15 minutes)
    for t in list(verification_failed_attempts.keys()):
        if current_time - verification_failed_attempts[t]["last_attempt"] > 900:  # 15 minutes
            del verification_failed_attempts[t]
    
    # Check if this token has too many failed attempts recently
    if token in verification_failed_attempts:
        attempt_data = verification_failed_attempts[token]
        time_since_last = current_time - attempt_data["last_attempt"]
        
        # If more than 3 failed attempts in the last 5 minutes, rate limit
        if attempt_data["count"] >= 3 and time_since_last < 300:  # 5 minutes
            return True
        
        # If last failed attempt was less than 30 seconds ago, rate limit
        if time_since_last < 30:  # 30 seconds cooldown after failed attempt
            return True
    
    return False

def record_failed_verification(token: str):
    """Record a failed verification attempt"""
    current_time = time.time()
    
    if token in verification_failed_attempts:
        verification_failed_attempts[token]["count"] += 1
        verification_failed_attempts[token]["last_attempt"] = current_time
    else:
        verification_failed_attempts[token] = {
            "count": 1,
            "last_attempt": current_time
        }

def clear_failed_verification(token: str):
    """Clear failed verification attempts for a token (called on successful verification)"""
    if token in verification_failed_attempts:
        del verification_failed_attempts[token]

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class EmailVerification(BaseModel):
    token: str


def generate_verification_token():
    return secrets.token_urlsafe(32)


def send_verification_email(email: str, verification_token: str):
    """Send email verification email"""
    try:
        verification_url = f"http://localhost:5173/verify-email?token={verification_token}"
        
        subject = "Verify your email address - Scientific Text Annotator"
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">Welcome to Scientific Text Annotator!</h2>
                <p>Thank you for registering! Please verify your email address to complete your account setup.</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" style="background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">Verify Email Address</a>
                </div>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; background-color: #f3f4f6; padding: 10px; border-radius: 5px; font-family: monospace;">{verification_url}</p>
                <p style="color: #666; font-size: 14px;">This link will expire in 24 hours for security reasons.</p>
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                <p style="color: #666; font-size: 12px;">If you didn't create an account, please ignore this email.</p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Welcome to Scientific Text Annotator!
        
        Thank you for registering! Please verify your email address by clicking the link below:
        
        {verification_url}
        
        This link will expire in 24 hours for security reasons.
        
        If you didn't create an account, please ignore this email.
        """
        
        # Check if SMTP is configured
        if not settings.smtp_host or not settings.smtp_username or not settings.smtp_password:
            # Fall back to console output for development
            print(f"VERIFICATION EMAIL FOR {email}:")
            print(f"Verification URL: {verification_url}")
            print("=" * 50)
            print("⚠️  SMTP not configured - email printed to console only")
            print("To receive actual emails, configure SMTP settings in .env file")
            return True
        
        # Send actual email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{settings.smtp_from_name} <{settings.smtp_from_email or settings.smtp_username}>"
        msg['To'] = email
        
        # Attach both text and HTML versions
        text_part = MIMEText(text_body, 'plain')
        html_part = MIMEText(html_body, 'html')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        # Send email via SMTP
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            if settings.smtp_use_tls:
                server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(msg)
        
        print(f"✅ Verification email sent successfully to {email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send verification email to {email}: {e}")
        # Still print to console as fallback
        print(f"VERIFICATION EMAIL FOR {email}:")
        print(f"Verification URL: {verification_url}")
        print("=" * 50)
        return False

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict


class TokenData(BaseModel):
    email: Optional[str] = None


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    db = get_db()
    user = db.table("users").select("*").eq("email", token_data.email).execute()
    if not user.data:
        raise credentials_exception
    return user.data[0]


@router.post("/register")
async def register(user: UserCreate):
    try:
        # Use admin client to bypass RLS
        from app.database import get_admin_db
        db = get_admin_db()
        
        # Check if user exists
        existing_user = db.table("users").select("*").eq("email", user.email).execute()
        if existing_user.data:
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": "Email already registered"
                }
            )
        
        # Generate verification token
        verification_token = generate_verification_token()
        verification_expires = datetime.utcnow() + timedelta(hours=24)
        
        # Create user (not verified yet)
        hashed_password = get_password_hash(user.password)
        new_user = {
            "email": user.email,
            "full_name": user.full_name,
            "hashed_password": hashed_password,
            "is_active": True,
            "email_verified": False,
            "email_verification_token": verification_token,
            "email_verification_expires": verification_expires.isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = db.table("users").insert(new_user).execute()
        created_user = result.data[0]
        
        # Send verification email
        send_verification_email(user.email, verification_token)
        
        return {
            "message": "Registration successful! Please check your email to verify your account.",
            "email": user.email,
            "verification_required": True
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": f"Registration error: {str(e)}"
            }
        )


@router.post("/verify-email")
async def verify_email(verification: EmailVerification):
    try:
        # Rate limiting check (only for failed attempts)
        if is_rate_limited(verification.token):
            print(f"🚫 Rate limited verification attempt for token: {verification.token[:10]}...")
            return JSONResponse(
                status_code=429,
                content={
                    "error": True,
                    "message": "Too many failed verification attempts. Please wait before trying again."
                }
            )
        
        from app.database import get_admin_db
        db = get_admin_db()
        
        print(f"🔍 Email verification request for token: {verification.token[:10]}...")
        
        # Find user with this verification token
        user = db.table("users").select("*").eq("email_verification_token", verification.token).execute()
        if not user.data:
            print(f"❌ Token not found in database: {verification.token[:10]}...")
            # Record failed attempt
            record_failed_verification(verification.token)
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": "Invalid verification token"
                }
            )
        
        user_data = user.data[0]
        print(f"✅ User found: {user_data['email']} (verified: {user_data.get('email_verified', False)})")
        
        # Check if already verified
        if user_data.get("email_verified", False):
            print(f"⚠️ Email already verified for user: {user_data['email']}")
            # Clear any failed attempts since verification is successful
            clear_failed_verification(verification.token)
            # Return success with user data for already verified accounts
            return {
                "message": "Email is already verified!",
                "access_token": None,
                "token_type": "bearer",
                "user": {
                    "id": user_data["id"],
                    "email": user_data["email"],
                    "full_name": user_data["full_name"]
                }
            }
        
        # Check if token has expired
        if user_data.get("email_verification_expires"):
            expires_at = datetime.fromisoformat(user_data["email_verification_expires"].replace('Z', '+00:00'))
            if datetime.utcnow().replace(tzinfo=expires_at.tzinfo) > expires_at:
                print(f"⏰ Token expired for user: {user_data['email']}")
                # Record failed attempt for expired token
                record_failed_verification(verification.token)
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": True,
                        "message": "Verification token has expired"
                    }
                )
        
        # Mark email as verified
        print(f"✅ Marking email as verified for user: {user_data['email']}")
        db.table("users").update({
            "email_verified": True,
            "email_verification_token": None,
            "email_verification_expires": None,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", user_data["id"]).execute()
        
        # Clear any failed verification attempts since this was successful
        clear_failed_verification(verification.token)
        
        # Create access token for automatic login
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user_data["email"]}, expires_delta=access_token_expires
        )
        
        print(f"🎉 Email verification successful for: {user_data['email']}")
        return {
            "message": "Email verified successfully!",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user_data["id"],
                "email": user_data["email"],
                "full_name": user_data["full_name"]
            }
        }
    except Exception as e:
        print(f"💥 Email verification error: {str(e)}")
        # Record failed attempt for any server errors
        record_failed_verification(verification.token)
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": f"Email verification error: {str(e)}"
            }
        )


@router.post("/resend-verification")
async def resend_verification(email_request: dict):
    try:
        from app.database import get_admin_db
        db = get_admin_db()
        
        email = email_request.get("email")
        if not email:
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": "Email is required"
                }
            )
        
        # Find unverified user
        user = db.table("users").select("*").eq("email", email).eq("email_verified", False).execute()
        if not user.data:
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": "User not found or already verified"
                }
            )
        
        # Generate new verification token
        verification_token = generate_verification_token()
        verification_expires = datetime.utcnow() + timedelta(hours=24)
        
        # Update user with new token
        db.table("users").update({
            "email_verification_token": verification_token,
            "email_verification_expires": verification_expires.isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }).eq("email", email).execute()
        
        # Send verification email
        send_verification_email(email, verification_token)
        
        return {"message": "Verification email sent successfully!"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": f"Failed to resend verification: {str(e)}"
            }
        )


@router.post("/create-test-user")
async def create_test_user():
    """Create a test user for development"""
    try:
        # Use admin client to bypass RLS
        from app.database import get_admin_db
        db = get_admin_db()
        
        # Check if test user already exists
        existing = db.table("users").select("*").eq("email", "test@example.com").execute()
        if existing.data:
            return {"message": "Test user already exists", "email": "test@example.com"}
        
        # Create test user
        hashed_password = get_password_hash("password123")
        new_user = {
            "email": "test@example.com",
            "full_name": "Test User",
            "hashed_password": hashed_password,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = db.table("users").insert(new_user).execute()
        return {
            "message": "Test user created successfully",
            "email": "test@example.com",
            "password": "password123",
            "user_id": result.data[0]["id"] if result.data else None
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": f"Failed to create test user: {str(e)}"
            }
        )


@router.post("/login")
async def login(user_credentials: UserLogin):
    try:
        db = get_db()
        
        # Get user from database
        user = db.table("users").select("*").eq("email", user_credentials.email).execute()
        if not user.data or not verify_password(user_credentials.password, user.data[0]["hashed_password"]):
            return JSONResponse(
                status_code=401,
                content={
                    "error": True,
                    "message": "Incorrect email or password"
                }
            )
        
        user_data = user.data[0]
        
        # Check if email is verified
        if not user_data.get("email_verified", False):
            return JSONResponse(
                status_code=403,
                content={
                    "error": True,
                    "message": "Please verify your email address before logging in",
                    "verification_required": True
                }
            )
        
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user_data["email"]}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user_data["id"],
                "email": user_data["email"],
                "full_name": user_data["full_name"]
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": f"Login error: {str(e)}"
            }
        )


@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user


@router.get("/test")
async def test_db():
    """Test endpoint to check database connectivity"""
    try:
        db = get_db()
        # Try a simple query
        result = db.table('users').select('id').limit(1).execute()
        return {
            "status": "ok",
            "message": "Database connection successful",
            "has_users": len(result.data) > 0 if result.data else False
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": f"Database connection failed: {str(e)}",
                "detail": str(e)
            }
        )


@router.post("/logout")
async def logout():
    return {"message": "Successfully logged out"}


# Session endpoint for frontend to get current user
@router.get("/session")
async def get_session(request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))):
    try:
        if not credentials:
            return {"user": None}
            
        token = credentials.credentials
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if not email:
            return {"user": None}
        db = get_db()
        user = db.table("users").select("*").eq("email", email).execute()
        if not user.data:
            return {"user": None}
        user_data = user.data[0]
        return {"user": {
            "id": user_data["id"],
            "email": user_data["email"],
            "full_name": user_data["full_name"],
            "avatar_url": user_data.get("avatar_url", ""),
            "created_at": user_data["created_at"],
            "updated_at": user_data.get("updated_at", user_data["created_at"])
        }}
    except Exception:
        return {"user": None}


# Profile update endpoint
@router.put("/profile")
async def update_profile(profile: UserProfileUpdate, current_user: dict = Depends(get_current_user)):
    try:
        db = get_db()
        update_data = {}
        if profile.full_name is not None:
            update_data["full_name"] = profile.full_name
        if profile.avatar_url is not None:
            update_data["avatar_url"] = profile.avatar_url
        if not update_data:
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": "No profile fields to update"
                }
            )
        result = db.table("users").update(update_data).eq("id", current_user["id"]).execute()
        updated_user = result.data[0] if result.data else current_user
        return {"user": {
            "id": updated_user["id"],
            "email": updated_user["email"],
            "full_name": updated_user["full_name"],
            "avatar_url": updated_user.get("avatar_url", ""),
            "created_at": updated_user["created_at"],
            "updated_at": updated_user.get("updated_at", updated_user["created_at"])
        }}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": f"Profile update error: {str(e)}"
            }
        )
