"""
Google OAuth authentication module for NYU workspace accounts
"""
import os
import logging
from functools import wraps
from flask import session, redirect, url_for, request
from google.auth.transport.requests import Request
from google.oauth2.id_token import verify_oauth2_token
from google_auth_oauthlib.flow import Flow
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
ALLOWED_DOMAIN = 'nyu.edu'  # Only allow NYU workspace accounts

def get_oauth_flow(redirect_uri):
    """Create and return Google OAuth flow"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise ValueError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in environment variables")
    
    return Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['openid', 'email', 'profile'],
        redirect_uri=redirect_uri
    )

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get the current logged-in user's email"""
    return session.get('user_email')

def is_nyu_account(email):
    """Check if email is from NYU workspace"""
    return email.lower().endswith(f'@{ALLOWED_DOMAIN}')
