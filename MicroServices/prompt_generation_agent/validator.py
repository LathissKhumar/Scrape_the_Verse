import re
from typing import Any

from models import StructuredOutput
from utils import logger


class PromptValidator:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate(
        self, output: StructuredOutput, context: dict[str, Any]
    ) -> tuple[bool, list[str], list[str]]:
        self.errors = []
        self.warnings = []

        self._check_company_name(output)
        self._check_website(output)
        self._check_prompt_type(output)
        self._check_existing_website_acknowledged(output)
        self._check_business_context(output)
        self._check_seo_issues_represented(output, context)
        self._check_business_problems_represented(output)
        self._check_opportunities_represented(output)
        self._check_page_recommendations_grounded(output, context)
        self._check_no_unsupported_claims(output)
        self._check_no_build_from_scratch(output)
        self._check_preservation_rules(output)
        self._check_success_criteria(output)
        self._check_prompt_not_empty(output)
        self._check_prompt_sufficiently_detailed(output)
        self._check_exact_25_sections(output)

        is_valid = len(self.errors) == 0
        logger.info(
            f"Validation result: {'PASS' if is_valid else 'FAIL'} - Errors: {len(self.errors)}, Warnings: {len(self.warnings)}"
        )
        return is_valid, self.errors, self.warnings

    def _check_company_name(self, output: StructuredOutput):
        if not output.company_name or not output.company_name.strip():
            self.errors.append("Company name is missing or empty")

    def _check_website(self, output: StructuredOutput):
        if not output.website or not output.website.strip():
            self.errors.append("Website URL is missing or empty")
        elif not output.website.startswith("http"):
            self.warnings.append("Website URL may not be valid (missing protocol)")

    def _check_prompt_type(self, output: StructuredOutput):
        valid_types = [
            "WEBSITE_REDESIGN",
            "SEO_OPTIMIZATION",
            "UX_CONVERSION_OPTIMIZATION",
            "COMBINED_WEBSITE_OPTIMIZATION",
        ]
        if not output.prompt_type or output.prompt_type not in valid_types:
            self.errors.append(f"Invalid or missing prompt type: {output.prompt_type}")

    def _check_existing_website_acknowledged(self, output: StructuredOutput):
        prompt = output.generated_prompt.lower()
        if (
            "existing website" not in prompt
            and "current website" not in prompt
            and "existing site" not in prompt
        ):
            self.warnings.append(
                "Prompt may not explicitly acknowledge this is an existing website"
            )

        if (
            "build from scratch" in prompt
            or "create a new website" in prompt
            or "new website from scratch" in prompt
        ):
            self.warnings.append(
                "Prompt contains 'build from scratch' language - not appropriate for existing website"
            )

    def _check_business_context(self, output: StructuredOutput):
        prompt = output.generated_prompt
        if not output.business_summary.get("company_name"):
            self.errors.append("Business context missing company name")
        if not output.business_summary.get("primary_services"):
            self.warnings.append("Business context missing primary services")

    def _check_seo_issues_represented(
        self, output: StructuredOutput, context: dict[str, Any]
    ):
        prompt = output.generated_prompt.lower()
        seo_issues = context.get("top_seo_issues", [])

        if not seo_issues:
            self.warnings.append("No SEO issues in context to validate against")
            return

        represented = 0
        for issue in seo_issues[:10]:
            issue_type = issue.get("type", "").lower()
            if issue_type in prompt or issue.get("title", "").lower()[:30] in prompt:
                represented += 1

        if represented < min(3, len(seo_issues)):
            self.warnings.append(
                f"Only {represented}/{min(10, len(seo_issues))} top SEO issues appear represented in prompt"
            )

    def _check_business_problems_represented(self, output: StructuredOutput):
        prompt = output.generated_prompt.lower()
        if not output.identified_problems:
            self.warnings.append("No business problems to validate against")
            return

        business_problems = [
            p for p in output.identified_problems if p.get("source") == "Business"
        ]
        if not business_problems:
            self.warnings.append("No business-sourced problems found")
            return

        represented = 0
        for prob in business_problems[:5]:
            title = prob.get("title", "").lower()
            problem = prob.get("problem", "").lower()
            if title[:30] in prompt or problem[:50] in prompt:
                represented += 1

        if represented == 0:
            self.warnings.append(
                "No business problems appear to be represented in the prompt"
            )
        elif represented < len(business_problems):
            self.warnings.append(
                f"Only {represented}/{len(business_problems)} business problems represented"
            )

    def _check_opportunities_represented(self, output: StructuredOutput):
        prompt = output.generated_prompt.lower()
        if not output.business_opportunities:
            self.warnings.append("No business opportunities to validate against")
            return

        represented = 0
        for opp in output.business_opportunities[:5]:
            opp_text = opp.get("opportunity", "").lower()
            if opp_text[:40] in prompt:
                represented += 1

        if represented == 0:
            self.warnings.append(
                "No business opportunities appear to be represented in the prompt"
            )
        elif represented < len(output.business_opportunities):
            self.warnings.append(
                f"Only {represented}/{len(output.business_opportunities)} opportunities represented"
            )

    def _check_page_recommendations_grounded(
        self, output: StructuredOutput, context: dict[str, Any]
    ):
        prompt = output.generated_prompt
        important_pages = context.get("important_pages", [])
        service_pages = context.get("service_pages", [])

        all_known_urls = [p["url"] for p in important_pages] + [
            p["url"] for p in service_pages
        ]

        mentioned_urls = 0
        for url in all_known_urls[:15]:
            if url in prompt:
                mentioned_urls += 1

        if len(all_known_urls) > 0 and mentioned_urls == 0:
            self.warnings.append(
                "No specific page URLs from analysis appear in prompt - recommendations may not be page-grounded"
            )

    def _check_no_unsupported_claims(self, output: StructuredOutput):
        prompt = output.generated_prompt.lower()

        forbidden_patterns = [
            (r"\b\d+% traffic increase\b", "specific traffic increase percentage"),
            (r"\brank #?1\b", "guaranteed #1 ranking"),
            (r"\b\d+x revenue\b", "revenue multiplier claim"),
            (r"\b\d+ customers\b", "specific customer count"),
            (r"\b\d+ reviews\b", "specific review count"),
            (r"guaranteed top", "guaranteed ranking"),
            (r"instant ranking", "instant results claim"),
        ]

        for pattern, description in forbidden_patterns:
            if re.search(pattern, prompt):
                self.warnings.append(
                    f"Prompt may contain unsupported claim: {description}"
                )

    def _check_no_build_from_scratch(self, output: StructuredOutput):
        prompt = output.generated_prompt.lower()
        forbidden = [
            "build from scratch",
            "create a new website",
            "new website from scratch",
            "completely new website",
            "start from zero",
            "brand new website",
        ]

        for phrase in forbidden:
            if phrase in prompt:
                self.warnings.append(
                    f"Prompt contains forbidden phrase for existing website: '{phrase}'"
                )

    def _check_preservation_rules(self, output: StructuredOutput):
        if not output.preservation_rules or len(output.preservation_rules) < 3:
            self.warnings.append(
                "Preservation rules missing or insufficient (need at least 3)"
            )

        required_preservations = ["company name", "location", "contact", "service"]
        found = 0
        for rule in output.preservation_rules:
            rule_lower = rule.lower()
            for req in required_preservations:
                if req in rule_lower:
                    found += 1
                    break

        if found < 3:
            self.warnings.append(
                "Preservation rules may not cover all required elements (company, location, contact, services)"
            )

    def _check_success_criteria(self, output: StructuredOutput):
        if not output.success_criteria or len(output.success_criteria) < 3:
            self.warnings.append(
                "Success criteria missing or insufficient (need at least 3 measurable criteria)"
            )

        has_measurable = False
        for criterion in output.success_criteria:
            if any(
                word in criterion.lower()
                for word in [
                    "%",
                    "percent",
                    "increase",
                    "improve",
                    "achieve",
                    "rank",
                    "score",
                    "rate",
                    "traffic",
                    "conversion",
                    "vitals",
                    "speed",
                ]
            ):
                has_measurable = True
                break

        if not has_measurable:
            self.warnings.append("Success criteria may not be sufficiently measurable")

    def _check_prompt_not_empty(self, output: StructuredOutput):
        if not output.generated_prompt or len(output.generated_prompt.strip()) < 100:
            self.warnings.append("Generated prompt is empty or too short")

    def _check_prompt_sufficiently_detailed(self, output: StructuredOutput):
        prompt = output.generated_prompt
        if len(prompt) < 2000:
            self.warnings.append(
                f"Prompt may be too brief ({len(prompt)} chars) - consider more detail"
            )

    def _check_exact_25_sections(self, output: StructuredOutput):
        """Validate exactly 25 sections in correct order with no extras."""
        prompt = output.generated_prompt
        if not prompt:
            self.errors.append("Generated prompt is empty")
            return

        required_sections = [
            "ROLE",
            "WEBSITE PURPOSE",
            "BUSINESS CONTEXT",
            "TARGET AUDIENCE",
            "WEBSITE GOALS",
            "BRAND DIRECTION",
            "SITE ARCHITECTURE",
            "NAVIGATION",
            "HOMEPAGE",
            "ABOUT PAGE",
            "SERVICE PAGES",
            "CONTACT PAGE",
            "UI DESIGN",
            "UX DESIGN",
            "CONTENT REQUIREMENTS",
            "SEO IMPLEMENTATION",
            "LOCAL SEO",
            "CONVERSION FLOW",
            "MOBILE EXPERIENCE",
            "TRUST ELEMENTS",
            "PRESERVATION RULES",
            "DO NOT INVENT",
            "SUCCESS CRITERIA",
            "FINAL IMPLEMENTATION INSTRUCTION",
        ]

        # Find all section headers in the prompt (lines that match exactly)
        lines = prompt.split("\n")
        found_sections = []
        for line in lines:
            line_stripped = line.strip()
            if line_stripped in required_sections:
                found_sections.append(line_stripped)

        # Check count
        if len(found_sections) != 25:
            self.errors.append(
                f"Prompt has {len(found_sections)} sections, expected exactly 25. Found: {found_sections}"
            )
            return

        # Check order
        for i, expected in enumerate(required_sections):
            if i < len(found_sections) and found_sections[i] != expected:
                self.errors.append(
                    f"Section {i + 1} should be '{expected}', found '{found_sections[i]}'"
                )
                return

        # Check first section is ROLE
        if not prompt.lstrip().startswith("ROLE"):
            self.errors.append("Prompt must start immediately with 'ROLE'")

        # Check last section is FINAL IMPLEMENTATION INSTRUCTION
        if "FINAL IMPLEMENTATION INSTRUCTION" not in found_sections[-1:]:
            self.errors.append(
                "Prompt must end with 'FINAL IMPLEMENTATION INSTRUCTION'"
            )

        # Check for forbidden reasoning patterns
        forbidden_patterns = [
            ("we are given", "reasoning about generation process"),
            ("steps:", "planning steps"),
            ("let's", "planning language"),
            ("we must", "meta-commentary"),
            ("we need to", "meta-commentary"),
            ("now, we", "generation process commentary"),
            ("let us", "planning language"),
            ("first,", "reasoning steps"),
            ("second,", "reasoning steps"),
            ("third,", "reasoning steps"),
            ("map the sections", "planning language"),
            ("section by section", "planning language"),
            ("output requirements", "meta-commentary"),
            ("generate the 25 sections", "meta-commentary"),
            ("the 25 sections", "meta-commentary"),
        ]

        prompt_lower = prompt.lower()
        for pattern, description in forbidden_patterns:
            if pattern in prompt_lower:
                self.errors.append(
                    f"Prompt contains forbidden reasoning pattern: '{pattern}' ({description})"
                )

        # Check for invented numerical targets
        import re

        invented_targets = [
            (
                r"\b\d+%\s*(traffic|conversion|increase|improvement)\b",
                "invented percentage target",
            ),
            (r"\btop\s*[1-3]\b", "invented ranking target"),
            (r"\brank\s*#?\d+\b", "invented ranking target"),
            (r"\bpage[s]?peed\s*[89]\d\b", "invented pagespeed target"),
            (r"\bseo\s*score\s*[89]\d\b", "invented SEO score target"),
            (r"\bcore\s*web\s*vitals.*\d+\.?\d*\s*s\b", "invented CWV target"),
            (r"\bincrease.*\d+%\b", "invented increase target"),
            (r"\b\d+x\s*(revenue|conversion|traffic)\b", "invented multiplier target"),
        ]

        for pattern, description in invented_targets:
            if re.search(pattern, prompt_lower):
                self.errors.append(
                    f"Prompt contains invented numerical target: {description}"
                )

        # Check for unsupported certifications/trust signals
        unsupported_trust = [
            (r"\bknmt\b", "KNMT certification not verified in source"),
            (r"\bsbb\b", "SBB membership not verified in source"),
            (r"\bcertif(ied|ication)\b", "certification not verified in source"),
            (r"\bmembers?hip\b", "membership not verified in source"),
            (r"\baward\b", "award not verified in source"),
            (r"\bbadge\b", "badge not verified in source"),
            (r"\btestimonial\b", "testimonial not verified in source"),
            (r"\breview\b", "review count not verified in source"),
        ]

        for pattern, description in unsupported_trust:
            if re.search(pattern, prompt_lower):
                self.warnings.append(
                    f"Prompt may reference unsupported trust signal: {description}"
                )

        # Check for "build from scratch" language
        build_from_scratch = [
            "build from scratch",
            "create a new website",
            "new website from scratch",
            "completely new website",
            "start from zero",
            "brand new website",
            "from the ground up",
        ]

        for phrase in build_from_scratch:
            if phrase in prompt_lower:
                self.errors.append(
                    f"Prompt contains forbidden 'build from scratch' language: '{phrase}'"
                )

        # Check for traffic/ranking claims
        traffic_claims = [
            (r"\bhigh.?traffic\b", "unverified high traffic claim"),
            (
                r"\bprimary.?conversion.?landing\b",
                "unverified primary conversion claim",
            ),
            (r"\bmain.?conversion\b", "unverified conversion claim"),
        ]

        for pattern, description in traffic_claims:
            if re.search(pattern, prompt_lower):
                self.warnings.append(
                    f"Prompt may contain unverified traffic/conversion claim: {description}"
                )


from config import settings
from prompts import REPAIR_SYSTEM_PROMPT, build_repair_prompt


def repair_prompt(
    original_prompt: str,
    errors: list[str],
    warnings: list[str],
    context: dict[str, Any],
) -> str:
    logger.info("Attempting prompt repair")

    try:
        import httpx
    except ImportError:
        return original_prompt

    user_prompt = build_repair_prompt(original_prompt, errors, warnings, context)

    messages = [
        {"role": "system", "content": REPAIR_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{settings.ollama_base_url}/api/chat",
                json={
                    "model": settings.ollama_model,
                    "messages": messages,
                    "stream": False,
                    "options": {"temperature": 0.1, "num_predict": 1000},
                },
            )
            response.raise_for_status()
            result = response.json()
            msg = result.get("message", {})
            generated = msg.get("content", "").strip()
            if not generated:
                generated = msg.get("thinking", "").strip()
            return generated if generated else original_prompt
    except Exception as e:
        logger.error(f"Repair failed: {e}")
        return original_prompt
