from leadfinder.crawler.provider_decision import (
    FailureNature,
    ProviderDecisionEngine,
    ProviderRecommendation,
)
from leadfinder.crawler.result_models import BlockType, CrawlResult


def test_provider_decision_transient_network_retry():
    engine = ProviderDecisionEngine()
    crawl_res = CrawlResult(
        url="https://example.com",
        status_code=502,
        error="Network connection reset (ECONNRESET)",
        blocked=False,
    )
    nature = engine.classify_failure(crawl_res)
    assert nature == FailureNature.TRANSIENT_NETWORK

    rec, reason = engine.decide_action(crawl_res, attempt=1, brightdata_configured=True)
    assert rec == ProviderRecommendation.LOCAL_RETRY_BACKOFF


def test_provider_decision_bot_block_escalates_to_brightdata():
    engine = ProviderDecisionEngine()
    crawl_res = CrawlResult(
        url="https://example.com",
        status_code=403,
        blocked=True,
        block_type=BlockType.CAPTCHA,
        html="<html>Please solve captcha to continue</html>",
    )
    nature = engine.classify_failure(crawl_res)
    assert nature == FailureNature.BOT_BLOCKED

    rec, reason = engine.decide_action(crawl_res, attempt=1, brightdata_configured=True)
    assert rec == ProviderRecommendation.BRIGHTDATA_FALLBACK


def test_provider_decision_timeout_increases_limit():
    engine = ProviderDecisionEngine()
    crawl_res = CrawlResult(
        url="https://example.com",
        status_code=504,
        error="Navigation timeout 30000ms exceeded",
        blocked=False,
    )
    nature = engine.classify_failure(crawl_res)
    assert nature == FailureNature.TIMEOUT

    rec, reason = engine.decide_action(
        crawl_res, attempt=1, brightdata_configured=False
    )
    assert rec == ProviderRecommendation.INCREASE_TIMEOUT
