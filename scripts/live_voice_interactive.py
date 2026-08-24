#!/usr/bin/env python3
"""
Real-Time Interactive Voice Agent CLI Tester.
Allows testing the AI Sales Voice Agent live with custom speech inputs,
verifying 2-strike soft convincing with free PDF audit delivery, objection handling,
questions, and calendar meeting booking in real time.
"""

import asyncio

from MicroServices.Voice_Agent.state_machine import VoiceConversationEngine


def print_header():
    print("\n" + "═" * 75)
    print(" 🎙️  AGENCYOS VOICE AGENT — REAL-TIME INTERACTIVE CALL TESTER")
    print("═" * 75)
    print(" Instructions:")
    print(" • Type your response as the business owner (or test 'No', questions, etc.)")
    print(" • Type 'exit' or 'quit' at any time to end the test.")
    print("═" * 75 + "\n")


async def run_interactive_call():
    print_header()

    # Configure test prospect
    company_name = (
        input("Enter Company Name [default: Horizon Dental]: ").strip()
        or "Horizon Dental"
    )
    contact_name = (
        input("Enter Contact Name [default: Dr. Evans]: ").strip() or "Dr. Evans"
    )
    has_website_input = (
        input("Does the company have a website? (y/n) [default: y]: ").strip().lower()
    )
    has_website = False if has_website_input == "n" else True

    print("\n" + "─" * 75)
    print(f"📞 Calling {company_name} ({contact_name})... [Connected]")
    print("─" * 75)

    engine = VoiceConversationEngine(
        company_name=company_name,
        contact_name=contact_name,
        has_website=has_website,
        prompt_pack={
            "key_problems": [
                "Mobile page speed takes 4.5s to load",
                "Missing Google Maps local schema",
            ],
            "value_angles": ["Capture 2x more local mobile appointments"],
        },
    )

    # 1. Opening turn
    opening = engine.start_conversation()
    print("\n🤖 Sarah (Agent):")
    print(f'   "{opening}"\n')

    # 2. Interactive turn loop
    turn_count = 1
    while engine.current_state != "CLOSING":
        try:
            user_input = input(f"👤 {contact_name} (Turn {turn_count}) > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nCall ended by tester.")
            break

        if not user_input or user_input.lower() in ("exit", "quit", "q"):
            print("\nEnding live call simulation.")
            break

        print("\n⏳ [Sarah is thinking & listening...]")
        res = await engine.process_turn_async(user_input)

        print("🤖 Sarah (Agent):")
        print(f'   "{res["agent_response"]}"')

        pdf_status = (
            "📄 [FREE AUDIT PDF TRIGGERED & SENT]"
            if engine.pdf_audit_sent
            else "No PDF"
        )
        print(
            f"   ─── [Intent: {res.get('intent', 'N/A')}] | [State: {res['new_state']}] | [PDF: {pdf_status}] | [Interest Score: {engine.interest_score}/100]\n"
        )

        turn_count += 1

        if res["new_state"] == "CLOSING":
            print("📴 [Call Ended & Disconnected by Agent]")
            break

    # 3. Final Summary
    print("\n" + "═" * 75)
    print(" 📊 FINAL CALL REPORT & CRM SUMMARY")
    print("═" * 75)
    print(f" • Company:              {engine.company_name}")
    print(f" • Contact:              {engine.contact_name}")
    print(
        f" • Final Disposition:    {engine.disposition.value if engine.disposition else 'COMPLETED'}"
    )
    print(f" • Final Interest Score: {engine.interest_score}/100")
    print(f" • Free PDF Audit Sent:  {'YES ✅' if engine.pdf_audit_sent else 'NO ❌'}")
    print(f" • Meeting Scheduled:    {engine.booked_meeting_time or 'None'}")
    print(f" • Total Turns:          {len(engine.transcript)}")
    print("═" * 75 + "\n")


if __name__ == "__main__":
    asyncio.run(run_interactive_call())
