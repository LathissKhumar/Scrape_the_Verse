from leadfinder.diagnosis.evidence import DiagnosisEvidenceBuilder
from leadfinder.models.schemas import ScrapingTask
from leadfinder.validation.schemas import FieldMetric, ValidationResult


def test_diagnosis_evidence_builder():
    builder = DiagnosisEvidenceBuilder()
    task = ScrapingTask(
        task_id="t_diag_1",
        objective="Scrape product cards",
        target_urls=["https://example.com/shop"],
        fields=["name", "price"],
    )
    val_result = ValidationResult(
        status="degraded",
        health_score=0.55,
        quality_score=0.60,
        record_count=10,
        expected_record_count=100,
        field_metrics={
            "name": FieldMetric(coverage=0.90, valid_count=9),
            "price": FieldMetric(coverage=0.20, valid_count=2, placeholder_count=3),
        },
    )
    raw_html = """
    <html>
        <body>
            <div class="shop-grid">
                <article class="card">
                    <h2 class="title">Product 1</h2>
                    <span class="val">$10</span>
                </article>
            </div>
        </body>
    </html>
    """
    extracted_records = [{"name": "Product 1", "price": None}]

    evidence = builder.build_evidence(
        task=task,
        validation_result=val_result,
        raw_results=raw_html,
        extracted_results=extracted_records,
    )

    assert evidence["task_id"] == "t_diag_1"
    assert "price" in evidence["affected_fields"]
    assert evidence["raw_content_available"] is True
    assert len(evidence["relevant_snippets"]) > 0
    assert len(evidence["sample_extracted_records"]) == 1
