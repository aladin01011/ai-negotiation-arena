'use client';

// ============================================================================
// Simulation Control Panel
// ============================================================================

import React, { useState } from 'react';
import type { SimulationStatus } from '@/lib/types';

interface SimulationControlsProps {
  status: SimulationStatus;
  isConnected: boolean;
  roundsCompleted: number;
  totalRounds: number;
  onStart: (rounds: number, matchType: string) => void;
  onPause: () => void;
  onResume: () => void;
  onStop: () => void;
  onSpeedChange: (speed: number) => void;
}

const MATCH_TYPES = [
  { value: 'round_robin', label: 'Round Robin' },
  { value: 'random_pairs', label: 'Random Pairs' },
  { value: 'swiss', label: 'Swiss System' },
  { value: 'elimination', label: 'Elimination' },
];

export default function SimulationControls({
  status,
  isConnected,
  roundsCompleted,
  totalRounds,
  onStart,
  onPause,
  onResume,
  onStop,
  onSpeedChange,
}: SimulationControlsProps) {
  const [rounds, setRounds] = useState(100);
  const [matchType, setMatchType] = useState('round_robin');
  const [speed, setSpeed] = useState(1);

  const isIdle = status === 'idle';
  const isRunning = status === 'running';
  const isPaused = status === 'paused';
  const isCompleted = status === 'completed';

  const handleStart = () => {
    onStart(rounds, matchType);
  };

  const handleSpeedChange = (newSpeed: number) => {
    const clamped = Math.max(0.1, Math.min(10, newSpeed));
    setSpeed(clamped);
    onSpeedChange(clamped);
  };

  return (
    <div className="card">
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
        Simulation Controls
      </h3>

      {/* Connection status */}
      <div className="flex items-center gap-2 mb-4 text-xs">
        <span
          className={`w-2 h-2 rounded-full ${
            isConnected ? 'bg-green-500 pulse-dot' : 'bg-red-500'
          }`}
        />
        <span className="text-gray-500">
          {isConnected ? 'Connected' : 'Disconnected'}
        </span>
        {!isIdle && (
          <span className="ml-auto">
            {roundsCompleted} / {totalRounds} rounds
          </span>
        )}
      </div>

      {/* Status badge */}
      <div className="mb-4">
        <span className={`badge-${status}`}>
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
      </div>

      {/* Configuration (only when idle) */}
      {isIdle && (
        <div className="space-y-3 mb-4">
          <div>
            <label className="block text-xs text-gray-500 mb-1">Rounds</label>
            <input
              type="number"
              value={rounds}
              onChange={(e) => setRounds(Math.max(10, Math.min(10000, Number(e.target.value))))}
              className="w-full bg-surface-50 border border-surface-200 rounded px-3 py-2 text-sm
                         focus:outline-none focus:border-arena-500 focus:ring-1 focus:ring-arena-500/30"
              min={10}
              max={10000}
            />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Match Type</label>
            <select
              value={matchType}
              onChange={(e) => setMatchType(e.target.value)}
              className="w-full bg-surface-50 border border-surface-200 rounded px-3 py-2 text-sm
                         focus:outline-none focus:border-arena-500 focus:ring-1 focus:ring-arena-500/30"
            >
              {MATCH_TYPES.map((mt) => (
                <option key={mt.value} value={mt.value}>
                  {mt.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}

      {/* Speed control (when running) */}
      {(isRunning || isPaused) && (
        <div className="mb-4">
          <label className="block text-xs text-gray-500 mb-1">
            Speed: {speed.toFixed(1)}x
          </label>
          <input
            type="range"
            min={0.1}
            max={10}
            step={0.1}
            value={speed}
            onChange={(e) => handleSpeedChange(Number(e.target.value))}
            className="w-full accent-arena-500"
          />
          <div className="flex justify-between text-[10px] text-gray-600">
            <span>0.1x</span>
            <span>10x</span>
          </div>
        </div>
      )}

      {/* Action buttons */}
      <div className="flex gap-2">
        {isIdle && (
          <button
            onClick={handleStart}
            disabled={!isConnected}
            className="flex-1 bg-arena-600 hover:bg-arena-500 disabled:bg-gray-700 disabled:text-gray-500
                       text-white font-medium py-2 px-4 rounded text-sm transition-colors"
          >
            ▶ Start
          </button>
        )}

        {isRunning && (
          <button
            onClick={onPause}
            className="flex-1 bg-yellow-600 hover:bg-yellow-500 text-white font-medium
                       py-2 px-4 rounded text-sm transition-colors"
          >
            ⏸ Pause
          </button>
        )}

        {isPaused && (
          <button
            onClick={onResume}
            className="flex-1 bg-arena-600 hover:bg-arena-500 text-white font-medium
                       py-2 px-4 rounded text-sm transition-colors"
          >
            ▶ Resume
          </button>
        )}

        {(isRunning || isPaused) && (
          <button
            onClick={onStop}
            className="flex-1 bg-red-700 hover:bg-red-600 text-white font-medium
                       py-2 px-4 rounded text-sm transition-colors"
          >
            ⏹ Stop
          </button>
        )}
      </div>

      {/* Progress bar */}
      {!isIdle && totalRounds > 0 && (
        <div className="mt-4">
          <div className="w-full bg-surface-100 rounded-full h-1.5">
            <div
              className="bg-arena-500 h-1.5 rounded-full transition-all duration-300"
              style={{ width: `${(roundsCompleted / totalRounds) * 100}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
}