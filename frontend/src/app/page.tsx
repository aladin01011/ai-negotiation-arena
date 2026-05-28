'use client';

// ============================================================================
// AI Negotiation Arena — Main Dashboard
// ============================================================================

import React, { useEffect } from 'react';
import { useSimulation } from '@/hooks/useSimulation';
import SimulationControls from '@/components/dashboard/SimulationControls';
import AgentLeaderboard from '@/components/dashboard/AgentLeaderboard';
import CooperationChart from '@/components/dashboard/CooperationChart';
import StrategyDistribution from '@/components/dashboard/StrategyDistribution';
import EventLog from '@/components/dashboard/EventLog';
import { APP_NAME } from '@/lib/constants';

export default function DashboardPage() {
  const {
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
  } = useSimulation();

  return (
    <div className="min-h-screen bg-[#0f1117]">
      {/* Header */}
      <header className="border-b border-[#2e3140] bg-[#1a1d27]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-14">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-arena-600/20 border border-arena-600/30 flex items-center justify-center">
                <span className="text-arena-400 text-lg">🏛</span>
              </div>
              <div>
                <h1 className="text-sm font-bold text-gray-200">{APP_NAME}</h1>
                <p className="text-[10px] text-gray-500">Multi-Agent Strategic Simulation</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              {/* Navigation */}
              <nav className="hidden sm:flex items-center gap-1 text-xs">
                <a
                  href="/"
                  className="px-3 py-1.5 rounded bg-surface-100 text-gray-200 font-medium"
                >
                  Dashboard
                </a>
                <a
                  href="/agents"
                  className="px-3 py-1.5 rounded text-gray-500 hover:text-gray-300 transition-colors"
                >
                  Agents
                </a>
                <a
                  href="/analytics"
                  className="px-3 py-1.5 rounded text-gray-500 hover:text-gray-300 transition-colors"
                >
                  Analytics
                </a>
              </nav>

              {/* Status indicator */}
              <div className="flex items-center gap-1.5 text-xs">
                <span
                  className={`w-1.5 h-1.5 rounded-full ${
                    isConnected ? 'bg-green-500 pulse-dot' : 'bg-red-500'
                  }`}
                />
                <span className="text-gray-500 hidden sm:inline">
                  {isConnected ? 'Live' : 'Offline'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Error banner */}
        {error && (
          <div className="mb-4 px-4 py-3 bg-red-900/20 border border-red-800/30 rounded-lg">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        {/* Stats bar */}
        {status !== 'idle' && (
          <div className="flex gap-4 mb-6 text-xs">
            <div className="card flex-1 py-3 px-4">
              <span className="text-gray-500">Status</span>
              <span className={`ml-2 badge-${status}`}>
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </span>
            </div>
            <div className="card flex-1 py-3 px-4">
              <span className="text-gray-500">Rounds</span>
              <span className="ml-2 text-gray-200 font-mono">
                {roundsCompleted} / {totalRounds}
              </span>
            </div>
            <div className="card flex-1 py-3 px-4">
              <span className="text-gray-500">Agents</span>
              <span className="ml-2 text-gray-200 font-mono">{agents.length}</span>
            </div>
            <div className="card flex-1 py-3 px-4">
              <span className="text-gray-500">Top Agent</span>
              <span className="ml-2 text-gray-200">
                {standings[0]?.name || '—'}
              </span>
            </div>
          </div>
        )}

        {/* Main grid */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left column: Controls + Charts */}
          <div className="lg:col-span-3 space-y-6">
            {/* Controls + Summary row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <SimulationControls
                status={status}
                isConnected={isConnected}
                roundsCompleted={roundsCompleted}
                totalRounds={totalRounds}
                onStart={start}
                onPause={pause}
                onResume={resume}
                onStop={stop}
                onSpeedChange={setSpeed}
              />
              <div className="md:col-span-2">
                <StrategyDistribution standings={standings} />
              </div>
            </div>

            {/* Cooperation chart */}
            <CooperationChart
              matches={latestMatches}
              roundsCompleted={roundsCompleted}
            />

            {/* Event log */}
            <EventLog matches={latestMatches} />
          </div>

          {/* Right column: Leaderboard */}
          <div className="lg:col-span-1">
            <AgentLeaderboard standings={standings} />
          </div>
        </div>

        {/* Empty state */}
        {status === 'idle' && !error && (
          <div className="text-center py-20">
            <div className="text-6xl mb-6">🏛</div>
            <h2 className="text-xl font-bold text-gray-300 mb-2">
              Welcome to the Arena
            </h2>
            <p className="text-sm text-gray-500 max-w-md mx-auto mb-8">
              Configure your simulation and watch AI agents compete, cooperate,
              and evolve in real-time. Start by clicking the button on the left.
            </p>
            <div className="inline-flex items-center gap-6 text-xs text-gray-600">
              <span>🤝 8 Strategies</span>
              <span>⚡ Real-time</span>
              <span>🧠 Game Theory</span>
              <span>📊 Live Analytics</span>
            </div>
          </div>
        )}

        {/* Completed state */}
        {status === 'completed' && (
          <div className="mt-6 card text-center py-6 border-arena-600/30">
            <div className="text-4xl mb-2">🏆</div>
            <h2 className="text-lg font-bold text-gray-200 mb-1">
              Simulation Complete
            </h2>
            <p className="text-sm text-gray-500">
              {roundsCompleted} rounds completed with {agents.length} agents.
            </p>
            <p className="text-xs text-gray-600 mt-1">
              Winner: {standings[0]?.name} ({standings[0]?.strategy}) —{' '}
              {standings[0]?.total_score.toFixed(0)} points
            </p>
          </div>
        )}
      </main>
    </div>
  );
}