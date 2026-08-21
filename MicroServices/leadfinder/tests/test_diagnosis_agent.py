import json
import pytest
from app.agents.diagnosis import DiagnosisAgent
from app.diagnosis.schemas import RepairStrategy, RootCause
from app.models.schemas import ScrapingTask
from app.validation.schemas import FieldMetric, ValidationResult
from app.tests.conftest import MockLLMClient


@pytest.mark.asyncio
async def test_diagnosis_agent_llm_selector_drift():
    mock_llm_response = json.dumps({
        "diagnosis_status": "diagnosed",
        "root_cause": "SELECTOR_DRIFT",
        "confidence": 0.92,
        "failure_category": "EXTRACTION_DEGRADATION",
        "affected_stage": "css_extraction",
        "affected_fields": ["price"],
        "evidence": ["Class name changed from .price to .current-price in card container"],
        "repair_strategy": "REPAIR_CSS_SELECTORS",
        "repair_targets": ["price"],
        "recommended_action": "REPAIR_EXTRACTION_SCHEMA",
    })

    mock_llm = MockLLMClient(response_text=mock_llm_response)
    agent = DiagnosisAgent(llm_client=mock_llm)

    task = ScrapingTask(
        task_id="t_diag_agent",
        objective="Scrape prices",
        target_urls=["https://example.com/items"],
        fields=["name", "price"],
    )
    val_result = ValidationResult(
        status="degraded",
        health_score=0.62,
        quality_score=0.65,
        record_count=20,
        field_metrics={
            "name": FieldMetric(coverage=1.0),
            "price": FieldMetric(coverage=0.15),
        },
    )

    diag = await agent.diagnose(
        task=task,
        validation_result=val_result,
        raw_results="<div class='item'><h2>Name</h2><span class='current-price'>$10</span></div>",
    )

    assert diag.root_cause == RootCause.SELECTOR_DRIFT
    assert diag.confidence == 0.92
    assert diag.repair_strategy == RepairStrategy.REPAIR_CSS_SELECTORS
    assert diag.affected_fields == ["price"]
