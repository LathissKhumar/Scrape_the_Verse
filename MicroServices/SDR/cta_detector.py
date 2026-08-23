"""
Conversion & CTA Detector (Layer 3 in AI SDR Architecture).
Scans crawled website pages for conversion signals, lead capture forms, click-to-call, and chatbots.
"""

from typing import Any, Dict, List


class CTADetector:
    """
    Evaluates conversion readiness and conversion friction on prospect websites.
    """

    @staticmethod
    def analyze_conversion_signals(pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        has_contact_form = False
        has_phone_cta = False
        has_booking_engine = False
        has_live_chat = False
        has_lead_magnet = False

        total_pages = len(pages)
        cta_buttons_found = []

        for page in pages:
            text = (page.get("title", "") + " " + " ".join(page.get("h1", [])) + " " + " ".join(page.get("h2", []))).lower()
            links = [l.get("href", "").lower() for l in page.get("links", []) if isinstance(l, dict)]

            # Check phone CTA
            if any("tel:" in l for l in links) or "call us" in text or "call now" in text:
                has_phone_cta = True

            # Check contact / booking forms
            if any(k in text for k in ["book online", "schedule appointment", "free quote", "get a quote", "contact us", "reserve"]):
                has_contact_form = True

            if any(k in text for k in ["calendly", "acuity", "opentable", "resy", "booksy", "mindbody", "janeapp"]):
                has_booking_engine = True

            # Check live chat
            if any(k in text for k in ["crisp", "intercom", "drift", "tidio", "livechat", "whatsapp", "chat with us"]):
                has_live_chat = True

        conversion_score = 100
        issues = []

        if not has_phone_cta:
            conversion_score -= 20
            issues.append("No prominent Click-to-Call CTA button detected above the fold.")

        if not has_contact_form and not has_booking_engine:
            conversion_score -= 30
            issues.append("Missing instant online booking or lead capture form.")

        if not has_live_chat:
            conversion_score -= 15
            issues.append("No instant chat or WhatsApp messaging widget for fast lead capture.")

        conversion_score = max(20, conversion_score)

        return {
            "conversion_score": conversion_score,
            "has_phone_cta": has_phone_cta,
            "has_contact_form": has_contact_form,
            "has_booking_engine": has_booking_engine,
            "has_live_chat": has_live_chat,
            "conversion_issues": issues,
            "conversion_grade": "High" if conversion_score >= 80 else ("Moderate" if conversion_score >= 50 else "Low/Leaking Leads"),
        }
