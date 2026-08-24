"use client";

import React, { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search,
  Sparkles,
  Heart,
  Calendar,
  Gem,
  Settings,
  ArrowLeft,
  ChevronDown,
  SlidersHorizontal,
  Package,
  Activity,
  MessageSquareText,
  Radio,
  Layers,
  Server,
  Zap,
  CheckCircle2,
  X,
  Bell,
  Wifi,
  WifiOff,
  RefreshCw,
  PhoneCall,
  LayoutDashboard,
  Cpu,
  Send,
  Database,
  Sliders,
  ShieldCheck,
} from "lucide-react";
import Link from "next/link";
import { DashboardTab, LeadRecord } from "./types";
import { mockLeads } from "./mockData";
import { DashboardOverview } from "./DashboardOverview";
import { LeadDiscoveryPage } from "./LeadDiscoveryPage";
import { LeadAnalysisPage } from "./LeadAnalysisPage";
import { ProposalStudioPage } from "./ProposalStudioPage";
import { OutreachHubPage } from "./OutreachHubPage";
import { VoiceAgentPage } from "./VoiceAgentPage";
import { PipelinePage } from "./PipelinePage";
import { ScraperStudioPage } from "./ScraperStudioPage";
import { checkAllServicesHealth, ServiceHealthStatus } from "@/lib/api/client";
import { useTimelineStream, TimelineEvent } from "@/hooks/useTimelineStream";

export const DashboardShell: React.FC = () => {
  const [activeTab, setActiveTab] = useState<DashboardTab>("overview");
  const [selectedLead, setSelectedLead] = useState<LeadRecord>(mockLeads[0]);
  const [quickSearchQuery, setQuickSearchQuery] = useState("");

  // Backend Health & Mode State
  const [servicesHealth, setServicesHealth] = useState<
    Record<string, ServiceHealthStatus>
  >({});
  const [isCheckingHealth, setIsCheckingHealth] = useState(false);
  const [showHealthModal, setShowHealthModal] = useState(false);
  const [showNotificationsTray, setShowNotificationsTray] = useState(false);
  const [activeToast, setActiveToast] = useState<TimelineEvent | null>(null);

  // SSE Stream Listener
  const { events: timelineEvents, isConnected: isSseConnected } =
    useTimelineStream(true);

  // Trigger toast on new SSE event
  useEffect(() => {
    if (timelineEvents.length > 0) {
      const latest = timelineEvents[0];
      const timer = setTimeout(() => {
        setActiveToast(latest);
      }, 0);
      const dismissTimer = setTimeout(() => {
        setActiveToast(null);
      }, 5000);
      return () => {
        clearTimeout(timer);
        clearTimeout(dismissTimer);
      };
    }
  }, [timelineEvents]);

  // Initial & Periodic Health Check
  const probeHealth = useCallback(async () => {
    setIsCheckingHealth(true);
    try {
      const res = await checkAllServicesHealth();
      setServicesHealth(res);
    } catch {
      // ignore
    } finally {
      setIsCheckingHealth(false);
    }
  }, []);

  useEffect(() => {
    let isCancelled = false;
    async function runProbe() {
      setIsCheckingHealth(true);
      try {
        const res = await checkAllServicesHealth();
        if (!isCancelled) {
          setServicesHealth(res);
        }
      } catch {
        // ignore
      } finally {
        if (!isCancelled) {
          setIsCheckingHealth(false);
        }
      }
    }

    runProbe();
    const interval = setInterval(runProbe, 20000);
    return () => {
      isCancelled = true;
      clearInterval(interval);
    };
  }, []);

  const totalOnline = Object.values(servicesHealth).filter(
    (s) => s.isOnline,
  ).length;
  const isAllOnline = totalOnline === 4;
  const isAnyOnline = totalOnline > 0;

  const sidebarRailItems = [
    {
      id: "overview" as DashboardTab,
      icon: LayoutDashboard,
      label: "Command Center",
      tag: "Overview",
    },
    {
      id: "discovery" as DashboardTab,
      icon: Search,
      label: "Lead Discovery",
      tag: "Harvest",
    },
    {
      id: "analysis" as DashboardTab,
      icon: Cpu,
      label: "360° AI Audit",
      tag: "SWOT",
    },
    {
      id: "proposals" as DashboardTab,
      icon: Sparkles,
      label: "Proposal Studio",
      tag: "Deals",
    },
    {
      id: "outreach" as DashboardTab,
      icon: Send,
      label: "Outreach Hub",
      tag: "Campaigns",
    },
    {
      id: "calls" as DashboardTab,
      icon: PhoneCall,
      label: "Voice Agent",
      tag: "Live SDR",
    },
    {
      id: "pipeline" as DashboardTab,
      icon: Layers,
      label: "Pipeline CRM",
      tag: "Kanban",
    },
    {
      id: "scrapers" as DashboardTab,
      icon: Settings,
      label: "DCA Config",
      tag: "Self-Heal",
    },
  ];

  const handleNavigateTab = (tab: DashboardTab, leadId?: string) => {
    setActiveTab(tab);
    if (leadId) {
      const found = mockLeads.find((l) => l.id === leadId);
      if (found) setSelectedLead(found);
    }
  };

  const getPageTitle = () => {
    switch (activeTab) {
      case "overview":
        return "COMMAND CENTER";
      case "discovery":
        return "LEAD DISCOVERY";
      case "analysis":
        return "360° AI AUDIT";
      case "proposals":
        return "PROPOSAL STUDIO";
      case "outreach":
        return "OUTREACH HUB";
      case "calls":
        return "VOICE AGENT";
      case "pipeline":
        return "PIPELINE CRM";
      case "scrapers":
        return "SCRAPER OPERATIONS";
      default:
        return "COMMAND CENTER";
    }
  };

  return (
    <div className="min-h-screen text-white selection:bg-sky-400 selection:text-[#07090D] font-body relative overflow-x-hidden">
      {/* 1. GLASSMORPHISM WAVE EFFECT ABSTRACT BACKGROUND (DASHBOARD ONLY) */}
      <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
        <div
          className="absolute inset-0 bg-cover bg-center bg-no-repeat filter brightness-105 saturate-[1.15]"
          style={{
            backgroundImage: "url('/images/dashboard_bg.jpg')",
          }}
        />
        {/* Subtle translucent dark overlay for high readability */}
        <div className="absolute inset-0 bg-[#060911]/30 backdrop-blur-[1px]" />
      </div>

      {/* 2. FLOATING LIQUID GLASS TOP HEADER */}
      <header className="fixed top-3 sm:top-5 left-3 sm:left-5 right-3 sm:right-5 z-40 h-16 max-w-[1780px] mx-auto rounded-2xl sm:rounded-3xl bg-white/[0.08] backdrop-blur-[35px] backdrop-saturate-[160%] border border-white/[0.22] shadow-[0_15px_35px_rgba(0,0,0,0.35),inset_0_1px_2px_rgba(255,255,255,0.45)] px-4 sm:px-6 flex items-center justify-between gap-4">
        {/* Left: Brand Logo + Current Page Title Breadcrumb */}
        <div className="flex items-center gap-3.5 shrink-0">
          <Link
            href="/"
            className="flex items-center gap-2.5 group hover:scale-105 transition-transform shrink-0"
            title="Return to AgencyOS Home"
          >
            <img
              src="/images/AgencyOS_Logo.png"
              alt="AgencyOS Logo"
              className="w-8 h-8 object-contain"
            />
            <span className="font-extrabold text-lg tracking-tight font-display text-white">
              AgencyOS
            </span>
          </Link>

          <div className="flex items-center gap-2.5 pl-3 border-l border-white/20">
            <span className="text-[11px] font-mono uppercase tracking-widest text-white/50 hidden sm:inline">
              Workspace /
            </span>
            <h1 className="text-sm sm:text-base font-bold text-white tracking-tight font-display">
              {getPageTitle()}
            </h1>
            <span className="text-[9px] font-mono uppercase px-2.5 py-0.5 rounded-full bg-sky-500/15 border border-sky-400/30 text-sky-200 font-bold backdrop-blur-md">
              {sidebarRailItems.find((i) => i.id === activeTab)?.tag ||
                "Active"}
            </span>
          </div>
        </div>

        {/* Center: Integrated Quick Search Bar */}
        <div className="flex-1 max-w-lg mx-2 sm:mx-6">
          <div className="relative flex items-center w-full">
            <Search className="absolute left-3.5 w-4 h-4 text-white/50 pointer-events-none" />
            <input
              type="text"
              value={quickSearchQuery}
              onChange={(e) => setQuickSearchQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && quickSearchQuery.trim()) {
                  setActiveTab("discovery");
                }
              }}
              placeholder="Quick search leads, target companies, domains, or audit URLs..."
              className="w-full h-9 pl-9 pr-8 rounded-2xl bg-white/[0.08] hover:bg-white/[0.12] focus:bg-white/[0.15] border border-white/[0.20] focus:border-sky-400/60 text-xs text-white placeholder-white/50 focus:outline-none transition-all shadow-inner backdrop-blur-xl"
            />
            {quickSearchQuery && (
              <button
                onClick={() => setQuickSearchQuery("")}
                className="absolute right-2.5 p-1 text-white/50 hover:text-white transition cursor-pointer"
                title="Clear"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </div>

        {/* Right: Quick Action Controls */}
        <div className="flex items-center gap-2.5 sm:gap-3 shrink-0">
          {/* Swarm Health Status Button */}
          <button
            onClick={() => setShowHealthModal(true)}
            className="px-3 py-1.5 rounded-full bg-white/[0.08] hover:bg-white/[0.15] border border-white/[0.20] text-xs font-mono font-semibold text-white/90 hover:text-white flex items-center gap-2 transition cursor-pointer backdrop-blur-xl"
            title="View Microservices Swarm Status"
          >
            <span
              className={`w-2 h-2 rounded-full ${isAllOnline ? "bg-emerald-400 animate-pulse shadow-[0_0_8px_#34d399]" : "bg-amber-400"}`}
            />
            <span className="hidden sm:inline">Swarm</span>
            <span className="text-sky-300 font-bold">{totalOnline}/4</span>
          </button>

          {/* SSE Stream Status Pill */}
          <button
            onClick={() => setShowNotificationsTray(!showNotificationsTray)}
            className={`relative p-2 rounded-2xl border text-xs transition cursor-pointer backdrop-blur-xl ${
              isSseConnected
                ? "bg-white/[0.10] border-white/[0.25] text-sky-300 hover:bg-white/[0.18]"
                : "bg-white/[0.06] border-white/[0.15] text-white/60 hover:bg-white/[0.10]"
            }`}
            title="Real-Time SSE Timeline Stream"
          >
            <Bell className="w-4 h-4" />
            {timelineEvents.length > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-sky-400 text-black text-[9px] font-black flex items-center justify-center shadow-md">
                {timelineEvents.length > 9 ? "9+" : timelineEvents.length}
              </span>
            )}
          </button>

          {/* Landing Page Link */}
          <Link
            href="/"
            className="px-4 py-1.5 rounded-full bg-white text-[#07090D] hover:bg-slate-100 font-bold text-xs flex items-center gap-1.5 transition shadow-lg hover:shadow-sky-500/20"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Landing Page</span>
          </Link>
        </div>
      </header>

      {/* 3. FLOATING REAL-TIME SSE TOAST NOTIFICATION */}
      <AnimatePresence>
        {activeToast && (
          <motion.div
            initial={{ opacity: 0, y: -20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -20, scale: 0.95 }}
            className="fixed top-24 right-6 z-50 max-w-sm w-full p-4 rounded-2xl bg-white/[0.12] border border-white/[0.28] shadow-[0_20px_60px_rgba(0,0,0,0.45),inset_0_1px_2px_rgba(255,255,255,0.4)] backdrop-blur-3xl text-white"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center gap-2.5">
                <span className="w-2 h-2 rounded-full bg-sky-400 animate-ping" />
                <span className="text-xs font-mono font-bold text-sky-300 uppercase tracking-wider">
                  Live Swarm Event
                </span>
              </div>
              <button
                onClick={() => setActiveToast(null)}
                className="text-white/50 hover:text-white transition cursor-pointer"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
            <div className="mt-2 text-sm font-semibold text-white">
              {activeToast.topic}
            </div>
            <div className="mt-1 text-xs text-white/70 font-mono line-clamp-2">
              {JSON.stringify(activeToast.data)}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 4. REAL-TIME NOTIFICATIONS TRAY MODAL */}
      <AnimatePresence>
        {showNotificationsTray && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -10 }}
            className="fixed top-20 right-8 z-40 w-96 max-h-[500px] flex flex-col rounded-3xl bg-white/[0.10] border border-white/[0.25] shadow-[0_25px_70px_rgba(0,0,0,0.5),inset_0_1px_2px_rgba(255,255,255,0.4)] backdrop-blur-3xl overflow-hidden"
          >
            <div className="p-4 border-b border-white/15 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Radio className="w-4 h-4 text-sky-400 animate-pulse" />
                <span className="text-sm font-bold text-white">
                  Live Swarm Event Stream
                </span>
              </div>
              <button
                onClick={() => setShowNotificationsTray(false)}
                className="text-white/50 hover:text-white cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="p-4 flex-1 overflow-y-auto space-y-2.5 text-xs">
              {timelineEvents.length === 0 ? (
                <div className="text-center py-8 text-white/50">
                  <Activity className="w-6 h-6 mx-auto mb-2 opacity-50" />
                  <p>Awaiting live events from Lead Manager (:8082)...</p>
                </div>
              ) : (
                timelineEvents.map((evt) => (
                  <div
                    key={evt.id}
                    className="p-3 rounded-2xl bg-white/[0.05] border border-white/[0.12] hover:bg-white/[0.09] transition"
                  >
                    <div className="flex items-center justify-between text-[11px] text-sky-300 font-mono">
                      <span>{evt.topic}</span>
                      <span className="text-white/50">
                        {new Date(evt.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="mt-1 text-white/90 text-xs font-mono">
                      {JSON.stringify(evt.data)}
                    </p>
                  </div>
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 5. BACKEND MICROSERVICES HEALTH MODAL */}
      <AnimatePresence>
        {showHealthModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-2xl"
            onClick={() => setShowHealthModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="max-w-md w-full rounded-3xl bg-white/[0.10] border border-white/[0.25] p-6 shadow-[0_30px_80px_rgba(0,0,0,0.55),inset_0_1px_2px_rgba(255,255,255,0.4)] backdrop-blur-3xl relative"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between pb-4 border-b border-white/15">
                <div className="flex items-center gap-2.5">
                  <Server className="w-5 h-5 text-sky-400" />
                  <h3 className="text-base font-bold text-white">
                    AgencyOS Microservices Swarm
                  </h3>
                </div>
                <button
                  onClick={() => setShowHealthModal(false)}
                  className="p-1 rounded-xl hover:bg-white/10 text-white/50 hover:text-white cursor-pointer"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="mt-4 space-y-3">
                {[
                  {
                    key: "leadfinder",
                    name: "leadfinder (Google Maps & DCA)",
                    port: 8000,
                    service: servicesHealth.leadfinder,
                  },
                  {
                    key: "sdr",
                    name: "SDR Intelligence Agent",
                    port: 8081,
                    service: servicesHealth.sdr,
                  },
                  {
                    key: "lead_manager",
                    name: "Lead Manager (System of Record)",
                    port: 8082,
                    service: servicesHealth.lead_manager,
                  },
                  {
                    key: "voice_agent",
                    name: "Voice Agent (Twilio Carrier)",
                    port: 8084,
                    service: servicesHealth.voice_agent,
                  },
                ].map((item) => {
                  const isOnline = item.service?.isOnline;
                  return (
                    <div
                      key={item.key}
                      className="p-3.5 rounded-2xl bg-white/[0.06] border border-white/[0.14] flex items-center justify-between"
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={`w-2.5 h-2.5 rounded-full ${
                            isOnline
                              ? "bg-emerald-400 shadow-[0_0_10px_#34d399]"
                              : "bg-white/30"
                          }`}
                        />
                        <div>
                          <div className="text-xs font-semibold text-white">
                            {item.name}
                          </div>
                          <div className="text-[10px] font-mono text-white/60">
                            Port {item.port} •{" "}
                            {isOnline
                              ? `${item.service?.latencyMs}ms latency`
                              : "Offline / Mock Fallback"}
                          </div>
                        </div>
                      </div>

                      <div
                        className={`text-[10px] font-mono font-bold px-2.5 py-0.5 rounded-full ${
                          isOnline
                            ? "bg-emerald-400/20 border border-emerald-400/35 text-emerald-300"
                            : "bg-white/10 border border-white/15 text-white/50"
                        }`}
                      >
                        {isOnline ? "ONLINE" : "STANDBY"}
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="mt-6 flex items-center justify-between pt-4 border-t border-white/15">
                <button
                  onClick={probeHealth}
                  disabled={isCheckingHealth}
                  className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/[0.14] hover:bg-white/[0.22] border border-white/[0.25] text-xs font-semibold text-white transition cursor-pointer"
                >
                  <RefreshCw
                    className={`w-3.5 h-3.5 ${isCheckingHealth ? "animate-spin" : ""}`}
                  />
                  <span>Re-Probe Swarm</span>
                </button>
                <button
                  onClick={() => setShowHealthModal(false)}
                  className="px-4 py-2 rounded-full bg-white/[0.08] hover:bg-white/[0.14] border border-white/[0.18] text-xs font-medium text-white/80 hover:text-white transition cursor-pointer"
                >
                  Close
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 6. MAIN WORKSPACE CONTAINER WITH LIQUID GLASS SIDEBAR DOCK */}
      <div className="pt-24 pl-4 sm:pl-24 pr-4 sm:pr-8 max-w-[1780px] mx-auto w-full pb-16 relative z-10">
        {/* Fixed Left Navigation Bar (Floating Glass Dock) */}
        <aside className="hidden md:flex flex-col justify-between py-3 px-2 rounded-[28px] bg-white/[0.08] border border-white/[0.22] shadow-[0_20px_50px_rgba(0,0,0,0.45),inset_0_1px_2px_rgba(255,255,255,0.4)] backdrop-blur-[40px] fixed left-4 sm:left-6 top-[92px] bottom-6 z-30 group/sidebar w-16 hover:w-[268px] transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] shrink-0 overflow-hidden">
          {/* Navigation Items */}
          <div className="flex flex-col justify-between h-full w-full gap-1.5 py-1">
            {/* Rail Section Title */}
            <div className="px-2.5 py-0.5 flex items-center justify-between text-[10px] font-mono uppercase tracking-widest text-white/50 opacity-0 group-hover/sidebar:opacity-100 transition-opacity duration-200 whitespace-nowrap overflow-hidden">
              <span>Workspace</span>
              <span className="text-sky-300 font-bold">8 Hubs</span>
            </div>

            {sidebarRailItems.map((item, idx) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={idx}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex-1 min-h-[42px] px-2 rounded-2xl flex items-center gap-3 transition-all duration-200 cursor-pointer relative overflow-hidden group/item ${
                    isActive
                      ? "bg-white/[0.22] border border-white/[0.35] text-white shadow-md font-bold"
                      : "text-white/70 hover:text-white hover:bg-white/[0.12] hover:border hover:border-white/[0.18]"
                  }`}
                  title={item.label}
                >
                  {/* Active Left Indicator Bar */}
                  {isActive && (
                    <span className="absolute left-0 top-1/2 -translate-y-1/2 w-1.5 h-6 rounded-r-full bg-sky-400 shadow-[0_0_12px_#38bdf8]" />
                  )}

                  {/* Icon Container */}
                  <div
                    className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 transition-transform duration-200 group-hover/item:scale-105 ${
                      isActive
                        ? "bg-white/[0.18] text-sky-300"
                        : "bg-transparent text-white/80 group-hover/item:text-white"
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                  </div>

                  {/* Expanding Dynamic Label with Tag */}
                  <div className="opacity-0 group-hover/sidebar:opacity-100 transition-opacity duration-200 whitespace-nowrap overflow-hidden flex items-center justify-between flex-1 pr-1 text-left">
                    <span className="text-xs font-semibold tracking-tight text-white group-hover/item:text-white truncate">
                      {item.label}
                    </span>
                    <span className="text-[9px] font-mono uppercase px-2 py-0.5 rounded-md bg-white/[0.08] border border-white/[0.14] text-white/70 shrink-0 ml-2">
                      {item.tag}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        </aside>

        {/* Right Main Content Viewport */}
        <main className="flex-1 min-w-0">
          {/* Header Title Bar */}
          <div className="flex items-center justify-between gap-4 mb-6">
            <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-white font-display uppercase drop-shadow-sm">
              {getPageTitle()}
            </h1>
          </div>

          {activeTab === "overview" && (
            <DashboardOverview
              onNavigateTab={handleNavigateTab}
              onSelectLead={setSelectedLead}
            />
          )}
          {activeTab === "discovery" && (
            <LeadDiscoveryPage
              onNavigateTab={handleNavigateTab}
              onSelectLead={setSelectedLead}
            />
          )}
          {activeTab === "analysis" && (
            <LeadAnalysisPage
              selectedLead={selectedLead}
              onNavigateTab={handleNavigateTab}
              onSelectLead={setSelectedLead}
            />
          )}
          {activeTab === "proposals" && (
            <ProposalStudioPage
              selectedLead={selectedLead}
              onNavigateTab={handleNavigateTab}
              onSelectLead={setSelectedLead}
            />
          )}
          {activeTab === "outreach" && (
            <OutreachHubPage
              selectedLead={selectedLead}
              onNavigateTab={handleNavigateTab}
              onSelectLead={setSelectedLead}
            />
          )}
          {activeTab === "calls" && (
            <VoiceAgentPage onNavigateTab={handleNavigateTab} />
          )}
          {activeTab === "pipeline" && (
            <PipelinePage
              onNavigateTab={handleNavigateTab}
              onSelectLead={setSelectedLead}
            />
          )}
          {activeTab === "scrapers" && <ScraperStudioPage />}
        </main>
      </div>
    </div>
  );
};
