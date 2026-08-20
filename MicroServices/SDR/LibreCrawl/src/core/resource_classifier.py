"""
Resource Classification System (Phase 1)
Accurately classifies crawled resources into distinct categories:
html, image, css, javascript, pdf, font, video, audio, xml, json, binary, unknown.

Provides explicit boolean indicators:
- is_html_document
- is_indexable_document
- is_seo_page
"""

import os
import re
from urllib.parse import urlparse
from typing import Dict, Any, Tuple, Optional


ALLOWED_RESOURCE_TYPES = {
    "html", "image", "css", "javascript", "pdf", 
    "font", "video", "audio", "xml", "json", "binary", "unknown"
}

IMAGE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", 
    ".ico", ".bmp", ".tiff", ".avif", ".heic"
}
CSS_EXTENSIONS = {".css"}
JS_EXTENSIONS = {".js", ".mjs", ".cjs"}
PDF_EXTENSIONS = {".pdf"}
FONT_EXTENSIONS = {".woff", ".woff2", ".ttf", ".eot", ".otf"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".ogv", ".avi", ".mov", ".mkv"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".aac", ".flac", ".m4a"}
XML_EXTENSIONS = {".xml", ".rss", ".atom"}
JSON_EXTENSIONS = {".json"}


class ResourceClassifier:
    """
    Determines resource classification using evidence in strict priority order:
    1. HTTP Content-Type header
    2. HTML parser / DOM structure success
    3. URL extension
    4. Response body magic bytes / signatures
    """

    @staticmethod
    def classify_resource(
        url: str,
        content_type: str = "",
        response_body: Optional[bytes] = None,
        is_html_parsed: bool = False
    ) -> Dict[str, Any]:
        """
        Classifies a URL / response resource and returns a dictionary of flags.
        """
        ct_clean = (content_type or "").lower().split(";")[0].strip()
        parsed_url = urlparse(url or "")
        path_lower = parsed_url.path.lower()
        _, ext = os.path.splitext(path_lower)

        resource_type = "unknown"

        # 1. Evidence Level 1: HTTP Content-Type Header
        if "text/html" in ct_clean or "application/xhtml+xml" in ct_clean:
            resource_type = "html"
        elif ct_clean.startswith("image/"):
            resource_type = "image"
        elif "text/css" in ct_clean:
            resource_type = "css"
        elif "javascript" in ct_clean or "text/ecmascript" in ct_clean:
            resource_type = "javascript"
        elif "application/pdf" in ct_clean:
            resource_type = "pdf"
        elif ct_clean.startswith("font/") or "application/x-font" in ct_clean or "font-woff" in ct_clean:
            resource_type = "font"
        elif ct_clean.startswith("video/"):
            resource_type = "video"
        elif ct_clean.startswith("audio/"):
            resource_type = "audio"
        elif "application/xml" in ct_clean or "text/xml" in ct_clean:
            resource_type = "xml"
        elif "application/json" in ct_clean or "text/json" in ct_clean:
            resource_type = "json"
        elif ct_clean in ("application/octet-stream", "application/zip", "application/x-tar", "application/gzip"):
            resource_type = "binary"

        # 2. Evidence Level 2: HTML Parsing Success
        if resource_type == "unknown" or resource_type == "binary":
            if is_html_parsed:
                resource_type = "html"

        # 3. Evidence Level 3: URL Extension Fallback
        if resource_type in ("unknown", "binary"):
            if ext in IMAGE_EXTENSIONS:
                resource_type = "image"
            elif ext in CSS_EXTENSIONS:
                resource_type = "css"
            elif ext in JS_EXTENSIONS:
                resource_type = "javascript"
            elif ext in PDF_EXTENSIONS:
                resource_type = "pdf"
            elif ext in FONT_EXTENSIONS:
                resource_type = "font"
            elif ext in VIDEO_EXTENSIONS:
                resource_type = "video"
            elif ext in AUDIO_EXTENSIONS:
                resource_type = "audio"
            elif ext in XML_EXTENSIONS:
                resource_type = "xml"
            elif ext in JSON_EXTENSIONS:
                resource_type = "json"
            elif ext in (".html", ".htm", ".shtml", ".php", ".asp", ".aspx", ".jsp"):
                resource_type = "html"

        # 4. Evidence Level 4: Magic Bytes Inspection (if body provided)
        if resource_type == "unknown" and response_body and len(response_body) > 4:
            if response_body.startswith(b"<!DOCTYPE") or response_body.startswith(b"<html") or response_body.startswith(b"<?xml"):
                if b"<html" in response_body[:500].lower():
                    resource_type = "html"
                elif b"<?xml" in response_body[:100].lower():
                    resource_type = "xml"
            elif response_body.startswith(b"\x89PNG") or response_body.startswith(b"\xff\xd8\xff") or response_body.startswith(b"GIF8"):
                resource_type = "image"
            elif response_body.startswith(b"%PDF"):
                resource_type = "pdf"

        # If extension indicates image/css/js but content-type was missing/generic, extension wins
        if ext in IMAGE_EXTENSIONS and resource_type != "image":
            resource_type = "image"
        elif ext in CSS_EXTENSIONS and resource_type != "css":
            resource_type = "css"
        elif ext in JS_EXTENSIONS and resource_type != "javascript":
            resource_type = "javascript"

        is_html_document = (resource_type == "html")
        
        # Indexable document: HTML or PDF documents
        is_indexable_document = resource_type in ("html", "pdf")
        
        # SEO page: Indexable HTML pages intended for search engines
        is_seo_page = is_html_document

        return {
            "resource_type": resource_type,
            "is_html_document": is_html_document,
            "is_indexable_document": is_indexable_document,
            "is_seo_page": is_seo_page,
            "content_type": ct_clean
        }
