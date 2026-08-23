'use client'
import { motion } from 'framer-motion'
import { type ReactNode } from 'react'

interface ButtonProps {
  children: ReactNode
  variant?: 'primary' | 'secondary' | 'ghost'
  onClick?: () => void
  className?: string
  id?: string
}

export function Button({
  children,
  variant = 'primary',
  onClick,
  className = '',
  id,
}: ButtonProps) {
  const base =
    'relative inline-flex items-center justify-center gap-2.5 px-7 py-3.5 rounded-full font-body font-bold text-sm tracking-wide transition-all duration-300 cursor-pointer overflow-hidden outline-none group'

  const styles = {
    primary: {
      background: 'linear-gradient(135deg, #38BDF8 0%, #0284C7 50%, #6366F1 100%)',
      color: '#FFFFFF',
      boxShadow: '0 10px 30px rgba(56, 189, 248, 0.4), inset 0 1px 1.5px rgba(255, 255, 255, 0.6)',
      border: '1px solid rgba(255, 255, 255, 0.4)',
    },
    secondary: {
      background: 'rgba(255, 255, 255, 0.08)',
      color: '#FFFFFF',
      border: '1px solid rgba(255, 255, 255, 0.25)',
      backdropFilter: 'blur(16px)',
      boxShadow: '0 8px 25px rgba(0, 0, 0, 0.25), inset 0 1px 1px rgba(255, 255, 255, 0.3)',
    },
    ghost: {
      background: 'transparent',
      color: '#E2E8F0',
      border: '1px solid rgba(255, 255, 255, 0.12)',
    },
  }

  return (
    <motion.button
      id={id}
      className={`${base} ${className}`}
      style={styles[variant]}
      onClick={onClick}
      whileHover={{ scale: 1.03, y: -2 }}
      whileTap={{ scale: 0.97 }}
    >
      {/* Top Specular Shine Accent */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/80 to-transparent pointer-events-none" />

      {/* Sweep Light Reflection on Hover */}
      <div className="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/25 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-in-out pointer-events-none" />

      <span className="relative z-10 flex items-center gap-2">{children}</span>
    </motion.button>
  )
}
