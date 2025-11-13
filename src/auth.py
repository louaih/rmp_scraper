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
import json

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
OAUTH_REDIRECT_URI = os.getenv('OAUTH_REDIRECT_URI')  # e.g., https://profs.louai.dev/oauth/callback
ALLOWED_DOMAIN = 'nyu.edu'  # Only allow NYU workspace accounts

def get_oauth_flow(redirect_uri=None):
    """Create and return Google OAuth flow"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise ValueError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in environment variables")
    
    # Use environment variable if set, otherwise use provided redirect_uri
    final_redirect_uri = OAUTH_REDIRECT_URI or redirect_uri
    if not final_redirect_uri:
        raise ValueError("redirect_uri must be provided or OAUTH_REDIRECT_URI environment variable must be set")
    
    # Try to load from client_secret.json if it exists
    client_secrets_file = 'client_secret.json'
    if os.path.exists(client_secrets_file):
        return Flow.from_client_secrets_file(
            client_secrets_file,
            scopes=['openid', 'email', 'profile'],
            redirect_uri=final_redirect_uri
        )
    else:
        # Fall back to environment variables
        client_config = {
            "installed": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [final_redirect_uri]
            }
        }
        return Flow.from_client_config(
            client_config,
            scopes=['openid', 'email', 'profile'],
            redirect_uri=final_redirect_uri
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
