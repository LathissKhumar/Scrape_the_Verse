"""Safely executes and applies structured candidate repair plans without arbitrary code injection."""

from typing import Any, Optional
from leadfinder.config.logging import get_logger
from leadfinder.extraction.schema import ExtractionSchema
from leadfinder.healing.patcher import RepairPatcher
from leadfinder.healing.schemas import RepairPlan

logger = get_logger("REPAIR_EXECUTOR")


class RepairExecutor:
    """Safely executes and applies structured candidate repair plans without arbitrary code injection."""

    def __init__(self) -> None:
        self.patcher = RepairPatcher()

    def apply_candidate(
        self,
        plan: RepairPlan,
        schema: ExtractionSchema,
        scraper_config: Optional[dict[str, Any]] = None,
    ) -> tuple[ExtractionSchema, dict[str, Any]]:
        """Apply a validated candidate RepairPlan to produce an updated ExtractionSchema and scraper config."""
        logger.debug(
            f"Executing repair plan {plan.repair_id} (level={plan.level}, type={plan.repair_type.value})"
        )
        updated_config = dict(scraper_config or {})

        # Level 1: Extraction-level repair
        if plan.level == 1 or plan.target_component == "extraction":
            new_schema = self.patcher.apply_patch(schema=schema, plan=plan)
            return new_schema, updated_config

        # Level 2: Scraper-level configuration repair
        if plan.level == 2 or plan.target_component == "scraper":
            patch_data = plan.patch or plan.proposed_configuration
            if isinstance(patch_data, dict):
                for key, value in patch_data.items():
                    if isinstance(value, dict) and key in updated_config and isinstance(updated_config[key], dict):
                        updated_config[key].update(value)
                    else:
                        updated_config[key] = value
            return schema, updated_config

        # Level 3: Collector refactor fallback
        if plan.level == 3 or plan.target_component == "collector":
            candidate_col_id = plan.proposed_configuration.get("collector_id") or plan.patch.get("collector_id")
            if candidate_col_id:
                updated_config["candidate_collector_id"] = candidate_col_id
            return schema, updated_config

        # Default fallback
        return schema, updated_config

