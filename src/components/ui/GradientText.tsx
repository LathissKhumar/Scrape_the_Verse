'use client'
import { type ReactNode } from 'react'

type GradientVariant = 'brand' | 'failure' | 'healing' | 'recovery'

const GRADIENTS: Record<GradientVariant, string> = {
  brand:
    'linear-gradient(135deg, #240044 0%, #6D28D9 22%, #EC0AFF 45%, #FF1744 68%, #00E5FF 100%)',
  failure: 'linear-gradient(135deg, #FF1744, #EC0AFF)',
  healing: 'linear-gradient(135deg, #EC0AFF, #6D28D9)',
  recovery: 'linear-gradient(135deg, #6D28D9, #00E5FF)',
}

interface GradientTextProps {
  children: ReactNode
  className?: string
  gradient?: GradientVariant
}

export function GradientText({
  children,
  className = '',
  gradient = 'brand',
}: GradientTextProps) {
  return (
    <span
      className={`inline-block bg-clip-text text-transparent ${className}`}
      style={{ backgroundImage: GRADIENTS[gradient] }}
    >
      {children}
    </span>
  )
}
