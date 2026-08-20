'use client'
import { useRef } from 'react'
import { useWebAnimation } from '@/hooks/useWebAnimation'
import type { WebNode, WebEdge } from '@/lib/types'

export function WebCanvas({
  nodes,
  edges,
  className = '',
}: {
  nodes: WebNode[]
  edges: WebEdge[]
  className?: string
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  useWebAnimation(canvasRef, { nodes, edges })

  return (
    <canvas
      ref={canvasRef}
      className={`w-full h-full ${className}`}
      aria-hidden="true"
    />
  )
}
