import os
from datetime import timedelta

class Config:
    """Flask configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'spoms-secret-key-change-in-production-2026'
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_SAMESITE = 'Lax'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
