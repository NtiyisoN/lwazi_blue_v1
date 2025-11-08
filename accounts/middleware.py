"""
Rate limiting middleware for authentication endpoints
"""
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.utils import timezone
import hashlib


class RateLimitMiddleware:
    """
    Rate limit authentication attempts to prevent brute force attacks
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Configure rate limits for different endpoints
        self.rate_limits = {
            '/accounts/login/': {'max_attempts': 5, 'window': 300},  # 5 attempts per 5 min
            '/accounts/register/': {'max_attempts': 3, 'window': 3600},  # 3 attempts per hour
            '/accounts/otp-login/': {'max_attempts': 3, 'window': 300},  # 3 attempts per 5 min
            '/accounts/request-otp/': {'max_attempts': 5, 'window': 600},  # 5 attempts per 10 min
        }
    
    def __call__(self, request):
        # Check if this is a rate-limited endpoint
        if request.path in self.rate_limits and request.method == 'POST':
            if not self._check_rate_limit(request):
                return HttpResponseForbidden(
                    'Too many attempts. Please try again later.'
                )
        
        response = self.get_response(request)
        return response
    
    def _check_rate_limit(self, request):
        """
        Check if user has exceeded rate limit
        """
        # Get client identifier (IP address + user agent hash)
        client_ip = self._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        identifier = hashlib.md5(
            f"{client_ip}:{user_agent}".encode()
        ).hexdigest()
        
        # Get rate limit config for this endpoint
        config = self.rate_limits.get(request.path, {})
        max_attempts = config.get('max_attempts', 5)
        window = config.get('window', 300)
        
        # Create cache key
        cache_key = f'ratelimit:{request.path}:{identifier}'
        
        # Get current attempt count
        attempts = cache.get(cache_key, 0)
        
        if attempts >= max_attempts:
            return False
        
        # Increment attempt count
        cache.set(cache_key, attempts + 1, window)
        return True
    
    def _get_client_ip(self, request):
        """
        Get client IP address from request
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

