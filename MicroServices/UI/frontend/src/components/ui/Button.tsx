'use client'
import { motion } from 'framer-motion'
import { type ReactNode } from 'react'

interface ButtonProps {
  children: ReactNode
  variant?: 'primary' | 'secondary' | 'ghost'
  onClick?: (e?: React.MouseEvent<HTMLButtonElement>) => void
  className?: string
  id?: string
  'data-cursor-hover'?: boolean
}

export function Button({
  children,
  variant = 'primary',
  onClick,
  className = '',
  id,
  'data-cursor-hover': dataCursorHover,
}: ButtonProps) {
  const base =
    'relative inline-flex items-center justify-center gap-2.5 px-6 py-3 rounded-full font-body font-semibold text-sm transition-all duration-200 cursor-pointer overflow-hidden outline-none'

  const styles = {
    primary: {
      background: '#FFFFFF',
      color: '#07090D',
      boxShadow: '0 4px 20px rgba(255, 255, 255, 0.2), inset 0 1px 1px rgba(255, 255, 255, 0.8)',
      border: '1px solid rgba(255, 255, 255, 0.9)',
    },
    secondary: {
      background: 'rgba(255, 255, 255, 0.08)',
      color: '#F8FAFC',
      border: '1px solid rgba(255, 255, 255, 0.18)',
      backdropFilter: 'blur(16px)',
      WebkitBackdropFilter: 'blur(16px)',
      boxShadow: '0 4px 16px rgba(0, 0, 0, 0.2), inset 0 1px 1px rgba(255, 255, 255, 0.15)',
    },
    ghost: {
      background: 'transparent',
      color: '#CBD5E1',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      backdropFilter: 'blur(12px)',
      WebkitBackdropFilter: 'blur(12px)',
    },
  }

  return (
    <motion.button
      id={id}
      data-cursor-hover={dataCursorHover}
      className={`${base} ${className}`}
      style={styles[variant]}
      onClick={onClick}
      whileHover={{ scale: 1.02, y: -1 }}
      whileTap={{ scale: 0.98 }}
      transition={{ type: 'spring', stiffness: 400, damping: 25 }}
    >
      {children}
    </motion.button>
  )
}
