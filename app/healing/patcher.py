from typing import Any, Optional
from app.config.logging import get_logger
from app.extraction.schema import ExtractionSchema, ExtractionStrategyEnum, FieldRule
from app.healing.schemas import RepairPlan, RepairType

logger = get_logger("HEALING_PATCHER")


class RepairPatcher:
    """Applies minimal, non-destructive patches to ExtractionSchema configurations."""

    @staticmethod
    def apply_patch(schema: ExtractionSchema, plan: RepairPlan) -> ExtractionSchema:
        """Derive a new patched ExtractionSchema based on the proposed RepairPlan."""
        logger.info(f"Applying patch for repair_id={plan.repair_id} ({plan.repair_type.value})")

        # Deep copy or reconstruct fields
        new_fields = [FieldRule(**f.model_dump()) for f in schema.fields]
        new_strategy = schema.strategy
        new_base_selector = schema.base_selector
        new_strict_schema = schema.strict_schema

        patch_data = plan.patch or {}

        # 1. Strategy change
        if "strategy" in patch_data:
            try:
                new_strategy = ExtractionStrategyEnum(patch_data["strategy"])
            except (ValueError, KeyError):
                logger.warning(f"Unknown strategy in patch: {patch_data['strategy']}")
        elif plan.repair_type == RepairType.SWITCH_EXTRACTION_STRATEGY:
            proposed_strategy = plan.proposed_configuration.get("strategy")
            if proposed_strategy:
                new_strategy = ExtractionStrategyEnum(proposed_strategy)

        # 2. Base selector update
        if "base_selector" in patch_data:
            new_base_selector = patch_data["base_selector"]
        elif "base_selector" in plan.proposed_configuration:
            new_base_selector = plan.proposed_configuration["base_selector"]

        # 3. Strict schema update
        if "strict_schema" in patch_data:
            new_strict_schema = bool(patch_data["strict_schema"])

        # 4. Field rules update
        patched_fields_data = patch_data.get("fields") or plan.proposed_configuration.get("fields")
        if patched_fields_data and isinstance(patched_fields_data, list):
            fields_by_name = {f.name: f for f in new_fields}
            for field_update in patched_fields_data:
                if not isinstance(field_update, dict):
                    continue
                name = field_update.get("name")
                if not name:
                    continue

                if name in fields_by_name:
                    existing_rule = fields_by_name[name]
                    # Update existing field rule properties
                    for key, val in field_update.items():
                        if hasattr(existing_rule, key) and val is not None:
                            setattr(existing_rule, key, val)
                else:
                    # New field rule added
                    new_rule = FieldRule(**field_update)
                    new_fields.append(new_rule)
                    fields_by_name[name] = new_rule

        # 5. Direct field mapping in proposed_configuration (e.g. {"title": "h2", "price": ".price"})
        for field_name in plan.affected_fields:
            if field_name in plan.proposed_configuration and isinstance(plan.proposed_configuration[field_name], str):
                target_val = plan.proposed_configuration[field_name]
                for f in new_fields:
                    if f.name == field_name:
                        if plan.repair_type in (RepairType.REPAIR_CSS_SELECTORS, RepairType.REPAIR_XPATH_SELECTORS):
                            f.selector = target_val
                        elif plan.repair_type == RepairType.REPAIR_REGEX_PATTERN:
                            f.regex_pattern = target_val

        return ExtractionSchema(
            strategy=new_strategy,
            base_selector=new_base_selector,
            fields=new_fields,
            strict_schema=new_strict_schema,
        )
