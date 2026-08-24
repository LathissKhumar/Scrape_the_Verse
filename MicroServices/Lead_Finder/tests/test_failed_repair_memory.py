from leadfinder.healing.failed_memory import FailedRepairMemory


def test_failed_repair_memory_recording_and_suppression(tmp_path):
    db_file = str(tmp_path / "test_failed_mem.sqlite")
    failed_mem = FailedRepairMemory(db_path=db_file)

    domain = "shop.example.com"
    sig = "sig_12345"
    failing_config = {"fields": [{"name": "price", "selector": ".invalid-price"}]}

    # 1. Not suppressed initially
    assert failed_mem.is_suppressed(domain, sig, failing_config) is False

    # 2. Record 1 failure -> still not suppressed (needs 2 failures)
    failed_mem.record_failure(domain, sig, failing_config, reason="Bad selector")
    assert failed_mem.is_suppressed(domain, sig, failing_config) is False

    # 3. Record 2nd failure -> suppressed
    failed_mem.record_failure(domain, sig, failing_config, reason="Still bad selector")
    assert (
        failed_mem.is_suppressed(domain, sig, failing_config, ttl_seconds=3600) is True
    )

    # 4. Check penalty
    penalty = failed_mem.get_penalty(domain, sig, failing_config)
    assert penalty > 0.0

    # 5. Check different config is not suppressed
    working_config = {"fields": [{"name": "price", "selector": ".real-price"}]}
    assert failed_mem.is_suppressed(domain, sig, working_config) is False
