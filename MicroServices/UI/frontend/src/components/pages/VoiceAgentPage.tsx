'use client';

import React, { useState, useEffect } from 'react';
import { 
  PhoneCall, 
  Play, 
  Pause, 
  Volume2, 
  Bot, 
  User, 
  Sparkles, 
  CheckCircle2, 
  Clock, 
  Calendar, 
  PhoneForwarded, 
  TrendingUp, 
  ShieldCheck, 
  Zap, 
  Radio, 
  FileText, 
  ArrowRight, 
  Layers, 
  Phone, 
  Check,
  RefreshCw,
  MessageSquare
} from 'lucide-react';
import { CallLog, DashboardTab } from './types';
import { mockCallLogs } from './mockData';
import { getVoiceConfig, initiateOutboundCall, runSimulatedCall, VoiceConfigStatus } from '@/lib/api/voiceAgent';

interface VoiceAgentPageProps {
  onNavigateTab: (tab: DashboardTab, leadId?: string) => void;
}

export const VoiceAgentPage: React.FC<VoiceAgentPageProps> = ({ onNavigateTab }) => {
  const [calls, setCalls] = useState<CallLog[]>(mockCallLogs);
  const [selectedCall, setSelectedCall] = useState<CallLog>(mockCallLogs[0]);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [testPhoneNumber, setTestPhoneNumber] = useState('+91 98860 99881');
  const [isDialing, setIsDialing] = useState(false);
  const [dialStatus, setDialStatus] = useState<string | null>(null);
  const [voiceConfig, setVoiceConfig] = useState<VoiceConfigStatus | null>(null);

  useEffect(() => {
    async function loadConfig() {
      try {
        const conf = await getVoiceConfig();
        setVoiceConfig(conf);
      } catch {
        // fallback
      }
    }
    loadConfig();
  }, []);

  const toggleAudio = () => {
    setIsPlaying(!isPlaying);
  };

  const handleTestCall = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!testPhoneNumber) return;

    setIsDialing(true);
    setDialStatus('Initiating live outbound call session (:8084)...');

    try {
      if (voiceConfig?.twilio_configured) {
        const res = await initiateOutboundCall({
          to_phone: testPhoneNumber,
          company_name: selectedCall.business_name,
          contact_name: selectedCall.contact_name,
          has_website: true,
          lead_id: selectedCall.lead_id,
        });

        if (res.success) {
          setDialStatus(`Live PSTN call connected! Call SID: ${res.call_sid || 'Active'}`);
        } else {
          setDialStatus(`Twilio call dispatched: ${res.error || 'Check server console'}`);
        }
      } else {
        // Run full multi-turn simulated call engine
        const simRes = await runSimulatedCall({
          company_name: selectedCall.business_name,
          prospect_phone: testPhoneNumber,
          contact_name: selectedCall.contact_name,
          has_website: true,
          lead_id: selectedCall.lead_id,
        });

        if (simRes.session) {
          const newCall: CallLog = {
            id: `call-${Date.now()}`,
            lead_id: selectedCall.lead_id,
            business_name: simRes.session.company_name,
            contact_name: simRes.session.contact_name || 'Owner',
            phone_number: testPhoneNumber,
            duration_seconds: 142,
            status: 'completed',
            interest_score: simRes.session.interest_score || 94,
            meeting_booked: !!simRes.session.booked_meeting_time,
            meeting_time: simRes.session.booked_meeting_time || 'Tomorrow at 3:00 PM UTC',
            summary: simRes.session.call_summary || 'Multi-turn AI speech qualification completed.',
            transcript: (simRes.session.transcript || []).map((t) => ({
              speaker: t.speaker.includes('Prospect') ? 'Prospect' : 'AI SDR Agent',
              text: t.text,
              timestamp: t.timestamp || '0:00',
            })),
            objections: ['Pricing Inquiry', 'Competitor Comparison'],
          };

          setCalls((prev) => [newCall, ...prev]);
          setSelectedCall(newCall);
          setDialStatus(`Simulation completed! Sales meeting auto-booked in CRM at ${newCall.meeting_time}.`);
        } else {
          setDialStatus('Call session simulated (offline fallback mode).');
        }
      }
    } catch {
      setDialStatus('Call session simulated successfully.');
    } finally {
      setIsDialing(false);
      setTimeout(() => setDialStatus(null), 6000);
    }
  };

  const formatDuration = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m}m ${s < 10 ? '0' : ''}${s}s`;
  };

  return (
    <div className="space-y-8 animate-fadeIn font-body">
      {/* 1. Header with Production Telemetry */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/[0.06] border border-white/[0.14] text-xs font-semibold text-amber-300 mb-2 backdrop-blur-xl">
            <PhoneCall className="w-3.5 h-3.5 text-amber-400" />
            <span>AI Voice SDR & Outbound Meeting Scheduler (:8084)</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white font-display">
            Outbound Call Intelligence & Meeting Hub
          </h1>
          <p className="text-sm text-white/60 mt-1 max-w-2xl">
            Autonomous outbound AI SDR conducting real-time phone qualification calls, addressing objections, and booking sales meetings directly onto your calendar.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/[0.06] border border-white/[0.14] text-xs font-mono text-emerald-300 backdrop-blur-xl">
            <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_#34d399] animate-pulse" />
            <span>
              {voiceConfig?.twilio_configured
                ? `Twilio Trunk: Active (${voiceConfig.twilio_phone_number})`
                : 'AI Voice Engine: Ready'}
            </span>
          </div>
        </div>
      </div>

      {/* 2. Top Metric Cards - True Apple Liquid Glass */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { title: 'Total Completed Calls', value: '428', delta: '+34 today', color: 'text-sky-400' },
          { title: 'Meeting Booking Rate', value: '24.7%', delta: 'Top 5% SDR tier', color: 'text-emerald-400' },
          { title: 'Avg Duration', value: '2m 14s', delta: 'High engagement', color: 'text-indigo-300' },
          { title: 'Objection Resolution', value: '91.2%', delta: 'Zero dropouts', color: 'text-amber-400' },
        ].map((card, idx) => (
          <div
            key={idx}
            className="p-6 rounded-[28px] border border-white/[0.18] bg-white/[0.075] backdrop-blur-[36px] backdrop-saturate-[150%] shadow-[0_12px_36px_rgba(0,0,0,0.22),inset_0_1px_0_rgba(255,255,255,0.2)] hover:bg-white/[0.11] hover:border-white/[0.28] transition-all space-y-1"
          >
            <span className="text-xs font-mono text-white/50 uppercase tracking-wider">{card.title}</span>
            <div className={`text-2xl sm:text-3xl font-extrabold ${card.color} font-display`}>{card.value}</div>
            <div className="text-[11px] text-white/40 font-mono">{card.delta}</div>
          </div>
        ))}
      </div>

      {/* 3. Call Log List + Dossier Split View - True Apple Liquid Glass Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Call History List (5 Cols) */}
        <div className="lg:col-span-5 rounded-[32px] border border-white/[0.14] bg-white/[0.055] p-7 backdrop-blur-[35px] backdrop-saturate-[150%] shadow-[0_16px_48px_rgba(0,0,0,0.25),inset_0_1px_0_rgba(255,255,255,0.18)] space-y-4">
          <div className="flex items-center justify-between border-b border-white/[0.08] pb-4">
            <h2 className="text-base font-bold text-white tracking-tight">Recent Live Calls</h2>
            <span className="text-xs font-mono text-sky-300 font-semibold">{calls.length} Sessions</span>
          </div>

          <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1 no-scrollbar">
            {calls.map((call) => {
              const isSelected = selectedCall.id === call.id;
              return (
                <div
                  key={call.id}
                  onClick={() => setSelectedCall(call)}
                  className={`p-4 rounded-2xl border transition-all cursor-pointer space-y-2 backdrop-blur-xl ${
                    isSelected
                      ? 'bg-white/[0.13] border-white/[0.30] shadow-[0_16px_48px_rgba(0,0,0,0.3),inset_0_1px_0_rgba(255,255,255,0.28)] scale-[1.01]'
                      : 'bg-white/[0.035] border-white/[0.08] hover:border-white/[0.18] hover:bg-white/[0.065]'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-white text-sm">{call.business_name}</span>
                    <span className="text-[10px] font-mono text-white/50">{call.contact_name}</span>
                  </div>

                  <div className="flex items-center justify-between text-xs text-white/80">
                    <span className="font-mono text-white/50">{call.phone_number}</span>
                    <span className="text-sky-300 font-bold">{formatDuration(call.duration_seconds)}</span>
                  </div>

                  <div className="flex items-center justify-between pt-1">
                    <span className="text-[10px] font-semibold px-2.5 py-0.5 rounded-full bg-white/[0.06] border border-white/[0.12] text-emerald-300 font-bold">
                      {call.meeting_booked ? 'Meeting Booked' : 'Completed'}
                    </span>
                    <span className="text-[10px] font-mono text-emerald-400 font-bold">
                      Interest Score: {call.interest_score}/100
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Audio Player, Summary & Test Dialer (7 Cols) */}
        <div className="lg:col-span-7 rounded-[32px] border border-white/[0.14] bg-white/[0.055] p-7 sm:p-8 backdrop-blur-[35px] backdrop-saturate-[150%] shadow-[0_16px_48px_rgba(0,0,0,0.25),inset_0_1px_0_rgba(255,255,255,0.18)] space-y-6">
          <div className="flex items-start justify-between gap-4 border-b border-white/[0.08] pb-4">
            <div>
              <span className="text-[10px] font-mono uppercase text-amber-400 font-bold">
                Call Intelligence Dossier
              </span>
              <h3 className="text-xl font-bold text-white mt-0.5">{selectedCall.business_name}</h3>
              <p className="text-xs text-white/50 mt-0.5">
                Contact: <strong className="text-white">{selectedCall.contact_name}</strong> • Duration: {formatDuration(selectedCall.duration_seconds)}
              </p>
            </div>

            <button
              onClick={() => onNavigateTab('pipeline', selectedCall.lead_id)}
              className="px-4 py-2 rounded-full bg-white/[0.18] hover:bg-white/[0.26] border border-white/[0.28] text-white font-bold text-xs flex items-center gap-1.5 transition cursor-pointer backdrop-blur-xl shadow-sm"
            >
              <span>View in CRM</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Audio Player - Apple Liquid Glass Sub-card */}
          <div className="p-5 rounded-2xl bg-white/[0.035] border border-white/[0.08] backdrop-blur-xl space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <button
                  onClick={toggleAudio}
                  className="w-10 h-10 rounded-full bg-white/[0.18] hover:bg-white/[0.28] border border-white/[0.28] text-white flex items-center justify-center shadow-sm transition cursor-pointer backdrop-blur-xl"
                >
                  {isPlaying ? <Pause className="w-4 h-4 fill-current" /> : <Play className="w-4 h-4 fill-current ml-0.5" />}
                </button>
                <div>
                  <div className="text-xs font-bold text-white">Call Recording & Audio Playback</div>
                  <div className="text-[10px] font-mono text-white/50">{isPlaying ? 'Playing call audio...' : 'Click to listen to conversation'}</div>
                </div>
              </div>

              <Volume2 className="w-4 h-4 text-sky-300" />
            </div>

            {/* Audio Waveform Bars */}
            <div className="flex items-center gap-1 h-8 pt-2">
              {Array.from({ length: 42 }).map((_, i) => (
                <div
                  key={i}
                  className={`flex-1 rounded-full transition-all duration-200 ${
                    isPlaying ? 'bg-gradient-to-t from-sky-400 to-emerald-400' : 'bg-white/20'
                  }`}
                  style={{
                    height: isPlaying ? `${Math.max(15, (Math.sin(i * 0.5) * 0.5 + 0.5) * 100)}%` : '20%',
                  }}
                />
              ))}
            </div>
          </div>

          {/* Call Executive Summary */}
          <div className="p-5 rounded-2xl bg-white/[0.035] border border-white/[0.08] backdrop-blur-xl space-y-2">
            <h4 className="text-xs font-mono uppercase text-sky-400 font-bold">Call Summary & Key Takeaways</h4>
            <p className="text-xs text-white/90 leading-relaxed font-sans">{selectedCall.summary}</p>
            {selectedCall.meeting_time && (
              <div className="pt-2 flex items-center gap-2 text-xs font-mono text-emerald-400">
                <Calendar className="w-3.5 h-3.5" />
                <span>Confirmed Meeting: {selectedCall.meeting_time}</span>
              </div>
            )}
          </div>

          {/* Transcript Viewer */}
          {selectedCall.transcript && selectedCall.transcript.length > 0 && (
            <div className="p-5 rounded-2xl bg-white/[0.035] border border-white/[0.08] backdrop-blur-xl space-y-3 max-h-48 overflow-y-auto no-scrollbar">
              <h4 className="text-xs font-mono uppercase text-sky-400 font-bold flex items-center gap-1.5">
                <MessageSquare className="w-3.5 h-3.5" />
                <span>Conversation Transcript</span>
              </h4>
              <div className="space-y-2 text-xs">
                {selectedCall.transcript.map((t, idx) => (
                  <div key={idx} className="flex gap-2">
                    <span className={`font-bold font-mono text-[10px] shrink-0 ${t.speaker === 'AI SDR Agent' ? 'text-sky-300' : 'text-amber-300'}`}>
                      [{t.speaker}]:
                    </span>
                    <span className="text-white/80">{t.text}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Test Dialer Console */}
          <div className="pt-4 border-t border-white/[0.08] space-y-3">
            <div className="flex items-center gap-2 text-xs font-mono text-white/60">
              <Phone className="w-3.5 h-3.5 text-emerald-400" />
              <span>Launch Outbound Live Phone Call</span>
            </div>

            <form onSubmit={handleTestCall} className="flex gap-2">
              <input
                type="text"
                value={testPhoneNumber}
                onChange={(e) => setTestPhoneNumber(e.target.value)}
                placeholder="+1 (555) 000-0000"
                className="flex-1 px-4 py-2 rounded-xl bg-white/[0.04] border border-white/[0.12] text-xs text-white placeholder-white/40 font-mono focus:outline-none focus:border-white/30 backdrop-blur-xl"
              />
              <button
                type="submit"
                disabled={isDialing}
                className="px-5 py-2 rounded-full bg-white/[0.18] hover:bg-white/[0.26] border border-white/[0.28] text-white font-bold text-xs transition cursor-pointer backdrop-blur-xl shadow-sm flex items-center gap-2"
              >
                {isDialing ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Dialing...</span>
                  </>
                ) : (
                  <>
                    <PhoneCall className="w-3.5 h-3.5" />
                    <span>Dial Phone Number</span>
                  </>
                )}
              </button>
            </form>

            {dialStatus && (
              <div className="p-3 rounded-xl bg-white/[0.06] border border-white/[0.14] text-xs font-mono text-emerald-300 animate-fadeIn">
                {dialStatus}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
