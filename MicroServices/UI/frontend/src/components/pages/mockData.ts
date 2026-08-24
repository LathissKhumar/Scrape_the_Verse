import {
  LeadRecord,
  SEOMetric,
  BusinessAnalysis,
  Proposal,
  OutreachAsset,
  CallLog,
  ScraperStatusRecord,
} from "./types";

export const mockLeads: LeadRecord[] = [
  {
    id: "lead-001",
    business_name: "Apex Solar Energy Solutions",
    category: "Commercial Solar EPC",
    location: "Bangalore, KA, India",
    phone_number: "+91 98450 12890",
    website: "https://apexsolarenergy.in",
    rating: 4.8,
    reviews_count: 142,
    source: "Google Maps",
    decision_path: "website_analysis",
    stage: "proposal_ready",
    lead_quality_score: 94,
    seo_score: 48,
    business_score: 91,
    opportunity_priority: "High",
    estimated_deal_value: 145,
    contact_person: "Rajesh K. Verma",
    email: "rajesh.verma@apexsolarenergy.in",
    last_activity: "12 mins ago",
    created_at: "2026-08-23T14:20:00Z",
  },
  {
    id: "lead-002",
    business_name: "Metro Commercial Plumbing & HVAC",
    category: "Commercial HVAC & Mechanical",
    location: "Dallas, TX, USA",
    phone_number: "+1 (214) 555-0199",
    website: "https://metrodallasplumbing.com",
    rating: 4.6,
    reviews_count: 89,
    source: "Yelp",
    decision_path: "website_analysis",
    stage: "outreach_active",
    lead_quality_score: 88,
    seo_score: 54,
    business_score: 84,
    opportunity_priority: "High",
    estimated_deal_value: 95,
    contact_person: "David Miller",
    email: "david.miller@metrodallasplumbing.com",
    last_activity: "45 mins ago",
    created_at: "2026-08-23T12:10:00Z",
  },
  {
    id: "lead-003",
    business_name: "Gupta Industrial Hardware & Fasteners",
    category: "Industrial Hardware & Fasteners",
    location: "Chennai, TN, India",
    phone_number: "+91 94440 88214",
    website: "https://guptahardwaretraders.com",
    rating: 4.4,
    reviews_count: 56,
    source: "IndiaMART",
    decision_path: "voice_bot_pitch",
    stage: "call_booked",
    lead_quality_score: 82,
    seo_score: 36,
    business_score: 89,
    opportunity_priority: "High",
    estimated_deal_value: 68,
    contact_person: "Suresh Gupta",
    email: "suresh@guptahardwaretraders.com",
    last_activity: "1 hour ago",
    created_at: "2026-08-23T10:45:00Z",
  },
  {
    id: "lead-004",
    business_name: "Sterling & Partners Corporate Law",
    category: "Corporate Legal Advisory",
    location: "London, Greater London, UK",
    phone_number: "+44 20 7946 0912",
    website: "https://sterlingadvisorylegal.co.uk",
    rating: 4.9,
    reviews_count: 215,
    source: "Avvo",
    decision_path: "website_analysis",
    stage: "negotiation",
    lead_quality_score: 97,
    seo_score: 42,
    business_score: 96,
    opportunity_priority: "High",
    estimated_deal_value: 185,
    contact_person: "Eleanor Vance, Managing Partner",
    email: "e.vance@sterlingadvisorylegal.co.uk",
    last_activity: "2 hours ago",
    created_at: "2026-08-23T08:30:00Z",
  },
  {
    id: "lead-005",
    business_name: "Horizon Advanced Dental Care",
    category: "Cosmetic & Implant Dentistry",
    location: "Austin, TX, USA",
    phone_number: "+1 (512) 555-0188",
    website: "https://horizondentalcare-austin.com",
    rating: 4.9,
    reviews_count: 348,
    source: "Google Maps",
    decision_path: "website_analysis",
    stage: "call_booked",
    lead_quality_score: 95,
    seo_score: 51,
    business_score: 93,
    opportunity_priority: "High",
    estimated_deal_value: 128,
    contact_person: "Dr. Michael Evans, DDS",
    email: "drmichael@horizondentalcare-austin.com",
    last_activity: "Just now",
    created_at: "2026-08-23T15:10:00Z",
  },
  {
    id: "lead-006",
    business_name: "Pacific Coast Roofing & Waterproofing",
    category: "Commercial Roofing Contractors",
    location: "Seattle, WA, USA",
    phone_number: "+1 (206) 555-0144",
    website: "https://pacificcoastroofingcontractors.com",
    rating: 4.7,
    reviews_count: 112,
    source: "Google Maps",
    decision_path: "website_analysis",
    stage: "discovered",
    lead_quality_score: 84,
    seo_score: 46,
    business_score: 88,
    opportunity_priority: "High",
    estimated_deal_value: 115,
    contact_person: "Robert Langdon",
    email: "rlangdon@pacificcoastroofingcontractors.com",
    last_activity: "3 hours ago",
    created_at: "2026-08-23T06:15:00Z",
  },
  {
    id: "lead-007",
    business_name: "Zenith Health & Orthopedic Institute",
    category: "Specialty Orthopedic Surgery",
    location: "San Francisco, CA, USA",
    phone_number: "+1 (415) 555-0133",
    website: "https://zenithorthoclinic.com",
    rating: 4.9,
    reviews_count: 310,
    source: "Google Maps",
    decision_path: "website_analysis",
    stage: "won",
    lead_quality_score: 98,
    seo_score: 64,
    business_score: 94,
    opportunity_priority: "High",
    estimated_deal_value: 195,
    contact_person: "Dr. Sarah Jenkins, MD",
    email: "sarah.jenkins@zenithorthoclinic.com",
    last_activity: "1 day ago",
    created_at: "2026-08-22T09:00:00Z",
  },
  {
    id: "lead-008",
    business_name: "Kavita Logistics & Cold Chain Freight",
    category: "Refrigerated Supply Chain Logistics",
    location: "Mumbai, MH, India",
    phone_number: "+91 98200 44119",
    website: "https://kavitalogisticsfreight.in",
    rating: 4.5,
    reviews_count: 74,
    source: "IndiaMART",
    decision_path: "voice_bot_pitch",
    stage: "outreach_active",
    lead_quality_score: 86,
    seo_score: 39,
    business_score: 87,
    opportunity_priority: "High",
    estimated_deal_value: 89,
    contact_person: "Amitabh Deshmukh",
    email: "amitabh@kavitalogisticsfreight.in",
    last_activity: "4 hours ago",
    created_at: "2026-08-23T05:00:00Z",
  },
];

export const mockSEOMetrics: Record<string, SEOMetric[]> = {
  "lead-001": [
    {
      category: "Core Web Vitals & Mobile Latency",
      score: 36,
      status: "critical",
      details:
        "LCP is 4.8s on 4G connections. Uncompressed hero background (3.4MB) and 18 render-blocking JavaScript bundles causing 64% bounce rate.",
    },
    {
      category: "Local SEO & Schema Markup",
      score: 52,
      status: "warning",
      details:
        "Missing LocalBusiness and AggregateRating JSON-LD schema. Duplicate H1 tags on 14 subpages and missing city-specific keywords.",
    },
    {
      category: "Conversion Flow & Interactive Funnel",
      score: 41,
      status: "critical",
      details:
        "No online solar subsidy calculator, contact form has 9 required fields, and the phone button is not configured as a tap-to-call link on mobile.",
    },
    {
      category: "Security, TLS & Technical Architecture",
      score: 78,
      status: "good",
      details:
        "Valid Let’s Encrypt TLS certificate with HTTP/2 enabled. Server response time (TTFB) is acceptable at 420ms on Apache/2.4.",
    },
  ],
  "lead-002": [
    {
      category: "Emergency Dispatch Conversion Speed",
      score: 44,
      status: "critical",
      details:
        "Mobile site takes 3.9s to load. Lacks instant 24/7 emergency dispatch booking button, resulting in direct lost revenue to local competitors.",
    },
    {
      category: "Google Maps Pack & Geo-Targeting",
      score: 58,
      status: "warning",
      details:
        "Inconsistent NAP citations across Yelp, Angi, and Google Business Profile. Missing service area radius schemas for Fort Worth and Arlington.",
    },
    {
      category: "Commercial Service Subpage SEO",
      score: 49,
      status: "warning",
      details:
        "Commercial Boiler and HVAC subpages lack targeted meta descriptions and case study proof metrics, scoring low in search intent.",
    },
    {
      category: "Mobile UX & Responsive Layout",
      score: 65,
      status: "good",
      details:
        "Clean layout structure but tap targets are closely spaced (<32px) leading to mobile usability warnings in Google Search Console.",
    },
  ],
  "lead-003": [
    {
      category: "Digital Catalog & Search Indexability",
      score: 28,
      status: "critical",
      details:
        "Zero standalone website indexation. Entire product list relies on unindexed PDF catalog sheets and third-party IndiaMART listing.",
    },
    {
      category: "B2B Wholesale Ordering UX",
      score: 34,
      status: "critical",
      details:
        "No automated RFQ (Request for Quote) system or WhatsApp instant inventory check. Wholesale buyers forced into manual phone calls.",
    },
    {
      category: "Brand Credibility & Industry Trust",
      score: 72,
      status: "good",
      details:
        "Verified GSTIN registration and 15+ years of verified business operations in Chennai Ambattur industrial hub.",
    },
    {
      category: "Domain & Email Deliverability",
      score: 45,
      status: "warning",
      details:
        "Custom domain registered without SPF, DKIM, or DMARC records configured, causing outgoing business quotes to land in spam.",
    },
  ],
  "lead-004": [
    {
      category: "Enterprise Client Conversion Architecture",
      score: 41,
      status: "critical",
      details:
        "Static WordPress site built in 2019. Lacks client onboarding intake workflows, confidential consultation scheduler, and client document portal.",
    },
    {
      category: "High-Intent Legal Keyword Rankings",
      score: 48,
      status: "warning",
      details:
        'Ranking on page 3 for "commercial M&A legal advisory London". Zero authoritative topic clusters or recent regulatory breakdown whitepapers.',
    },
    {
      category: "Brand Authority & Social Proof Signals",
      score: 84,
      status: "good",
      details:
        "Chambers UK and Legal 500 accredited partner profiles, but badges are static low-res raster images without outbound verification links.",
    },
    {
      category: "Core Web Vitals & Script Optimization",
      score: 38,
      status: "critical",
      details:
        "Heavy 4.2MB page weight with uncompressed partner portraits and 14 obsolete tracking scripts resulting in 5.2s Largest Contentful Paint.",
    },
  ],
  "lead-005": [
    {
      category: "Cosmetic Dentistry Patient Funnel",
      score: 46,
      status: "critical",
      details:
        'Lacks interactive "Smile Simulation" preview tool and real-time online appointment booking integration with Dentrix/OpenDental.',
    },
    {
      category: "Local Map Pack & Review Velocity",
      score: 79,
      status: "good",
      details:
        "Outstanding 348 reviews (4.9 rating), but missing automated review response schema and local clinic treatment area pages.",
    },
    {
      category: "Mobile Page Speed & Media Optimization",
      score: 51,
      status: "warning",
      details:
        "High-resolution before/after dental case galleries served in uncompressed PNG format (6.8MB), causing 4.1s mobile load time.",
    },
    {
      category: "Security & HIPAA Compliance Badging",
      score: 82,
      status: "good",
      details:
        "Valid SSL and secure form gateway, but lacks explicit patient privacy badges and financing calculator.",
    },
  ],
};

export const mockBusinessAnalysis: Record<string, BusinessAnalysis> = {
  "lead-001": {
    lead_id: "lead-001",
    strengths: [
      "Top-rated commercial installer in Bangalore with 142 5-star Google reviews",
      "Direct Tier-1 partnerships with solar inverter brands (Tata Power Solar, Havells, Sungrow)",
      "Experienced in-house engineering team with 15MW+ rooftop deployments",
    ],
    weaknesses: [
      "Mobile website conversion rate is sub 1.1% due to 4.8s loading delay",
      "Lacks an automated WhatsApp solar subsidy calculator for factory owners",
      "Zero dedicated landing pages for commercial warehouse rooftop installations",
    ],
    opportunities: [
      "Karnataka Industrial Rooftop Solar Policy 2026 offering 25% tax credits",
      "Deploying an automated WhatsApp estimation bot to qualify high-capacity factory leads",
      'Capturing the top-3 Google Map pack position for "commercial solar EPC Bangalore"',
    ],
    threats: [
      "Aggressive Google Search ad bidding from venture-backed solar aggregators",
      "Commercial clients opting for competitors with instant digital quote engines",
    ],
    competitors: [
      {
        name: "SunPower Karnataka",
        advantage: "Instant online quote generator & WhatsApp bot",
      },
      {
        name: "Tata Power Solar Regional",
        advantage: "National brand authority and extensive financing",
      },
      {
        name: "Orb Energy Bangalore",
        advantage: "In-house credit underwriting and quick turnaround",
      },
    ],
    recommended_offer:
      "Commercial Solar Growth Engine: Sub-second Next.js portal, interactive WhatsApp ROI calculator, and Local SEO dominance.",
    expected_outcomes:
      "+180% Qualified Commercial Inquiries, 3.2x Mobile Conversion Speed, $140,000+ pipeline added in 90 days.",
    estimated_impact_score: 9.4,
  },
  "lead-002": {
    lead_id: "lead-002",
    strengths: [
      "Established 18-year commercial client base across Dallas-Fort Worth metroplex",
      "Licensed master technicians with 24/7 commercial emergency dispatch capabilities",
      "Strong B2B relationships with property management firms and restaurants",
    ],
    weaknesses: [
      "Mobile emergency dispatch funnel has high drop-off due to slow load times",
      "No instant online dispatch tracker or customer text update system",
      "Inconsistent local citations causing rank fluctuation outside core zip code",
    ],
    opportunities: [
      "Commercial preventative maintenance retainers for multi-unit retail complexes",
      '1-Click "Dispatch Now" mobile micro-portal with live arrival countdown',
      'Dominating local search for "commercial refrigeration repair Dallas"',
    ],
    threats: [
      "National franchise operators spending heavily on local Google Local Services Ads (LSA)",
      "Customer churn during peak summer heatwaves due to delayed quote follow-up",
    ],
    competitors: [
      {
        name: "Dallas Commercial HVAC Pro",
        advantage: "Guaranteed 60-min emergency response app",
      },
      {
        name: "Texas Mechanical Solutions",
        advantage: "Automated quarterly maintenance contract portal",
      },
    ],
    recommended_offer:
      "Rapid Commercial HVAC Dispatch Suite: Sub-second emergency mobile booking, automated SMS status dispatch, and local SEO dominance.",
    expected_outcomes:
      "+45 Monthly High-Margin Service Contracts, 70% Faster Emergency Booking Velocity.",
    estimated_impact_score: 8.9,
  },
  "lead-004": {
    lead_id: "lead-004",
    strengths: [
      "Distinguished Tier-1 corporate boutique with £50M+ in cross-border M&A transactions",
      "Senior partners with Oxford/Cambridge pedigrees and Chambers UK ranking",
      "High client retention rate (88%) among mid-market tech startups and private equity",
    ],
    weaknesses: [
      "Dated web presence fails to communicate premium prestige to foreign PE investors",
      "No confidential client intake onboarding or interactive fee estimate calculator",
      "Lacks structured content marketing or thought leadership on UK corporate compliance",
    ],
    opportunities: [
      "Targeting US venture capital firms investing in UK AI and biotech startups",
      "Premium private deal room and digital retainer consultation experience",
      'Ranking top-3 for "cross-border tech M&A legal advisory London"',
    ],
    threats: [
      "Magic Circle legal spin-offs deploying modern digital client portals",
      "High acquisition cost for unsolicited inbound enterprise inquiries",
    ],
    competitors: [
      {
        name: "Kemp Corporate Legal London",
        advantage: "Interactive startup equity & compliance portal",
      },
      {
        name: "Mayfair Venture Advisory",
        advantage:
          "High-visibility thought leadership podcast and research desk",
      },
    ],
    recommended_offer:
      "Prestige Legal Growth Suite: Bespoke headless brand portal, confidential partner booking experience, and UK corporate SEO authority.",
    expected_outcomes:
      "3-4 High-Value Retainer Engagements (£60k–£120k annually), 5x increase in qualified overseas M&A inquiries.",
    estimated_impact_score: 9.7,
  },
};

export const mockProposals: Record<string, Proposal> = {
  "lead-001": {
    id: "prop-001",
    lead_id: "lead-001",
    title: "CleanTech Commercial Revenue Growth & High-Velocity Lead Engine",
    executive_summary:
      "Apex Solar is a premier commercial solar EPC in Bangalore, yet digital conversion leakage is costing an estimated 35-50 high-value industrial inquiries monthly. This proposal outlines the turnkey deployment of a sub-second Next.js growth portal, automated WhatsApp solar ROI calculator, and commercial SEO dominance.",
    identified_problems: [
      "Severe mobile latency (4.8s LCP) causing 64% prospective client bounce rate",
      "Absence of instant quote/subsidy calculator mechanisms for factory owners",
      "Competitors dominating top-3 Google Map pack for high-margin industrial keywords",
    ],
    proposed_solution:
      "Deployment of the NextGen CleanTech Growth Architecture: Sub-second headless web portal, interactive WhatsApp ROI estimation bot, and specialized local SEO dominance suite.",
    deliverables: [
      {
        title: "Sub-Second Next.js High-Conversion Web Architecture",
        timeline: "Week 1 - 2",
        price: 55,
      },
      {
        title: "Interactive Solar ROI & Subsidy WhatsApp Bot Engine",
        timeline: "Week 2 - 3",
        price: 42,
      },
      {
        title: "Commercial EPC Local SEO Domination Suite (Top-3 Ranking)",
        timeline: "Week 3 - 4",
        price: 48,
      },
    ],
    total_investment: 145,
    roi_estimate:
      "Expected return of $1,400+ in new commercial solar installations within 90 days.",
    status: "ready",
    created_at: "2026-08-23",
  },
  "lead-002": {
    id: "prop-002",
    lead_id: "lead-002",
    title:
      "Emergency Commercial HVAC Dispatch & Preventative Contract Growth Suite",
    executive_summary:
      "Metro Commercial Plumbing & HVAC has an exceptional 18-year local reputation in Dallas. This proposal provides the modern infrastructure needed to capture 100% of urgent commercial emergency calls and convert them into recurring quarterly maintenance contracts.",
    identified_problems: [
      "Slow mobile page load (3.9s) resulting in abandoned emergency service calls",
      "Lack of 1-click emergency dispatch scheduler with automated SMS arrival tracking",
      "Under-optimized service area pages for high-growth suburbs in DFW",
    ],
    proposed_solution:
      "Deploy a high-speed emergency response mobile engine with instant technician dispatch integration, automated SMS confirmations, and geo-targeted commercial HVAC landing pages.",
    deliverables: [
      {
        title: "Rapid-Load Emergency Dispatch Mobile Web Experience",
        timeline: "Week 1 - 2",
        price: 38,
      },
      {
        title: "Automated SMS Dispatch & Review Generation Engine",
        timeline: "Week 2 - 3",
        price: 26,
      },
      {
        title: "DFW Commercial Geo-SEO & Local Service Ad Funnel",
        timeline: "Week 3 - 4",
        price: 28,
      },
    ],
    total_investment: 92,
    roi_estimate:
      "Projected $850+ in annual recurring maintenance contracts and 35+ emergency calls monthly.",
    status: "ready",
    created_at: "2026-08-23",
  },
  "lead-004": {
    id: "prop-004",
    lead_id: "lead-004",
    title:
      "Prestige Corporate Legal Advisory Digital Transformation & Authority Suite",
    executive_summary:
      "Sterling & Partners represents premier mid-market M&A and corporate clients in London. This proposal elevates the digital prestige of the firm, streamlining confidential partner consultations and capturing high-intent international deal inquiries.",
    identified_problems: [
      "Legacy website fails to project the firm’s prestige and Tier-1 market position",
      "Friction in confidential partner onboarding and intake scheduling",
      "Zero organic search visibility for high-yield cross-border M&A advisory searches",
    ],
    proposed_solution:
      "Design and deploy a bespoke, ultra-fast headless corporate legal portal with encrypted client intake forms, private partner booking calendars, and authoritative legal thought leadership hubs.",
    deliverables: [
      {
        title: "Bespoke Ultra-Fast Corporate Brand & Deal Showcase Portal",
        timeline: "Week 1 - 3",
        price: 85,
      },
      {
        title:
          "Confidential Client Intake & Encrypted Partner Scheduling Suite",
        timeline: "Week 3 - 5",
        price: 45,
      },
      {
        title:
          "London & International Corporate Law Thought Leadership SEO Suite",
        timeline: "Week 5 - 6",
        price: 55,
      },
    ],
    total_investment: 185,
    roi_estimate:
      "Estimated $1,800+ in new retained corporate accounts over the next 12 months.",
    status: "ready",
    created_at: "2026-08-23",
  },
};

export const mockOutreachAssets: Record<string, OutreachAsset[]> = {
  "lead-001": [
    {
      id: "out-001",
      lead_id: "lead-001",
      channel: "email",
      subject:
        "Quick question regarding Apex Solar’s commercial inquiries in Bangalore",
      content: `Hi Rajesh,\n\nNoticed Apex Solar has built an exceptional track record with over 140+ 5-star reviews across Bangalore—congratulations on the recent industrial rooftop projects in Peenya and Whitefield.\n\nWhile reviewing your digital footprint, our AI audit noticed mobile visitors face a 4.8s loading delay, and potential factory owners cannot calculate their Karnataka solar subsidy ROI on the spot. Competitors like SunPower Karnataka are currently capturing those instant searches.\n\nWe prepared a complimentary 1-page breakdown showing how adding an instant WhatsApp ROI calculator would capture an extra 30–40 commercial solar contracts per quarter.\n\nWould you be open to a 7-minute look at the numbers this Thursday at 3 PM?\n\nBest regards,\nSarah Jenkins | AgencyOS Growth Engineering`,
      sequence_step: 1,
      status: "ready",
    },
    {
      id: "out-002",
      lead_id: "lead-001",
      channel: "linkedin",
      content: `Rajesh, loved the recent 500kW rooftop installation Apex Solar completed in Whitefield. Noticed your web presence could easily 2x commercial factory inquiries with an automated subsidy ROI calculator. Sent a quick 1-page PDF breakdown to your email—happy to connect!`,
      sequence_step: 2,
      status: "ready",
    },
    {
      id: "out-003",
      lead_id: "lead-001",
      channel: "call_script",
      content: `[GREETING]: Hi Rajesh, this is Alex calling on behalf of AgencyOS CleanTech Intelligence. Calling regarding Apex Solar's commercial installations in Bangalore.\n[HOOK]: Saw your stellar 142 reviews. Quick question: are your sales engineers finding that factory owners prefer calculating their rooftop solar subsidy on WhatsApp before booking an on-site audit?\n[OBJECTION - "We already have a web designer"]: Absolutely, your site has great testimonials. The issue is factory owners on mobile wait 4+ seconds and bounce to competitors before submitting a quote.\n[CTA]: I have a 3-minute interactive model built specifically for Apex Solar. Would tomorrow at 11:30 AM or 3:00 PM work for a brief walkthrough?`,
      sequence_step: 3,
      status: "ready",
    },
  ],
  "lead-002": [
    {
      id: "out-004",
      lead_id: "lead-002",
      channel: "email",
      subject:
        "Emergency commercial HVAC dispatch inquiry for Metro Dallas Plumbing",
      content: `Hi David,\n\nSaw Metro Commercial Plumbing's outstanding 18-year track record across Dallas. With the upcoming summer heatwave across DFW, commercial HVAC emergencies will surge.\n\nOur automated audit noticed your mobile site takes 3.9s to load and lacks a 1-click "Dispatch Now" emergency button. Restaurants and property managers searching on mobile are bouncing to local operators who offer real-time dispatch tracking.\n\nWe mapped out how a sub-second dispatch portal can add 30+ emergency commercial maintenance retainers for Metro Dallas this quarter.\n\nDo you have 5 minutes for a brief call tomorrow afternoon?\n\nBest,\nDavid Vance | AgencyOS Engineering`,
      sequence_step: 1,
      status: "ready",
    },
  ],
};

export const mockCallLogs: CallLog[] = [
  {
    id: "call-001",
    lead_id: "lead-005",
    business_name: "Horizon Advanced Dental Care",
    contact_name: "Dr. Michael Evans, DDS",
    phone_number: "+1 (512) 555-0188",
    duration_seconds: 168,
    status: "completed",
    interest_score: 92,
    meeting_booked: true,
    meeting_time: "2026-08-27 02:00 PM CST",
    summary:
      "Dr. Evans confirmed interest in modernizing his dental clinic mobile booking portal and integrating an automated patient review generation system. Scheduled live zoom demo for Thursday at 2 PM.",
    transcript: [
      {
        speaker: "AI SDR Agent",
        text: "Hello Dr. Evans, calling from AgencyOS Healthcare Solutions. Calling regarding Horizon Dental in Austin. Am I speaking with the clinic director?",
        timestamp: "00:02",
      },
      {
        speaker: "Prospect",
        text: "Yes, this is Dr. Evans. I have about two minutes before my next patient.",
        timestamp: "00:09",
      },
      {
        speaker: "AI SDR Agent",
        text: "Totally respect your time, Doctor! Saw your stellar 348 5-star reviews on Google. Quick question: are your staff spending too much time fielding manual phone calls for cosmetic smile consultations that could be booked online in 30 seconds?",
        timestamp: "00:16",
      },
      {
        speaker: "Prospect",
        text: "Yeah, our front desk gets completely overwhelmed around lunchtime. But we already use an appointment software.",
        timestamp: "00:34",
      },
      {
        speaker: "AI SDR Agent",
        text: "Understood! Most Austin dentists have software, but patients on mobile wait 4+ seconds and bounce before finishing. We build sub-second booking funnels that sync directly into your calendar and increase cosmetic cases by 40%.",
        timestamp: "00:46",
      },
      {
        speaker: "Prospect",
        text: "How much does this typically run?",
        timestamp: "01:05",
      },
      {
        speaker: "AI SDR Agent",
        text: "It pays for itself with just one single cosmetic implant case per quarter. I can show you a live interactive mock model built for Horizon Dental this Thursday at 2 PM. Would that work for you?",
        timestamp: "01:14",
      },
      {
        speaker: "Prospect",
        text: "Thursday at 2 PM works. Send the calendar invite to drmichael@horizondentalcare-austin.com.",
        timestamp: "01:32",
      },
      {
        speaker: "AI SDR Agent",
        text: "Confirmed Dr. Evans! Calendar invite and 1-page overview are sent. Looking forward to speaking Thursday at 2 PM!",
        timestamp: "01:42",
      },
    ],
    objections: [
      "Short time window",
      "Existing software in place",
      "Pricing inquiry",
    ],
  },
  {
    id: "call-002",
    lead_id: "lead-003",
    business_name: "Gupta Industrial Hardware & Fasteners",
    contact_name: "Suresh Gupta",
    phone_number: "+91 94440 88214",
    duration_seconds: 142,
    status: "completed",
    interest_score: 88,
    meeting_booked: true,
    meeting_time: "2026-08-26 11:30 AM IST",
    summary:
      "Lead expressed strong interest in getting a dedicated digital catalog and instant WhatsApp wholesale ordering portal to compete with tier-1 suppliers.",
    transcript: [
      {
        speaker: "AI SDR Agent",
        text: "Namaste Suresh ji, calling from AgencyOS B2B Growth. Am I speaking with the proprietor of Gupta Hardware in Chennai?",
        timestamp: "00:02",
      },
      {
        speaker: "Prospect",
        text: "Haan, Suresh speaking. What is this about?",
        timestamp: "00:08",
      },
      {
        speaker: "AI SDR Agent",
        text: "We saw your strong hardware catalog on IndiaMART. Many industrial dealers in Ambattur lose wholesale re-orders because factory buyers cannot check live stock on WhatsApp. We build turnkey WhatsApp ordering catalogs in 48 hours.",
        timestamp: "00:15",
      },
      {
        speaker: "Prospect",
        text: "Is it complicated? My staff is not very technical.",
        timestamp: "00:32",
      },
      {
        speaker: "AI SDR Agent",
        text: "It runs 100% on WhatsApp—no apps to install. If your staff can send a WhatsApp photo, they can manage orders in 5 seconds and save 15 hours of phone calls weekly.",
        timestamp: "00:45",
      },
      {
        speaker: "Prospect",
        text: "Okay, sounds useful. Show me a demo this Wednesday morning.",
        timestamp: "01:12",
      },
      {
        speaker: "AI SDR Agent",
        text: "Confirmed Suresh ji! Wednesday 11:30 AM IST is booked. Details are sent to your WhatsApp number.",
        timestamp: "01:22",
      },
    ],
    objections: ["Technical complexity skepticism", "Staff usability"],
  },
  {
    id: "call-003",
    lead_id: "lead-001",
    business_name: "Apex Solar Energy Solutions",
    contact_name: "Rajesh K. Verma",
    phone_number: "+91 98450 12890",
    duration_seconds: 118,
    status: "completed",
    interest_score: 84,
    meeting_booked: false,
    summary:
      "2-strike soft convincing flow: Prospect initially hesitated on pricing, agent smoothly offered the free 1-page commercial audit PDF, and prospect gladly accepted via email.",
    transcript: [
      {
        speaker: "AI SDR Agent",
        text: "Hello Rajesh ji, Sarah calling from AgencyOS CleanTech. Calling regarding Apex Solar rooftop projects in Bangalore.",
        timestamp: "00:02",
      },
      {
        speaker: "Prospect",
        text: "Hi Sarah, we are quite busy with installations right now, not looking for marketing services.",
        timestamp: "00:12",
      },
      {
        speaker: "AI SDR Agent",
        text: "Totally understand, Rajesh! We actually already prepared a complimentary 1-page website audit PDF showing where mobile factory inquiries are dropping off on your site. Can I at least shoot that over to your email for your records?",
        timestamp: "00:24",
      },
      {
        speaker: "Prospect",
        text: "Oh, you already prepared it? Sure, you can email it to rajesh.verma@apexsolarenergy.in.",
        timestamp: "00:42",
      },
      {
        speaker: "AI SDR Agent",
        text: "Sent! It includes the speed metrics and the WhatsApp quote bot preview. Have a great day and good luck with the installations!",
        timestamp: "00:55",
      },
    ],
    objections: [
      "Busy / not looking for services (Resolved via free PDF audit gift)",
    ],
  },
];

export const mockScraperStatuses: ScraperStatusRecord[] = [
  {
    id: "sc-01",
    collector_id: "c_mt1qfvqx1051f3m8r9",
    name: "Google Maps Business Intelligence Fleet",
    target_domain: "google.com/maps",
    status: "READY",
    records_extracted: 14820,
    health_score: 0.99,
    healing_attempts: 0,
  },
  {
    id: "sc-02",
    collector_id: "c_mt1klz941e6wjo8o6y",
    name: "IndiaMART B2B Merchant Discovery",
    target_domain: "dir.indiamart.com",
    status: "READY",
    records_extracted: 32400,
    health_score: 0.97,
    healing_attempts: 1,
    last_healed: "2026-08-23 14:10 UTC",
  },
  {
    id: "sc-03",
    collector_id: "c_mt38sv49yfrrosp1u",
    name: "Yelp Local Business & Review Collector",
    target_domain: "yelp.com",
    status: "READY",
    records_extracted: 9140,
    health_score: 0.96,
    healing_attempts: 0,
  },
  {
    id: "sc-04",
    collector_id: "c_mt39jryq1q6vcwtxcy",
    name: "Avvo Legal & Professional Registry",
    target_domain: "avvo.com",
    status: "READY",
    records_extracted: 4380,
    health_score: 0.94,
    healing_attempts: 0,
  },
  {
    id: "sc-05",
    collector_id: "c_mt99plwq481abce92z",
    name: "Bright Data Scraping Browser (Self-Healing Headless)",
    target_domain: "brightdata.com/scraping-browser",
    status: "READY",
    records_extracted: 68250,
    health_score: 1.0,
    healing_attempts: 2,
    last_healed: "2026-08-23 18:22 UTC",
  },
];
