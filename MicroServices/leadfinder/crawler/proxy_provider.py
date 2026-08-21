"""Proxy provider interface for legitimate infrastructure network routing."""

from typing import Dict, List, Optional
from pydantic import BaseModel


class ProxyConfig(BaseModel):
    """Proxy server configuration."""
    server: str
    username: Optional[str] = None
    password: Optional[str] = None
    bypass: Optional[str] = None


class ProxyProvider:
    """Provides proxy configuration for infrastructure network routing (never used to evade blocks)."""

    def __init__(self, proxies: Optional[List[ProxyConfig]] = None):
        self._proxies = proxies or []
        self._current_index = 0

    def get_proxy(self) -> Optional[Dict[str, str]]:
        """Return next configured proxy dictionary for Playwright launch arguments."""
        if not self._proxies:
            return None

        p = self._proxies[self._current_index % len(self._proxies)]
        self._current_index += 1

        proxy_dict = {"server": p.server}
        if p.username:
            proxy_dict["username"] = p.username
        if p.password:
            proxy_dict["password"] = p.password
        if p.bypass:
            proxy_dict["bypass"] = p.bypass

        return proxy_dict
