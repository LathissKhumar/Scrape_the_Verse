import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from graph import graph
from state import PromptGenerationState
from utils import setup_logging


def print_header():
    print("=" * 50)
    print("PROMPT GENERATION AGENT")
    print("=" * 50)
    print()
    print("This version supports existing websites only.")
    print()


def print_completion(state: PromptGenerationState):
    print()
    print("=" * 50)
    print("COMPLETE")
    print("=" * 50)
    print()
    print(f"Company: {state.get('company_name', 'N/A')}")
    print(f"Prompt Type: {state.get('prompt_type', 'N/A')}")
    print(
        f"SEO Report: {Path(state.get('seo_report_path', '')).name if state.get('seo_report_path') else 'NOT FOUND'}"
    )
    print(
        f"Business Analysis: {Path(state.get('business_report_path', '')).name if state.get('business_report_path') else 'NOT FOUND'}"
    )
    print()
    if state.get("generated_prompt"):
        print("Generated Prompt:")
        print("-" * 40)
        print(
            state["generated_prompt"][:500] + "..."
            if len(state["generated_prompt"]) > 500
            else state["generated_prompt"]
        )
        print("-" * 40)
    print()
    if state.get("output_json_path"):
        print(f"Output JSON: {state['output_json_path']}")
    if state.get("output_md_path"):
        print(f"Output Markdown: {state['output_md_path']}")
    print()

    if state.get("warnings"):
        print("Warnings:")
        for w in state["warnings"]:
            print(f"  - {w}")
        print()

    if state.get("errors"):
        print("Errors:")
        for e in state["errors"]:
            print(f"  - {e}")
        print()


def main():
    setup_logging(settings.log_level)

    print_header()

    company_name = input("Enter company name:\n> ").strip()

    if not company_name:
        print("No company name provided. Exiting.")
        return

    print()
    print(f"Processing: {company_name}")
    print()

    initial_state: PromptGenerationState = {
        "company_name": company_name,
        "normalized_name": "",
        "seo_report_path": None,
        "business_report_path": None,
        "seo_data": {},
        "business_data": {},
        "website_intelligence": {},
        "business_intelligence": {},
        "website_exists": False,
        "prompt_type": None,
        "prompt_context": {},
        "generated_prompt": None,
        "structured_output": None,
        "validation_errors": [],
        "validation_warnings": [],
        "errors": [],
        "warnings": [],
        "repair_attempts": 0,
    }

    try:
        result = graph.invoke(initial_state)
        print_completion(result)

        if result.get("errors"):
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
