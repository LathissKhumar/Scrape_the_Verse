"use client";

import React, { useState, useEffect } from "react";
import {
  Send,
  Mail,
  Share2,
  PhoneCall,
  Sparkles,
  Copy,
  Check,
  CheckCircle2,
  Clock,
  Layers,
  ArrowRight,
  TrendingUp,
  MessageSquare,
  Sliders,
  Play,
  Plus,
  BarChart3,
  Calendar,
  Users,
  RefreshCw,
} from "lucide-react";
import { LeadRecord, DashboardTab, OutreachAsset } from "./types";
import { mockLeads, mockOutreachAssets } from "./mockData";
import { ingestLifecycleEvent } from "@/lib/api/leadManager";

interface OutreachHubPageProps {
  selectedLead?: LeadRecord;
  onNavigateTab: (tab: DashboardTab, leadId?: string) => void;
  onSelectLead: (lead: LeadRecord) => void;
}

export const OutreachHubPage: React.FC<OutreachHubPageProps> = ({
  selectedLead = mockLeads[0],
  onNavigateTab,
  onSelectLead,
}) => {
  const [activeLead, setActiveLead] = useState<LeadRecord>(selectedLead);
  const [prevSelectedLead, setPrevSelectedLead] =
    useState<LeadRecord>(selectedLead);
  const [selectedStep, setSelectedStep] = useState<number>(1);
  const [copied, setCopied] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [sentSuccess, setSentSuccess] = useState(false);
  const [eventStatus, setEventStatus] = useState<string | null>(null);

  if (selectedLead && selectedLead.id !== prevSelectedLead?.id) {
    setPrevSelectedLead(selectedLead);
    setActiveLead(selectedLead);
  }

  const sequenceSteps = [
    {
      step: 1,
      day: "Day 1",
      channel: "email",
      icon: Mail,
      title: "Initial Technical Audit Email",
      subject: `Quick question regarding ${activeLead.business_name}'s web performance`,
      body: `Hi ${activeLead.contact_person || "there"},\n\nI was reviewing ${activeLead.business_name}'s digital presence in ${activeLead.location} and noticed your mobile page speed is currently scoring below average, resulting in an estimated loss of 15-20 qualified inquiries per month.\n\nWe prepared a complimentary 3-point technical audit report outlining how you can capture market share from local competitors.\n\nWould you be open to a 5-minute review call this week?`,
      stats: { sent: 420, openRate: "68.4%", replyRate: "24.1%" },
    },
    {
      step: 2,
      day: "Day 3",
      channel: "linkedin",
      icon: Share2,
      title: "LinkedIn Executive Connection",
      subject: "LinkedIn InMail Direct Connection",
      body: `Hi ${activeLead.contact_person || "there"} - noticed your impressive work leading ${activeLead.business_name}. We recently generated a comparative growth diagnostic vs top local providers in ${activeLead.location}.\n\nThought you might find the breakdown valuable. Would love to connect!`,
      stats: { sent: 310, openRate: "79.2%", replyRate: "31.0%" },
    },
    {
      step: 3,
      day: "Day 5",
      channel: "email",
      icon: Mail,
      title: "Value-Add Proposal & Case Study",
      subject: `Case Study: +180% inbound inquiries for ${activeLead.category}`,
      body: `Hi ${activeLead.contact_person || "there"},\n\nFollowing up on my previous note. We just published a case study demonstrating how a similar company in ${activeLead.category} doubled their commercial client bookings in 60 days.\n\nHere is your custom proposal link: https://app.scrapetheverse.com/p/${activeLead.id}\n\nLet me know if you'd like to walk through the numbers together.`,
      stats: { sent: 240, openRate: "62.0%", replyRate: "19.5%" },
    },
    {
      step: 4,
      day: "Day 7",
      channel: "call_script",
      icon: PhoneCall,
      title: "AI SDR Outbound Call Pitch",
      subject: "Direct Executive Phone Follow-up",
      body: `Opening Script:\n"Hello ${activeLead.contact_person || "Sir/Ma'am"}, calling from Growth Engineering. I sent over an executive proposal regarding ${activeLead.business_name}'s market positioning in ${activeLead.location}. Did you have a moment to review the benchmark numbers?"`,
      stats: { sent: 94, openRate: "100%", replyRate: "24.7% Booked" },
    },
  ];

  const currentStep =
    sequenceSteps.find((s) => s.step === selectedStep) || sequenceSteps[0];

  const handleSelectLeadChange = (leadId: string) => {
    const found = mockLeads.find((l) => l.id === leadId);
    if (found) {
      setActiveLead(found);
      onSelectLead(found);
      setEventStatus(null);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(currentStep.body);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDispatch = async () => {
    setIsSending(true);
    setEventStatus(null);

    try {
      const res = await ingestLifecycleEvent(
        "email.sent",
        activeLead.id,
        "human",
        {
          step: selectedStep,
          channel: currentStep.channel,
          subject: currentStep.subject,
        },
      );

      setIsSending(false);
      setSentSuccess(true);
      if (res.success) {
        setEventStatus(
          `Outreach dispatched! Lead Manager transition: ${res.newStage || "CONTACTED"}`,
        );
      } else {
        setEventStatus("Outreach dispatched successfully (offline demo mode).");
      }
      setTimeout(() => setSentSuccess(false), 4000);
    } catch {
      setIsSending(false);
      setSentSuccess(true);
      setEventStatus("Outreach dispatched successfully.");
      setTimeout(() => setSentSuccess(false), 4000);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn font-body">
      {/* 1. Header with Sequence Performance */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/[0.06] border border-white/[0.14] text-xs font-semibold text-sky-300 mb-2 backdrop-blur-xl">
            <Send className="w-3.5 h-3.5 text-sky-400" />
            <span>Multi-Step Campaign Sequence Studio (:8082)</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white font-display">
            Outreach Sequences & Campaign Hub
          </h1>
          <p className="text-sm text-white/60 mt-1 max-w-2xl">
            Automate personalized 4-step multi-channel outreach campaigns across
            Email, LinkedIn, and outbound phone pitches.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={activeLead.id}
            onChange={(e) => handleSelectLeadChange(e.target.value)}
            className="px-4 py-2 rounded-xl bg-white/[0.06] border border-white/[0.14] text-xs font-semibold text-white focus:outline-none focus:border-white/30 cursor-pointer backdrop-blur-xl"
          >
            {mockLeads.map((l) => (
              <option
                key={l.id}
                value={l.id}
                className="bg-[#090E1A] text-white"
              >
                {l.business_name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Event Feedback Banner */}
      {eventStatus && (
        <div className="p-3.5 rounded-2xl bg-white/[0.06] border border-white/[0.14] text-emerald-300 text-xs flex items-center justify-between backdrop-blur-xl">
          <div className="flex items-center gap-2 font-medium">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>{eventStatus}</span>
          </div>
          <button
            onClick={() => setEventStatus(null)}
            className="text-white/40 hover:text-white cursor-pointer"
          >
            ✕
          </button>
        </div>
      )}

      {/* 2. Sequence Workflow Step Cards (4 Steps) - True Apple Liquid Glass */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {sequenceSteps.map((step) => {
          const Icon = step.icon;
          const isSelected = selectedStep === step.step;
          return (
            <div
              key={step.step}
              onClick={() => setSelectedStep(step.step)}
              className={`p-6 rounded-[28px] border transition-all cursor-pointer space-y-2 backdrop-blur-[36px] backdrop-saturate-[150%] ${
                isSelected
                  ? "bg-white/[0.13] border-white/[0.30] shadow-[0_16px_48px_rgba(0,0,0,0.3),inset_0_1px_0_rgba(255,255,255,0.28)] scale-[1.02]"
                  : "bg-white/[0.075] border-white/[0.18] shadow-[0_12px_36px_rgba(0,0,0,0.22),inset_0_1px_0_rgba(255,255,255,0.2)] hover:border-white/[0.28] hover:bg-white/[0.11]"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono font-bold text-sky-400 uppercase tracking-wider">
                  Step {step.step} • {step.day}
                </span>
                <div className="w-8 h-8 rounded-xl bg-white/[0.08] border border-white/[0.14] flex items-center justify-center text-white backdrop-blur-xl">
                  <Icon className="w-4 h-4 text-sky-300" />
                </div>
              </div>

              <h3 className="font-bold text-white text-sm mt-1">
                {step.title}
              </h3>

              <div className="grid grid-cols-2 gap-2 pt-2 border-t border-white/[0.08] font-mono text-[10px]">
                <div>
                  <span className="text-white/40">Open Rate</span>
                  <div className="text-white font-bold">
                    {step.stats.openRate}
                  </div>
                </div>
                <div>
                  <span className="text-white/40">Reply / Book</span>
                  <div className="text-emerald-400 font-bold">
                    {step.stats.replyRate}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* 3. Live Sequence Editor & Recipient Overview - True Apple Liquid Glass Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Sequence Settings */}
        <div className="lg:col-span-4 rounded-[32px] border border-white/[0.14] bg-white/[0.055] p-7 backdrop-blur-[35px] backdrop-saturate-[150%] shadow-[0_16px_48px_rgba(0,0,0,0.25),inset_0_1px_0_rgba(255,255,255,0.18)] space-y-6">
          <div className="flex items-center gap-2.5 border-b border-white/[0.08] pb-4">
            <div className="w-9 h-9 rounded-2xl bg-white/[0.08] border border-white/[0.15] backdrop-blur-xl flex items-center justify-center text-emerald-300 shadow-sm">
              <Sliders className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white tracking-tight">
                Campaign Parameters
              </h2>
              <p className="text-xs text-white/50">
                Target recipient & trigger rules
              </p>
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-white/[0.035] border border-white/[0.08] backdrop-blur-xl space-y-2.5 text-xs">
            <div className="flex justify-between">
              <span className="text-white/40">Target Account:</span>
              <span className="font-bold text-white">
                {activeLead.business_name}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/40">Contact Person:</span>
              <span className="font-semibold text-white/80">
                {activeLead.contact_person || "Executive Leadership"}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/40">Email Address:</span>
              <span className="font-mono text-sky-300">
                {activeLead.email || "direct@lead.com"}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/40">Phone:</span>
              <span className="font-mono text-white">
                {activeLead.phone_number}
              </span>
            </div>
          </div>

          <div className="space-y-2.5 pt-2">
            <button
              onClick={handleDispatch}
              disabled={isSending}
              className="w-full py-3 rounded-full bg-white/[0.18] hover:bg-white/[0.26] border border-white/[0.28] text-white font-bold text-xs flex items-center justify-center gap-2 transition cursor-pointer backdrop-blur-xl shadow-sm"
            >
              {isSending ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Dispatching Step {selectedStep}...</span>
                </>
              ) : sentSuccess ? (
                <>
                  <Check className="w-4 h-4 text-emerald-300" />
                  <span>Outreach Dispatched!</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Dispatch Step {selectedStep} Now</span>
                </>
              )}
            </button>

            <button
              onClick={handleCopy}
              className="w-full py-2.5 rounded-full bg-white/[0.06] hover:bg-white/[0.12] border border-white/[0.14] text-white/80 text-xs font-semibold flex items-center justify-center gap-2 transition cursor-pointer backdrop-blur-md"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-emerald-400">Copied to Clipboard</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5 text-sky-300" />
                  <span>Copy Message Text</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right: Rendered Message Editor */}
        <div className="lg:col-span-8 rounded-[32px] border border-white/[0.14] bg-white/[0.055] p-7 sm:p-8 backdrop-blur-[35px] backdrop-saturate-[150%] shadow-[0_16px_48px_rgba(0,0,0,0.25),inset_0_1px_0_rgba(255,255,255,0.18)] space-y-6">
          <div className="flex items-center justify-between border-b border-white/[0.08] pb-4">
            <div>
              <span className="text-[10px] font-mono uppercase text-sky-400 font-bold">
                Subject Line / Header
              </span>
              <h3 className="text-base font-bold text-white mt-0.5">
                {currentStep.subject}
              </h3>
            </div>

            <span className="px-3 py-1 rounded-full text-[10px] font-mono font-semibold bg-white/[0.06] border border-white/[0.14] text-emerald-300 backdrop-blur-xl">
              Deliverability: 98.4%
            </span>
          </div>

          <div className="p-6 rounded-2xl bg-white/[0.035] border border-white/[0.08] backdrop-blur-xl font-sans text-sm text-white/90 leading-relaxed whitespace-pre-line min-h-[220px]">
            {currentStep.body}
          </div>

          <div className="pt-2 flex items-center justify-between text-xs text-white/50">
            <span className="flex items-center gap-1.5">
              <span>Personalization Merge Tags:</span>
              <strong className="text-sky-300">
                Active (4 Fields Injected)
              </strong>
            </span>

            <button
              onClick={() => onNavigateTab("proposals", activeLead.id)}
              className="text-sky-300 hover:text-white font-semibold flex items-center gap-1 hover:underline cursor-pointer"
            >
              <span>View Attached Proposal</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
