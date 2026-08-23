import { 
  LeadRecord, 
  SEOMetric, 
  BusinessAnalysis, 
  Proposal, 
  OutreachAsset, 
  CallLog, 
  ScraperStatusRecord 
} from './types';

export const mockLeads: LeadRecord[] = [
  {
    id: 'lead-001',
    business_name: 'Apex Solar Energy Solutions',
    category: 'Solar Panel Installation',
    location: 'Bangalore, India',
    phone_number: '+91 98450 12890',
    website: 'https://apexsolarenergy.in',
    rating: 4.8,
    reviews_count: 142,
    source: 'Google Maps',
    decision_path: 'website_analysis',
    stage: 'proposal_ready',
    lead_quality_score: 94,
    seo_score: 52,
    business_score: 88,
    opportunity_priority: 'High',
    estimated_deal_value: 12500,
    contact_person: 'Rajesh K. Verma',
    email: 'contact@apexsolarenergy.in',
    last_activity: '12 mins ago',
    created_at: '2026-08-22',
  },
  {
    id: 'lead-002',
    business_name: 'Metro Commercial Plumbing & HVAC',
    category: 'Commercial Plumbing',
    location: 'Dallas, TX, USA',
    phone_number: '+1 (214) 555-0199',
    website: 'https://metrodallasplumbing.com',
    rating: 4.6,
    reviews_count: 89,
    source: 'Yelp',
    decision_path: 'website_analysis',
    stage: 'outreach_active',
    lead_quality_score: 86,
    seo_score: 61,
    business_score: 79,
    opportunity_priority: 'High',
    estimated_deal_value: 8400,
    contact_person: 'David Miller',
    email: 'dmiller@metrodallasplumbing.com',
    last_activity: '45 mins ago',
    created_at: '2026-08-22',
  },
  {
    id: 'lead-003',
    business_name: 'Gupta Steel & Hardware Traders',
    category: 'Industrial Hardware',
    location: 'Chennai, India',
    phone_number: '+91 94440 88214',
    website: '',
    rating: 4.3,
    reviews_count: 38,
    source: 'IndiaMART',
    decision_path: 'voice_bot_pitch',
    stage: 'call_booked',
    lead_quality_score: 78,
    business_score: 82,
    opportunity_priority: 'Medium',
    estimated_deal_value: 4500,
    contact_person: 'Suresh Gupta',
    last_activity: '2 hours ago',
    created_at: '2026-08-22',
  },
  {
    id: 'lead-004',
    business_name: 'Sterling & Partners Legal Advisory',
    category: 'Corporate Law',
    location: 'London, UK',
    phone_number: '+44 20 7946 0912',
    website: 'https://sterlingadvisorylegal.co.uk',
    rating: 4.9,
    reviews_count: 215,
    source: 'Avvo',
    decision_path: 'website_analysis',
    stage: 'negotiation',
    lead_quality_score: 96,
    seo_score: 44,
    business_score: 95,
    opportunity_priority: 'High',
    estimated_deal_value: 28000,
    contact_person: 'Eleanor Vance',
    email: 'e.vance@sterlingadvisorylegal.co.uk',
    last_activity: '3 hours ago',
    created_at: '2026-08-21',
  },
  {
    id: 'lead-005',
    business_name: 'Prestige Automotive Fleet Specialists',
    category: 'Automotive Dealership',
    location: 'Chicago, IL, USA',
    phone_number: '+1 (312) 555-0842',
    website: 'https://prestigefleetchicago.com',
    rating: 4.4,
    reviews_count: 67,
    source: 'Custom',
    decision_path: 'website_analysis',
    stage: 'discovered',
    lead_quality_score: 72,
    seo_score: 58,
    business_score: 74,
    opportunity_priority: 'Medium',
    estimated_deal_value: 6200,
    contact_person: 'Anthony Rossi',
    last_activity: 'Just now',
    created_at: '2026-08-22',
  },
  {
    id: 'lead-006',
    business_name: 'Zenith Health & Orthopedic Clinic',
    category: 'Healthcare & Wellness',
    location: 'San Francisco, CA, USA',
    phone_number: '+1 (415) 555-0133',
    website: 'https://zenithorthoclinic.com',
    rating: 4.9,
    reviews_count: 310,
    source: 'Google Maps',
    decision_path: 'website_analysis',
    stage: 'won',
    lead_quality_score: 98,
    seo_score: 68,
    business_score: 92,
    opportunity_priority: 'High',
    estimated_deal_value: 18500,
    contact_person: 'Dr. Sarah Jenkins',
    email: 'sarah@zenithorthoclinic.com',
    last_activity: '1 day ago',
    created_at: '2026-08-20',
  }
];

export const mockSEOMetrics: Record<string, SEOMetric[]> = {
  'lead-001': [
    { category: 'Mobile UX & Page Speed', score: 38, status: 'critical', details: 'LCP is 4.8s on mobile. Uncompressed images and blocking scripts.' },
    { category: 'On-Page SEO & Meta Tags', score: 55, status: 'warning', details: 'Missing OpenGraph tags, duplicate H1 tags across 14 service subpages.' },
    { category: 'Conversion Signals & CTA', score: 42, status: 'critical', details: 'No floating contact button, phone number is non-clickable on mobile.' },
    { category: 'Backlinks & Domain Authority', score: 71, status: 'good', details: 'Healthy directory profile across Justdial & Google Business.' }
  ]
};

export const mockBusinessAnalysis: Record<string, BusinessAnalysis> = {
  'lead-001': {
    lead_id: 'lead-001',
    strengths: [
      'Top-rated installer in Bangalore with 142 5-star Google reviews',
      'Direct partnerships with tier-1 solar inverter manufacturers',
      'Strong local physical presence and fleet of installation engineers'
    ],
    weaknesses: [
      'Mobile website conversion rate is sub 1.2% due to slow loading speeds',
      'No automated WhatsApp quote calculator or online appointment booking',
      'Lacks targeted commercial rooftop landing pages for industrial clients'
    ],
    opportunities: [
      'Industrial rooftop subsidy schemes launched in Karnataka',
      'Automating lead capture via interactive ROI solar savings calculator',
      'Local SEO ranking capture for "commercial solar EPC Bangalore"'
    ],
    threats: [
      'Aggressive PPC ad bidding from venture-backed solar aggregators',
      'Client drop-off to competitors with instant online quote systems'
    ],
    competitors: [
      { name: 'SunPower Karnataka', advantage: 'Instant online quote engine' },
      { name: 'Tata Power Solar Regional', advantage: 'National brand authority' }
    ],
    recommended_offer: 'High-Converting Commercial Solar Growth Suite + Instant WhatsApp Quote Automation',
    expected_outcomes: '+180% Qualified Commercial Inquiries, 3.2x Mobile Conversion Speed',
    estimated_impact_score: 9.4
  }
};

export const mockProposals: Record<string, Proposal> = {
  'lead-001': {
    id: 'prop-001',
    lead_id: 'lead-001',
    title: 'Digital Revenue Growth & High-Velocity Lead Engine Proposal',
    executive_summary: 'Apex Solar is a premier solar EPC in Bangalore, yet digital conversion leakage is costing an estimated 35-50 high-value commercial inquiries monthly. This proposal outlines the deployment of a high-speed conversion funnel, automated WhatsApp solar ROI calculator, and commercial SEO positioning.',
    identified_problems: [
      'Severe mobile latency (4.8s LCP) causing 62% visitor bounce rate',
      'Absence of instant quote/calculator mechanisms for commercial leads',
      'Competitors dominating top-3 map pack for high-intent keywords'
    ],
    proposed_solution: 'Deployment of the NextGen CleanTech Growth Architecture: Sub-second headless web portal, interactive WhatsApp ROI estimation bot, and specialized local SEO dominance suite.',
    deliverables: [
      { title: 'Sub-Second Next.js High-Conversion Web Architecture', timeline: 'Week 1 - 2', price: 4500 },
      { title: 'Interactive Solar ROI & Subsidy WhatsApp Bot Engine', timeline: 'Week 2 - 3', price: 3500 },
      { title: 'Commercial EPC Local SEO Domination Suite (Top-3 Ranking)', timeline: 'Week 3 - 4', price: 4500 }
    ],
    total_investment: 12500,
    roi_estimate: 'Expected return of $85,000+ in new commercial solar installations within 90 days.',
    status: 'ready',
    created_at: '2026-08-22'
  }
};

export const mockOutreachAssets: Record<string, OutreachAsset[]> = {
  'lead-001': [
    {
      id: 'out-001',
      lead_id: 'lead-001',
      channel: 'email',
      subject: 'Quick question regarding Apex Solar’s mobile inquiries in Bangalore',
      content: `Hi Rajesh,\n\nNoticed Apex Solar has built an exceptional track record with over 140+ 5-star reviews across Bangalore—congratulations on the recent industrial rooftop projects.\n\nWhile reviewing your digital footprint, our AI audit noticed mobile visitors face a 4.8s loading delay, and potential commercial clients cannot calculate their subsidy ROI on the spot. Competitors like SunPower Karnataka are currently capturing those instant searches.\n\nWe prepared a custom 1-page breakdown showing how adding an instant WhatsApp ROI calculator would capture an extra 30–40 commercial solar contracts per quarter.\n\nWould you be open to a 7-minute look at the numbers this Thursday at 3 PM?\n\nBest regards,\nAI SDR Agent | Scrape-Verse Growth Team`,
      sequence_step: 1,
      status: 'ready'
    },
    {
      id: 'out-002',
      lead_id: 'lead-001',
      channel: 'linkedin',
      content: `Rajesh, loved the recent solar rooftop project completed in Whitefield. Noticed your site could easily 2x commercial inquiries with an instant ROI calculator. Shared a quick breakdown to your email—happy to connect!`,
      sequence_step: 2,
      status: 'ready'
    },
    {
      id: 'out-003',
      lead_id: 'lead-001',
      channel: 'call_script',
      content: `[GREETING]: Hi Rajesh, this is Alex calling on behalf of Scrape-Verse CleanTech Growth. Calling regarding Apex Solar's commercial installations in Bangalore.\n[HOOK]: Saw your stellar 142 reviews. Quick question: are your team noticing that commercial factory owners prefer calculating their rooftop solar ROI on WhatsApp before picking up the phone?\n[OBJECTION - "We already have a website"]: Absolutely, your site has great testimonials. The issue is factory owners on mobile wait 4+ seconds and bounce to competitors before submitting a quote.\n[CTA]: I have a 3-minute interactive model built for Apex Solar. Would tomorrow at 11 AM or 3 PM work for a brief walkthrough?`,
      sequence_step: 3,
      status: 'ready'
    }
  ]
};

export const mockCallLogs: CallLog[] = [
  {
    id: 'call-001',
    lead_id: 'lead-003',
    business_name: 'Gupta Steel & Hardware Traders',
    contact_name: 'Suresh Gupta',
    phone_number: '+91 94440 88214',
    duration_seconds: 142,
    status: 'completed',
    interest_score: 85,
    meeting_booked: true,
    meeting_time: '2026-08-25 11:30 AM IST',
    summary: 'Lead expressed high interest in getting a dedicated digital catalog and WhatsApp ordering portal to compete with larger suppliers.',
    transcript: [
      { speaker: 'AI SDR Agent', text: 'Hello Suresh ji, calling from Scrape-the-Verse B2B Growth. Am I speaking with the proprietor of Gupta Steel?', timestamp: '00:02' },
      { speaker: 'Prospect', text: 'Yes, Suresh speaking. What is this regarding?', timestamp: '00:08' },
      { speaker: 'AI SDR Agent', text: 'We noticed your strong catalog on IndiaMART in Chennai. Many hardware dealers lose out on wholesale repeat orders because buyers cannot browse real-time inventory on WhatsApp. We build turnkey ordering portals in 48 hours.', timestamp: '00:15' },
      { speaker: 'Prospect', text: 'Is it expensive? We already pay for IndiaMART.', timestamp: '00:32' },
      { speaker: 'AI SDR Agent', text: 'Not at all. It integrates with your existing inventory and costs less than a single batch shipment, saving 15 hours of manual phone coordination weekly. Would you like a 10-minute live demonstration this Tuesday morning?', timestamp: '00:45' },
      { speaker: 'Prospect', text: 'Okay, Tuesday 11:30 AM works. Send me details on WhatsApp on this number.', timestamp: '01:15' },
      { speaker: 'AI SDR Agent', text: 'Confirmed Suresh ji! Meeting scheduled for Tuesday at 11:30 AM. Details are on your WhatsApp.', timestamp: '01:25' }
    ],
    objections: ['IndiaMART cost skepticism', 'Implementation simplicity']
  }
];

export const mockScraperStatuses: ScraperStatusRecord[] = [
  {
    id: 'sc-01',
    collector_id: 'c_mt1qfvqx1051f3m8r9',
    name: 'Google Maps Business Directory',
    target_domain: 'google.com/maps',
    status: 'READY',
    records_extracted: 14820,
    health_score: 0.98,
    healing_attempts: 0
  },
  {
    id: 'sc-02',
    collector_id: 'c_mt1klz941e6wjo8o6y',
    name: 'IndiaMART B2B Discovery',
    target_domain: 'dir.indiamart.com',
    status: 'READY',
    records_extracted: 32400,
    health_score: 0.96,
    healing_attempts: 1,
    last_healed: '2026-08-21 14:10'
  },
  {
    id: 'sc-03',
    collector_id: 'c_mt38sv49yfrrosp1u',
    name: 'Yelp Local Business Collector',
    target_domain: 'yelp.com',
    status: 'READY',
    records_extracted: 8910,
    health_score: 0.94,
    healing_attempts: 0
  },
  {
    id: 'sc-04',
    collector_id: 'c_mt39jryq1q6vcwtxcy',
    name: 'Avvo Legal & Professional Registry',
    target_domain: 'avvo.com',
    status: 'READY',
    records_extracted: 4120,
    health_score: 0.92,
    healing_attempts: 0
  }
];
