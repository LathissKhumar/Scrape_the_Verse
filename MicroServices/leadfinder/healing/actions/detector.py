"""Detector for identifying blocking UI interactions, cookie banners, modals, and dynamic triggers."""

import re
from typing import Any

from bs4 import BeautifulSoup

from leadfinder.config.logging import get_logger
from leadfinder.healing.actions.models import ActionType

logger = get_logger("ACTION_ISSUE_DETECTOR")

_HAS_TEXT_REGEX = re.compile(r"has-text\('([^']+)'\)")


class ActionIssueDetector:
    """Inspects raw rendered HTML and page state to diagnose interaction barriers."""

    COOKIE_SELECTORS = [
        "#onetrust-accept-btn-handler",
        "button#accept-cookies",
        "button.accept-cookie",
        "button[data-testid='cookie-accept']",
        "button:has-text('Accept all')",
        "button:has-text('Accept Cookies')",
        "button:has-text('I agree')",
        "button:has-text('Allow all')",
        ".cookie-consent button.btn-primary",
        "[aria-label*='cookie' i] button",
    ]

    MODAL_DISMISS_SELECTORS = [
        "button.modal-close",
        "button.dialog-close",
        "button[aria-label='Close']",
        "button.close-modal",
        ".modal-backdrop",
        "[aria-modal='true'] button.close",
        "button:has-text('No thanks')",
        "button:has-text('Dismiss')",
    ]

    LOAD_MORE_SELECTORS = [
        "button.load-more",
        "button.btn-load-more",
        "button:has-text('Load More')",
        "button:has-text('Show more')",
        "button:has-text('View more')",
        "a.load-more-btn",
        ".pagination-next",
    ]

    EXPAND_SELECTORS = [
        "button:has-text('Read more')",
        "button:has-text('Show details')",
        "details summary",
        ".accordion-trigger",
    ]

    def detect_blocking_issues(self, html: str) -> list[dict[str, Any]]:
        """Identify interaction bottlenecks present in the DOM."""
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        issues: list[dict[str, Any]] = []

        # 1. Check for Cookie Consent Banners
        for sel in self.COOKIE_SELECTORS:
            # Check simple ID or class matches in soup
            clean_sel = sel.split(":")[0] if ":" in sel else sel
            if clean_sel.startswith("#"):
                el = soup.find(id=clean_sel[1:])
            elif clean_sel.startswith("."):
                el = soup.find(class_=clean_sel[1:])
            else:
                el = None

            text_pattern = _HAS_TEXT_REGEX.search(sel)
            if text_pattern:
                target_text = text_pattern.group(1).lower()
                for btn in soup.find_all(["button", "a"]):
                    if target_text in btn.get_text().strip().lower():
                        el = btn
                        break

            if el:
                issues.append(
                    {
                        "issue_type": "COOKIE_CONSENT_BANNER",
                        "recommended_action": ActionType.ACCEPT_COOKIE,
                        "target_selector": sel,
                        "element_text": el.get_text().strip()[:50] if el else "",
                    }
                )
                break

        # 2. Check for Blocking Modals / Overlays
        for sel in self.MODAL_DISMISS_SELECTORS:
            text_pattern = _HAS_TEXT_REGEX.search(sel)
            matched = False
            if text_pattern:
                target_text = text_pattern.group(1).lower()
                for btn in soup.find_all(["button", "a", "div"]):
                    if (
                        target_text in btn.get_text().strip().lower()
                        and len(btn.get_text().strip()) < 30
                    ):
                        issues.append(
                            {
                                "issue_type": "BLOCKING_MODAL_OVERLAY",
                                "recommended_action": ActionType.DISMISS_OVERLAY,
                                "target_selector": sel,
                            }
                        )
                        matched = True
                        break
            if matched:
                break

        # 3. Check for Load More / Pagination triggers
        for sel in self.LOAD_MORE_SELECTORS:
            text_pattern = _HAS_TEXT_REGEX.search(sel)
            if text_pattern:
                target_text = text_pattern.group(1).lower()
                for btn in soup.find_all(["button", "a"]):
                    if target_text in btn.get_text().strip().lower():
                        issues.append(
                            {
                                "issue_type": "PAGINATION_LOAD_MORE_REQUIRED",
                                "recommended_action": ActionType.CLICK_LOAD_MORE,
                                "target_selector": sel,
                            }
                        )
                        break

        # 4. Check for Infinite Scroll Requirement (e.g. low initial records or presence of scroll indicators)
        if len(soup.find_all(["article", "li", "div"])) > 20 and len(html) < 25000:
            issues.append(
                {
                    "issue_type": "LAZY_LOAD_SCROLL_REQUIRED",
                    "recommended_action": ActionType.SCROLL,
                    "target_selector": "window",
                    "value": "2000",
                }
            )

        return issues
