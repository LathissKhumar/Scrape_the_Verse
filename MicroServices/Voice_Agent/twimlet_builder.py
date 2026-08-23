"""
Twimlet-Native Multi-Turn TwiML Generator for AgencyOS Voice Agent.

Generates pre-chained Twilio-hosted (twimlets.com/echo) TwiML URLs that enable
robust multi-turn speech conversations on PSTN phone calls without needing
local HTTP tunnels (ngrok/Cloudflare) or external webhook servers.

Conversation Flow:
  Turn 1: Opening Greeting -> <Gather input="speech" action="Pitch_URL">
  Turn 2: Pitch & Discovery -> <Gather input="speech" action="Booking_URL">
  Turn 3: Demo Confirmation & Booking -> <Say> Confirmation -> <Hangup>
"""

import logging
import urllib.parse
from typing import Optional

logger = logging.getLogger("TwimletBuilder")

TWIMLET_ECHO_BASE = "https://twimlets.com/echo"


def encode_twimlet_url(twiml_xml: str) -> str:
    """Encodes TwiML XML into a Twimlets Echo URL."""
    encoded = urllib.parse.quote(twiml_xml, safe="")
    return f"{TWIMLET_ECHO_BASE}?Twiml={encoded}"


def build_conversation_tree(
    company_name: str = "Apex Roofing Solutions",
    contact_name: Optional[str] = "Lathiss",
    has_website: bool = False,
) -> str:
    """
    Builds a complete, compact 3-turn interactive sales conversation tree
    encoded as nested Twimlets Echo URLs.

    Returns the root URL to pass directly to twilio.calls.create(url=...).
    """
    name = contact_name or "there"
    comp = company_name or "your company"

    # ── Turn 3: Confirmation / Booking ──────────────────────────────────────────
    booked_xml = (
        f'<Response>'
        f'<Say voice="alice">Awesome! I have marked down our 10-minute discovery demo. '
        f'We sent the calendar invite and digital audit to your inbox. Thank you {name}, talk soon!</Say>'
        f'<Hangup/>'
        f'</Response>'
    )
    booked_url = encode_twimlet_url(booked_xml)

    # ── Turn 2: Pitch & Discovery ───────────────────────────────────────────────
    if not has_website:
        pitch_say = (
            f"Great! We help businesses like {comp} launch mobile websites that add 15 to 20 client inquiries a month. "
            f"Can we set up a quick 10-minute demo on Thursday or Friday?"
        )
    else:
        pitch_say = (
            f"Great! Our technical audit revealed 2 speed and SEO barriers on {comp}'s website that drop mobile inquiries. "
            f"Can we set up a quick 10-minute demo on Thursday or Friday to show you the fixes?"
        )

    pitch_fallback_say = "Thank you for your time. Have a wonderful day!"

    pitch_xml = (
        f'<Response>'
        f'<Gather input="speech" action="{booked_url}" method="POST" speechTimeout="auto" timeout="5" language="en-US">'
        f'<Say voice="alice">{pitch_say}</Say>'
        f'</Gather>'
        f'<Say voice="alice">{pitch_fallback_say}</Say>'
        f'<Hangup/>'
        f'</Response>'
    )
    pitch_url = encode_twimlet_url(pitch_xml)

    # ── Turn 1: Opening Greeting ────────────────────────────────────────────────
    if not has_website:
        opening_say = (
            f"Hi {name}, this is Sarah from AgencyOS. "
            f"We noticed {comp} does not currently have a mobile-verified website. "
            f"Do you have 30 seconds to chat?"
        )
    else:
        opening_say = (
            f"Hi {name}, this is Sarah from AgencyOS. "
            f"We completed a digital health audit of {comp}'s website. "
            f"Do you have 30 seconds to chat?"
        )

    opening_fallback_say = "Thanks for your time. Have a great day!"

    opening_xml = (
        f'<Response>'
        f'<Gather input="speech" action="{pitch_url}" method="POST" speechTimeout="auto" timeout="5" language="en-US">'
        f'<Say voice="alice">{opening_say}</Say>'
        f'</Gather>'
        f'<Say voice="alice">{opening_fallback_say}</Say>'
        f'<Hangup/>'
        f'</Response>'
    )
    root_url = encode_twimlet_url(opening_xml)

    logger.info(f"Built Twimlet conversation tree for '{comp}' ({name}): URL length = {len(root_url)} chars")
    return root_url
