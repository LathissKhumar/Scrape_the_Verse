"""
Canonical Evidence Normalizer

Extracts and classifies evidence from SEO and Business Analysis reports
into a deterministic, structured format for the Website Planner.
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EvidenceType(str, Enum):
    VERIFIED_FACT = "VERIFIED_FACT"
    GROUNDED_FINDING = "GROUNDED_FINDING"
    GROUNDED_RECOMMENDATION = "GROUNDED_RECOMMENDATION"
    UNKNOWN = "UNKNOWN"


class EvidenceSource(str, Enum):
    SEO_REPORT = "SEO_REPORT"
    BUSINESS_ANALYSIS = "BUSINESS_ANALYSIS"
    BOTH = "BOTH"


@dataclass
class CanonicalEvidenceItem:
    """A single piece of classified evidence."""

    id: str
    type: EvidenceType
    source: EvidenceSource
    category: str  # e.g., "service", "contact", "seo_issue", "customer_need", etc.
    claim: str  # Human-readable statement
    raw_data: dict[str, Any]  # Original data for traceability
    confidence: float = 1.0
    urls: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "source": self.source.value,
            "category": self.category,
            "claim": self.claim,
            "raw_data": self.raw_data,
            "confidence": self.confidence,
            "urls": self.urls,
        }


@dataclass
class CanonicalEvidence:
    """Complete canonical evidence package."""

    verified_business_facts: list[CanonicalEvidenceItem] = field(default_factory=list)
    verified_services: list[CanonicalEvidenceItem] = field(default_factory=list)
    verified_customer_information: list[CanonicalEvidenceItem] = field(
        default_factory=list
    )
    verified_contact_information: list[CanonicalEvidenceItem] = field(
        default_factory=list
    )
    seo_findings: list[CanonicalEvidenceItem] = field(default_factory=list)
    page_specific_findings: list[CanonicalEvidenceItem] = field(default_factory=list)
    business_problems: list[CanonicalEvidenceItem] = field(default_factory=list)
    business_opportunities: list[CanonicalEvidenceItem] = field(default_factory=list)
    customer_needs: list[CanonicalEvidenceItem] = field(default_factory=list)
    recommended_pages: list[CanonicalEvidenceItem] = field(default_factory=list)
    existing_strengths: list[CanonicalEvidenceItem] = field(default_factory=list)
    preservation_requirements: list[CanonicalEvidenceItem] = field(default_factory=list)
    unknown_information: list[CanonicalEvidenceItem] = field(default_factory=list)

    def all_items(self) -> list[CanonicalEvidenceItem]:
        return (
            self.verified_business_facts
            + self.verified_services
            + self.verified_customer_information
            + self.verified_contact_information
            + self.seo_findings
            + self.page_specific_findings
            + self.business_problems
            + self.business_opportunities
            + self.customer_needs
            + self.recommended_pages
            + self.existing_strengths
            + self.preservation_requirements
            + self.unknown_information
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "verified_business_facts": [
                e.to_dict() for e in self.verified_business_facts
            ],
            "verified_services": [e.to_dict() for e in self.verified_services],
            "verified_customer_information": [
                e.to_dict() for e in self.verified_customer_information
            ],
            "verified_contact_information": [
                e.to_dict() for e in self.verified_contact_information
            ],
            "seo_findings": [e.to_dict() for e in self.seo_findings],
            "page_specific_findings": [
                e.to_dict() for e in self.page_specific_findings
            ],
            "business_problems": [e.to_dict() for e in self.business_problems],
            "business_opportunities": [
                e.to_dict() for e in self.business_opportunities
            ],
            "customer_needs": [e.to_dict() for e in self.customer_needs],
            "recommended_pages": [e.to_dict() for e in self.recommended_pages],
            "existing_strengths": [e.to_dict() for e in self.existing_strengths],
            "preservation_requirements": [
                e.to_dict() for e in self.preservation_requirements
            ],
            "unknown_information": [e.to_dict() for e in self.unknown_information],
        }

    def save(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


def _make_id(prefix: str, index: int) -> str:
    return f"{prefix}_{index:04d}"


def normalize_evidence(
    seo_intelligence: dict[str, Any],
    business_intelligence: dict[str, Any],
) -> CanonicalEvidence:
    """
    Main entry point: converts raw intelligence into canonical evidence.
    """
    evidence = CanonicalEvidence()
    idx = 0

    # === VERIFIED BUSINESS FACTS ===
    bp = business_intelligence.get("business_profile", {})

    # Company name
    name = bp.get("business_name", {}).get("value") or bp.get("official_name", {}).get(
        "value"
    )
    if name and name != "Not specified":
        idx += 1
        evidence.verified_business_facts.append(
            CanonicalEvidenceItem(
                id=_make_id("fact", idx),
                type=EvidenceType.VERIFIED_FACT,
                source=EvidenceSource.BUSINESS_ANALYSIS,
                category="company_name",
                claim=f"Company name: {name}",
                raw_data={"field": "business_name/official_name", "value": name},
                confidence=1.0,
            )
        )

    # Industry
    industry = bp.get("industry", {}).get("value")
    if industry and industry != "Not specified":
        idx += 1
        evidence.verified_business_facts.append(
            CanonicalEvidenceItem(
                id=_make_id("fact", idx),
                type=EvidenceType.VERIFIED_FACT,
                source=EvidenceSource.BUSINESS_ANALYSIS,
                category="industry",
                claim=f"Industry: {industry}",
                raw_data={"field": "industry", "value": industry},
                confidence=1.0,
            )
        )

    # Location
    location = business_intelligence.get("location") or bp.get(
        "geographic_market", {}
    ).get("value")
    if location and location != "Not specified":
        idx += 1
        evidence.verified_business_facts.append(
            CanonicalEvidenceItem(
                id=_make_id("fact", idx),
                type=EvidenceType.VERIFIED_FACT,
                source=EvidenceSource.BUSINESS_ANALYSIS,
                category="location",
                claim=f"Location: {location}",
                raw_data={"field": "location/geographic_market", "value": location},
                confidence=1.0,
            )
        )
        evidence.verified_contact_information.append(
            CanonicalEvidenceItem(
                id=_make_id("contact", idx),
                type=EvidenceType.VERIFIED_FACT,
                source=EvidenceSource.BUSINESS_ANALYSIS,
                category="physical_address",
                claim=f"Physical address: {location}",
                raw_data={"field": "location", "value": location},
                confidence=1.0,
            )
        )

    # Website URL
    website = business_intelligence.get("website")
    if website:
        idx += 1
        evidence.verified_business_facts.append(
            CanonicalEvidenceItem(
                id=_make_id("fact", idx),
                type=EvidenceType.VERIFIED_FACT,
                source=EvidenceSource.BOTH,
                category="website_url",
                claim=f"Website: {website}",
                raw_data={"field": "website", "value": website},
                confidence=1.0,
            )
        )

    # Business type/model
    for field_name in ["business_type", "business_model"]:
        val = bp.get(field_name, {}).get("value")
        if val and val != "Not specified":
            idx += 1
            evidence.verified_business_facts.append(
                CanonicalEvidenceItem(
                    id=_make_id("fact", idx),
                    type=EvidenceType.VERIFIED_FACT,
                    source=EvidenceSource.BUSINESS_ANALYSIS,
                    category=field_name,
                    claim=f"{field_name.replace('_', ' ').title()}: {val}",
                    raw_data={"field": field_name, "value": val},
                    confidence=1.0,
                )
            )

    # === VERIFIED SERVICES ===
    sa = business_intelligence.get("service_analysis", {})
    for svc in sa.get("services", []):
        idx += 1
        svc_name = svc.get("name", "")
        if svc_name:
            is_core = svc.get("importance") == "core"
            has_page = svc.get("has_dedicated_page", False)
            confidence = svc.get("confidence", 0.0)

            evidence.verified_services.append(
                CanonicalEvidenceItem(
                    id=_make_id("svc", idx),
                    type=EvidenceType.VERIFIED_FACT,
                    source=EvidenceSource.BUSINESS_ANALYSIS,
                    category="service",
                    claim=f"Verified service: {svc_name} ({'core' if is_core else 'secondary'})",
                    raw_data={
                        "name": svc_name,
                        "description": svc.get("description", ""),
                        "category": svc.get("category"),
                        "importance": svc.get("importance"),
                        "target_customer": svc.get("target_customer"),
                        "customer_problem_solved": svc.get("customer_problem_solved"),
                        "visibility": svc.get("visibility"),
                        "discoverability": svc.get("discoverability"),
                        "has_dedicated_page": has_page,
                        "cta_present": svc.get("cta_present", False),
                        "confidence": confidence,
                        "evidence_ids": svc.get("evidence_ids", []),
                    },
                    confidence=confidence,
                )
            )

            if is_core and not has_page:
                idx += 1
                evidence.recommended_pages.append(
                    CanonicalEvidenceItem(
                        id=_make_id("rec_page", idx),
                        type=EvidenceType.GROUNDED_RECOMMENDATION,
                        source=EvidenceSource.BOTH,
                        category="service_page",
                        claim=f"Create dedicated page for core service: {svc_name}",
                        raw_data={
                            "service_name": svc_name,
                            "reason": "Core service lacks dedicated page",
                            "customer_problem": svc.get("customer_problem_solved", ""),
                            "target_customer": svc.get("target_customer", ""),
                        },
                        confidence=confidence,
                    )
                )

    # === VERIFIED CUSTOMER INFORMATION ===
    ca = business_intelligence.get("customer_analysis", {})
    for seg in ca.get("segments", []):
        idx += 1
        evidence.verified_customer_information.append(
            CanonicalEvidenceItem(
                id=_make_id("cust", idx),
                type=EvidenceType.VERIFIED_FACT,
                source=EvidenceSource.BUSINESS_ANALYSIS,
                category="customer_segment",
                claim=f"Customer segment: {seg.get('segment_name', '')}",
                raw_data={
                    "segment_name": seg.get("segment_name", ""),
                    "description": seg.get("description", ""),
                    "is_primary": seg.get("is_primary", False),
                    "why_it_matters": seg.get("why_it_matters", ""),
                    "needs": seg.get("needs", []),
                    "intent_signals": seg.get("intent_signals", []),
                    "confidence": seg.get("confidence", 0.0),
                    "evidence_ids": seg.get("evidence_ids", []),
                },
                confidence=seg.get("confidence", 0.0),
            )
        )

        # Extract customer needs as separate items
        for need in seg.get("needs", []):
            idx += 1
            evidence.customer_needs.append(
                CanonicalEvidenceItem(
                    id=_make_id("need", idx),
                    type=EvidenceType.VERIFIED_FACT,
                    source=EvidenceSource.BUSINESS_ANALYSIS,
                    category="customer_need",
                    claim=f"Customer need ({seg.get('segment_name', '')}): {need}",
                    raw_data={"segment": seg.get("segment_name", ""), "need": need},
                    confidence=seg.get("confidence", 0.0),
                )
            )

    # === VERIFIED CONTACT INFORMATION ===
    # Only add what's explicitly in the source
    # Phone, email, booking URL would be added here if present

    # === SEO FINDINGS ===
    # Category scores
    cat_scores = seo_intelligence.get("category_scores", {})
    for cat, score in cat_scores.items():
        idx += 1
        evidence.seo_findings.append(
            CanonicalEvidenceItem(
                id=_make_id("seo_cat", idx),
                type=EvidenceType.GROUNDED_FINDING,
                source=EvidenceSource.SEO_REPORT,
                category="category_score",
                claim=f"SEO category '{cat}' score: {score}/100",
                raw_data={"category": cat, "score": score},
                confidence=1.0,
            )
        )

    overall_score = seo_intelligence.get("overall_score", 0)
    idx += 1
    evidence.seo_findings.append(
        CanonicalEvidenceItem(
            id=_make_id("seo_overall", idx),
            type=EvidenceType.GROUNDED_FINDING,
            source=EvidenceSource.SEO_REPORT,
            category="overall_score",
            claim=f"Overall SEO score: {overall_score}/100",
            raw_data={"overall_score": overall_score},
            confidence=1.0,
        )
    )

    # Technical findings
    for finding in seo_intelligence.get("technical_findings", []):
        idx += 1
        evidence.seo_findings.append(
            CanonicalEvidenceItem(
                id=_make_id("seo_tech", idx),
                type=EvidenceType.GROUNDED_FINDING,
                source=EvidenceSource.SEO_REPORT,
                category="technical_issue",
                claim=f"Technical issue: {finding.get('title', finding.get('type', 'Unknown'))}",
                raw_data=finding,
                confidence=1.0,
                urls=[finding.get("url", "")] if finding.get("url") else [],
            )
        )

    # SEO findings (on-page)
    for finding in seo_intelligence.get("seo_findings", []):
        idx += 1
        evidence.seo_findings.append(
            CanonicalEvidenceItem(
                id=_make_id("seo_onpage", idx),
                type=EvidenceType.GROUNDED_FINDING,
                source=EvidenceSource.SEO_REPORT,
                category="onpage_issue",
                claim=f"On-page SEO issue: {finding.get('title', finding.get('type', 'Unknown'))}",
                raw_data=finding,
                confidence=1.0,
                urls=[finding.get("url", "")] if finding.get("url") else [],
            )
        )

    # Accessibility findings
    for finding in seo_intelligence.get("content_findings", []):
        idx += 1
        evidence.seo_findings.append(
            CanonicalEvidenceItem(
                id=_make_id("seo_acc", idx),
                type=EvidenceType.GROUNDED_FINDING,
                source=EvidenceSource.SEO_REPORT,
                category="accessibility_issue",
                claim=f"Accessibility issue: {finding.get('title', finding.get('type', 'Unknown'))}",
                raw_data=finding,
                confidence=1.0,
                urls=[finding.get("url", "")] if finding.get("url") else [],
            )
        )

    # === PAGE-SPECIFIC FINDINGS ===
    for page in seo_intelligence.get("important_pages", []):
        idx += 1
        issues = page.get("issues", [])
        evidence.page_specific_findings.append(
            CanonicalEvidenceItem(
                id=_make_id("page", idx),
                type=EvidenceType.GROUNDED_FINDING,
                source=EvidenceSource.SEO_REPORT,
                category="page_analysis",
                claim=f"Page analysis: {page.get('title', page.get('url', 'Unknown'))}",
                raw_data={
                    "url": page.get("url", ""),
                    "title": page.get("title", ""),
                    "meta_description": page.get("meta_description", ""),
                    "h1": page.get("h1", ""),
                    "word_count": page.get("word_count", 0),
                    "issues": issues,
                },
                confidence=1.0,
                urls=[page.get("url", "")],
            )
        )

    for page in seo_intelligence.get("service_page_findings", []):
        idx += 1
        issues = page.get("issues", [])
        evidence.page_specific_findings.append(
            CanonicalEvidenceItem(
                id=_make_id("svc_page", idx),
                type=EvidenceType.GROUNDED_FINDING,
                source=EvidenceSource.SEO_REPORT,
                category="service_page_analysis",
                claim=f"Service page analysis: {page.get('title', page.get('url', 'Unknown'))}",
                raw_data={
                    "url": page.get("url", ""),
                    "title": page.get("title", ""),
                    "meta_description": page.get("meta_description", ""),
                    "h1": page.get("h1", ""),
                    "word_count": page.get("word_count", 0),
                    "issues": issues,
                },
                confidence=1.0,
                urls=[page.get("url", "")],
            )
        )

    # === BUSINESS PROBLEMS ===
    for prob in business_intelligence.get("business_problems", []):
        idx += 1
        evidence.business_problems.append(
            CanonicalEvidenceItem(
                id=_make_id("biz_prob", idx),
                type=EvidenceType.GROUNDED_FINDING,
                source=EvidenceSource.BUSINESS_ANALYSIS,
                category="business_problem",
                claim=f"Business problem: {prob.get('title', prob.get('problem', 'Unknown'))}",
                raw_data=prob,
                confidence=prob.get("confidence", 0.0),
            )
        )

    # === BUSINESS OPPORTUNITIES ===
    for opp in business_intelligence.get("opportunities", []):
        idx += 1
        evidence.business_opportunities.append(
            CanonicalEvidenceItem(
                id=_make_id("biz_opp", idx),
                type=EvidenceType.GROUNDED_RECOMMENDATION,
                source=EvidenceSource.BUSINESS_ANALYSIS,
                category="business_opportunity",
                claim=f"Opportunity: {opp.get('opportunity', 'Unknown')}",
                raw_data=opp,
                confidence=opp.get("confidence", 0.0),
            )
        )

    # === EXISTING STRENGTHS ===
    for strength in seo_intelligence.get("strengths", []):
        idx += 1
        evidence.existing_strengths.append(
            CanonicalEvidenceItem(
                id=_make_id("strength", idx),
                type=EvidenceType.GROUNDED_FINDING,
                source=EvidenceSource.SEO_REPORT,
                category="strength",
                claim=f"Strength: {strength}",
                raw_data={"description": strength},
                confidence=1.0,
            )
        )

    # === PRESERVATION REQUIREMENTS ===
    # Company info
    for item in evidence.verified_business_facts:
        if item.category in ("company_name", "location", "website_url", "industry"):
            idx += 1
            evidence.preservation_requirements.append(
                CanonicalEvidenceItem(
                    id=_make_id("preserve", idx),
                    type=EvidenceType.GROUNDED_RECOMMENDATION,
                    source=item.source,
                    category="preservation",
                    claim=f"PRESERVE: {item.claim}",
                    raw_data=item.raw_data,
                    confidence=item.confidence,
                )
            )

    # Services
    for item in evidence.verified_services:
        idx += 1
        evidence.preservation_requirements.append(
            CanonicalEvidenceItem(
                id=_make_id("preserve", idx),
                type=EvidenceType.GROUNDED_RECOMMENDATION,
                source=item.source,
                category="preservation",
                claim=f"PRESERVE: Verified service - {item.raw_data.get('name', 'Unknown')}",
                raw_data=item.raw_data,
                confidence=item.confidence,
            )
        )

    # Contact info
    for item in evidence.verified_contact_information:
        idx += 1
        evidence.preservation_requirements.append(
            CanonicalEvidenceItem(
                id=_make_id("preserve", idx),
                type=EvidenceType.GROUNDED_RECOMMENDATION,
                source=item.source,
                category="preservation",
                claim=f"PRESERVE: Contact info - {item.claim}",
                raw_data=item.raw_data,
                confidence=item.confidence,
            )
        )

    # Existing strengths
    for item in evidence.existing_strengths:
        idx += 1
        evidence.preservation_requirements.append(
            CanonicalEvidenceItem(
                id=_make_id("preserve", idx),
                type=EvidenceType.GROUNDED_RECOMMENDATION,
                source=item.source,
                category="preservation",
                claim=f"PRESERVE: {item.claim}",
                raw_data=item.raw_data,
                confidence=item.confidence,
            )
        )

    # === UNKNOWN INFORMATION ===
    # Track what's explicitly NOT in the source
    unknown_items = [
        ("phone", "Phone number not provided in source data"),
        ("email", "Email address not provided in source data"),
        ("booking_url", "Online booking URL not provided in source data"),
        ("opening_hours", "Opening hours not provided in source data"),
        (
            "certifications",
            "Certifications/memberships (KNMT, SBB) not explicitly verified in source",
        ),
        ("team_members", "Team member names/credentials not in source"),
        ("pricing", "Service pricing not in source"),
        ("reviews_count", "Review count not in source"),
        ("traffic_stats", "Traffic/ranking statistics not in source"),
        ("conversion_rate", "Conversion rate not in source"),
    ]

    for key, desc in unknown_items:
        idx += 1
        evidence.unknown_information.append(
            CanonicalEvidenceItem(
                id=_make_id("unknown", idx),
                type=EvidenceType.UNKNOWN,
                source=EvidenceSource.BOTH,
                category=key,
                claim=f"UNKNOWN - {desc}",
                raw_data={"category": key, "note": "Do not invent"},
                confidence=0.0,
            )
        )

    return evidence
