"""
Scheduling Agent for Lead Manager.
Generates RFC 5545 compliant .ics calendar files.
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from icalendar import Calendar, Event, vCalAddress, vText

from ..config.logging import get_logger
from ..domain.meeting import Meeting
from ..domain.stage import MeetingStatus

logger = get_logger("SchedulingAgent")


class SchedulingAgent:
    @staticmethod
    def generate_ics_content(
        meeting_id: str,
        title: str,
        start_time: datetime,
        duration_minutes: int,
        organizer_email: str,
        attendee_email: str,
        description: str | None = None,
        location_url: str | None = None,
    ) -> str:
        cal = Calendar()
        cal.add("prodid", "-//AgencyOS//LeadManager 1.0//EN")
        cal.add("version", "2.0")
        cal.add("calscale", "GREGORIAN")
        cal.add("method", "REQUEST")

        event = Event()
        event.add("summary", title)
        event.add("uid", f"{meeting_id}@agencyos.local")
        event.add("dtstamp", datetime.now(timezone.utc))
        event.add("dtstart", start_time)
        event.add("dtend", start_time + timedelta(minutes=duration_minutes))

        if description:
            event.add("description", description)
        if location_url:
            event.add("location", location_url)

        organizer = vCalAddress(f"MAILTO:{organizer_email}")
        organizer.params["cn"] = vText("AgencyOS Specialist")
        event["organizer"] = organizer

        attendee = vCalAddress(f"MAILTO:{attendee_email}")
        attendee.params["cn"] = vText("Valued Prospect")
        attendee.params["ROLE"] = vText("REQ-PARTICIPANT")
        event.add("attendee", attendee, encode=0)

        event.add("status", "CONFIRMED")
        cal.add_component(event)

        return cal.to_ical().decode("utf-8")

    async def create_meeting_proposal(
        self,
        lead_id: str,
        title: str,
        proposed_time_iso: str,
        duration_minutes: int,
        organizer_email: str,
        attendee_email: str,
        conversation_id: str | None = None,
        notes: str | None = None,
    ) -> Meeting:
        try:
            start_dt = datetime.fromisoformat(proposed_time_iso)
            if start_dt.tzinfo is None:
                start_dt = start_dt.replace(tzinfo=timezone.utc)
        except Exception:
            start_dt = datetime.now(timezone.utc) + timedelta(days=2, hours=10)

        meet_id = f"meet_{uuid4().hex[:12]}"
        ics = self.generate_ics_content(
            meeting_id=meet_id,
            title=title,
            start_time=start_dt,
            duration_minutes=duration_minutes,
            organizer_email=organizer_email,
            attendee_email=attendee_email,
            description=notes or f"Discovery and growth strategy meeting for {title}.",
        )

        return Meeting(
            id=meet_id,
            lead_id=lead_id,
            conversation_id=conversation_id,
            title=title,
            scheduled_at=start_dt.isoformat(),
            duration_minutes=duration_minutes,
            timezone="UTC",
            status=MeetingStatus.REQUESTED,
            ics_content=ics,
            organizer_email=organizer_email,
            attendee_email=attendee_email,
            notes=notes,
        )
