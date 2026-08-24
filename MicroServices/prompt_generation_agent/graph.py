from pathlib import Path

from config import settings
from extractors import (
    classify_prompt_type,
)
from langgraph.graph import END, StateGraph
from prompt_generator import (
    build_prompt_context,
    build_structured_output,
    generate_prompt_with_llm,
)
from report_discovery import (
    discover_business_report,
    discover_seo_report,
    select_best_match,
    validate_website_exists,
)
from state import PromptGenerationState
from utils import load_json_file, logger
from validator import PromptValidator, repair_prompt


def discover_reports_node(state: PromptGenerationState) -> PromptGenerationState:
    logger.info("=== Node: discover_reports ===")
    company_name = state["company_name"]
    normalized = "".join(c.lower() for c in company_name if c.isalnum())
    state["normalized_name"] = normalized

    seo_path, seo_candidates = discover_seo_report(company_name)
    if seo_candidates and len(seo_candidates) > 1:
        selected = select_best_match(seo_candidates, "SEO", company_name)
        if selected:
            seo_path = selected.filepath
    state["seo_report_path"] = seo_path

    biz_path, biz_candidates = discover_business_report(company_name)
    if biz_candidates and len(biz_candidates) > 1:
        selected = select_best_match(biz_candidates, "Business Analysis", company_name)
        if selected:
            biz_path = selected.filepath
    state["business_report_path"] = biz_path

    if seo_path:
        logger.info(f"Found SEO report: {seo_path}")
    else:
        state["errors"].append(f"SEO analysis report not found for {company_name}")

    if biz_path:
        logger.info(f"Found Business Analysis report: {biz_path}")
    else:
        state["errors"].append(f"Business Analysis report not found for {company_name}")

    return state


def validate_reports_node(state: PromptGenerationState) -> PromptGenerationState:
    logger.info("=== Node: validate_reports ===")

    if state["errors"]:
        return state

    from utils import load_json_file

    seo_data, seo_error = load_json_file(state["seo_report_path"])
    if seo_error:
        state["errors"].append(f"Invalid SEO report: {seo_error}")
    else:
        state["seo_data"] = seo_data

    biz_data, biz_error = load_json_file(state["business_report_path"])
    if biz_error:
        state["errors"].append(f"Invalid Business Analysis report: {biz_error}")
    else:
        state["business_data"] = biz_data

    if state["seo_data"]:
        website_exists = validate_website_exists(state["seo_data"])
        state["website_exists"] = website_exists
        if not website_exists:
            state["errors"].append(
                "This version supports existing websites only. SEO report indicates no website or crawl failed."
            )
        else:
            logger.info("Website exists validated")

    return state


def load_preprocessed_intelligence_node(
    state: PromptGenerationState,
) -> PromptGenerationState:
    """Load preprocessed intelligence files (much faster than extracting from raw reports)."""
    logger.info("=== Node: load_preprocessed_intelligence ===")

    if state["errors"]:
        return state

    normalized = state.get("normalized_name", "")
    if not normalized:
        normalized = "".join(c.lower() for c in state["company_name"] if c.isalnum())
        state["normalized_name"] = normalized

    intelligence_dir = Path(settings.output_dir) / "intelligence"
    seo_intel_path = intelligence_dir / f"{normalized}_seo_intelligence.json"
    biz_intel_path = intelligence_dir / f"{normalized}_business_intelligence.json"

    # Try to load preprocessed files
    if seo_intel_path.exists() and biz_intel_path.exists():
        logger.info("Loading preprocessed intelligence files...")
        seo_intel, seo_error = load_json_file(str(seo_intel_path))
        biz_intel, biz_error = load_json_file(str(biz_intel_path))

        if not seo_error and not biz_error:
            state["website_intelligence"] = seo_intel
            state["business_intelligence"] = biz_intel
            logger.info("Loaded preprocessed intelligence successfully")
            return state
        else:
            logger.warning("Preprocessed files invalid, will extract from raw reports")

    # Fallback: extract from raw reports
    logger.info("Preprocessed intelligence not found, extracting from raw reports...")

    if state.get("seo_data"):
        try:
            from extractors import extract_website_intelligence

            seo_intel = extract_website_intelligence(
                state["seo_data"], state["seo_report_path"]
            )
            state["website_intelligence"] = seo_intel.model_dump()
            logger.info(
                f"Extracted website intelligence: score={seo_intel.overall_score}"
            )
        except Exception as e:
            logger.error(f"Website intelligence extraction failed: {e}")
            state["errors"].append(f"Failed to extract website intelligence: {e}")

    if state.get("business_data"):
        try:
            from extractors import extract_business_intelligence

            biz_intel = extract_business_intelligence(
                state["business_data"], state["business_report_path"]
            )
            state["business_intelligence"] = biz_intel.model_dump()
            logger.info(
                f"Extracted business intelligence: {len(biz_intel.service_analysis.services)} services"
            )
        except Exception as e:
            logger.error(f"Business intelligence extraction failed: {e}")
            state["errors"].append(f"Failed to extract business intelligence: {e}")

    return state


def classify_prompt_type_node(state: PromptGenerationState) -> PromptGenerationState:
    logger.info("=== Node: classify_prompt_type ===")

    if state["errors"]:
        return state

    try:
        from models import BusinessIntelligence, WebsiteIntelligence

        seo = WebsiteIntelligence(**state["website_intelligence"])
        biz = BusinessIntelligence(**state["business_intelligence"])

        prompt_type = classify_prompt_type(seo, biz)
        state["prompt_type"] = prompt_type.value
        logger.info(f"Classified prompt type: {prompt_type.value}")
    except Exception as e:
        logger.error(f"Prompt type classification failed: {e}")
        state["errors"].append(f"Failed to classify prompt type: {e}")

    return state


def build_prompt_context_node(state: PromptGenerationState) -> PromptGenerationState:
    logger.info("=== Node: build_prompt_context ===")

    if state["errors"]:
        return state

    try:
        from models import BusinessIntelligence, PromptType, WebsiteIntelligence

        seo = WebsiteIntelligence(**state["website_intelligence"])
        biz = BusinessIntelligence(**state["business_intelligence"])
        prompt_type = PromptType(state["prompt_type"])

        context = build_prompt_context(seo, biz, prompt_type)
        state["prompt_context"] = context
        logger.info("Prompt context built successfully")
    except Exception as e:
        logger.error(f"Prompt context building failed: {e}")
        state["errors"].append(f"Failed to build prompt context: {e}")

    return state


def generate_prompt_node(state: PromptGenerationState) -> PromptGenerationState:
    logger.info("=== Node: generate_prompt ===")

    if state["errors"]:
        return state

    try:
        generated = generate_prompt_with_llm(state["prompt_context"])
        if not generated:
            state["errors"].append("LLM generation returned empty prompt")
        else:
            state["generated_prompt"] = generated

            from models import BusinessIntelligence, PromptType, WebsiteIntelligence

            seo = WebsiteIntelligence(**state["website_intelligence"])
            biz = BusinessIntelligence(**state["business_intelligence"])
            prompt_type = PromptType(state["prompt_type"])

            structured = build_structured_output(
                seo,
                biz,
                prompt_type,
                generated,
                state["prompt_context"],
                state["seo_report_path"],
                state["business_report_path"],
            )
            state["structured_output"] = structured.model_dump()
            logger.info("Prompt generated and structured output built")
    except Exception as e:
        logger.error(f"Prompt generation failed: {e}")
        state["errors"].append(f"Failed to generate prompt: {e}")

    return state


def validate_prompt_node(state: PromptGenerationState) -> PromptGenerationState:
    logger.info("=== Node: validate_prompt ===")

    if state["errors"] or not state.get("structured_output"):
        return state

    try:
        from models import StructuredOutput

        structured = StructuredOutput(**state["structured_output"])

        validator = PromptValidator()
        is_valid, errors, warnings = validator.validate(
            structured, state["prompt_context"]
        )

        state["validation_errors"] = errors
        state["validation_warnings"] = warnings

        if not is_valid and state.get("repair_attempts", 0) < 1:
            logger.warning("Validation failed, attempting repair...")
            repaired = repair_prompt(
                state["generated_prompt"],
                errors,
                warnings,
                state["prompt_context"],
            )
            if repaired and repaired != state["generated_prompt"]:
                state["generated_prompt"] = repaired
                state["repair_attempts"] = state.get("repair_attempts", 0) + 1

                structured = build_structured_output(
                    WebsiteIntelligence(**state["website_intelligence"]),
                    BusinessIntelligence(**state["business_intelligence"]),
                    PromptType(state["prompt_type"]),
                    repaired,
                    state["prompt_context"],
                    state["seo_report_path"],
                    state["business_report_path"],
                )
                state["structured_output"] = structured.model_dump()

                validator2 = PromptValidator()
                is_valid2, errors2, warnings2 = validator2.validate(
                    structured, state["prompt_context"]
                )
                state["validation_errors"] = errors2
                state["validation_warnings"] = warnings2

        logger.info(
            f"Validation complete: valid={is_valid}, errors={len(errors)}, warnings={len(warnings)}"
        )
    except Exception as e:
        logger.error(f"Prompt validation failed: {e}")
        state["errors"].append(f"Validation error: {e}")

    return state


def save_outputs_node(state: PromptGenerationState) -> PromptGenerationState:
    logger.info("=== Node: save_outputs ===")

    if state["errors"] or not state.get("structured_output"):
        return state

    try:
        import json
        from pathlib import Path

        from models import StructuredOutput

        structured = StructuredOutput(**state["structured_output"])
        output_dir = Path(settings.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        base_name = f"{state['normalized_name']}_website_prompt"

        json_path = output_dir / f"{base_name}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(structured.model_dump(), f, indent=2, ensure_ascii=False)
        logger.info(f"Saved JSON: {json_path}")

        md_path = output_dir / f"{base_name}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(structured.generated_prompt)
        logger.info(f"Saved Markdown: {md_path}")

        state["output_json_path"] = str(json_path)
        state["output_md_path"] = str(md_path)
    except Exception as e:
        logger.error(f"Output saving failed: {e}")
        state["errors"].append(f"Failed to save outputs: {e}")

    return state


def build_graph() -> StateGraph:
    workflow = StateGraph(PromptGenerationState)

    workflow.add_node("discover_reports", discover_reports_node)
    workflow.add_node("validate_reports", validate_reports_node)
    workflow.add_node("load_intelligence", load_preprocessed_intelligence_node)
    workflow.add_node("classify_prompt_type", classify_prompt_type_node)
    workflow.add_node("build_prompt_context", build_prompt_context_node)
    workflow.add_node("generate_prompt", generate_prompt_node)
    workflow.add_node("validate_prompt", validate_prompt_node)
    workflow.add_node("save_outputs", save_outputs_node)

    workflow.set_entry_point("discover_reports")
    workflow.add_edge("discover_reports", "validate_reports")
    workflow.add_edge("validate_reports", "load_intelligence")
    workflow.add_edge("load_intelligence", "classify_prompt_type")
    workflow.add_edge("classify_prompt_type", "build_prompt_context")
    workflow.add_edge("build_prompt_context", "generate_prompt")
    workflow.add_edge("generate_prompt", "validate_prompt")
    workflow.add_edge("validate_prompt", "save_outputs")
    workflow.add_edge("save_outputs", END)

    return workflow.compile()


graph = build_graph()
