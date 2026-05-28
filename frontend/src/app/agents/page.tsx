'use client';

// ============================================================================
// Agent Explorer Page
// ============================================================================

import React, { useState, useEffect } from 'react';
import { getStrategies } from '@/lib/api';
import type { StrategyInfo, Agent } from '@/lib/types';
import { STRATEGY_COLORS } from '@/lib/constants';

export default function AgentsPage() {
  const [strategies, setStrategies] = useState<StrategyInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getStrategies()
      .then(setStrategies)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-[#0f1117]">
      {/* Header */}
      <header className="border-b border-[#2e3140] bg-[#1a1d27]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-14">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-purple-600/20 border border-purple-600/30 flex items-center justify-center">
                <span className="text-purple-400 text-lg">🧠</span>
              </div>
              <div>
                <h1 className="text-sm font-bold text-gray-200">Agent Strategies</h1>
                <p className="text-[10px] text-gray-500">Available agent behaviors</p>
              </div>
            </div>
            <nav className="flex items-center gap-1 text-xs">
              <a href="/" className="px-3 py-1.5 rounded text-gray-500 hover:text-gray-300">
                Dashboard
              </a>
              <a
                href="/agents"
                className="px-3 py-1.5 rounded bg-surface-100 text-gray-200 font-medium"
              >
                Agents
              </a>
              <a href="/analytics" className="px-3 py-1.5 rounded text-gray-500 hover:text-gray-300">
                Analytics
              </a>
            </nav>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {loading ? (
          <div className="text-center py-20">
            <p className="text-gray-500">Loading strategies...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {strategies.map((strategy) => {
              const colorKey = strategy.id;
              const color = STRATEGY_COLORS[colorKey] || '#6b7280';
              return (
                <div key={strategy.id} className="card hover:border-opacity-60 transition-all">
                  <div className="flex items-center gap-3 mb-3">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: color }}
                    />
                    <h3 className="text-sm font-semibold text-gray-200">
                      {strategy.name}
                    </h3>
                  </div>
                  <p className="text-xs text-gray-400 leading-relaxed">
                    {strategy.description}
                  </p>
                  <div className="mt-3 pt-3 border-t border-surface-200">
                    <code className="text-[10px] text-gray-600">
                      ID: {strategy.id}
                    </code>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}