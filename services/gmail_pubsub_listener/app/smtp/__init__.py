"""SMTP email dispatching package."""
from app.smtp.sender import GmailSMTPSender, OutboundEmail, SendResult

__all__ = ["GmailSMTPSender", "OutboundEmail", "SendResult"]
