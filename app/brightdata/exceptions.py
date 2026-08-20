"""Exceptions raised during Bright Data Scraper Studio execution."""


class BrightDataError(Exception):
    """Base exception for all Bright Data operations."""


class BrightDataConfigError(BrightDataError):
    """Raised when required Bright Data configuration (API key or Collector ID) is missing."""


class BrightDataAuthError(BrightDataError):
    """Raised when Bright Data authentication fails (401/403)."""


class BrightDataJobError(BrightDataError):
    """Raised when a Bright Data scraping job fails remotely or returns an error."""


class BrightDataTimeoutError(BrightDataError):
    """Raised when polling for Bright Data job results exceeds the maximum duration."""


class BrightDataEmptyResultError(BrightDataError):
    """Raised when Bright Data successfully completes but returns zero records."""

