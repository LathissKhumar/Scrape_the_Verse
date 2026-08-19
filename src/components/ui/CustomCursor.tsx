'use client'
import { useEffect, useRef } from 'react'

export function CustomCursor() {
  const dotRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const dot = dotRef.current
    if (!dot) return

    let mouseX = window.innerWidth / 2
    let mouseY = window.innerHeight / 2
    let dotX = mouseX
    let dotY = mouseY
    let animId: number

    const onMouseMove = (e: MouseEvent) => {
      mouseX = e.clientX
      mouseY = e.clientY
    }

    const onMouseEnterInteractive = () => {
      dot.classList.add('cursor-enlarged')
    }

    const onMouseLeaveInteractive = () => {
      dot.classList.remove('cursor-enlarged')
    }

    window.addEventListener('mousemove', onMouseMove, { passive: true })

    const attachListeners = () => {
      document.querySelectorAll('a, button, [data-cursor-hover], input, select').forEach((el) => {
        el.removeEventListener('mouseenter', onMouseEnterInteractive)
        el.removeEventListener('mouseleave', onMouseLeaveInteractive)
        el.addEventListener('mouseenter', onMouseEnterInteractive)
        el.addEventListener('mouseleave', onMouseLeaveInteractive)
      })
    }

    attachListeners()
    const observer = new MutationObserver(attachListeners)
    observer.observe(document.body, { childList: true, subtree: true })

    const render = () => {
      dotX += (mouseX - dotX) * 0.14
      dotY += (mouseY - dotY) * 0.14
      dot.style.transform = `translate3d(${dotX}px, ${dotY}px, 0) translate(-50%, -50%)`
      animId = requestAnimationFrame(render)
    }
    animId = requestAnimationFrame(render)

    return () => {
      window.removeEventListener('mousemove', onMouseMove)
      cancelAnimationFrame(animId)
      observer.disconnect()
    }
  }, [])

  return (
    <>
      <div
        ref={dotRef}
        aria-hidden="true"
        className="fixed top-0 left-0 w-3 h-3 rounded-full bg-cyan-400 pointer-events-none z-[99999] mix-blend-screen shadow-[0_0_12px_rgba(56,189,248,0.8)] transition-[width,height,background-color,border-radius] duration-200 ease-out will-change-transform hidden md:block"
        style={{ transform: 'translate3d(-100px, -100px, 0)' }}
      />
      <style jsx global>{`
        .cursor-enlarged {
          width: 44px !important;
          height: 44px !important;
          background-color: rgba(129, 140, 248, 0.35) !important;
          border: 1.5px solid rgba(56, 189, 248, 0.8) !important;
          backdrop-filter: blur(2px);
          box-shadow: 0 0 25px rgba(56, 189, 248, 0.5) !important;
        }
        @media (min-width: 768px) {
          a, button, [data-cursor-hover] {
            cursor: none !important;
          }
        }
      `}</style>
    </>
  )
}
