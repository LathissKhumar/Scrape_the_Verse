from typing import Dict, Any

def is_html_page(p: Dict[str, Any]) -> bool:
    """
    Strictly checks if a page dictionary represents an HTML document.
    Prevents non-HTML assets (PNG, JPG, SVG, PDF, CSS, JS) from triggering false SEO issues.
    """
    if not isinstance(p, dict):
        return False

    if p.get('is_html_document') is False:
        return False

    res_type = str(p.get('resource_type') or '').lower().strip()
    if res_type and res_type != 'html':
        return False

    ct = str(p.get('content_type') or '').lower().strip()
    if ct and 'html' not in ct:
        return False

    url = str(p.get('url') or '').lower().split('?')[0]
    non_html_exts = (
        '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico', 
        '.pdf', '.css', '.js', '.woff', '.woff2', '.mp4', '.xml', '.json'
    )
    if any(url.endswith(ext) for ext in non_html_exts):
        return False

    return True

from .technical import run_technical_audit
from .onpage import run_onpage_audit
from .content import run_content_audit
from .schema import run_schema_audit
from .local import run_local_audit
from .performance import run_performance_audit

__all__ = [
    'is_html_page',
    'run_technical_audit',
    'run_onpage_audit',
    'run_content_audit',
    'run_schema_audit',
    'run_local_audit',
    'run_performance_audit',
]

