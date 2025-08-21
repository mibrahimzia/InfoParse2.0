"""
API Key authentication and management
"""
import os
import secrets
from datetime import datetime, timedelta
from cachetools import TTLCache
import logging

logger = logging.getLogger("webtapi.auth")

# In-memory storage (replace with database in production)
api_keys = TTLCache(maxsize=1000, ttl=86400)  # 24-hour TTL
key_usage = TTLCache(maxsize=1000, ttl=86400)  # 24-hour TTL

# Default rate limits
DEFAULT_RATE_LIMITS = {
    "free": 100,  # 100 requests per day
    "basic": 1000,
    "pro": 10000,
    "enterprise": 100000
}

# Persistent demo key that doesn't change between restarts
DEMO_API_KEY = "demo_key_12345"

def initialize_auth():
    """Initialize the authentication system with a demo key"""
    api_keys[DEMO_API_KEY] = {
        "plan": "free",
        "created_at": datetime.now(),
        "rate_limit": DEFAULT_RATE_LIMITS["free"]
    }
    key_usage[DEMO_API_KEY] = 0
    logger.info(f"Demo API key initialized: {DEMO_API_KEY}")

def generate_api_key(plan="free"):
    """Generate a new API key"""
    key = f"sk_{secrets.token_urlsafe(32)}"
    api_keys[key] = {
        "plan": plan,
        "created_at": datetime.now(),
        "rate_limit": DEFAULT_RATE_LIMITS.get(plan, 100)
    }
    key_usage[key] = 0
    return key

def validate_api_key(api_key):
    """Validate an API key and check rate limits"""
    if api_key not in api_keys:
        return False, "Invalid API key"
    
    # Check rate limits
    usage = key_usage.get(api_key, 0)
    limit = api_keys[api_key]["rate_limit"]
    
    if usage >= limit:
        return False, "Rate limit exceeded"
    
    # Increment usage
    key_usage[api_key] = usage + 1
    return True, "OK"

def get_usage_stats(api_key):
    """Get usage statistics for an API key"""
    if api_key not in api_keys:
        return None
    
    return {
        "usage": key_usage.get(api_key, 0),
        "limit": api_keys[api_key]["rate_limit"],
        "plan": api_keys[api_key]["plan"],
        "remaining": api_keys[api_key]["rate_limit"] - key_usage.get(api_key, 0)
    }

# Initialize the auth system when this module is imported
initialize_auth()