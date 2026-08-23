'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import { API_URLS } from '@/lib/api/client';

export interface TimelineEvent {
  id: string;
  topic: string;
  timestamp: string;
  data: Record<string, unknown>;
}

export function useTimelineStream(enabled: boolean = true) {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [lastEvent, setLastEvent] = useState<TimelineEvent | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const clearEvents = useCallback(() => {
    setEvents([]);
  }, []);

  useEffect(() => {
    if (!enabled || typeof window === 'undefined') {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
        setIsConnected(false);
      }
      return;
    }

    const sseUrl = `${API_URLS.LEAD_MANAGER}/api/v1/timeline/stream`;
    let es: EventSource | null = null;
    let reconnectTimeout: NodeJS.Timeout | null = null;

    function connect() {
      try {
        es = new EventSource(sseUrl);
        eventSourceRef.current = es;

        es.onopen = () => {
          setIsConnected(true);
        };

        es.onmessage = (event) => {
          try {
            const raw = JSON.parse(event.data);
            const timelineItem: TimelineEvent = {
              id: `evt-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`,
              topic: raw.topic || 'activity',
              timestamp: new Date().toISOString(),
              data: raw.data || raw,
            };

            setLastEvent(timelineItem);
            setEvents((prev) => [timelineItem, ...prev.slice(0, 49)]); // keep latest 50 events
          } catch {
            // non-json keep-alive
          }
        };

        es.onerror = () => {
          setIsConnected(false);
          if (es) {
            es.close();
            es = null;
          }
          // Retry connection after 5 seconds
          reconnectTimeout = setTimeout(connect, 5000);
        };
      } catch {
        setIsConnected(false);
      }
    }

    connect();

    return () => {
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
      if (es) es.close();
      eventSourceRef.current = null;
      setIsConnected(false);
    };
  }, [enabled]);

  return {
    events,
    lastEvent,
    isConnected,
    clearEvents,
  };
}
