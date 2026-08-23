"""Tests for MIME email parser."""
import email.message
from app.parser.mime import MIMEParser
from app.parser.headers import decode_rfc2047, parse_sender, parse_references


def test_decode_rfc2047():
    encoded = "=?UTF-8?B?UmU6IFdlYnNpdGUgUHJvcG9zYWw=?="
    decoded = decode_rfc2047(encoded)
    assert decoded == "Re: Website Proposal"


def test_parse_sender():
    raw_from = "John Doe <john.doe@example.com>"
    email_addr, display_name = parse_sender(raw_from)
    assert email_addr == "john.doe@example.com"
    assert display_name == "John Doe"


def test_parse_references():
    raw_refs = "<msg_1@mail.com> <msg_2@mail.com>, <msg_3@mail.com>"
    refs = parse_references(raw_refs)
    assert refs == ["msg_1@mail.com", "msg_2@mail.com", "msg_3@mail.com"]


def test_parse_simple_email():
    raw_email = (
        b"From: Alice <alice@client.com>\r\n"
        b"To: Bob <bob@agency.com>\r\n"
        b"Subject: Meeting Inquiry\r\n"
        b"Message-ID: <msg_abc_123@client.com>\r\n"
        b"Date: Mon, 20 Jan 2025 10:00:00 +0000\r\n"
        b"Content-Type: text/plain; charset=utf-8\r\n"
        b"\r\n"
        b"Hi Bob,\nLet's schedule a call this Thursday.\r\n"
    )

    parsed = MIMEParser.parse_rfc822(raw_email, uid=101, mailbox="INBOX")

    assert parsed.id == "msg_abc_123@client.com"
    assert parsed.sender_email == "alice@client.com"
    assert parsed.sender_name == "Alice"
    assert parsed.to == ["bob@agency.com"]
    assert parsed.subject == "Meeting Inquiry"
    assert "schedule a call" in (parsed.text_body or "")
    assert parsed.uid == 101


def test_parse_multipart_email():
    msg = email.message.EmailMessage()
    msg["From"] = "prospect@store.com"
    msg["To"] = "sales@agency.com"
    msg["Subject"] = "Pricing Question"
    msg["Message-ID"] = "<msg_multi_999@store.com>"
    msg["In-Reply-To"] = "<out_orig_888@agency.com>"
    msg["References"] = "<out_orig_888@agency.com>"
    msg.set_content("Can you send me your pricing sheet?")
    msg.add_alternative("<p>Can you send me your <b>pricing sheet</b>?</p>", subtype="html")

    raw_bytes = msg.as_bytes()
    parsed = MIMEParser.parse_rfc822(raw_bytes, uid=102, mailbox="INBOX")

    assert parsed.sender_email == "prospect@store.com"
    assert parsed.in_reply_to == "out_orig_888@agency.com"
    assert parsed.references == ["out_orig_888@agency.com"]
    assert "pricing sheet" in (parsed.text_body or "")
    assert "<b>pricing sheet</b>" in (parsed.html_body or "")
