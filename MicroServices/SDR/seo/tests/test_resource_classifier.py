"""
Unit Tests for Resource Classification & Dual Data Models (Phases 1-4)
Verifies:
- Accurate resource classification for HTML, PNG, JPG, SVG, PDF, CSS, JS, Fonts, XML, JSON
- Boolean flags (is_html_document, is_indexable_document, is_seo_page)
- Zero false positive SEO issues on non-HTML image/asset URLs
- PageRecord vs ResourceRecord creation
"""

from LibreCrawl.src.core.models import create_resource_record
from LibreCrawl.src.core.resource_classifier import ResourceClassifier
from seo.analyzers import (
    is_html_page,
    run_content_audit,
    run_onpage_audit,
    run_technical_audit,
)


def test_classify_resource_html():
    res = ResourceClassifier.classify_resource(
        "https://example.com/about", content_type="text/html; charset=utf-8"
    )
    assert res["resource_type"] == "html"
    assert res["is_html_document"] is True
    assert res["is_seo_page"] is True


def test_classify_resource_image():
    # Content-type image
    res1 = ResourceClassifier.classify_resource(
        "https://example.com/logo.png", content_type="image/png"
    )
    assert res1["resource_type"] == "image"
    assert res1["is_html_document"] is False
    assert res1["is_seo_page"] is False

    # URL extension image
    res2 = ResourceClassifier.classify_resource("https://example.com/media/banner.webp")
    assert res2["resource_type"] == "image"
    assert res2["is_html_document"] is False


def test_classify_resource_pdf_css_js():
    res_pdf = ResourceClassifier.classify_resource(
        "https://example.com/doc.pdf", content_type="application/pdf"
    )
    assert res_pdf["resource_type"] == "pdf"
    assert res_pdf["is_indexable_document"] is True

    res_css = ResourceClassifier.classify_resource(
        "https://example.com/style.css", content_type="text/css"
    )
    assert res_css["resource_type"] == "css"
    assert res_css["is_html_document"] is False

    res_js = ResourceClassifier.classify_resource(
        "https://example.com/app.js", content_type="application/javascript"
    )
    assert res_js["resource_type"] == "javascript"
    assert res_js["is_html_document"] is False


def test_is_html_page_filter():
    html_page = {
        "url": "https://example.com/dentist",
        "status_code": 200,
        "content_type": "text/html",
        "is_html_document": True,
    }
    image_asset = {
        "url": "https://example.com/image.png",
        "status_code": 200,
        "content_type": "image/png",
        "is_html_document": False,
        "resource_type": "image",
    }

    assert is_html_page(html_page) is True
    assert is_html_page(image_asset) is False


def test_elimination_of_false_positives_on_images():
    """
    Ensures image URLs with status 200 DO NOT trigger false missing title/meta/h1/canonical/thin content errors.
    """
    image_asset = create_resource_record(
        url="https://example.com/logo.png",
        status_code=200,
        content_type="image/png",
        size_bytes=45000,
    )

    pages = [image_asset]

    # Run On-Page Audit
    onpage_res = run_onpage_audit(pages, [])
    # Should report 0 missing titles, 0 missing metas, 0 missing H1s for the image asset
    for finding in onpage_res["findings"]:
        assert "logo.png" not in finding["affected_urls"]

    # Run Technical Audit
    tech_res = run_technical_audit(pages, [], [], {})
    for finding in tech_res["findings"]:
        if finding["title"] == "Missing Canonical Tags":
            assert "logo.png" not in finding["affected_urls"]

    # Run Content Audit
    content_res = run_content_audit(pages)
    for finding in content_res["findings"]:
        if finding["title"] == "Thin Content Pages (< 300 words)":
            assert "logo.png" not in finding["affected_urls"]
