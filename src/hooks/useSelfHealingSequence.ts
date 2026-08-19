'use client'
import { useState, useCallback, useRef } from 'react'

export type HealingPhase = 'idle' | 'running' | 'failure' | 'healing' | 'recovered'

interface EventEntry {
  time: string
  type: string
  message: string
}

export function useSelfHealingSequence() {
  const [phase, setPhase] = useState<HealingPhase>('idle')
  const [eventLog, setEventLog] = useState<EventEntry[]>([])
  const timeouts = useRef<ReturnType<typeof setTimeout>[]>([])

  const addEvent = useCallback((type: string, message: string) => {
    const time = new Date().toLocaleTimeString('en-US', { hour12: false })
    setEventLog((prev) => [...prev, { time, type, message }])
  }, [])

  const start = useCallback(() => {
    timeouts.current.forEach(clearTimeout)
    setEventLog([])
    setPhase('running')
    addEvent('info', 'Collector: restaurant-discovery — Running')

    const schedule = (fn: () => void, delay: number) =>
      setTimeout(fn, delay)

    timeouts.current = [
      schedule(() => addEvent('info', '✓ 127 records extracted'), 800),
      schedule(() => addEvent('info', '✓ Data validated'), 1200),
      schedule(() => { setPhase('failure'); addEvent('warning', '⚠ Website structure changed') }, 2000),
      schedule(() => addEvent('error', '⚠ Selector no longer found'), 2400),
      schedule(() => addEvent('error', '⚠ Extraction returned empty'), 2700),
      schedule(() => { setPhase('healing'); addEvent('healing', 'SELF-HEALING AGENT ACTIVATED') }, 3000),
      schedule(() => addEvent('healing', 'Analyzing new page structure…'), 3800),
      schedule(() => addEvent('healing', 'Generating repair strategy…'), 4600),
      schedule(() => addEvent('healing', 'Testing new extraction path…'), 5400),
      schedule(() => addEvent('success', '✓ Validation successful'), 6200),
      schedule(() => { setPhase('recovered'); addEvent('success', '✓ Collector restored — 129 records extracted') }, 6800),
    ]
  }, [addEvent])

  const reset = useCallback(() => {
    timeouts.current.forEach(clearTimeout)
    setPhase('idle')
    setEventLog([])
  }, [])

  return { phase, eventLog, start, reset }
}
