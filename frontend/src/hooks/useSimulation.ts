'use client';

// ============================================================================
// Simulation State Management Hook
// ============================================================================

import { useState, useCallback, useEffect } from 'react';
import type {
  SimulationState,
  SimulationStatus,
  StandingsEntry,
  MatchResult,
  Agent,
  ClientCommand,
  ServerEvent,
} from '@/lib/types';
import { useWebSocket } from './useWebSocket';

interface UseSimulationReturn {
  /** Current simulation state */
  simulation: SimulationState | null;
  /** Current standings sorted by score */
  standings: StandingsEntry[];
  /** All agents in the simulation */
  agents: Agent[];
  /** Latest round results */
  latestMatches: MatchResult[];
  /** Number of rounds completed */
  roundsCompleted: number;
  /** Total rounds configured */
  totalRounds: number;
  /** WebSocket connection status */
  isConnected: boolean;
  /** Simulation status */
  status: SimulationStatus;
  /** Error message if any */
  error: string | null;

  // Actions
  start: (rounds?: number, matchType?: string) => void;
  pause: () => void;
  resume: () => void;
  stop: () => void;
  setSpeed: (multiplier: number) => void;
  reset: () => void;
}

/**
 * Hook that manages simulation state via WebSocket.
 *
 * Provides a clean interface for components to control
 * and observe the simulation without dealing with raw WebSocket events.
 */
export function useSimulation(simulationId?: string): UseSimulationReturn {
  const { isConnected, send, onEvent } = useWebSocket(simulationId);

  const [simulation, setSimulation] = useState<SimulationState | null>(null);
  const [standings, setStandings] = useState<StandingsEntry[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [latestMatches, setLatestMatches] = useState<MatchResult[]>([]);
  const [roundsCompleted, setRoundsCompleted] = useState(0);
  const [totalRounds, setTotalRounds] = useState(100);
  const [status, setStatus] = useState<SimulationStatus>('idle');
  const [error, setError] = useState<string | null>(null);

  // Subscribe to WebSocket events
  useEffect(() => {
    const unsub = onEvent((event: ServerEvent) => {
      switch (event.event) {
        case 'simulation.started':
          setStatus('running');
          setTotalRounds(event.total_rounds);
          setRoundsCompleted(0);
          setError(null);
          setSimulation({
            simulation_id: event.simulation_id,
            status: 'running',
            rounds_completed: 0,
            total_rounds: event.total_rounds,
            agent_count: event.agent_count,
            elapsed_seconds: 0,
          });
          break;

        case 'simulation.paused':
          setStatus('paused');
          break;

        case 'simulation.resumed':
          setStatus('running');
          break;

        case 'simulation.ended':
          setStatus('completed');
          if (event.final_state) {
            setStandings(event.final_state.standings);
          }
          setSimulation((prev) =>
            prev
              ? { ...prev, status: 'completed', elapsed_seconds: event.final_state.elapsed_seconds }
              : null
          );
          break;

        case 'round.result':
          setLatestMatches(event.matches);
          setRoundsCompleted(event.round_number);
          break;

        case 'standings.update':
          setStandings(event.standings);
          break;

        case 'agents.list':
          setAgents(event.agents);
          break;

        case 'error':
          setError(event.message);
          break;

        case 'simulation.speed_changed':
          // Speed change acknowledged
          break;
      }
    });

    return unsub;
  }, [onEvent]);

  const start = useCallback(
    (rounds: number = 100, matchType: string = 'round_robin') => {
      setError(null);
      setStandings([]);
      setLatestMatches([]);
      setRoundsCompleted(0);
      send({
        type: 'simulation.start',
        payload: { rounds, match_type: matchType },
      });
    },
    [send]
  );

  const pause = useCallback(() => {
    send({ type: 'simulation.pause' });
  }, [send]);

  const resume = useCallback(() => {
    send({ type: 'simulation.resume' });
  }, [send]);

  const stop = useCallback(() => {
    send({ type: 'simulation.stop' });
  }, [send]);

  const setSpeed = useCallback(
    (multiplier: number) => {
      send({ type: 'simulation.speed', multiplier });
    },
    [send]
  );

  const reset = useCallback(() => {
    setSimulation(null);
    setStandings([]);
    setAgents([]);
    setLatestMatches([]);
    setRoundsCompleted(0);
    setStatus('idle');
    setError(null);
  }, []);

  return {
    simulation,
    standings,
    agents,
    latestMatches,
    roundsCompleted,
    totalRounds,
    isConnected,
    status,
    error,
    start,
    pause,
    resume,
    stop,
    setSpeed,
    reset,
  };
}