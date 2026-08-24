"""
Data Normalization Layer (Layer 2 in AI SDR Architecture).
Cleans, standardizes, deduplicates, and enriches lead data before the Analysis Layer.
"""

import hashlib
import re
import urllib.parse
from typing import Any


class DataNormalizer:
    """
    Standardizes contact details, validates email and website format,
    and assigns canonical industry tags.
    """

    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    PHONE_DIGITS_REGEX = re.compile(r"\D")

    INDUSTRY_KEYWORD_MAP = {
        "Healthcare & Medical": [
            "clinic",
            "dental",
            "dentist",
            "doctor",
            "health",
            "hospital",
            "physio",
            "chiro",
            "med",
            "ortho",
        ],
        "Legal & Professional Services": [
            "law",
            "attorney",
            "legal",
            "lawyer",
            "advocate",
            "notary",
            "cpa",
            "accounting",
            "tax",
            "consulting",
        ],
        "Home Services & Trades": [
            "plumb",
            "electric",
            "roof",
            "hvac",
            "paint",
            "contractor",
            "solar",
            "builder",
            "cleaning",
            "landscap",
        ],
        "Hospitality & Dining": [
            "restaurant",
            "cafe",
            "bistro",
            "bakery",
            "bar",
            "grill",
            "hotel",
            "catering",
            "lounge",
            "pizza",
        ],
        "Automotive": [
            "auto",
            "car",
            "mechanic",
            "tire",
            "garage",
            "collision",
            "dealership",
            "towing",
        ],
        "Real Estate": [
            "realty",
            "estate",
            "realtor",
            "property",
            "mortgage",
            "broker",
        ],
        "Fitness & Beauty": [
            "gym",
            "fitness",
            "crossfit",
            "spa",
            "salon",
            "barber",
            "yoga",
            "pilates",
            "massage",
        ],
    }

    @classmethod
    def clean_website_url(cls, raw_url: str | None) -> tuple[str | None, str | None]:
        """
        Cleans and extracts standardized URL and clean domain.
        """
        if not raw_url or raw_url.strip() in ("", "None", "null", "N/A"):
            return None, None

        cleaned = raw_url.strip()
        if not cleaned.startswith("http://") and not cleaned.startswith("https://"):
            cleaned = f"https://{cleaned}"

        parsed = urllib.parse.urlparse(cleaned)
        domain = parsed.netloc.lower()
        domain = domain.removeprefix("www.")

        return cleaned, domain

    @classmethod
    def clean_phone(cls, raw_phone: str | None) -> str | None:
        if not raw_phone:
            return None
        digits = cls.PHONE_DIGITS_REGEX.sub("", str(raw_phone))
        if len(digits) >= 10:
            return (
                f"+{digits}" if not str(raw_phone).startswith("+") else str(raw_phone)
            )
        return raw_phone.strip() if raw_phone.strip() else None

    @classmethod
    def validate_email(cls, email: str | None) -> tuple[bool, str | None]:
        if not email or not isinstance(email, str):
            return False, None
        clean_email = email.strip().lower()
        if cls.EMAIL_REGEX.match(clean_email):
            return True, clean_email
        return False, None

    @classmethod
    def classify_industry(
        cls,
        company_name: str,
        given_industry: str | None = None,
        keywords: list[str] | None = None,
    ) -> str:
        if (
            given_industry
            and given_industry.strip()
            and given_industry.strip().lower() not in ("other", "unknown")
        ):
            return given_industry.strip()

        search_text = f"{company_name} {' '.join(keywords or [])}".lower()
        for category, kw_list in cls.INDUSTRY_KEYWORD_MAP.items():
            if any(k in search_text for k in kw_list):
                return category

        return "Commercial Services"

    @classmethod
    def generate_dedupe_key(
        cls, company_name: str, domain: str | None, phone: str | None
    ) -> str:
        """
        Generates deterministic deduplication hash based on domain, phone, or company name.
        """
        key_parts = []
        if domain:
            key_parts.append(f"domain:{domain.lower()}")
        if phone:
            key_parts.append(f"phone:{phone}")
        if not key_parts:
            key_parts.append(
                f"name:{re.sub(r'[^a-zA-Z0-9]', '', company_name.lower())}"
            )

        seed = "|".join(key_parts)
        return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]

    @classmethod
    def normalize_lead(cls, raw_lead: dict[str, Any]) -> dict[str, Any]:
        """
        Normalizes a raw Lead Finder prospect.
        """
        company_name = (
            raw_lead.get("company_name") or raw_lead.get("name") or "Unnamed Business"
        ).strip()
        raw_url = (
            raw_lead.get("website_url")
            or raw_lead.get("website")
            or raw_lead.get("url")
        )
        cleaned_url, domain = cls.clean_website_url(raw_url)

        raw_phone = raw_lead.get("primary_contact_phone") or raw_lead.get("phone")
        cleaned_phone = cls.clean_phone(raw_phone)

        raw_email = raw_lead.get("primary_contact_email") or raw_lead.get("email")
        is_email_valid, cleaned_email = cls.validate_email(raw_email)

        industry = cls.classify_industry(
            company_name=company_name,
            given_industry=raw_lead.get("industry") or raw_lead.get("category"),
            keywords=raw_lead.get("keywords") or [],
        )

        dedupe_key = cls.generate_dedupe_key(company_name, domain, cleaned_phone)

        return {
            "dedupe_key": dedupe_key,
            "company_name": company_name,
            "website_url": cleaned_url,
            "domain": domain,
            "has_website": bool(cleaned_url and domain),
            "primary_contact_name": raw_lead.get("primary_contact_name")
            or raw_lead.get("contact_name"),
            "primary_contact_email": cleaned_email,
            "is_email_valid": is_email_valid,
            "primary_contact_phone": cleaned_phone,
            "location": raw_lead.get("location")
            or raw_lead.get("address")
            or raw_lead.get("city"),
            "industry": industry,
            "campaign_id": raw_lead.get("campaign_id"),
            "source": raw_lead.get("source") or "leadfinder",
            "metadata": raw_lead.get("metadata") or {},
        }
