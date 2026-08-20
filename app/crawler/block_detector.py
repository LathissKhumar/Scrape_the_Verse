"""Block and challenge detector for identifying rate limits, CAPTCHAs, and security challenges."""

import logging
from typing import Any, Dict, Tuple
from app.crawler.result_models import BlockType

logger = logging.getLogger("CRAWLER_BLOCK_DETECTOR")


class BlockDetector:
    """Detects and classifies anti-bot challenges, CAPTCHAs, and access blocks transparently."""

    CHALLENGE_SIGNATURES = [
        "cloudflare",
        "attention required! | cloudflare",
        "cf-chl-bypass",
        "challenge-running",
        "perimeterx",
        "px-captcha",
        "akamai",
        "access denied - you don't have permission",
        "datadome",
        "shieldsquare",
        "kasada",
        "incapsula",
        "distil networks",
        "cs_503_link",
        "dogsofamazon",
        "api-services-support@amazon.com",
    ]

    CAPTCHA_SIGNATURES = [
        "recaptcha",
        "are you a human",
        "g-recaptcha",
        "hcaptcha",
        "cf-turnstile",
        "solve the captcha",
        "verify you are human",
        "enter the characters you see below",
        "validatecaptcha",
        "type the characters you see in this image",
    ]

    ACCESS_DENIED_SIGNATURES = [
        "access denied",
        "forbidden: you don't have permission",
        "403 forbidden",
        "ip address has been banned",
        "request blocked",
        "waf block",
        "503 service unavailable",
    ]

    AUTH_SIGNATURES = [
        "login required",
        "please log in to continue",
        "sign in to your account",
        "authentication required",
    ]

    def detect_block(
        self,
        status_code: int,
        headers: Dict[str, str],
        html: str,
        url: str = "",
    ) -> Tuple[bool, BlockType, Dict[str, Any]]:
        """Inspect HTTP status, headers, and DOM content to classify block status."""
        html_lower = html.lower() if html else ""
        diagnostics: Dict[str, Any] = {"status_code": status_code, "url": url}

        # 1. Inspect HTTP status codes
        if status_code == 429:
            retry_after = headers.get("retry-after") or headers.get("Retry-After")
            diagnostics["retry_after"] = retry_after
            return True, BlockType.RATE_LIMITED, diagnostics

        if status_code in (401, 407):
            return True, BlockType.AUTH_REQUIRED, diagnostics

        if status_code == 403:
            # Check if 403 has specific challenge or captcha signature
            for sig in self.CAPTCHA_SIGNATURES:
                if sig in html_lower:
                    diagnostics["matched_signature"] = sig
                    return True, BlockType.CAPTCHA, diagnostics

            for sig in self.CHALLENGE_SIGNATURES:
                if sig in html_lower:
                    diagnostics["matched_signature"] = sig
                    return True, BlockType.SECURITY_CHALLENGE, diagnostics

            return True, BlockType.ACCESS_DENIED, diagnostics

        if status_code == 503:
            for sig in self.CAPTCHA_SIGNATURES:
                if sig in html_lower:
                    diagnostics["matched_signature"] = sig
                    return True, BlockType.CAPTCHA, diagnostics

            for sig in self.CHALLENGE_SIGNATURES:
                if sig in html_lower:
                    diagnostics["matched_signature"] = sig
                    return True, BlockType.SECURITY_CHALLENGE, diagnostics

            return True, BlockType.ACCESS_DENIED, diagnostics

        # 2. Inspect DOM content even on HTTP 200 (for soft-blocks)
        is_short_page = len(html_lower) < 5000

        for sig in self.CHALLENGE_SIGNATURES:
            if sig in html_lower:
                diagnostics["matched_signature"] = sig
                return True, BlockType.SECURITY_CHALLENGE, diagnostics

        for sig in self.CAPTCHA_SIGNATURES:
            if is_short_page and sig in html_lower:
                diagnostics["matched_signature"] = sig
                return True, BlockType.CAPTCHA, diagnostics
            elif not is_short_page:
                # On large pages, only trigger if it's an explicit challenge prompt or widget element
                if sig in ("are you a human", "cf-turnstile", "solve the captcha", "verify you are human",
                            "enter the characters you see below", "type the characters you see in this image"):
                    if sig in html_lower:
                        diagnostics["matched_signature"] = sig
                        return True, BlockType.CAPTCHA, diagnostics
                elif sig in ("hcaptcha", "recaptcha", "g-recaptcha"):
                    if f"class=\"{sig}\"" in html_lower or f"id=\"{sig}\"" in html_lower or f"class=\"h-captcha\"" in html_lower or f"class=\"g-recaptcha\"" in html_lower or "data-sitekey" in html_lower:
                        diagnostics["matched_signature"] = sig
                        return True, BlockType.CAPTCHA, diagnostics

        for sig in self.ACCESS_DENIED_SIGNATURES:
            if sig in html_lower and len(html_lower) < 2500:
                diagnostics["matched_signature"] = sig
                return True, BlockType.ACCESS_DENIED, diagnostics

        for sig in self.AUTH_SIGNATURES:
            if sig in html_lower and len(html_lower) < 2500:
                diagnostics["matched_signature"] = sig
                return True, BlockType.AUTH_REQUIRED, diagnostics

        # Not blocked
        return False, BlockType.NONE, diagnostics

