'use client';

// ============================================================================
// Analytics Page — post-simulation analysis
// ============================================================================

import React, { useState } from 'react';
import { useSimulation } from '@/hooks/useSimulation';
import { STRATEGY_COLORS } from '@/lib/constants';

export default function AnalyticsPage() {
  const { standings, agents, status, roundsCompleted, totalRounds } =
    useSimulation();

  return (
    <div className="min-h-screen bg-[#0f1117]">
      {/* Header */}
      <header className="border-b border-[#2e3140] bg-[#1a1d27]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-14">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-blue-600/20 border border-blue-600/30 flex items-center justify-center">
                <span className="text-blue-400 text-lg">📊</span>
              </div>
              <div>
                <h1 className="text-sm font-bold text-gray-200">Analytics</h1>
                <p className="text-[10px] text-gray-500">
                  Post-simulation analysis
                </p>
              </div>
            </div>
            <nav className="flex items-center gap-1 text-xs">
              <a
                href="/"
                className="px-3 py-1.5 rounded text-gray-500 hover:text-gray-300"
              >
                Dashboard
              </a>
              <a
                href="/agents"
                className="px-3 py-1.5 rounded text-gray-500 hover:text-gray-300"
              >
                Agents
              </a>
              <a
                href="/analytics"
                className="px-3 py-1.5 rounded bg-surface-100 text-gray-200 font-medium"
              >
                Analytics
              </a>
            </nav>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {status === 'idle' && (
          <div className="text-center py-20">
            <p className="text-gray-500 text-sm">
              Run a simulation first, then view the analytics here.
            </p>
          </div>
        )}

        {standings.length > 0 && (
          <div className="space-y-6">
            {/* Summary cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="card text-center py-6">
                <div className="text-2xl font-bold text-gray-200">
                  {roundsCompleted}
                </div>
                <div className="text-xs text-gray-500 mt-1">Rounds</div>
              </div>
              <div className="card text-center py-6">
                <div className="text-2xl font-bold text-gray-200">
                  {agents.length}
                </div>
                <div className="text-xs text-gray-500 mt-1">Agents</div>
              </div>
              <div className="card text-center py-6">
                <div className="text-2xl font-bold text-arena-400">
                  {standings[0]?.name || '—'}
                </div>
                <div className="text-xs text-gray-500 mt-1">Winner</div>
              </div>
              <div className="card text-center py-6">
                <div className="text-2xl font-bold text-gray-200">
                  {standings[0]?.total_score.toFixed(0) || '—'}
                </div>
                <div className="text-xs text-gray-500 mt-1">Top Score</div>
              </div>
            </div>

            {/* Strategy performance comparison */}
            <div className="card">
              <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
                Strategy Performance
              </h3>

              <div className="space-y-3">
                {(() => {
                  // Aggregate by strategy
                  const stratStats = new Map<
                    string,
                    { totalScore: number; count: number }
                  >();
                  standings.forEach((s) => {
                    const current = stratStats.get(s.strategy) || {
                      totalScore: 0,
                      count: 0,
                    };
                    current.totalScore += s.total_score;
                    current.count += 1;
                    stratStats.set(s.strategy, current);
                  });

                  const maxAvg = Math.max(
                    ...Array.from(stratStats.values()).map(
                      (v) => v.totalScore / v.count
                    ),
                    1
                  );

                  return Array.from(stratStats.entries())
                    .sort((a, b) => {
                      const avgA = a[1].totalScore / a[1].count;
                      const avgB = b[1].totalScore / b[1].count;
                      return avgB - avgA;
                    })
                    .map(([name, stats]) => {
                      const avgScore = stats.totalScore / stats.count;
                      const colorKey = name.toLowerCase().replace(/\s+/g, '_');
                      const color = STRATEGY_COLORS[colorKey] || '#6b7280';

                      return (
                        <div key={name}>
                          <div className="flex items-center justify-between text-xs mb-1">
                            <div className="flex items-center gap-2">
                              <span
                                className="w-2 h-2 rounded-full"
                                style={{ backgroundColor: color }}
                              />
                              <span className="text-gray-300">{name}</span>
                            </div>
                            <span className="text-gray-400 font-mono">
                              {avgScore.toFixed(1)} avg ({stats.count} agents)
                            </span>
                          </div>
                          <div className="w-full h-2 bg-surface-100 rounded-full">
                            <div
                              className="h-2 rounded-full transition-all"
                              style={{
                                width: `${(avgScore / maxAvg) * 100}%`,
                                backgroundColor: color,
                              }}
                            />
                          </div>
                        </div>
                      );
                    });
                })()}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}