import time
from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse
from ..schemas import ApiErrorResponse, ErrorCode

def rate_limit_by_ip(limit: int, window: int):
    """
    Simple rate limiting decorator using Django cache.
    limit: Max number of requests
    window: Time window in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Get IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            cache_key = f"ratelimit:{func.__name__}:{ip}"
            requests = cache.get(cache_key, [])
            
            # Clean up old requests outside the window
            now = time.time()
            requests = [r for r in requests if now - r < window]
            
            if len(requests) >= limit:
                error = ApiErrorResponse(
                    code=ErrorCode.PLANNER_EXECUTION_ERROR,
                    detail="You have exceeded the request limit. Please wait a moment before trying again."
                )
                return JsonResponse(error.model_dump(mode="json"), status=429)
            
            requests.append(now)
            cache.set(cache_key, requests, window)
            return func(request, *args, **kwargs)
        return wrapper
    return decorator
