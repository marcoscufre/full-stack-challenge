import requests
from abc import ABC, abstractmethod

from .config import provider_config


class ProviderError(Exception):
    """Base class for external provider errors."""
    def __init__(self, message: str, provider_name: str, status_code: int | None = None):
        self.message = message
        self.provider_name = provider_name
        self.status_code = status_code
        super().__init__(self.message)

class GeocodingError(ProviderError):
    pass

class RoutingError(ProviderError):
    pass

class ProviderRateLimitError(ProviderError):
    pass

class ProviderTimeoutError(ProviderError):
    pass


def handle_request_errors(provider_name: str):
    """Decorator or helper to map requests exceptions to ProviderErrors."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except requests.Timeout:
                raise ProviderTimeoutError(f"{provider_name} request timed out.", provider_name)
            except requests.HTTPError as e:
                status_code = e.response.status_code
                if status_code == 429:
                    raise ProviderRateLimitError(f"{provider_name} rate limit exceeded.", provider_name, status_code)
                raise ProviderError(f"{provider_name} HTTP error: {str(e)}", provider_name, status_code)
            except requests.RequestException as e:
                raise ProviderError(f"{provider_name} connection error: {str(e)}", provider_name)
        return wrapper
    return decorator
