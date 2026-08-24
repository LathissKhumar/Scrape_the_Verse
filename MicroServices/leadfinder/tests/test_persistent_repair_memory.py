from leadfinder.healing.persistent_memory import PersistentRepairMemory
from leadfinder.healing.schemas import RepairMemoryRecord, RepairType


def test_persistent_repair_memory_saves_and_reloads(tmp_path):
    db_file = str(tmp_path / "test_memory.db")
    mem1 = PersistentRepairMemory(db_path=db_file)
    rec = RepairMemoryRecord(
        domain="example.com",
        signature="sig_123",
        root_cause="SELECTOR_DRIFT",
        repair_type=RepairType.REPAIR_CSS_SELECTORS,
        successful_patch={"fields": [{"name": "price", "selector": ".new-price"}]},
        health_before=0.2,
        health_after=1.0,
        strategy="css",
    )
    mem1.record_success(rec)

    # Instantiate fresh memory instance pointing to same DB file
    mem2 = PersistentRepairMemory(db_path=db_file)
    match = mem2.lookup("example.com", "sig_123")
    assert match is not None
    assert match.domain == "example.com"
    assert match.signature == "sig_123"
    assert match.repair_type == RepairType.REPAIR_CSS_SELECTORS
    assert match.successful_patch["fields"][0]["selector"] == ".new-price"
    assert match.health_after == 1.0


def test_persistent_repair_memory_lookup_miss(tmp_path):
    db_file = str(tmp_path / "test_empty_memory.db")
    mem = PersistentRepairMemory(db_path=db_file)
    match = mem.lookup("unknown.com", "sig_999")
    assert match is None
