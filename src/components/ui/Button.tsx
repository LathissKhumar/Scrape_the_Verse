'use client'
import { motion, useReducedMotion } from 'framer-motion'
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
  const prefersReduced = useReducedMotion()

  const base =
    'relative inline-flex items-center gap-2 px-6 py-3 rounded font-mono font-semibold text-sm tracking-wide transition-all duration-200 cursor-pointer overflow-hidden border-0 outline-none'

  const styles = {
    primary: {
      background:
        'linear-gradient(135deg, #240044 0%, #6D28D9 22%, #EC0AFF 45%, #FF1744 68%, #00E5FF 100%)',
      color: '#05050A',
    },
    secondary: {
      background: 'transparent',
      color: '#F8FAFC',
      border: '1px solid rgba(236,10,255,0.5)',
    },
    ghost: {
      background: 'transparent',
      color: '#A1A1B5',
      border: '1px solid rgba(161,161,181,0.2)',
    },
  }

  return (
    <motion.button
      id={id}
      className={`${base} ${className}`}
      style={styles[variant]}
      onClick={onClick}
      whileHover={
        !prefersReduced
          ? { scale: 1.03, y: -1, boxShadow: '0 0 20px rgba(236,10,255,0.3)' }
          : {}
      }
      whileTap={!prefersReduced ? { scale: 0.97 } : {}}
    >
      {children}
    </motion.button>
  )
}
