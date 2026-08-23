'use client'
import { useState } from 'react'
import { motion } from 'framer-motion'

// Exact uploaded images from C:\Users\msuke\Documents\Scrape_the_Verse\images\
const UPLOADED_IMAGES = [
  { name: 'Google Maps', src: '/images/tech/Google_Maps_Logo_2020.svg.webp' },
  { name: 'Next.js', src: '/images/tech/nextjs.jpeg' },
  { name: 'DuckDuckGo', src: '/images/tech/Duck-Duck-Go-Featured-1000x450.jpg' },
  { name: 'Google Meet', src: '/images/tech/Goole-Meet.avif' },
  { name: 'CRM Integration', src: '/images/tech/20_crm.png' },
  { name: 'Tech Ecosystem', src: '/images/tech/7c7d23_de91fc0e3fd242fc8309486acdf78b7e_mv2.png' },
  { name: 'Scraper Engine', src: '/images/tech/images (1).png' },
  { name: 'Data Pipeline', src: '/images/tech/images (2).png' },
  { name: 'SEO Analyzer', src: '/images/tech/images (3).png' },
  { name: 'Lead Crawler', src: '/images/tech/images (4).png' },
  { name: 'Cloud Infra', src: '/images/tech/images.jpg' },
  { name: 'Intelligence Node', src: '/images/tech/images.png' },
]

// Duplicate array for seamless infinite right-to-left marquee loop
const MARQUEE_UPLOADED_IMAGES = [...UPLOADED_IMAGES, ...UPLOADED_IMAGES, ...UPLOADED_IMAGES]

export function TechStackSection() {
  return (
    <section
      id="tech-stack-section"
      className="py-10 md:py-14 relative border-b border-white/5 bg-transparent font-body overflow-hidden"
      aria-label="Integrated Tech Stack — Uploaded Images Slider"
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8 space-y-6">
        {/* Section Header */}
        <div className="text-center space-y-3 max-w-3xl mx-auto">
          <h2 className="text-3xl md:text-5xl font-bold font-display tracking-tight text-white">
            Built With Enterprise Technology
          </h2>
          <p className="text-xs sm:text-sm text-slate-300 font-body max-w-xl mx-auto leading-relaxed">
            The complete suite of scraping engines, AI frameworks, and developer tools powering Scrape-Verse.
          </p>
        </div>
      </div>

      {/* Continuously Moving Horizontal Marquee Track (Only Uploaded Images) */}
      <div className="relative w-full overflow-hidden mt-10">
        <motion.div
          className="flex items-center gap-16 sm:gap-24 w-max will-change-transform py-6 px-8"
          animate={{
            x: ['-33.33%', '0%'],
          }}
          transition={{
            x: {
              repeat: Infinity,
              repeatType: 'loop',
              duration: 32,
              ease: 'linear',
            },
          }}
        >
          {MARQUEE_UPLOADED_IMAGES.map((item, idx) => (
            <motion.div
              key={`${item.name}-${idx}`}
              whileHover={{ y: -4, scale: 1.08 }}
              data-cursor-hover
              title={item.name}
              className="h-20 sm:h-28 flex items-center justify-center shrink-0 group cursor-default"
            >
              <img
                src={item.src}
                alt={item.name}
                className="h-full w-auto max-w-[220px] object-contain rounded-xl drop-shadow-md group-hover:scale-108 transition-transform duration-300"
              />
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}