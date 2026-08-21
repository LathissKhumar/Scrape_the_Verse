import pytest
from leadfinder.crawler.circuit_breaker import DomainCircuitBreaker
from leadfinder.crawler.result_models import BlockType


def test_circuit_breaker_tripping():
    cb = DomainCircuitBreaker(failure_threshold=3, cooldown_seconds=60.0)
    url = "https://example.com/item"
    
    assert cb.allow_request(url) is True
    
    # Record blocks
    cb.record_result(url, blocked=True, block_type=BlockType.ACCESS_DENIED)
    cb.record_result(url, blocked=True, block_type=BlockType.ACCESS_DENIED)
    assert cb.allow_request(url) is True
    
    # 3rd failure trips the breaker
    cb.record_result(url, blocked=True, block_type=BlockType.ACCESS_DENIED)
    assert cb.allow_request(url) is False


def test_circuit_breaker_reset_on_success():
    cb = DomainCircuitBreaker(failure_threshold=3)
    url = "https://example.com/item"
    
    cb.record_result(url, blocked=True, block_type=BlockType.RATE_LIMITED)
    cb.record_result(url, blocked=True, block_type=BlockType.RATE_LIMITED)
    
    # Success resets consecutive failure count
    cb.record_result(url, blocked=False, block_type=BlockType.NONE)
    assert cb.get_failure_count(url) == 0
    assert cb.allow_request(url) is True
