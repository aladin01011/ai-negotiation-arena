// ============================================================================
// AI Negotiation Arena — REST API Client
// ============================================================================

import type {
  StrategyInfo,
  SimulationState,
  StandingsEntry,
  Agent,
  SimulationConfig,
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Generic fetch wrapper with error handling.
 */
async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const res = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const error = await res.text().catch(() => 'Unknown error');
    throw new Error(`API Error (${res.status}): ${error}`);
  }

  return res.json();
}

// ============================================================================
// Strategy Endpoints
// ============================================================================

/** Fetch all available agent strategies. */
export async function getStrategies(): Promise<StrategyInfo[]> {
  return fetchAPI<StrategyInfo[]>('/api/strategies');
}

// ============================================================================
// Simulation Endpoints
// ============================================================================

/** Create and start a new simulation. */
export async function createSimulation(
  config: Partial<SimulationConfig> = {}
): Promise<SimulationState> {
  return fetchAPI<SimulationState>('/api/simulations', {
    method: 'POST',
    body: JSON.stringify({
      rounds: config.rounds ?? 100,
      match_type: config.match_type ?? 'round_robin',
      speed_multiplier: config.speed_multiplier ?? 1.0,
    }),
  });
}

/** List all simulations. */
export async function listSimulations(): Promise<SimulationState[]> {
  return fetchAPI<SimulationState[]>('/api/simulations');
}

/** Get a specific simulation's state. */
export async function getSimulation(simulationId: string): Promise<SimulationState> {
  return fetchAPI<SimulationState>(`/api/simulations/${simulationId}`);
}

/** Get tournament standings for a simulation. */
export async function getStandings(
  simulationId: string
): Promise<{ standings: StandingsEntry[] }> {
  return fetchAPI<{ standings: StandingsEntry[] }>(
    `/api/simulations/${simulationId}/standings`
  );
}

/** Get all agents in a simulation. */
export async function getAgents(simulationId: string): Promise<Agent[]> {
  return fetchAPI<Agent[]>(`/api/simulations/${simulationId}/agents`);
}

/** Control a simulation (pause, resume, stop). */
export async function controlSimulation(
  simulationId: string,
  action: 'pause' | 'resume' | 'stop'
): Promise<SimulationState> {
  return fetchAPI<SimulationState>(
    `/api/simulations/${simulationId}/actions`,
    {
      method: 'POST',
      body: JSON.stringify({ action }),
    }
  );
}

/** Health check. */
export async function healthCheck(): Promise<{ status: string }> {
  return fetchAPI<{ status: string }>('/health');
}