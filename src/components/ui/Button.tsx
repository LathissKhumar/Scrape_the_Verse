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
    'relative inline-flex items-center gap-2.5 px-6 py-3 rounded-xl font-body font-medium text-sm transition-all duration-200 cursor-pointer overflow-hidden outline-none'

  const styles = {
    primary: {
      background: 'linear-gradient(135deg, #6D28D9 0%, #8B5CF6 50%, #38BDF8 100%)',
      color: '#FFFFFF',
      boxShadow: '0 8px 25px rgba(139, 92, 246, 0.25)',
      border: '1px solid rgba(255, 255, 255, 0.2)',
    },
    secondary: {
      background: 'rgba(255, 255, 255, 0.05)',
      color: '#F5F7FA',
      border: '1px solid rgba(255, 255, 255, 0.12)',
      backdropFilter: 'blur(12px)',
    },
    ghost: {
      background: 'transparent',
      color: '#A7AFBD',
      border: '1px solid rgba(255, 255, 255, 0.07)',
    },
  }

  return (
    <motion.button
      id={id}
      className={`${base} ${className}`}
      style={styles[variant]}
      onClick={onClick}
      whileHover={{ scale: 1.02, y: -1 }}
      whileTap={{ scale: 0.98 }}
    >
      {children}
    </motion.button>
  )
}
