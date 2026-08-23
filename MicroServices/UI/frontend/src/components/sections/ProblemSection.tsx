'use client'
import { motion } from 'framer-motion'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'

const WITHOUT_ITEMS = [
  'Manually search IndiaMART, Yelp, Google one by one',
  'Open each business website and inspect it yourself',
  'Audit SEO manually using separate tools',
  'Research the business, market, and customer profile',
  'Guess what digital service to pitch',
  'Write a cold outreach message from scratch',
  'Track leads in a spreadsheet',
]

const WITH_ITEMS = [
  'Leads discovered automatically from multiple sources',
  'Website crawled and audited by AI instantly',
  'Full SEO report generated with specific findings',
  'Business, market, and customer context built by agents',
  'Service recommendation generated from evidence',
  'Personalized outreach drafted automatically',
  'Lead pipeline managed with priority scoring',
]

const containerVariants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.07 },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 16 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: 'easeOut' as const },
  },
}

export function ProblemSection() {
  return (
    <section
      id="problem"
      className="py-10 md:py-14 relative border-b border-white/5 bg-transparent font-body overflow-hidden"
      aria-label="The Problem — Manual Research Bottleneck"
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8 space-y-16">
        {/* Header */}
        <motion.div
          className="text-center space-y-4 max-w-3xl mx-auto"
          initial={{ opacity: 0, y: 32 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-15%' }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        >
          <SectionLabel label="THE PROBLEM" />
          <h2 className="text-4xl md:text-5xl font-bold font-display tracking-tight text-text-primary">
            Every Agency Wastes Hours on Research{' '}
            <GradientText>That Should Take Seconds</GradientText>
          </h2>
          <p className="text-base text-text-secondary font-body max-w-2xl mx-auto leading-relaxed">
            Before pitching a single client, your team manually searches directories, opens websites,
            audits SEO, researches the business, studies the market, figures out what to offer, and
            then writes a proposal — for every single lead. AgencyOS eliminates that entire chain.
          </p>
        </motion.div>

        {/* Two-column comparison without frames, separated by a single vertical line */}
        <div className="relative max-w-5xl mx-auto">
          {/* Central Vertical Dividing Line for desktop */}
          <div className="hidden md:block absolute top-0 bottom-0 left-1/2 -translate-x-1/2 w-px bg-gradient-to-b from-transparent via-white/30 to-transparent pointer-events-none" />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-16 items-start">
            {/* Without AgencyOS */}
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: '-15%' }}
              transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
              className="space-y-6 md:pr-8"
            >
              <h3 className="text-xl font-bold font-display text-sky-400">
                Without AgencyOS
              </h3>
              <motion.ul
                className="space-y-4"
                variants={containerVariants}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, margin: '-15%' }}
              >
                {WITHOUT_ITEMS.map((item, i) => (
                  <motion.li
                    key={i}
                    variants={itemVariants}
                    className="flex items-start gap-3 text-sm sm:text-base font-body text-slate-300/90 leading-relaxed"
                  >
                    <span className="mt-2 w-1.5 h-1.5 rounded-full bg-sky-400 shrink-0 shadow-[0_0_8px_#38bdf8]" />
                    <span>{item}</span>
                  </motion.li>
                ))}
              </motion.ul>
            </motion.div>

            {/* With AgencyOS */}
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: '-15%' }}
              transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
              className="space-y-6 md:pl-8"
            >
              <h3 className="text-xl font-bold font-display text-cyan-300">
                With AgencyOS
              </h3>
              <motion.ul
                className="space-y-4"
                variants={containerVariants}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, margin: '-15%' }}
              >
                {WITH_ITEMS.map((item, i) => (
                  <motion.li
                    key={i}
                    variants={itemVariants}
                    className="flex items-start gap-3 text-sm sm:text-base font-body text-white leading-relaxed"
                  >
                    <span className="mt-2 w-1.5 h-1.5 rounded-full bg-cyan-300 shrink-0 shadow-[0_0_8px_#67e8f9]" />
                    <span className="font-medium">{item}</span>
                  </motion.li>
                ))}
              </motion.ul>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  )
}
