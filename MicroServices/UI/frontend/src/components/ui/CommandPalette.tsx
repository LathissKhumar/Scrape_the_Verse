'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  Sparkles,
  LayoutDashboard,
  Cpu,
  Send,
  PhoneCall,
  Layers,
  Settings,
  RefreshCw,
  Server,
  Building2,
  MapPin,
  ExternalLink,
  ArrowRight,
  Command,
  X,
  Zap,
  CheckCircle2,
  Globe,
  Radio,
  FileText
} from 'lucide-react';
import { DashboardTab, LeadRecord } from '../pages/types';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigateTab: (tab: DashboardTab, leadId?: string) => void;
  onSelectLead: (lead: LeadRecord) => void;
  onProbeHealth: () => void;
  onOpenHealthModal: () => void;
  leads: LeadRecord[];
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({
  isOpen,
  onClose,
  onNavigateTab,
  onSelectLead,
  onProbeHealth,
  onOpenHealthModal,
  leads = [],
}) => {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      setQuery('');
      setSelectedIndex(0);
      setTimeout(() => {
        inputRef.current?.focus();
      }, 50);
    }
  }, [isOpen]);

  // Global shortcut listeners
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        if (isOpen) onClose();
        else onClose(); // parent handles toggle
      }
      if (e.key === 'Escape' && isOpen) {
        e.preventDefault();
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Navigation Items
  const navItems = [
    { id: 'overview' as DashboardTab, label: 'Command Center', icon: LayoutDashboard, category: 'Navigation', shortcut: 'G O' },
    { id: 'discovery' as DashboardTab, label: 'Lead Discovery & Harvesting', icon: Search, category: 'Navigation', shortcut: 'G D' },
    { id: 'analysis' as DashboardTab, label: '360° AI Website Audit', icon: Cpu, category: 'Navigation', shortcut: 'G A' },
    { id: 'proposals' as DashboardTab, label: 'Proposal Studio & Pricing', icon: Sparkles, category: 'Navigation', shortcut: 'G P' },
    { id: 'outreach' as DashboardTab, label: 'Multi-Channel Outreach Hub', icon: Send, category: 'Navigation', shortcut: 'G M' },
    { id: 'calls' as DashboardTab, label: 'Voice Agent (AI SDR Telephony)', icon: PhoneCall, category: 'Navigation', shortcut: 'G V' },
    { id: 'pipeline' as DashboardTab, label: 'Pipeline CRM & Twenty CRM Bridge', icon: Layers, category: 'Navigation', shortcut: 'G C' },
    { id: 'scrapers' as DashboardTab, label: 'DCA Scraper Operations & Self-Healing', icon: Settings, category: 'Navigation', shortcut: 'G S' },
  ];

  // Quick Action Items
  const actionItems = [
    {
      id: 'probe-health',
      label: 'Re-Probe Backend Microservices Swarm',
      category: 'Actions',
      icon: RefreshCw,
      action: () => {
        onProbeHealth();
        onClose();
      },
    },
    {
      id: 'open-health-modal',
      label: 'Open Swarm Health Telemetry Inspector',
      category: 'Actions',
      icon: Server,
      action: () => {
        onOpenHealthModal();
        onClose();
      },
    },
  ];

  // Filter navigation
  const filteredNav = navItems.filter((item) =>
    item.label.toLowerCase().includes(query.toLowerCase())
  );

  // Filter leads
  const filteredLeads = query.trim()
    ? leads.filter(
        (lead) =>
          lead.business_name.toLowerCase().includes(query.toLowerCase()) ||
          (lead.category && lead.category.toLowerCase().includes(query.toLowerCase())) ||
          (lead.location && lead.location.toLowerCase().includes(query.toLowerCase()))
      ).slice(0, 4)
    : leads.slice(0, 3);

  // Filter actions
  const filteredActions = actionItems.filter((item) =>
    item.label.toLowerCase().includes(query.toLowerCase())
  );

  // Combined flat list for keyboard arrow navigation
  const allResults = [
    ...filteredNav.map((n) => ({ type: 'nav' as const, data: n })),
    ...filteredLeads.map((l) => ({ type: 'lead' as const, data: l })),
    ...filteredActions.map((a) => ({ type: 'action' as const, data: a })),
  ];

  const handleSelect = (index: number) => {
    const item = allResults[index];
    if (!item) return;

    if (item.type === 'nav') {
      onNavigateTab(item.data.id);
      onClose();
    } else if (item.type === 'lead') {
      onSelectLead(item.data);
      onNavigateTab('analysis', item.data.id);
      onClose();
    } else if (item.type === 'action') {
      item.data.action();
    }
  };

  const handleInputKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev + 1) % Math.max(1, allResults.length));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev - 1 + allResults.length) % Math.max(1, allResults.length));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      handleSelect(selectedIndex);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.15 }}
          className="fixed inset-0 z-50 flex items-start justify-center pt-24 sm:pt-28 px-4 bg-black/60 backdrop-blur-md"
          onClick={onClose}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -10 }}
            transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className="w-full max-w-2xl rounded-[28px] bg-white/[0.08] border border-white/[0.22] shadow-[0_30px_90px_rgba(0,0,0,0.6),inset_0_1px_0_rgba(255,255,255,0.25)] backdrop-blur-3xl overflow-hidden flex flex-col relative"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Top Atmospheric Glow inside modal */}
            <div className="absolute -top-24 left-1/2 -translate-x-1/2 w-96 h-32 bg-sky-400/20 rounded-full blur-[80px] pointer-events-none" />

            {/* Input Header */}
            <div className="relative p-4 sm:p-5 border-b border-white/10 flex items-center gap-3">
              <Search className="w-5 h-5 text-sky-400 shrink-0" />
              <input
                ref={inputRef}
                type="text"
                value={query}
                onChange={(e) => {
                  setQuery(e.target.value);
                  setSelectedIndex(0);
                }}
                onKeyDown={handleInputKeyDown}
                placeholder="Type a command, jump to a hub, or search leads..."
                className="w-full bg-transparent text-sm sm:text-base text-white placeholder-white/40 focus:outline-none font-sans"
              />
              <div className="flex items-center gap-1.5 shrink-0">
                <kbd className="px-2 py-0.5 rounded-lg bg-white/[0.08] border border-white/[0.12] text-[10px] font-mono text-white/60">
                  ESC
                </kbd>
                <button
                  onClick={onClose}
                  className="p-1 rounded-lg hover:bg-white/10 text-white/50 hover:text-white transition cursor-pointer"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Results List */}
            <div className="max-h-[380px] overflow-y-auto p-2 space-y-4">
              {allResults.length === 0 ? (
                <div className="text-center py-12 text-white/40">
                  <Search className="w-8 h-8 mx-auto mb-2 opacity-40" />
                  <p className="text-sm">No results found for &ldquo;{query}&rdquo;</p>
                  <p className="text-xs text-white/30 mt-1">Try searching for &quot;Audit&quot;, &quot;Discovery&quot;, or a company name</p>
                </div>
              ) : (
                <>
                  {/* Navigation Hubs */}
                  {filteredNav.length > 0 && (
                    <div>
                      <div className="px-3 py-1.5 text-[10px] font-mono uppercase tracking-widest text-white/40">
                        Navigation Hubs
                      </div>
                      <div className="space-y-1">
                        {filteredNav.map((nav, idx) => {
                          const Icon = nav.icon;
                          const flatIndex = idx;
                          const isSelected = selectedIndex === flatIndex;
                          return (
                            <button
                              key={nav.id}
                              onClick={() => {
                                onNavigateTab(nav.id);
                                onClose();
                              }}
                              onMouseEnter={() => setSelectedIndex(flatIndex)}
                              className={`w-full px-3 py-2.5 rounded-2xl flex items-center justify-between text-left transition-all cursor-pointer ${
                                isSelected
                                  ? 'bg-white/[0.14] border border-white/[0.22] text-white shadow-sm'
                                  : 'text-white/70 hover:bg-white/[0.05] border border-transparent'
                              }`}
                            >
                              <div className="flex items-center gap-3">
                                <div className={`w-8 h-8 rounded-xl flex items-center justify-center ${
                                  isSelected ? 'bg-sky-400/20 text-sky-300' : 'bg-white/[0.06] text-white/70'
                                }`}>
                                  <Icon className="w-4 h-4" />
                                </div>
                                <span className="text-xs sm:text-sm font-medium">{nav.label}</span>
                              </div>
                              <span className="text-[10px] font-mono text-white/40">{nav.shortcut}</span>
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  {/* Target Leads */}
                  {filteredLeads.length > 0 && (
                    <div>
                      <div className="px-3 py-1.5 text-[10px] font-mono uppercase tracking-widest text-white/40">
                        Target Accounts & Leads
                      </div>
                      <div className="space-y-1">
                        {filteredLeads.map((lead, idx) => {
                          const flatIndex = filteredNav.length + idx;
                          const isSelected = selectedIndex === flatIndex;
                          return (
                            <button
                              key={lead.id}
                              onClick={() => {
                                onSelectLead(lead);
                                onNavigateTab('analysis', lead.id);
                                onClose();
                              }}
                              onMouseEnter={() => setSelectedIndex(flatIndex)}
                              className={`w-full px-3 py-2.5 rounded-2xl flex items-center justify-between text-left transition-all cursor-pointer ${
                                isSelected
                                  ? 'bg-white/[0.14] border border-white/[0.22] text-white shadow-sm'
                                  : 'text-white/70 hover:bg-white/[0.05] border border-transparent'
                              }`}
                            >
                              <div className="flex items-center gap-3">
                                <div className={`w-8 h-8 rounded-xl flex items-center justify-center font-bold text-xs ${
                                  isSelected ? 'bg-sky-400/20 text-sky-300' : 'bg-white/[0.06] text-white/70'
                                }`}>
                                  {lead.business_name.substring(0, 2).toUpperCase()}
                                </div>
                                <div>
                                  <div className="text-xs sm:text-sm font-medium text-white">{lead.business_name}</div>
                                  <div className="text-[10px] font-mono text-white/50 flex items-center gap-2">
                                    <span>{lead.category || 'Enterprise'}</span>
                                    <span>•</span>
                                    <span>{lead.location || 'India'}</span>
                                  </div>
                                </div>
                              </div>
                              <span className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-white/[0.06] text-sky-300 border border-white/[0.08]">
                                Audit Lead →
                              </span>
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  {/* Quick System Actions */}
                  {filteredActions.length > 0 && (
                    <div>
                      <div className="px-3 py-1.5 text-[10px] font-mono uppercase tracking-widest text-white/40">
                        System Actions
                      </div>
                      <div className="space-y-1">
                        {filteredActions.map((act, idx) => {
                          const Icon = act.icon;
                          const flatIndex = filteredNav.length + filteredLeads.length + idx;
                          const isSelected = selectedIndex === flatIndex;
                          return (
                            <button
                              key={act.id}
                              onClick={act.action}
                              onMouseEnter={() => setSelectedIndex(flatIndex)}
                              className={`w-full px-3 py-2.5 rounded-2xl flex items-center justify-between text-left transition-all cursor-pointer ${
                                isSelected
                                  ? 'bg-white/[0.14] border border-white/[0.22] text-white shadow-sm'
                                  : 'text-white/70 hover:bg-white/[0.05] border border-transparent'
                              }`}
                            >
                              <div className="flex items-center gap-3">
                                <div className={`w-8 h-8 rounded-xl flex items-center justify-center ${
                                  isSelected ? 'bg-sky-400/20 text-sky-300' : 'bg-white/[0.06] text-white/70'
                                }`}>
                                  <Icon className="w-4 h-4" />
                                </div>
                                <span className="text-xs sm:text-sm font-medium">{act.label}</span>
                              </div>
                              <ArrowRight className="w-3.5 h-3.5 text-white/40" />
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>

            {/* Footer hints */}
            <div className="p-3 border-t border-white/10 bg-white/[0.02] flex items-center justify-between text-[11px] font-mono text-white/40 px-4">
              <div className="flex items-center gap-3">
                <span>Navigate <kbd className="px-1.5 py-0.5 rounded bg-white/[0.08] text-white/70">↑</kbd> <kbd className="px-1.5 py-0.5 rounded bg-white/[0.08] text-white/70">↓</kbd></span>
                <span>Select <kbd className="px-1.5 py-0.5 rounded bg-white/[0.08] text-white/70">↵</kbd></span>
              </div>
              <div className="flex items-center gap-1">
                <span>Spotlight</span>
                <span className="text-sky-400 font-bold"></span>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
export default CommandPalette;
