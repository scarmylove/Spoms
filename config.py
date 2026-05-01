import os
from datetime import timedelta

class Config:
    """Flask configuration for Vercel"""
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'spoms-secret-key-2026'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # Set to True with HTTPS
    SESSION_COOKIE_SAMESITE = 'Lax'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size