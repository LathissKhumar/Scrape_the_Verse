import { type ReactNode } from 'react'

export function ComicPanel({
  children,
  className = '',
  glowing = false,
}: {
  children: ReactNode
  className?: string
  glowing?: boolean
}) {
  return (
    <div
      className={`relative comic-panel bg-[#080810]/60 backdrop-blur-sm ${
        glowing ? 'glow-magenta' : ''
      } ${className}`}
    >
      {children}
    </div>
  )
}
