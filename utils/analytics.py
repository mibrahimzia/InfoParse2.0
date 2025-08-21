"""
Analytics and usage tracking utilities
"""
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger("webtapi.analytics")

# In-memory storage (replace with database in production)
usage_data = defaultdict(lambda: {
    "total_requests": 0,
    "last_used": None,
    "endpoints_created": 0,
    "daily_usage": defaultdict(int)
})

def track_usage(api_key, endpoint_created=False):
    """Track API usage"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    usage_data[api_key]["total_requests"] += 1
    usage_data[api_key]["last_used"] = datetime.now()
    usage_data[api_key]["daily_usage"][today] += 1
    
    if endpoint_created:
        usage_data[api_key]["endpoints_created"] += 1
    
    logger.info(f"Usage tracked for API key: {api_key}")

def get_usage_stats(api_key):
    """Get usage statistics for an API key"""
    if api_key not in usage_data:
        return None
    
    today = datetime.now().strftime("%Y-%m-%d")
    daily_usage = usage_data[api_key]["daily_usage"].get(today, 0)
    
    return {
        "total_requests": usage_data[api_key]["total_requests"],
        "endpoints_created": usage_data[api_key]["endpoints_created"],
        "last_used": usage_data[api_key]["last_used"],
        "daily_usage": daily_usage
    }

def get_all_usage_stats():
    """Get usage statistics for all API keys"""
    return dict(usage_data)