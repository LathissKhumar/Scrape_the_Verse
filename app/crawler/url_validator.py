"""URL security validator for web crawling to prevent SSRF and unauthorized scheme execution."""

import ipaddress
import socket
from urllib.parse import urlparse
from typing import Set


class SSRFSecurityError(ValueError):
    """Raised when a target URL violates SSRF security boundaries or allowed schemes."""
    pass


class UrlSecurityValidator:
    """Validates URLs for scheme compliance and enforces SSRF boundaries by blocking private subnets."""

    ALLOWED_SCHEMES: Set[str] = {"http", "https"}

    def __init__(self, allow_private: bool = False):
        self.allow_private = allow_private

    def validate_url(self, url: str) -> str:
        """Validate target URL scheme and enforce private/loopback/cloud metadata IP blocking.
        
        Args:
            url: The target URL string.
            
        Returns:
            The validated URL string verbatim.
            
        Raises:
            SSRFSecurityError: If scheme is disallowed or resolves to private/loopback/metadata IP.
        """
        if not url or not isinstance(url, str):
            raise SSRFSecurityError("Target URL cannot be empty.")

        url_str = url.strip()
        parsed = urlparse(url_str)

        if not parsed.scheme or parsed.scheme.lower() not in self.ALLOWED_SCHEMES:
            raise SSRFSecurityError(f"Invalid URL scheme '{parsed.scheme}'. Only http and https are allowed.")

        hostname = parsed.hostname
        if not hostname:
            raise SSRFSecurityError("Target URL must have a valid hostname.")

        if self.allow_private:
            return url_str

        # Check explicit hostname patterns
        hostname_lower = hostname.lower()
        if hostname_lower in ("localhost", "127.0.0.1", "::1", "169.254.169.254"):
            raise SSRFSecurityError(f"Private, loopback, or cloud metadata IP blocked: {hostname}")

        # Resolve IP addresses and inspect against private/loopback ranges
        try:
            addr_info = socket.getaddrinfo(hostname, None)
            for item in addr_info:
                ip_str = item[4][0]
                ip = ipaddress.ip_address(ip_str)
                if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
                    raise SSRFSecurityError(f"Private, loopback, or cloud metadata IP blocked: {hostname} ({ip_str})")
        except socket.gaierror:
            # If DNS fails at validation stage, allow execution layer to handle network resolution
            pass

        return url_str
