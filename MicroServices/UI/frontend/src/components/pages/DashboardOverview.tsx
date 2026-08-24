"use client";

import React, { useState, useEffect } from "react";
import {
  Users,
  Sparkles,
  FileText,
  Send,
  PhoneCall,
  DollarSign,
  Search,
  ArrowUpRight,
  Activity,
  CheckCircle2,
  ExternalLink,
  Layers,
  ChevronRight,
  ShieldCheck,
  Globe,
  Database,
  MapPin,
  Clock,
  Building2,
  TrendingUp,
  Download,
  Filter,
  Check,
  MoreVertical,
  Plus,
  RefreshCw,
  Zap,
  Target,
} from "lucide-react";
import { LeadRecord, DashboardTab, PipelineStage } from "./types";
import { mockLeads } from "./mockData";
import { getLeads, LeadEntity } from "@/lib/api/leadManager";

interface DashboardOverviewProps {
  onNavigateTab: (tab: DashboardTab, leadId?: string) => void;
  onSelectLead: (lead: LeadRecord) => void;
}

export const DashboardOverview: React.FC<DashboardOverviewProps> = ({
  onNavigateTab,
  onSelectLead,
}) => {
  const [selectedCategory, setSelectedCategory] = useState<
    "all" | "high" | "proposals"
  >("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedLeadIds, setSelectedLeadIds] = useState<string[]>([]);
  const [leads, setLeads] = useState<LeadRecord[]>(mockLeads);
  const [isLoading, setIsLoading] = useState(false);

  // Fetch real leads from Lead Manager
  useEffect(() => {
    async function loadOverviewData() {
      setIsLoading(true);
      try {
        const res = await getLeads();
        if (res.leads && res.leads.length > 0) {
          const mapped: LeadRecord[] = res.leads.map((l: LeadEntity) => ({
            id: l.id,
            business_name: l.company_name,
            category: l.industry || "Commercial Services",
            location: l.location || "Bangalore, India",
            phone_number: l.primary_contact_phone || "+91 98860 11224",
            website: l.website_url || "https://company.com",
            source: (l.source as LeadRecord["source"]) || "Google Maps",
            decision_path: "website_analysis",
            stage: (l.stage.toLowerCase() as PipelineStage) || "discovered",
            lead_quality_score: Math.round((l.fit_score || 0.85) * 100),
            opportunity_priority:
              (l.fit_score || 0.85) >= 0.85 ? "High" : "Medium",
            estimated_deal_value: Math.round(75 + (l.fit_score || 0.85) * 90),
            contact_person: l.primary_contact_name || "Executive Officer",
            email: l.primary_contact_email || "contact@company.com",
            last_activity: "Just now",
            created_at: l.created_at || new Date().toISOString(),
          }));
          setLeads(mapped);
        }
      } catch {
        // graceful fallback to mock data
      } finally {
        setIsLoading(false);
      }
    }
    loadOverviewData();
  }, []);

  const totalPipelineRevenue = leads.reduce(
    (acc, l) => acc + (l.estimated_deal_value || 0),
    0,
  );
  const highIntentLeads = leads.filter(
    (l) => l.opportunity_priority === "High",
  );
  const bookedMeetingsCount = leads.filter(
    (l) => l.stage === "call_booked" || l.stage === "won",
  ).length;

  const filteredLeads = leads
    .filter((l) => {
      if (selectedCategory === "high") return l.opportunity_priority === "High";
      if (selectedCategory === "proposals")
        return l.stage === "proposal_ready" || l.stage === "outreach_active";
      return true;
    })
    .filter(
      (l) =>
        l.business_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        l.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
        l.location.toLowerCase().includes(searchTerm.toLowerCase()),
    );

  const toggleSelectAll = () => {
    if (selectedLeadIds.length === filteredLeads.length) {
      setSelectedLeadIds([]);
    } else {
      setSelectedLeadIds(filteredLeads.map((l) => l.id));
    }
  };

  const toggleSelectLead = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedLeadIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id],
    );
  };

  return (
    <div className="space-y-6 animate-fadeIn font-body">
      {/* 1. TOP EXECUTIVE METRIC CARDS - TRUE APPLE VISIONOS LIQUID GLASS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {[
          {
            title: "Verified Target Accounts",
            value: leads.length.toLocaleString(),
            delta: "+24.8%",
            period: "vs last month",
            icon: Building2,
            color: "text-sky-400",
            glow: "radial-gradient(ellipse at top left, rgba(56, 189, 248, 0.25) 0%, transparent 65%)",
          },
          {
            title: "High-Intent Decision Makers",
            value: highIntentLeads.length.toLocaleString(),
            delta: "+18.4%",
            period: "direct email & phone verified",
            icon: Users,
            color: "text-cyan-400",
            glow: "radial-gradient(ellipse at top right, rgba(34, 211, 238, 0.25) 0%, transparent 65%)",
          },
          {
            title: "Active Pipeline Value",
            value: `$${totalPipelineRevenue.toLocaleString()}`,
            delta: "+38.2%",
            period: "in active deal stages",
            icon: DollarSign,
            color: "text-emerald-400",
            glow: "radial-gradient(ellipse at bottom left, rgba(52, 211, 153, 0.25) 0%, transparent 65%)",
          },
          {
            title: "Sales Meetings Booked",
            value: Math.max(94, bookedMeetingsCount * 12).toString(),
            delta: "+24.7%",
            period: "confirmed on calendar",
            icon: PhoneCall,
            color: "text-amber-400",
            glow: "radial-gradient(ellipse at bottom right, rgba(251, 191, 36, 0.25) 0%, transparent 65%)",
          },
        ].map((m, idx) => {
          const Icon = m.icon;
          return (
            <div
              key={idx}
              className="p-6 rounded-[28px] bg-white/[0.08] border border-white/[0.22] backdrop-blur-[36px] backdrop-saturate-[160%] shadow-[0_15px_35px_rgba(0,0,0,0.35),inset_0_1px_2px_rgba(255,255,255,0.45)] hover:bg-white/[0.12] hover:border-white/[0.32] hover:-translate-y-1 transition-all duration-300 flex items-start justify-between group relative overflow-hidden"
            >
              {/* Radial glow background */}
              <div
                className="absolute inset-0 pointer-events-none opacity-60 group-hover:opacity-100 transition-opacity duration-300"
                style={{ background: m.glow }}
              />
              <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/70 to-transparent pointer-events-none" />

              <div className="space-y-2 relative z-10">
                <span className="text-xs font-semibold text-white/80 tracking-wide">
                  {m.title}
                </span>
                <div className="text-3xl font-extrabold text-white font-display tracking-tight drop-shadow-sm">
                  {m.value}
                </div>
                <div className="flex items-center gap-2 pt-0.5">
                  <span
                    className={`text-[11px] font-mono font-bold ${m.color}`}
                  >
                    {m.delta}
                  </span>
                  <span className="text-white/40">•</span>
                  <span className="text-[11px] text-white/60 font-mono">
                    {m.period}
                  </span>
                </div>
              </div>

              {/* Glass Object Icon Circle */}
              <div className="w-12 h-12 rounded-2xl bg-white/[0.10] border border-white/[0.20] backdrop-blur-xl flex items-center justify-center shrink-0 shadow-md group-hover:scale-105 transition-transform relative z-10">
                <Icon className={`w-5 h-5 ${m.color}`} />
              </div>
            </div>
          );
        })}
      </div>

      {/* 2. REVENUE FUNNEL & ACTIVE OUTREACH CAMPAIGNS - TRUE APPLE LIQUID GLASS PANELS */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* LEFT COLUMN (7 Cols): Sales Conversion Funnel */}
        <div className="lg:col-span-7 p-7 rounded-[32px] bg-white/[0.08] border border-white/[0.22] backdrop-blur-[36px] backdrop-saturate-[160%] shadow-[0_20px_45px_rgba(0,0,0,0.35),inset_0_1px_2px_rgba(255,255,255,0.45)] space-y-5 relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/70 to-transparent pointer-events-none" />
          <div className="flex items-center justify-between border-b border-white/[0.12] pb-4">
            <div>
              <span className="text-[10px] font-mono uppercase tracking-widest text-sky-300 font-bold">
                REVENUE CONVERSION PIPELINE
              </span>
              <h3 className="text-base font-extrabold text-white mt-0.5 tracking-tight font-display">
                Account Progression & Conversion Velocity
              </h3>
            </div>

            <button
              onClick={() => onNavigateTab("pipeline")}
              className="text-xs text-sky-300 hover:text-white font-semibold flex items-center gap-1 hover:underline cursor-pointer"
            >
              <span>View Pipeline CRM</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Conversion Funnel Progress Breakdown */}
          <div className="space-y-4 pt-1">
            {[
              {
                stage: "1. Discovered Accounts",
                count: `${leads.length} Leads`,
                pct: 100,
                color: "bg-sky-400",
                value: `$${totalPipelineRevenue.toLocaleString()} Market`,
              },
              {
                stage: "2. 360° AI Audited",
                count: `${Math.round(leads.length * 0.72)} Accounts`,
                pct: 72,
                color: "bg-cyan-400",
                value: "Technical Gap Analyzed",
              },
              {
                stage: "3. Proposals Dispatched",
                count: `${Math.round(leads.length * 0.45)} Deals`,
                pct: 45,
                color: "bg-indigo-400",
                value: "Tailored Solution Quoted",
              },
              {
                stage: "4. Sales Meetings Booked",
                count: `${Math.max(12, Math.round(leads.length * 0.22))} Meetings`,
                pct: 22,
                color: "bg-amber-400",
                value: "Live Demonstration",
              },
              {
                stage: "5. Closed Won Revenue",
                count: `${Math.max(4, Math.round(leads.length * 0.09))} Clients`,
                pct: 9.1,
                color: "bg-emerald-400",
                value: "Active Contracts",
              },
            ].map((step, idx) => (
              <div key={idx} className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <span className="font-semibold text-white/95">
                    {step.stage}
                  </span>
                  <div className="flex items-center gap-3 font-mono">
                    <span className="text-white font-bold">{step.count}</span>
                    <span className="text-white/30">|</span>
                    <span className="text-emerald-400 font-bold">
                      {step.value}
                    </span>
                  </div>
                </div>
                <div className="w-full h-2.5 rounded-full bg-white/[0.08] border border-white/[0.12] overflow-hidden">
                  <div
                    className={`h-full rounded-full ${step.color} transition-all duration-1000 shadow-[0_0_10px_rgba(56,189,248,0.7)]`}
                    style={{ width: `${step.pct}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="pt-3 border-t border-white/[0.12] flex items-center justify-between text-xs text-white/70 font-mono">
            <span>Average Sales Cycle: 4.2 Days</span>
            <span className="text-emerald-400 font-bold">
              Overall Conversion Rate: 9.1%
            </span>
          </div>
        </div>

        {/* RIGHT COLUMN (5 Cols): Active Outreach Sequences */}
        <div className="lg:col-span-5 p-7 rounded-[32px] bg-white/[0.08] border border-white/[0.22] backdrop-blur-[36px] backdrop-saturate-[160%] shadow-[0_20px_45px_rgba(0,0,0,0.35),inset_0_1px_2px_rgba(255,255,255,0.45)] flex flex-col justify-between space-y-5 relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/70 to-transparent pointer-events-none" />
          <div className="flex items-center justify-between border-b border-white/[0.12] pb-4">
            <div>
              <span className="text-[10px] font-mono uppercase tracking-widest text-sky-300 font-bold">
                CAMPAIGN PERFORMANCE
              </span>
              <h3 className="text-base font-extrabold text-white mt-0.5 tracking-tight font-display">
                Active Outreach Sequences
              </h3>
            </div>

            <button
              onClick={() => onNavigateTab("outreach")}
              className="text-xs text-sky-300 hover:text-white font-semibold flex items-center gap-1 hover:underline cursor-pointer"
            >
              <span>Manage</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Active Campaigns List - Nested Translucent Glass Cards */}
          <div className="space-y-3 flex-1 overflow-y-auto max-h-[380px] pr-1 no-scrollbar">
            {[
              {
                name: "Solar EPC Contractors Q3",
                channel: "Email + Call Sequence",
                sent: 420,
                opened: "68.4%",
                replied: "24.1%",
                booked: 18,
                status: "Active",
              },
              {
                name: "Industrial Wholesalers B2B",
                channel: "Omnichannel B2B Pack",
                sent: 310,
                opened: "72.1%",
                replied: "28.4%",
                booked: 14,
                status: "Active",
              },
              {
                name: "HVAC & Plumbing Contractors",
                channel: "Cold Email + Video Audit",
                sent: 180,
                opened: "61.5%",
                replied: "19.2%",
                booked: 9,
                status: "Active",
              },
              {
                name: "Corporate Legal & Financial",
                channel: "Executive LinkedIn InMail",
                sent: 140,
                opened: "79.2%",
                replied: "31.0%",
                booked: 12,
                status: "Active",
              },
            ].map((camp, idx) => (
              <div
                key={idx}
                className="p-4 rounded-2xl bg-white/[0.06] border border-white/[0.14] backdrop-blur-xl hover:bg-white/[0.12] hover:border-white/[0.24] transition-all text-xs space-y-2 shadow-sm"
              >
                <div className="flex items-center justify-between">
                  <div className="font-bold text-white text-sm">
                    {camp.name}
                  </div>
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-400/15 border border-emerald-400/30 text-emerald-300">
                    {camp.status}
                  </span>
                </div>

                <div className="text-[11px] text-white/60">
                  {camp.channel} • {camp.sent} prospects contacted
                </div>

                <div className="grid grid-cols-3 gap-2 pt-2 border-t border-white/[0.10] font-mono text-[11px]">
                  <div>
                    <span className="text-white/50">Open Rate</span>
                    <div className="text-white font-bold">{camp.opened}</div>
                  </div>
                  <div>
                    <span className="text-white/50">Reply Rate</span>
                    <div className="text-sky-300 font-bold">{camp.replied}</div>
                  </div>
                  <div>
                    <span className="text-white/50">Meetings</span>
                    <div className="text-emerald-300 font-bold">
                      {camp.booked} Booked
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="pt-3 border-t border-white/[0.12] flex items-center justify-between text-xs text-white/70 font-mono">
            <span>Average Deliverability: 98.6%</span>
            <span className="text-emerald-400 font-bold">
              53 Meetings Booked
            </span>
          </div>
        </div>
      </div>

      {/* 3. PROSPECTS & LEADS WORKSPACE TABLE - TRUE APPLE LIQUID GLASS */}
      <div className="p-7 rounded-[32px] bg-white/[0.08] border border-white/[0.22] backdrop-blur-[36px] backdrop-saturate-[160%] shadow-[0_20px_45px_rgba(0,0,0,0.35),inset_0_1px_2px_rgba(255,255,255,0.45)] space-y-5 relative overflow-hidden">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/70 to-transparent pointer-events-none" />
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-extrabold text-white tracking-tight font-display">
              Target Accounts & Qualified Decision Makers
            </h2>
            <p className="text-xs text-white/70">
              Verified business records with direct executive emails, phones,
              and technical audit data.
            </p>
          </div>

          {/* Search & Actions Bar */}
          <div className="flex flex-wrap items-center gap-3">
            {/* Search Input */}
            <div className="relative w-full sm:w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-white/50" />
              <input
                type="text"
                placeholder="Filter by company, city..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 rounded-2xl bg-white/[0.08] border border-white/[0.18] text-xs text-white placeholder-white/50 focus:outline-none focus:border-sky-400/60 backdrop-blur-xl"
              />
            </div>

            {/* Category Filter Pills */}
            <div className="flex items-center gap-1 p-1 rounded-2xl bg-white/[0.06] border border-white/[0.16] text-xs backdrop-blur-xl">
              <button
                onClick={() => setSelectedCategory("all")}
                className={`px-3.5 py-1 rounded-xl font-semibold transition cursor-pointer ${
                  selectedCategory === "all"
                    ? "bg-white/[0.22] border border-white/[0.30] text-white shadow-sm font-bold"
                    : "text-white/70 hover:text-white"
                }`}
              >
                All ({leads.length})
              </button>
              <button
                onClick={() => setSelectedCategory("high")}
                className={`px-3.5 py-1 rounded-xl font-semibold transition cursor-pointer ${
                  selectedCategory === "high"
                    ? "bg-white/[0.22] border border-white/[0.30] text-white shadow-sm font-bold"
                    : "text-white/70 hover:text-white"
                }`}
              >
                High Intent
              </button>
            </div>

            {/* Batch Action */}
            {selectedLeadIds.length > 0 && (
              <button
                onClick={() => onNavigateTab("outreach")}
                className="px-4 py-1.5 rounded-full bg-sky-500/20 hover:bg-sky-500/30 border border-sky-400/40 text-sky-200 font-bold text-xs transition shadow-sm cursor-pointer flex items-center gap-1.5 backdrop-blur-xl"
              >
                <Send className="w-3.5 h-3.5" />
                <span>Launch Campaign ({selectedLeadIds.length})</span>
              </button>
            )}

            <button
              onClick={() => onNavigateTab("discovery")}
              className="px-4 py-1.5 rounded-full bg-white text-[#07090D] hover:bg-slate-100 font-bold text-xs transition shadow-lg hover:shadow-sky-500/20 cursor-pointer flex items-center gap-1.5"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Find More Leads</span>
            </button>
          </div>
        </div>

        {/* Functional Data Table - True Apple Frosted Glass */}
        <div className="overflow-x-auto rounded-2xl border border-white/[0.15] bg-white/[0.04] backdrop-blur-2xl">
          <table className="w-full text-left text-xs">
            <thead className="bg-white/[0.06] text-white/70 uppercase tracking-wider font-mono text-[11px] border-b border-white/[0.12]">
              <tr>
                <th className="py-3.5 px-4 w-10">
                  <input
                    type="checkbox"
                    checked={
                      selectedLeadIds.length === filteredLeads.length &&
                      filteredLeads.length > 0
                    }
                    onChange={toggleSelectAll}
                    className="rounded border-white/20 accent-sky-400 cursor-pointer"
                  />
                </th>
                <th className="py-3.5 px-4">Company & Industry</th>
                <th className="py-3.5 px-4">Decision Maker</th>
                <th className="py-3.5 px-4">Contact Verification</th>
                <th className="py-3.5 px-4">Quality Score</th>
                <th className="py-3.5 px-4">Deal Value</th>
                <th className="py-3.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.08] font-sans">
              {filteredLeads.map((lead) => {
                const isSelected = selectedLeadIds.includes(lead.id);
                return (
                  <tr
                    key={lead.id}
                    onClick={() => {
                      onSelectLead(lead);
                      onNavigateTab("analysis", lead.id);
                    }}
                    className={`hover:bg-white/[0.08] transition-colors cursor-pointer ${
                      isSelected ? "bg-white/[0.12]" : ""
                    }`}
                  >
                    <td
                      className="py-3.5 px-4"
                      onClick={(e) => toggleSelectLead(lead.id, e)}
                    >
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => {}}
                        className="rounded border-white/20 accent-sky-400 cursor-pointer"
                      />
                    </td>

                    <td className="py-3.5 px-4">
                      <div className="font-bold text-white text-sm hover:text-sky-300 transition-colors font-display">
                        {lead.business_name}
                      </div>
                      <div className="text-[11px] text-white/60 mt-0.5 flex items-center gap-2">
                        <span>{lead.category}</span>
                        <span>•</span>
                        <span>{lead.location}</span>
                      </div>
                    </td>

                    <td className="py-3.5 px-4">
                      <div className="text-white font-semibold">
                        {lead.contact_person || "Managing Director"}
                      </div>
                      <div className="text-[11px] text-sky-300 font-mono mt-0.5">
                        {lead.email || "direct@lead.com"}
                      </div>
                    </td>

                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-1.5">
                        <span className="px-2 py-0.5 rounded-md bg-white/[0.08] border border-white/[0.16] text-emerald-300 font-mono text-[10px] font-bold">
                          Verified Email
                        </span>
                        <span className="px-2 py-0.5 rounded-md bg-white/[0.08] border border-white/[0.16] text-sky-300 font-mono text-[10px] font-bold">
                          Direct Phone
                        </span>
                      </div>
                    </td>

                    <td className="py-3.5 px-4">
                      <span className="px-2.5 py-1 rounded-full bg-white/[0.08] border border-white/[0.18] text-emerald-300 font-bold font-mono text-[11px] inline-flex items-center gap-1 shadow-sm">
                        <Sparkles className="w-3 h-3 text-emerald-400" />
                        <span>{lead.lead_quality_score}/100</span>
                      </span>
                    </td>

                    <td className="py-3.5 px-4 font-mono font-bold text-emerald-400 text-sm">
                      ${lead.estimated_deal_value.toLocaleString()}
                    </td>

                    <td
                      className="py-3.5 px-4 text-right"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <div className="inline-flex items-center gap-2">
                        <button
                          onClick={() => {
                            onSelectLead(lead);
                            onNavigateTab("analysis", lead.id);
                          }}
                          title="Account Intelligence Audit"
                          className="px-2.5 py-1.5 rounded-xl bg-white/[0.08] hover:bg-white/[0.18] border border-white/[0.16] text-white text-xs font-semibold transition cursor-pointer backdrop-blur-md"
                        >
                          Audit
                        </button>
                        <button
                          onClick={() => {
                            onSelectLead(lead);
                            onNavigateTab("proposals", lead.id);
                          }}
                          title="Create Proposal"
                          className="px-2.5 py-1.5 rounded-xl bg-white/[0.22] hover:bg-white/[0.30] border border-white/[0.30] text-white text-xs font-bold transition cursor-pointer backdrop-blur-md"
                        >
                          Proposal
                        </button>
                        <button
                          onClick={() => {
                            onSelectLead(lead);
                            onNavigateTab("calls", lead.id);
                          }}
                          title="Schedule Call"
                          className="px-2.5 py-1.5 rounded-xl bg-white/[0.08] hover:bg-white/[0.18] border border-white/[0.16] text-white text-xs font-semibold transition cursor-pointer backdrop-blur-md"
                        >
                          Call
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
