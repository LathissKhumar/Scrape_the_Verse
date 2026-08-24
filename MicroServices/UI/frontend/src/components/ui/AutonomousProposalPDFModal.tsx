"use client";

import React, { useState, useEffect, useSyncExternalStore } from "react";
import { createPortal } from "react-dom";
import {
  FileText,
  Download,
  Printer,
  X,
  Sparkles,
  CheckCircle2,
  ExternalLink,
  Calendar,
  Layers,
  ArrowRight,
  ShieldCheck,
  Check,
  Copy,
} from "lucide-react";
import { LeadRecord } from "@/components/pages/types";
import { mockLeads } from "@/components/pages/mockData";

interface AutonomousProposalPDFModalProps {
  isOpen: boolean;
  onClose: () => void;
  lead?: LeadRecord;
}

const emptySubscribe = () => () => {};

export const AutonomousProposalPDFModal: React.FC<
  AutonomousProposalPDFModalProps
> = ({ isOpen, onClose, lead = mockLeads[0] }) => {
  const [activeLead, setActiveLead] = useState<LeadRecord>(lead);
  const [prevLead, setPrevLead] = useState<LeadRecord>(lead);
  const [copied, setCopied] = useState(false);
  const mounted = useSyncExternalStore(
    emptySubscribe,
    () => true,
    () => false,
  );

  if (lead && lead.id !== prevLead?.id) {
    setPrevLead(lead);
    setActiveLead(lead);
  }

  // Lock background scroll & handle ESC key
  useEffect(() => {
    if (!isOpen) return;

    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      document.body.style.overflow = originalOverflow;
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen || !mounted) return null;

  const targetWebsite =
    activeLead.website ||
    `https://${activeLead.business_name.toLowerCase().replace(/[^a-z0-9]/g, "")}.com`;
  const contactName =
    activeLead.contact_person ||
    (activeLead.email ? activeLead.email.split("@")[0] : "Aadhish");
  const currentDate = new Date().toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  });

  const handlePrint = () => {
    window.print();
  };

  const handleCopy = () => {
    setCopied(true);
    navigator.clipboard.writeText(`${targetWebsite}/proposal-deliverable`);
    setTimeout(() => setCopied(false), 2000);
  };

  const modalContent = (
    <div
      className="fixed inset-0 z-[99999] flex items-center justify-center p-3 sm:p-6 md:p-8 bg-black/85 backdrop-blur-2xl animate-fadeIn"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      {/* Container Dialog - Fixed Viewport Centered */}
      <div
        className="relative w-full max-w-4xl bg-[#07090D] border border-white/20 rounded-3xl shadow-[0_30px_100px_rgba(0,0,0,0.9)] overflow-hidden flex flex-col h-[88vh] max-h-[850px] animate-scaleUp"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Top Pinned Control Bar */}
        <div className="flex items-center justify-between px-5 sm:px-6 py-3.5 border-b border-white/10 bg-[#0B0F19]/95 backdrop-blur-xl shrink-0 z-20">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-sky-500/20 border border-sky-400/30 flex items-center justify-center text-sky-400">
              <FileText className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold text-white font-display">
                  Autonomous PDF Deliverable Viewer
                </h3>
                <span className="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 text-[10px] font-mono font-semibold border border-emerald-500/30">
                  GENERATED :8082
                </span>
              </div>
              <p className="text-[11px] text-white/50">
                High-fidelity client audit document synthesized by Layer 6
                Proposal Engine
              </p>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="flex items-center gap-2">
            <select
              value={activeLead.id}
              onChange={(e) => {
                const found = mockLeads.find((l) => l.id === e.target.value);
                if (found) setActiveLead(found);
              }}
              className="hidden sm:block px-3 py-1.5 rounded-xl bg-white/[0.08] border border-white/15 text-xs text-white font-medium focus:outline-none cursor-pointer"
            >
              {mockLeads.map((l) => (
                <option
                  key={l.id}
                  value={l.id}
                  className="bg-[#0B0F19] text-white"
                >
                  {l.business_name}
                </option>
              ))}
            </select>

            <button
              onClick={handleCopy}
              className="px-3 py-1.5 rounded-xl bg-white/[0.08] hover:bg-white/[0.15] border border-white/15 text-xs font-semibold text-white flex items-center gap-1.5 transition cursor-pointer"
            >
              {copied ? (
                <Check className="w-3.5 h-3.5 text-emerald-400" />
              ) : (
                <Copy className="w-3.5 h-3.5 text-sky-300" />
              )}
              <span className="hidden sm:inline">
                {copied ? "Copied" : "Share"}
              </span>
            </button>

            <button
              onClick={handlePrint}
              className="px-3.5 py-1.5 rounded-xl bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold text-xs flex items-center gap-1.5 transition cursor-pointer shadow-lg shadow-sky-500/20"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print / Save PDF</span>
            </button>

            <button
              onClick={onClose}
              className="w-8 h-8 rounded-xl bg-white/10 hover:bg-white/20 text-white/70 hover:text-white flex items-center justify-center transition cursor-pointer ml-1"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Scrollable PDF Document Canvas - Centered White Paper Document */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-8 bg-[#03060E]/90 custom-scrollbar">
          <div
            id="printable-pdf-document"
            className="w-full max-w-2xl mx-auto bg-white text-slate-900 rounded-xl shadow-2xl p-6 sm:p-10 font-sans text-xs sm:text-sm leading-relaxed space-y-7 print:p-0 print:shadow-none print:rounded-none"
            style={{ minHeight: "980px" }}
          >
            {/* Header Tagline */}
            <div className="border-b-2 border-sky-800 pb-3">
              <span className="text-[10px] sm:text-[11px] font-bold tracking-widest uppercase text-sky-700 font-mono">
                AGENCYOS GROWTH INTELLIGENCE
              </span>
              <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight mt-1">
                Autonomous Sales Audit &amp; Proposal
              </h1>
              <p className="text-[11px] text-slate-600 mt-1">
                <span className="font-semibold text-slate-800">
                  Prepared for:
                </span>{" "}
                {activeLead.business_name} |{" "}
                <span className="font-semibold text-slate-800">
                  Target Website:
                </span>{" "}
                <a
                  href={targetWebsite}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sky-700 underline"
                >
                  {targetWebsite}
                </a>
              </p>
            </div>

            {/* 1. Executive Summary & Diagnosis */}
            <div className="space-y-2.5">
              <h2 className="text-sm font-bold text-sky-900 flex items-center gap-2">
                <span>1. Executive Summary &amp; Diagnosis</span>
              </h2>
              <p className="text-[12px] text-slate-700 leading-normal">
                Dear{" "}
                {contactName.charAt(0).toUpperCase() + contactName.slice(1)},
                our autonomous sales intelligence agent evaluated{" "}
                <span className="font-semibold text-slate-900">
                  {activeLead.business_name}
                </span>
                &apos;s digital infrastructure, local search presence, and
                customer conversion funnels. Based on our automated multi-vector
                audit, we identified high-ROI growth opportunities to automate
                inbound lead acquisition, optimize mobile search rankings, and
                increase customer bookings.
              </p>

              {/* Audit Dimension Table */}
              <div className="overflow-hidden rounded-md border border-slate-200 mt-2.5">
                <table className="w-full text-left border-collapse text-[11px] sm:text-xs">
                  <thead>
                    <tr className="bg-sky-900 text-white font-semibold">
                      <th className="py-2 px-3">Audit Dimension</th>
                      <th className="py-2 px-3">Current Score</th>
                      <th className="py-2 px-3">Industry Benchmark</th>
                      <th className="py-2 px-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 text-slate-700">
                    <tr className="hover:bg-slate-50">
                      <td className="py-2 px-3 font-medium">
                        Mobile &amp; Speed Performance
                      </td>
                      <td className="py-2 px-3 font-bold text-slate-900">
                        82 / 100
                      </td>
                      <td className="py-2 px-3">85 / 100</td>
                      <td className="py-2 px-3 font-bold text-emerald-700">
                        OPTIMIZED
                      </td>
                    </tr>
                    <tr className="hover:bg-slate-50">
                      <td className="py-2 px-3 font-medium">
                        Search Engine Visibility (SEO)
                      </td>
                      <td className="py-2 px-3 font-bold text-slate-900">
                        64 / 100
                      </td>
                      <td className="py-2 px-3">90 / 100</td>
                      <td className="py-2 px-3 font-bold text-amber-700">
                        NEEDS UPGRADE
                      </td>
                    </tr>
                    <tr className="hover:bg-slate-50">
                      <td className="py-2 px-3 font-medium">
                        Conversion &amp; Lead Capture
                      </td>
                      <td className="py-2 px-3 font-bold text-slate-900">
                        68.0 / 100
                      </td>
                      <td className="py-2 px-3">95 / 100</td>
                      <td className="py-2 px-3 font-bold text-rose-700">
                        HIGH PRIORITY
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* 2. Recommended Strategic Packages */}
            <div className="space-y-2.5">
              <h2 className="text-sm font-bold text-sky-900">
                2. Recommended Strategic Packages
              </h2>
              <p className="text-[11px] text-slate-600">
                Below are the tailored implementation packages synthesized
                specifically for your business:
              </p>

              {/* Package Deliverables Matrix Table */}
              <div className="overflow-hidden rounded-md border border-slate-200">
                <table className="w-full text-left border-collapse text-[11px]">
                  <thead>
                    <tr className="bg-sky-900 text-white font-semibold">
                      <th className="py-2 px-2.5 w-[28%]">Service Package</th>
                      <th className="py-2 px-2.5 w-[28%]">Problem Solved</th>
                      <th className="py-2 px-2.5 w-[32%]">Key Deliverables</th>
                      <th className="py-2 px-2.5 w-[12%]">Priority</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 text-slate-700">
                    <tr className="hover:bg-slate-50 align-top">
                      <td className="py-2.5 px-2.5 font-bold text-slate-900">
                        24/7 Automated Booking &amp; Lead Capture Funnel
                      </td>
                      <td className="py-2.5 px-2.5 text-slate-600">
                        No automated instant booking mechanism to capture
                        high-intent inquiries 24/7.
                      </td>
                      <td className="py-2.5 px-2.5 text-slate-600 space-y-0.5">
                        <div>
                          • Instant appointment booking widget integration
                        </div>
                        <div>
                          • Click-to-call and WhatsApp fast-response widget
                        </div>
                        <div>
                          • Automated lead notification &amp; CRM dispatch
                          pipeline
                        </div>
                      </td>
                      <td className="py-2.5 px-2.5 font-bold text-sky-700 whitespace-nowrap">
                        Score: 85.0
                      </td>
                    </tr>

                    <tr className="hover:bg-slate-50 align-top">
                      <td className="py-2.5 px-2.5 font-bold text-slate-900">
                        Core Web Vitals &amp; Speed Boost
                      </td>
                      <td className="py-2.5 px-2.5 text-slate-600">
                        Slow load speeds (70/100) causing customer drop-off
                        before viewing services.
                      </td>
                      <td className="py-2.5 px-2.5 text-slate-600 space-y-0.5">
                        <div>
                          • Image compression and WebP next-gen format
                          conversion
                        </div>
                        <div>• Critical CSS inlining and script deferral</div>
                        <div>
                          • Server TTFB and caching optimization (&lt;1.8s
                          target)
                        </div>
                      </td>
                      <td className="py-2.5 px-2.5 font-bold text-sky-700 whitespace-nowrap">
                        Score: 72.5
                      </td>
                    </tr>

                    <tr className="hover:bg-slate-50 align-top">
                      <td className="py-2.5 px-2.5 font-bold text-slate-900">
                        Website Redesign &amp; Conversion Architecture
                      </td>
                      <td className="py-2.5 px-2.5 text-slate-600">
                        Suboptimal UX, low conversion signals (35/100), and
                        mobile layout barriers.
                      </td>
                      <td className="py-2.5 px-2.5 text-slate-600 space-y-0.5">
                        <div>• Modern, responsive mobile UX overhaul</div>
                        <div>
                          • High-conversion booking and contact architecture
                        </div>
                        <div>• Speed-optimized clean code framework</div>
                        <div>• Brand identity and trust badges integration</div>
                      </td>
                      <td className="py-2.5 px-2.5 font-bold text-sky-700 whitespace-nowrap">
                        Score: 59.5
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* 3. Next Steps & Implementation Roadmap */}
            <div className="space-y-1.5 pt-1">
              <h2 className="text-sm font-bold text-sky-900">
                3. Next Steps &amp; Implementation Roadmap
              </h2>
              <p className="text-[12px] text-slate-700">
                We have reserved 3 dedicated Google Meet slots for a 15-minute
                live demo and implementation walkthrough. Please check your
                calendar invitation email to select your preferred time slot.
              </p>
            </div>

            {/* Document Footer */}
            <div className="pt-4 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between text-[10px] text-slate-400 font-mono gap-1">
              <span>
                Generated autonomously on {currentDate} | AgencyOS Autonomous
                Sales System
              </span>
              <span className="font-semibold text-slate-500">Page 1 of 1</span>
            </div>
          </div>
        </div>

        {/* Modal Bottom Footer */}
        <div className="px-6 py-3 border-t border-white/10 bg-[#0B0F19] flex items-center justify-between text-xs text-white/50 shrink-0 z-20">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>
              Digital signature &amp; audit checksum verified by MicroService
              :8082
            </span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-xl bg-white/10 hover:bg-white/15 text-white font-medium transition cursor-pointer"
          >
            Close Viewer
          </button>
        </div>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
};
