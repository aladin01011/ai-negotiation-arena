// ============================================================================
// AI Negotiation Arena — Constants
// ============================================================================

export const APP_NAME = 'AI Negotiation Arena';
export const APP_TAGLINE = 'Where agents learn to compete, cooperate, and survive';

/** WebSocket URL (defaults to localhost in dev) */
export const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';

/** Simulation defaults */
export const DEFAULT_ROUNDS = 100;
export const DEFAULT_AGENTS = 20;
export const MIN_ROUNDS = 10;
export const MAX_ROUNDS = 10_000;
export const MIN_SPEED = 0.1;
export const MAX_SPEED = 10.0;

/** Colors for strategies (for consistent chart rendering) */
export const STRATEGY_COLORS: Record<string, string> = {
  always_cooperate: '#22c55e', // green
  always_defect: '#ef4444',    // red
  tit_for_tat: '#3b82f6',      // blue
  grim_trigger: '#f59e0b',     // amber
  pavlov: '#8b5cf6',           // purple
  random: '#ec4899',           // pink
  generous_tft: '#14b8a6',     // teal
  adaptive: '#f97316',         // orange
};

/** Personality labels mapped to colors */
export const PERSONALITY_COLORS: Record<string, string> = {
  Cooperative: '#22c55e',
  Competitive: '#ef4444',
  Grudger: '#f59e0b',
  Mirror: '#3b82f6',
  Balanced: '#8b5cf6',
};

/** Action display values */
export const ACTION_LABELS = {
  cooperate: { label: 'Cooperate', emoji: '🤝', color: '#22c55e' },
  defect: { label: 'Defect', emoji: '🔪', color: '#ef4444' },
};