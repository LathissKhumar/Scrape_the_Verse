"""Body parsing and sanitization utilities."""
import re
from typing import Optional, Tuple
import email.message


def html_to_plain_text(html_content: str) -> str:
    """Converts HTML content to clean plain text."""
    if not html_content:
        return ""
    # Remove style and script tags
    cleaned = re.sub(r"<(script|style).*?>.*?</\1>", "", html_content, flags=re.DOTALL | re.IGNORECASE)
    # Replace <br> and <p> with newlines
    cleaned = re.sub(r"<br\s*/?>", "\n", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"</p>", "\n\n", cleaned, flags=re.IGNORECASE)
    # Strip remaining HTML tags
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    # Replace HTML entities
    cleaned = (
        cleaned.replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
    )
    # Collapse multiple blank lines
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def extract_body_parts(msg: email.message.Message) -> Tuple[Optional[str], Optional[str]]:
    """Traverses MIME parts to extract (plain_text_body, html_body)."""
    text_parts = []
    html_parts = []

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))

            # Skip attachments
            if "attachment" in content_disposition:
                continue

            payload = part.get_payload(decode=True)
            if not payload:
                continue

            charset = part.get_content_charset() or "utf-8"
            try:
                decoded_str = payload.decode(charset, errors="replace")
            except Exception:
                decoded_str = payload.decode("latin1", errors="replace")

            if content_type == "text/plain":
                text_parts.append(decoded_str)
            elif content_type == "text/html":
                html_parts.append(decoded_str)
    else:
        content_type = msg.get_content_type()
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            try:
                decoded_str = payload.decode(charset, errors="replace")
            except Exception:
                decoded_str = payload.decode("latin1", errors="replace")

            if content_type == "text/html":
                html_parts.append(decoded_str)
            else:
                text_parts.append(decoded_str)

    plain_text = "\n\n".join(text_parts).strip() if text_parts else None
    html = "\n\n".join(html_parts).strip() if html_parts else None

    # If only HTML is present, generate plain text fallback
    if not plain_text and html:
        plain_text = html_to_plain_text(html)

    return plain_text, html
