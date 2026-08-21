from leadfinder.healing.observability import RepairObservability, RepairSessionTelemetry


def test_repair_observability_recording_and_summary(tmp_path):
    log_file = str(tmp_path / "sessions.jsonl")
    obs = RepairObservability(log_path=log_file)

    session1 = RepairSessionTelemetry(
        task_id="t1",
        domain="store.com",
        root_cause="SELECTOR_DRIFT",
        initial_health=0.20,
        final_health=1.00,
        improvement=0.80,
        attempts_count=1,
        accepted=True,
        persisted=True,
        confidence_level="high",
        duration_ms=450.0,
    )
    obs.record_session(session1)

    session2 = RepairSessionTelemetry(
        task_id="t2",
        domain="other.com",
        root_cause="BOT_BLOCKED",
        initial_health=0.0,
        final_health=0.0,
        improvement=0.0,
        attempts_count=3,
        accepted=False,
        persisted=False,
        confidence_level="low",
        duration_ms=1200.0,
    )
    obs.record_session(session2)

    recent = obs.get_recent_sessions(limit=10)
    assert len(recent) == 2

    summary = obs.get_summary()
    assert summary["total_sessions"] == 2
    assert summary["accepted_count"] == 1
    assert summary["success_rate"] == 0.50
    assert summary["persisted_count"] == 1
