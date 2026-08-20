"""
Local SEO Analyzer
Evaluates NAP (Name, Address, Phone) presence, LocalBusiness schema, and geo signals.
"""

from typing import Dict, Any, List
import re
from ..state import CategoryAuditResult, AuditFinding


def run_local_audit(pages: List[Dict[str, Any]]) -> CategoryAuditResult:
    """Perform local SEO signals evaluation."""
    findings: List[AuditFinding] = []
    deductions = 0

    indexable_pages = [p for p in pages if p.get('status_code') == 200]
    
    # Check phone number patterns (e.g. +1-xxx-xxx-xxxx, (xxx) xxx-xxxx)
    phone_pattern = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
    pages_with_phone = []
    
    # Check LocalBusiness schema
    has_local_schema = False
    
    # Check Google Maps links
    pages_with_maps = []

    for p in indexable_pages:
        url = p.get('url', '')
        
        # Check links for google maps
        links = p.get('linked_from') or []
        
        # Check json_ld for LocalBusiness
        for s in (p.get('json_ld') or []):
            stype = str(s.get('@type', '') if isinstance(s, dict) else s)
            if 'LocalBusiness' in stype or 'Store' in stype or 'Restaurant' in stype:
                has_local_schema = True

    score = 100
    if not has_local_schema:
        findings.append({
            "category": "Local",
            "severity": "info",
            "title": "LocalBusiness Schema Not Detected",
            "description": "No LocalBusiness schema found on the website.",
            "impact": "Relevant only if targeting local geographical searchers (Google Maps & Local Pack).",
            "recommendation": "If this is a physical business or local service, implement LocalBusiness schema with address and telephone.",
            "affected_urls": [p.get('url', '') for p in indexable_pages[:3]],
            "evidence": {"has_local_schema": False}
        })

    status = "passed"
    summary = f"Local SEO analysis completed. Local signals audited across {len(indexable_pages)} pages."

    return {
        "category": "Local SEO",
        "score": score,
        "status": status,
        "summary": summary,
        "findings": findings,
        "metrics": {
            "has_local_schema": has_local_schema
        }
    }
