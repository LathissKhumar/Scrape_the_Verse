'use client'
import { useEffect, useRef } from 'react'
import type { WebNode, WebEdge } from '@/lib/types'

interface UseWebAnimationOptions {
  nodes: WebNode[]
  edges: WebEdge[]
}

export function useWebAnimation(
  canvasRef: React.RefObject<HTMLCanvasElement | null>,
  options: UseWebAnimationOptions
) {
  const animFrameRef = useRef<number>(0)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const dpr = window.devicePixelRatio || 1
    let width = canvas.offsetWidth
    let height = canvas.offsetHeight

    const setSize = () => {
      width = canvas.offsetWidth
      height = canvas.offsetHeight
      canvas.width = width * dpr
      canvas.height = height * dpr
      ctx.scale(dpr, dpr)
    }
    setSize()

    // One particle per animated edge
    const particles = options.edges
      .filter((e) => e.animated)
      .map((edge) => ({ edge, offset: Math.random() }))

    let lastTime = 0

    const draw = (time: number) => {
      const dt = Math.min((time - lastTime) / 1000, 0.05)
      lastTime = time

      ctx.clearRect(0, 0, width, height)

      // Draw static edges first
      options.edges.forEach((edge) => {
        const from = options.nodes[edge.from]
        const to = options.nodes[edge.to]
        if (!from || !to) return
        ctx.beginPath()
        ctx.moveTo(from.x * width, from.y * height)
        ctx.lineTo(to.x * width, to.y * height)
        ctx.strokeStyle = edge.color ?? 'rgba(109,40,217,0.25)'
        ctx.lineWidth = 1
        ctx.stroke()
      })

      // Animate particles along edges
      particles.forEach((p) => {
        p.offset = (p.offset + dt * 0.25) % 1
        const from = options.nodes[p.edge.from]
        const to = options.nodes[p.edge.to]
        if (!from || !to) return
        const px = from.x * width + (to.x - from.x) * width * p.offset
        const py = from.y * height + (to.y - from.y) * height * p.offset
        ctx.beginPath()
        ctx.arc(px, py, 2.5, 0, Math.PI * 2)
        ctx.fillStyle = p.edge.color ?? '#EC0AFF'
        ctx.shadowBlur = 10
        ctx.shadowColor = p.edge.color ?? '#EC0AFF'
        ctx.fill()
        ctx.shadowBlur = 0
      })

      // Draw nodes on top
      options.nodes.forEach((node) => {
        const nx = node.x * width
        const ny = node.y * height
        const r = node.radius ?? 5
        ctx.beginPath()
        ctx.arc(nx, ny, r, 0, Math.PI * 2)
        ctx.fillStyle = node.color ?? '#6D28D9'
        ctx.shadowBlur = 12
        ctx.shadowColor = node.color ?? '#6D28D9'
        ctx.fill()
        ctx.shadowBlur = 0

        if (node.label) {
          ctx.font = `10px Consolas, monospace`
          ctx.fillStyle = '#A1A1B5'
          ctx.textAlign = 'center'
          ctx.fillText(node.label, nx, ny + r + 13)
        }
      })

      animFrameRef.current = requestAnimationFrame(draw)
    }

    animFrameRef.current = requestAnimationFrame(draw)

    const handleResize = () => setSize()
    window.addEventListener('resize', handleResize)

    return () => {
      cancelAnimationFrame(animFrameRef.current)
      window.removeEventListener('resize', handleResize)
    }
  }, [canvasRef, options])
}
