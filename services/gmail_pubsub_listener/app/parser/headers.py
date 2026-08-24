"""Email header parsing and decoding utilities."""

import email.utils
from email.header import decode_header


def decode_rfc2047(header_val: str | None) -> str | None:
    """Decodes internationalized RFC 2047 header values."""
    if not header_val:
        return None
    decoded_fragments = []
    try:
        for fragment, encoding in decode_header(header_val):
            if isinstance(fragment, bytes):
                decoded_fragments.append(
                    fragment.decode(encoding or "utf-8", errors="replace")
                )
            else:
                decoded_fragments.append(str(fragment))
        return "".join(decoded_fragments).strip()
    except Exception:
        return str(header_val).strip()


def parse_address_list(header_val: str | None) -> list[str]:
    """Parses a comma-separated list of email addresses into pure email addresses."""
    if not header_val:
        return []
    addresses = []
    for name, addr in email.utils.getaddresses([header_val]):
        if addr:
            addresses.append(addr.strip().lower())
    return addresses


def parse_sender(header_val: str | None) -> tuple[str, str | None]:
    """Extracts (email_address, display_name) from From: header."""
    if not header_val:
        return ("", None)
    name, addr = email.utils.parseaddr(header_val)
    decoded_name = decode_rfc2047(name) if name else None
    return (addr.strip().lower(), decoded_name)


def parse_references(header_val: str | None) -> list[str]:
    """Parses References or In-Reply-To headers into a list of Message-IDs."""
    if not header_val:
        return []
    # References are typically whitespace or comma separated <id1> <id2>
    items = header_val.replace(",", " ").split()
    clean_refs = []
    for item in items:
        clean = item.strip().strip("<>").strip()
        if clean:
            clean_refs.append(clean)
    return clean_refs


def clean_message_id(header_val: str | None) -> str | None:
    """Cleans <message-id> string."""
    if not header_val:
        return None
    return header_val.strip().strip("<>").strip()
