// ============================================================================
// AI Negotiation Arena — Type Definitions
// ============================================================================

/** Game actions an agent can take */
export type Action = 'cooperate' | 'defect';

/** Simulation status */
export type SimulationStatus = 'idle' | 'running' | 'paused' | 'completed' | 'error';

/** Match type for tournament structure */
export type MatchType = 'round_robin' | 'random_pairs' | 'swiss' | 'elimination';

// ============================================================================
// Agent Types
// ============================================================================

export interface Personality {
  trust: number;
  greed: number;
  risk_tolerance: number;
  forgiveness: number;
  reciprocity: number;
  spite: number;
}

export interface Agent {
  agent_id: string;
  name: string;
  strategy: string;
  strategy_description: string;
  personality: Personality;
  personality_label: string;
  total_score: number;
  is_alive: boolean;
  memory: {
    total_interactions: number;
    opponents_count: number;
    recent_history: InteractionRecord[];
  };
}

export interface InteractionRecord {
  opponent_id: string;
  own_action: Action;
  opponent_action: Action;
  payoff: number;
  round_number: number;
}

// ============================================================================
// Match & Round Types
// ============================================================================

export interface MatchResult {
  match_id: string;
  agent_a_id: string;
  agent_b_id: string;
  action_a: Action;
  action_b: Action;
  payoff_a: number;
  payoff_b: number;
  round_number: number;
}

export interface RoundResult {
  round_number: number;
  matches: MatchResult[];
}

// ============================================================================
// Standings Types
// ============================================================================

export interface StandingsEntry {
  rank: number;
  agent_id: string;
  name: string;
  strategy: string;
  personality_label: string;
  total_score: number;
  total_interactions: number;
}

// ============================================================================
// Simulation Types
// ============================================================================

export interface SimulationConfig {
  agent_configs?: AgentConfig[];
  rounds: number;
  match_type: MatchType;
  speed_multiplier: number;
}

export interface AgentConfig {
  name: string;
  strategy: string;
  trust: number;
  greed: number;
  forgiveness: number;
  reciprocity: number;
  spite: number;
  risk_tolerance: number;
}

export interface SimulationState {
  simulation_id: string;
  status: SimulationStatus;
  rounds_completed: number;
  total_rounds: number;
  agent_count: number;
  elapsed_seconds: number;
}

export interface SimulationSummary {
  simulation_id: string;
  total_rounds: number;
  total_agents: number;
  elapsed_seconds: number;
  status: SimulationStatus;
  standings: StandingsEntry[];
  top_agent: StandingsEntry | null;
}

// ============================================================================
// WebSocket Event Types
// ============================================================================

/** Events sent from server to client */
export type ServerEvent =
  | { event: 'simulation.started'; simulation_id: string; agent_count: number; total_rounds: number }
  | { event: 'simulation.paused'; simulation_id: string }
  | { event: 'simulation.resumed'; simulation_id: string }
  | { event: 'simulation.ended'; simulation_id: string; final_state: SimulationSummary }
  | { event: 'simulation.speed_changed'; multiplier: number }
  | { event: 'round.result'; simulation_id: string; round_number: number; matches: MatchResult[] }
  | { event: 'standings.update'; simulation_id: string; standings: StandingsEntry[] }
  | { event: 'agents.list'; agents: Agent[] }
  | { event: 'error'; message: string };

/** Commands sent from client to server */
export type ClientCommand =
  | { type: 'simulation.start'; payload?: { rounds?: number; match_type?: string } }
  | { type: 'simulation.pause' }
  | { type: 'simulation.resume' }
  | { type: 'simulation.stop' }
  | { type: 'simulation.speed'; multiplier: number };

// ============================================================================
// Strategy Info
// ============================================================================

export interface StrategyInfo {
  id: string;
  name: string;
  description: string;
}