'use client'
import { useEffect, useRef, useState } from 'react'
import { motion, useScroll } from 'framer-motion'
import { ArrowRight, ShieldCheck, Sparkles, Activity } from 'lucide-react'
import { GradientText } from '@/components/ui/GradientText'
import { Button } from '@/components/ui/Button'

const GLYPHS = '!<>-_\\/[]{}=+*^?#01~%'

export function Hero() {
  const [headingText, setHeadingText] = useState('SCRAPE-VERSE')
  const [isScrambled, setIsScrambled] = useState(false)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const { scrollYProgress } = useScroll()

  // 1. Text Scramble Effect
  useEffect(() => {
    const target = 'BEYOND LIMITS'
    let frame = 0
    const totalFrames = 36
    let animId: number

    const timeout = setTimeout(() => {
      const tick = () => {
        const progress = frame / totalFrames
        const result = target
          .split('')
          .map((char, idx) => {
            if (char === ' ') return ' '
            if (idx < Math.floor(progress * target.length)) return char
            return GLYPHS[Math.floor(Math.random() * GLYPHS.length)]
          })
          .join('')

        setHeadingText(result)
        frame++

        if (frame <= totalFrames) {
          animId = requestAnimationFrame(tick)
        } else {
          setHeadingText(target)
          setIsScrambled(true)
        }
      }
      tick()
    }, 300)

    return () => {
      clearTimeout(timeout)
      cancelAnimationFrame(animId)
    }
  }, [])

  // 2. Interactive Canvas Particles that collapse to center on scroll
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let animId: number
    const resize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }
    resize()
    window.addEventListener('resize', resize)

    const NUM_PARTICLES = 50
    const particles = Array.from({ length: NUM_PARTICLES }, () => {
      const x = Math.random() * window.innerWidth
      const y = Math.random() * window.innerHeight
      return {
        ox: x,
        oy: y,
        angle: Math.random() * Math.PI * 2,
        speed: Math.random() * 0.35 + 0.15,
        size: Math.random() * 2.2 + 0.6,
        color: Math.random() > 0.5 ? 'rgba(56, 189, 248,' : 'rgba(129, 140, 248,',
        alpha: Math.random() * 0.5 + 0.25,
      }
    })

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      const cx = window.innerWidth / 2
      const cy = window.innerHeight / 2
      const p = scrollYProgress.get()

      particles.forEach((pt) => {
        pt.angle += pt.speed * 0.015
        const driftX = pt.ox + Math.cos(pt.angle) * 35
        const driftY = pt.oy + Math.sin(pt.angle) * 35

        const currentX = driftX + (cx - driftX) * p * p
        const currentY = driftY + (cy - driftY) * p * p
        const opacity = Math.max(0.05, pt.alpha * (1 - p * 0.8))
        const radius = Math.max(0.5, pt.size * (1 - p * 0.4))

        ctx.beginPath()
        ctx.arc(currentX, currentY, radius, 0, Math.PI * 2)
        ctx.fillStyle = `${pt.color}${opacity})`
        ctx.fill()
      })

      animId = requestAnimationFrame(render)
    }
    render()

    return () => {
      window.removeEventListener('resize', resize)
      cancelAnimationFrame(animId)
    }
  }, [scrollYProgress])

  const subtitleWords = 'Scrape-Verse continuously discovers, researches and monitors businesses across the web while self-healing in real-time.'.split(
    ' '
  )

  return (
    <section
      id="hero"
      className="relative min-h-screen flex items-center justify-center pt-28 pb-16 px-6 lg:px-12 overflow-hidden border-b border-white/10 bg-transparent font-body"
      aria-label="Hero — Scrape-Verse web intelligence"
    >
      {/* Background Interactive Canvas Particles with Scroll Implosion */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 pointer-events-none z-0 opacity-60"
      />

      {/* Dynamic Ambient Background Glow */}
      <motion.div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] rounded-full pointer-events-none opacity-25 blur-[140px]"
        style={{
          background: 'radial-gradient(circle, #38BDF8 0%, #818CF8 50%, transparent 75%)',
        }}
        animate={{
          scale: [1, 1.08, 1],
          opacity: [0.2, 0.3, 0.2],
        }}
        transition={{ duration: 7, repeat: Infinity, ease: 'easeInOut' }}
      />

      {/* Hero Content Grid */}
      <div className="relative z-10 max-w-7xl mx-auto grid lg:grid-cols-12 gap-8 lg:gap-12 items-center w-full my-auto">
        {/* Left Column */}
        <motion.div
          className="lg:col-span-5 space-y-6"
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-sky-400/60 bg-white/15 text-xs font-mono font-bold text-white backdrop-blur-xl shadow-lg shadow-sky-500/20" data-cursor-hover>
            <ShieldCheck className="w-4 h-4 text-sky-400" />
            <span className="tracking-wider text-slate-100 uppercase">Self-Healing Web Intelligence</span>
          </div>

          <div className="space-y-2">
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-xs font-mono tracking-[0.35em] text-cyan-400 uppercase font-bold flex items-center gap-2"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>{headingText}</span>
            </motion.div>

            <h1 className="text-4xl sm:text-5xl lg:text-[56px] font-bold font-display leading-[1.08] tracking-tight text-text-primary">
              The web changes.
              <br />
              <GradientText className="py-0.5">
                Your intelligence adapts.
              </GradientText>
            </h1>
          </div>

          {/* Subtitle with staggered word entrance */}
          <div className="flex flex-wrap gap-x-1.5 gap-y-1 text-sm sm:text-base font-body leading-relaxed text-text-secondary max-w-lg">
            {subtitleWords.map((word, i) => (
              <motion.span
                key={i}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{
                  duration: 0.5,
                  delay: 0.4 + i * 0.03,
                  ease: [0.16, 1, 0.3, 1],
                }}
                className="inline-block"
              >
                {word}
              </motion.span>
            ))}
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-wrap items-center gap-3.5 pt-2">
            <Button
              id="hero-cta-primary"
              variant="primary"
              className="!text-sm !px-6 !py-3 shadow-xl shadow-sky-500/25 flex items-center gap-2"
              data-cursor-hover
            >
              <span>Explore Intelligence Engine</span>
              <ArrowRight className="w-4 h-4" />
            </Button>
            <Button
              id="hero-cta-secondary"
              variant="secondary"
              className="!text-sm !px-6 !py-3"
              data-cursor-hover
            >
              See How It Works
            </Button>
          </div>
        </motion.div>

        {/* Right Column — Cold Tech Animated Developer Workspace */}
        <motion.div
          className="lg:col-span-7 lg:pl-2"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
        >
          <motion.div
            className="glass-level-3 p-2.5 sm:p-3 relative overflow-hidden group rounded-2xl border border-white/25 shadow-2xl w-full"
            animate={{
              y: [0, -4, 0],
            }}
            transition={{
              duration: 5,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
            whileHover={{
              scale: 1.01,
              borderColor: 'rgba(56, 189, 248, 0.6)',
              boxShadow: '0 25px 70px rgba(56, 189, 248, 0.3)',
            }}
            data-cursor-hover
          >
            {/* Top Specular Shine Accent */}
            <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/70 to-transparent z-30" />

            {/* Cold Animated Desktop Container */}
            <div className="relative rounded-xl overflow-hidden h-[340px] sm:h-[400px] lg:h-[430px] w-full border border-sky-400/25 bg-black/40 shadow-inner">
              {/* Cold Tech Workspace Image */}
              <img
                src="/images/cold_tech_desktop_workspace.jpg"
                alt="Cold Tech Developer Desktop with Multi-Monitor Real-Time Web Intelligence Scraper"
                className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-700 filter brightness-105"
              />

              {/* 1. Live Animated Scanner Laser Beam */}
              <motion.div
                className="absolute inset-x-0 h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent shadow-[0_0_15px_#00d4ff] z-20 pointer-events-none opacity-80"
                animate={{
                  top: ['0%', '100%', '0%'],
                }}
                transition={{
                  duration: 6,
                  repeat: Infinity,
                  ease: 'easeInOut',
                }}
              />

              {/* 2. Top-Left Live Telemetry HUD Chip */}
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="absolute top-4 left-4 z-20 px-3 py-1.5 rounded-xl bg-[#07090D]/80 border border-sky-400/40 backdrop-blur-xl shadow-lg flex items-center gap-2 font-mono text-[11px] text-slate-100"
              >
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                <span className="font-bold text-cyan-300">LIVE ENGINE</span>
                <span className="text-slate-400">· 500M+ EPS</span>
              </motion.div>

              {/* 3. Bottom-Right Live Diagnostics Chip */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 }}
                className="absolute bottom-4 right-4 z-20 px-3 py-1.5 rounded-xl bg-[#07090D]/80 border border-indigo-400/40 backdrop-blur-xl shadow-lg flex items-center gap-2 font-mono text-[11px] text-slate-200"
              >
                <Activity className="w-3 h-3 text-sky-400 animate-pulse" />
                <span>AI: <strong className="text-emerald-400">OPTIMAL</strong></span>
              </motion.div>

              {/* 4. Ambient Cyan Vignette */}
              <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(56,189,248,0.2)_0%,transparent_60%)] pointer-events-none z-10" />
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}
