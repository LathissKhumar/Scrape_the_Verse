import os
import tempfile
import pytest
from app.healing.observability import RepairObservability, RepairSessionTelemetry

def test_repair_telemetry_load_persisted_sessions():
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".jsonl") as tmp:
        tmp_path = tmp.name

    try:
        obs = RepairObservability(log_path=tmp_path)
        s1 = RepairSessionTelemetry(
            task_id="t1",
            domain="store.example.com",
            root_cause="SELECTOR_DRIFT",
            initial_health=0.2,
            final_health=0.9,
            improvement=0.7,
            accepted=True,
            persisted=True,
            confidence_level="high",
            duration_ms=450.0,
        )
        s2 = RepairSessionTelemetry(
            task_id="t2",
            domain="blog.example.com",
            root_cause="BOT_BLOCK",
            initial_health=0.1,
            final_health=0.1,
            improvement=0.0,
            accepted=False,
            persisted=False,
            confidence_level="low",
            rejection_reason="Bot challenge unresolved",
            duration_ms=800.0,
        )
        obs.record_session(s1)
        obs.record_session(s2)

        # Create a fresh observability instance pointing to same file
        obs2 = RepairObservability(log_path=tmp_path)
        persisted = obs2.load_all_persisted_sessions()
        assert len(persisted) == 2
        assert persisted[0].domain == "store.example.com"
        assert persisted[0].accepted is True
        assert persisted[1].domain == "blog.example.com"
        assert persisted[1].accepted is False

        # Verify comprehensive metrics
        metrics = obs2.get_comprehensive_metrics()
        assert metrics["total_sessions"] == 2
        assert metrics["accepted_count"] == 1
        assert metrics["success_rate"] == 0.5
        assert "SELECTOR_DRIFT" in metrics["root_causes"]
        assert metrics["domain_stats"]["store.example.com"]["accepted"] == 1

        # Verify Markdown dashboard generation
        md_dash = obs2.generate_dashboard_markdown()
        assert "# Self-Healing Scraping Telemetry Dashboard" in md_dash
        assert "store.example.com" in md_dash
        assert "SELECTOR_DRIFT" in md_dash

        # Verify HTML dashboard generation
        html_dash = obs2.generate_dashboard_html()
        assert "<!DOCTYPE html>" in html_dash
        assert "Self-Healing Scraping Telemetry Dashboard" in html_dash
        assert "store.example.com" in html_dash
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
