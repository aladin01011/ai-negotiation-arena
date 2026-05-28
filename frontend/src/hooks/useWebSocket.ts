'use client';

// ============================================================================
// WebSocket Hook — handles real-time connection lifecycle
// ============================================================================

import { useEffect, useRef, useCallback, useState } from 'react';
import type { ServerEvent, ClientCommand } from '@/lib/types';
import { WS_URL } from '@/lib/constants';

type EventHandler = (event: ServerEvent) => void;

interface UseWebSocketReturn {
  isConnected: boolean;
  send: (command: ClientCommand) => void;
  onEvent: (handler: EventHandler) => () => void;
  reconnect: () => void;
}

/**
 * Custom hook for WebSocket connection management.
 *
 * Features:
 * - Auto-reconnection with exponential backoff
 * - Event subscription system
 * - Connection state tracking
 * - Cleanup on unmount
 */
export function useWebSocket(roomId?: string): UseWebSocketReturn {
  const wsRef = useRef<WebSocket | null>(null);
  const handlersRef = useRef<Set<EventHandler>>(new Set());
  const [isConnected, setIsConnected] = useState(false);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const reconnectAttemptRef = useRef(0);
  const MAX_RECONNECT_ATTEMPTS = 10;

  const connect = useCallback(() => {
    // Cleanup existing connection
    if (wsRef.current) {
      wsRef.current.close();
    }

    const url = roomId ? `${WS_URL}/${roomId}` : WS_URL;
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('[WS] Connected to', url);
      setIsConnected(true);
      reconnectAttemptRef.current = 0;
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as ServerEvent;
        handlersRef.current.forEach((handler) => handler(data));
      } catch (error) {
        console.error('[WS] Failed to parse message:', error);
      }
    };

    ws.onclose = () => {
      console.log('[WS] Disconnected');
      setIsConnected(false);
      wsRef.current = null;

      // Auto-reconnect with exponential backoff
      if (reconnectAttemptRef.current < MAX_RECONNECT_ATTEMPTS) {
        const delay = Math.min(
          1000 * Math.pow(2, reconnectAttemptRef.current),
          30000
        );
        console.log(`[WS] Reconnecting in ${delay}ms...`);
        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectAttemptRef.current++;
          connect();
        }, delay);
      }
    };

    ws.onerror = (error) => {
      console.error('[WS] Error:', error);
    };
  }, [roomId]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  const send = useCallback((command: ClientCommand) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(command));
    } else {
      console.warn('[WS] Cannot send — not connected');
    }
  }, []);

  const onEvent = useCallback((handler: EventHandler): (() => void) => {
    handlersRef.current.add(handler);
    return () => {
      handlersRef.current.delete(handler);
    };
  }, []);

  const reconnect = useCallback(() => {
    reconnectAttemptRef.current = 0;
    connect();
  }, [connect]);

  return { isConnected, send, onEvent, reconnect };
}