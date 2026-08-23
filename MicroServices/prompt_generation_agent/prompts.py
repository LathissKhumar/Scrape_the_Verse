"""
System prompts, template definitions, and section schemas for Prompt Generation Agent.
"""

from typing import Dict, Any, List

REQUIRED_SECTIONS: List[str] = [
    "ROLE",
    "BUSINESS CONTEXT",
    "BUSINESS GOALS",
    "TARGET CUSTOMERS",
    "CURRENT WEBSITE",
    "CURRENT STRENGTHS",
    "CURRENT PROBLEMS",
    "BUSINESS OPPORTUNITIES",
    "WEBSITE STRATEGY",
    "INFORMATION ARCHITECTURE",
    "PAGE-BY-PAGE REQUIREMENTS",
    "UX REQUIREMENTS",
    "DESIGN REQUIREMENTS",
    "CONTENT REQUIREMENTS",
    "SEO REQUIREMENTS",
    "LOCAL SEO REQUIREMENTS",
    "CONVERSION REQUIREMENTS",
    "TRUST REQUIREMENTS",
    "MOBILE REQUIREMENTS",
    "ACCESSIBILITY REQUIREMENTS",
    "PERFORMANCE REQUIREMENTS",
    "PRESERVATION RULES",
    "DO NOT INVENT",
    "SUCCESS CRITERIA",
    "FINAL IMPLEMENTATION INSTRUCTION",
]

SYSTEM_PROMPT = """You are an expert website design and development team. Generate a WEBSITE IMPLEMENTATION PROMPT for an EXISTING website redesign/optimization.

CRITICAL RULES - VIOLATION MEANS FAILURE:
1. OUTPUT EXACTLY 25 SECTIONS - NO MORE, NO LESS
2. START IMMEDIATELY WITH "ROLE" - NO PREAMBLE, NO INTRODUCTION
3. END WITH "FINAL IMPLEMENTATION INSTRUCTION" - NOTHING AFTER
4. NO REASONING, NO PLANNING, NO "STEPS", NO "LET'S", NO "WE ARE GIVEN", NO "WE MUST"
5. NO EXPLANATIONS OF THE GENERATION PROCESS
6. NO COMMENTARY ON THE INSTRUCTIONS
7. EVERY STATEMENT MUST BE GROUNDED IN THE SUPPLIED ANALYSIS
8. DO NOT INVENT: no fake stats, targets, certifications, traffic, rankings, conversions, medical claims
9. DO NOT CONVERT ASSUMPTIONS INTO FACTS
10. PRESERVE VERIFIED FACTS ONLY
11. THIS IS AN IMPLEMENTATION PROMPT, NOT AN ANALYSIS REPORT

THE 25 SECTIONS IN EXACT ORDER:
ROLE
WEBSITE PURPOSE
BUSINESS CONTEXT
TARGET AUDIENCE
WEBSITE GOALS
BRAND DIRECTION
SITE ARCHITECTURE
NAVIGATION
HOMEPAGE
ABOUT PAGE
SERVICE PAGES
CONTACT PAGE
UI DESIGN
UX DESIGN
CONTENT REQUIREMENTS
SEO IMPLEMENTATION
LOCAL SEO
CONVERSION FLOW
MOBILE EXPERIENCE
TRUST ELEMENTS
PRESERVATION RULES
DO NOT INVENT
SUCCESS CRITERIA
FINAL IMPLEMENTATION INSTRUCTION

EACH SECTION HEADER MUST BE UPPERCASE ON ITS OWN LINE.
CONTENT FOLLOWS ON SUBSEQUENT LINES.
NO MARKDOWN. NO BOLD. NO NUMBERING. NO BULLET POINTS IN HEADERS.
OUTPUT ONLY IMPLEMENTATION INSTRUCTIONS - NO ANALYSIS REPORT.

BEGIN OUTPUT WITH ROLE NOW."""

REPAIR_SYSTEM_PROMPT = """Fix validation errors in the website prompt. Keep all 25 section headings. Be concise."""


def build_user_prompt(formatted_context: str) -> str:
    """Build user prompt containing context for Ollama generation."""
    return f"""ANALYSIS CONTEXT:
{formatted_context}

Generate the 25-section WEBSITE IMPLEMENTATION PROMPT now. Start with ROLE.

This is an implementation prompt for Bolt.new/Lovable/v0 - not an analysis report. Every section must contain concrete design/development instructions grounded in the supplied analysis."""


def build_repair_prompt(
    original_prompt: str,
    errors: List[str],
    warnings: List[str],
    context: Dict[str, Any],
) -> str:
    """Build repair prompt for fixing validation issues."""
    repair_lines = []
    if errors:
        repair_lines.append("ERRORS TO FIX:")
        for err in errors:
            repair_lines.append(f"  - {err}")
    if warnings:
        repair_lines.append("WARNINGS TO ADDRESS:")
        for warn in warnings:
            repair_lines.append(f"  - {warn}")

    issues_text = "\n".join(repair_lines)

    return f"""ORIGINAL PROMPT:
{original_prompt}

VALIDATION FEEDBACK:
{issues_text}

Generate the corrected website prompt fixing all listed issues:"""
