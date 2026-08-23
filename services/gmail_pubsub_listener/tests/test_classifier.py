"""Tests for rule and LLM intent classifier."""
import pytest
from app.classification.rules import RuleClassifier
from app.classification.llm import LLMClassifier


def test_rule_classifier_out_of_office():
    res = RuleClassifier.classify("msg_1", "Automatic Reply: Out of office", "I will be away from my desk until Monday.")
    assert res is not None
    assert res.intent == "OUT_OF_OFFICE"
    assert res.suggested_action == "snooze_followup"


def test_rule_classifier_unsubscribe():
    res = RuleClassifier.classify("msg_2", "Please stop", "Please remove me from your mailing list and unsubscribe.")
    assert res is not None
    assert res.intent == "UNSUBSCRIBE"
    assert res.suggested_action == "suppress_contact"


def test_rule_classifier_bounce():
    res = RuleClassifier.classify("msg_3", "Delivery Status Notification (Failure)", "Mail delivery failed: 550 user unknown.")
    assert res is not None
    assert res.intent == "BOUNCE"
    assert res.suggested_action == "mark_bounced"


def test_rule_classifier_meeting():
    res = RuleClassifier.classify("msg_4", "Re: Proposal", "Sounds interesting, let's schedule a call this Friday.")
    assert res is not None
    assert res.intent == "REQUEST_MEETING"
    assert res.suggested_action == "create_meeting_task"


def test_rule_classifier_pricing():
    res = RuleClassifier.classify("msg_5", "Re: Services", "How much does it cost? Please share the pricing details.")
    assert res is not None
    assert res.intent == "REQUEST_PRICING"
    assert res.suggested_action == "send_pricing_details"


@pytest.mark.asyncio
async def test_llm_classifier_rule_delegation():
    classifier = LLMClassifier()
    res = await classifier.classify_message("msg_6", "Re: Quick chat", "Let's set up a demo next Tuesday.")
    assert res.intent == "REQUEST_MEETING"
    assert res.confidence >= 0.9
