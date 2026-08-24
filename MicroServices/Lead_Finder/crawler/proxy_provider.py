"""Proxy provider interface for legitimate infrastructure network routing."""

from pydantic import BaseModel


class ProxyConfig(BaseModel):
    """Proxy server configuration."""

    server: str
    username: str | None = None
    password: str | None = None
    bypass: str | None = None


class ProxyProvider:
    """Provides proxy configuration for infrastructure network routing (never used to evade blocks)."""

    def __init__(self, proxies: list[ProxyConfig] | None = None):
        self._proxies = proxies or []
        self._current_index = 0

    def get_proxy(self) -> dict[str, str] | None:
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
