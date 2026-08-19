import pytest
from app.crawler.block_detector import BlockDetector
from app.crawler.result_models import BlockType


def test_detect_http_status_blocks():
    detector = BlockDetector()
    blocked, b_type, diag = detector.detect_block(429, {}, "Too Many Requests", "https://example.com")
    assert blocked is True
    assert b_type == BlockType.RATE_LIMITED

    blocked, b_type, diag = detector.detect_block(403, {}, "Access Denied", "https://example.com")
    assert blocked is True
    assert b_type == BlockType.ACCESS_DENIED

    blocked, b_type, diag = detector.detect_block(401, {}, "Unauthorized", "https://example.com")
    assert blocked is True
    assert b_type == BlockType.AUTH_REQUIRED


def test_detect_captcha_and_challenge_in_html():
    detector = BlockDetector()
    html_cf = "<html><body><h1>Attention Required! | Cloudflare</h1><div>Please complete security check to proceed</div></body></html>"
    blocked, b_type, diag = detector.detect_block(200, {}, html_cf, "https://example.com")
    assert blocked is True
    assert b_type == BlockType.SECURITY_CHALLENGE

    html_fk = "<html><body><h1>Are you a human?</h1><p>Flipkart reCAPTCHA Confirming...</p></body></html>"
    blocked, b_type, diag = detector.detect_block(200, {}, html_fk, "https://flipkart.com")
    assert blocked is True
    assert b_type == BlockType.CAPTCHA

    html_ak = "<html><body><h1>Access Denied</h1><p>You don't have permission to access on this server. Reference #18.234</p></body></html>"
    blocked, b_type, diag = detector.detect_block(200, {}, html_ak, "https://target.com")
    assert blocked is True
    assert b_type == BlockType.ACCESS_DENIED


def test_clean_page_not_blocked():
    detector = BlockDetector()
    html = "<html><body><h1>Redmi Note 11 Pro</h1><div>Price: 15,999</div></body></html>"
    blocked, b_type, diag = detector.detect_block(200, {}, html, "https://example.com")
    assert blocked is False
    assert b_type == BlockType.NONE
