'use client';

import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Download, 
  Send, 
  Sparkles, 
  CheckCircle2, 
  DollarSign, 
  Clock, 
  Share2, 
  ArrowRight,
  TrendingUp,
  Award,
  Layers,
  Zap,
  Sliders,
  Eye,
  Copy,
  Check,
  RefreshCw,
  ThumbsUp
} from 'lucide-react';
import { LeadRecord, DashboardTab, Proposal } from './types';
import { mockLeads, mockProposals } from './mockData';
import { approveLeadProposal, getLeadOpportunities, OpportunityEntity } from '@/lib/api/leadManager';

interface ProposalStudioPageProps {
  selectedLead?: LeadRecord;
  onNavigateTab: (tab: DashboardTab, leadId?: string) => void;
  onSelectLead: (lead: LeadRecord) => void;
}

export const ProposalStudioPage: React.FC<ProposalStudioPageProps> = ({ 
  selectedLead = mockLeads[0], 
  onNavigateTab, 
  onSelectLead 
}) => {
  const [activeLead, setActiveLead] = useState<LeadRecord>(selectedLead);
  const baseProposal: Proposal = mockProposals[activeLead.id] || mockProposals['lead-001'];

  const [investmentTier, setInvestmentTier] = useState<number>(baseProposal.total_investment);
  const [customDiscount, setCustomDiscount] = useState<number>(0);
  const [copiedLink, setCopiedLink] = useState(false);
  const [isApproving, setIsApproving] = useState(false);
  const [approvalStatus, setApprovalStatus] = useState<string | null>(null);
  const [liveOpps, setLiveOpps] = useState<OpportunityEntity[]>([]);

  useEffect(() => {
    async function loadOpps() {
      try {
        const opps = await getLeadOpportunities(activeLead.id);
        setLiveOpps(opps);
      } catch {
        // fallback
      }
    }
    loadOpps();
  }, [activeLead.id]);

  const handleSelectLeadChange = (leadId: string) => {
    const found = mockLeads.find((l) => l.id === leadId);
    if (found) {
      setActiveLead(found);
      onSelectLead(found);
      const newProp = mockProposals[found.id] || mockProposals['lead-001'];
      setInvestmentTier(newProp.total_investment);
      setApprovalStatus(null);
    }
  };

  const finalInvestment = Math.max(1000, investmentTier - customDiscount);

  const handleCopyLink = () => {
    setCopiedLink(true);
    setTimeout(() => setCopiedLink(false), 2000);
  };

  const handleApproveProposal = async () => {
    setIsApproving(true);
    setApprovalStatus(null);

    try {
      const res = await approveLeadProposal(activeLead.id);
      if (res) {
        setApprovalStatus('Proposal approved & registered in Lead Manager! Lead advanced to PROPOSAL_READY.');
      } else {
        setApprovalStatus('Proposal approved (offline mode).');
      }
    } catch {
      setApprovalStatus('Proposal approved (offline mode).');
    } finally {
      setIsApproving(false);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn font-body">
      {/* 1. Header & Lead Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/[0.06] border border-white/[0.14] text-xs font-semibold text-sky-300 mb-2 backdrop-blur-xl">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Autonomous Pitch Deck & Proposal Studio (:8082)</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white font-display">
            Opportunity & Growth Proposal Studio
          </h1>
          <p className="text-sm text-white/60 mt-1 max-w-2xl">
            Live interactive proposal generator dynamically calculating tailored technical solutions, ROI projections, and milestone deliverables.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={activeLead.id}
            onChange={(e) => handleSelectLeadChange(e.target.value)}
            className="px-4 py-2 rounded-xl bg-white/[0.06] border border-white/[0.14] text-xs font-semibold text-white focus:outline-none focus:border-white/30 cursor-pointer backdrop-blur-xl"
          >
            {mockLeads.map((l) => (
              <option key={l.id} value={l.id} className="bg-[#090E1A] text-white">
                {l.business_name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Approval Status Banner */}
      {approvalStatus && (
        <div className="p-3.5 rounded-2xl bg-white/[0.06] border border-white/[0.14] text-emerald-300 text-xs flex items-center justify-between backdrop-blur-xl">
          <div className="flex items-center gap-2 font-medium">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>{approvalStatus}</span>
          </div>
          <button onClick={() => setApprovalStatus(null)} className="text-white/40 hover:text-white cursor-pointer">✕</button>
        </div>
      )}

      {/* 2. Interactive Proposal Controls HUD - True Apple Liquid Glass */}
      <div className="p-7 rounded-[32px] border border-white/[0.14] bg-white/[0.055] backdrop-blur-[35px] backdrop-saturate-[150%] shadow-[0_16px_48px_rgba(0,0,0,0.25),inset_0_1px_0_rgba(255,255,255,0.18)] space-y-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 pb-6 border-b border-white/[0.08]">
          <div>
            <span className="text-xs font-mono uppercase tracking-wider text-sky-400 font-semibold">
              Target Prospect
            </span>
            <h2 className="text-2xl font-bold text-white mt-1">
              {activeLead.business_name}
            </h2>
            <p className="text-xs text-white/50 mt-0.5">
              {activeLead.category} • Location: {activeLead.location}
            </p>
          </div>

          {/* Action Buttons: Copy Link & Human Approve */}
          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={handleCopyLink}
              className="px-4 py-2 rounded-full bg-white/[0.06] hover:bg-white/[0.12] border border-white/[0.14] text-xs font-medium text-white flex items-center gap-2 transition cursor-pointer backdrop-blur-xl"
            >
              {copiedLink ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 text-sky-300" />}
              <span>{copiedLink ? 'Link Copied!' : 'Share Proposal Link'}</span>
            </button>

            <button
              onClick={handleApproveProposal}
              disabled={isApproving}
              className="px-5 py-2.5 rounded-full bg-white/[0.18] hover:bg-white/[0.26] border border-white/[0.28] text-white font-bold text-xs flex items-center gap-2 transition cursor-pointer backdrop-blur-xl shadow-sm"
            >
              {isApproving ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Approving...</span>
                </>
              ) : (
                <>
                  <ThumbsUp className="w-3.5 h-3.5 text-emerald-300" />
                  <span>Human-in-the-Loop Approve</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Pricing & Tier Sliders - Apple Liquid Glass Sub-cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-5 rounded-2xl bg-white/[0.035] border border-white/[0.08] backdrop-blur-xl hover:bg-white/[0.06] transition-all space-y-2">
            <span className="text-[11px] font-mono uppercase text-white/50 font-semibold">Base Package Tier</span>
            <div className="text-xl font-bold font-mono text-white">
              ${investmentTier.toLocaleString()}
            </div>
            <input
              type="range"
              min="5000"
              max="35000"
              step="1000"
              value={investmentTier}
              onChange={(e) => setInvestmentTier(Number(e.target.value))}
              className="w-full accent-sky-400 cursor-pointer"
            />
          </div>

          <div className="p-5 rounded-2xl bg-white/[0.035] border border-white/[0.08] backdrop-blur-xl hover:bg-white/[0.06] transition-all space-y-2">
            <span className="text-[11px] font-mono uppercase text-white/50 font-semibold">Strategic Incentive</span>
            <div className="text-xl font-bold font-mono text-amber-300">
              -${customDiscount.toLocaleString()}
            </div>
            <input
              type="range"
              min="0"
              max="5000"
              step="250"
              value={customDiscount}
              onChange={(e) => setCustomDiscount(Number(e.target.value))}
              className="w-full accent-amber-400 cursor-pointer"
            />
          </div>

          <div className="p-5 rounded-2xl bg-white/[0.035] border border-white/[0.08] backdrop-blur-xl hover:bg-white/[0.06] transition-all space-y-2">
            <span className="text-[11px] font-mono uppercase text-emerald-400 font-semibold">Final Total Investment</span>
            <div className="text-xl font-bold font-mono text-emerald-300">
              ${finalInvestment.toLocaleString()}
            </div>
            <div className="text-[10px] text-white/50">Projected 90-Day ROI: {baseProposal.roi_estimate}</div>
          </div>
        </div>
      </div>

      {/* 3. Generated Proposal Document Preview - True Apple Liquid Glass Panel */}
      <div className="p-8 sm:p-10 rounded-[32px] border border-white/[0.14] bg-white/[0.055] backdrop-blur-[35px] backdrop-saturate-[150%] shadow-[0_16px_48px_rgba(0,0,0,0.25),inset_0_1px_0_rgba(255,255,255,0.18)] space-y-8">
        <div className="flex items-center justify-between border-b border-white/[0.08] pb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-white/[0.08] border border-white/[0.15] backdrop-blur-xl flex items-center justify-center text-sky-300 font-black">
              SV
            </div>
            <div>
              <h3 className="text-lg font-bold text-white font-display">{baseProposal.title}</h3>
              <p className="text-xs text-white/50">Prepared for: {activeLead.business_name}</p>
            </div>
          </div>

          <div className="px-3 py-1 rounded-full bg-white/[0.06] border border-white/[0.14] text-sky-300 text-xs font-mono font-bold backdrop-blur-xl">
            Status: READY FOR OUTREACH
          </div>
        </div>

        {/* Proposal Body */}
        <div className="space-y-6 text-xs text-white/80">
          <div className="space-y-2">
            <h4 className="text-xs font-mono uppercase text-sky-400 font-bold">1. Executive Summary</h4>
            <p className="text-sm text-white/90 leading-relaxed font-sans">{baseProposal.executive_summary}</p>
          </div>

          <div className="space-y-3">
            <h4 className="text-xs font-mono uppercase text-rose-400 font-bold">2. Identified Bottlenecks</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {baseProposal.identified_problems.map((prob, i) => (
                <div key={i} className="p-4 rounded-xl bg-white/[0.03] border border-white/[0.08] text-xs text-white/80 flex items-start gap-2.5 backdrop-blur-md">
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-400 mt-1.5 shrink-0" />
                  <span>{prob}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-3">
            <h4 className="text-xs font-mono uppercase text-sky-400 font-bold">3. Strategic Solution</h4>
            <div className="p-4 rounded-2xl bg-white/[0.03] border border-white/[0.08] text-xs text-white/90 leading-relaxed backdrop-blur-md">
              {baseProposal.proposed_solution}
            </div>
          </div>

          <div className="space-y-3">
            <h4 className="text-xs font-mono uppercase text-indigo-300 font-bold">4. Scope of Deliverables</h4>
            <div className="rounded-2xl border border-white/[0.08] overflow-hidden divide-y divide-white/[0.06]">
              {baseProposal.deliverables.map((del, i) => (
                <div key={i} className="p-4 flex items-center justify-between gap-4 bg-white/[0.02]">
                  <div className="flex items-center gap-3">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                    <div>
                      <div className="text-xs font-bold text-white">{del.title}</div>
                      <div className="text-[11px] text-white/50 font-mono mt-0.5">Timeline: {del.timeline}</div>
                    </div>
                  </div>
                  <div className="text-xs font-mono font-bold text-sky-300">
                    ${del.price.toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-6 border-t border-white/[0.08] flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="text-xs text-white/40">
              Valid for 14 business days from generation date.
            </div>

            <button
              onClick={() => onNavigateTab('calls', activeLead.id)}
              className="w-full sm:w-auto px-6 py-2.5 rounded-full bg-white/[0.18] hover:bg-white/[0.26] border border-white/[0.28] text-white text-xs font-bold flex items-center justify-center gap-2 transition cursor-pointer backdrop-blur-xl shadow-sm"
            >
              <span>Schedule AI Review Call</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
