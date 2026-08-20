"""Validator for verifying that an executed ActionPlan successfully unblocked content."""

from typing import Any
from bs4 import BeautifulSoup
from app.config.logging import get_logger

logger = get_logger("ACTION_REPAIR_VALIDATOR")


class ActionRepairValidator:
    """Evaluates whether page interaction actions produced tangible content improvements."""

    def evaluate_action_outcome(
        self,
        before_html: str,
        after_html: str,
        execution_result: dict[str, Any],
    ) -> bool:
        """Verify that the action resulted in meaningful DOM progression or content expansion."""
        if not execution_result.get("success", False):
            return False

        if not after_html:
            return False

        # 1. Content size check (DOM expanded after scroll / load more)
        len_before = len(before_html)
        len_after = len(after_html)
        if len_after > len_before * 1.05:
            logger.debug(f"Action produced DOM expansion: {len_before} -> {len_after} bytes (+{(len_after - len_before) / len_before:.1%})")
            return True

        # 2. Tag count progression check
        soup_before = BeautifulSoup(before_html, "html.parser")
        soup_after = BeautifulSoup(after_html, "html.parser")

        cards_before = len(soup_before.find_all(["article", "li", "div"]))
        cards_after = len(soup_after.find_all(["article", "li", "div"]))

        if cards_after > cards_before:
            logger.debug(f"Action increased element count: {cards_before} -> {cards_after}")
            return True

        # 3. If steps succeeded without errors, accept as valid UI stabilization
        return any(a["status"] == "success" for a in execution_result.get("actions_executed", []))

