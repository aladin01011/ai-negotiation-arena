'use client';

// ============================================================================
// Agent Leaderboard — real-time standings table
// ============================================================================

import React from 'react';
import type { StandingsEntry } from '@/lib/types';
import { STRATEGY_COLORS, PERSONALITY_COLORS } from '@/lib/constants';

interface AgentLeaderboardProps {
  standings: StandingsEntry[];
  maxDisplay?: number;
}

export default function AgentLeaderboard({
  standings,
  maxDisplay = 15,
}: AgentLeaderboardProps) {
  const displayed = standings.slice(0, maxDisplay);

  if (standings.length === 0) {
    return (
      <div className="card">
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
          Leaderboard
        </h3>
        <p className="text-gray-600 text-sm text-center py-8">
          No data yet. Start a simulation to see results.
        </p>
      </div>
    );
  }

  const maxScore = Math.max(...standings.map((s) => s.total_score), 1);

  return (
    <div className="card">
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
        Leaderboard
        <span className="ml-2 text-xs font-normal text-gray-600">
          ({standings.length} agents)
        </span>
      </h3>

      <div className="overflow-y-auto max-h-[500px] -mx-4 -mb-4">
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-[#1a1d27]">
            <tr className="text-xs text-gray-500 uppercase">
              <th className="px-4 py-2 text-left w-10">#</th>
              <th className="px-4 py-2 text-left">Agent</th>
              <th className="px-4 py-2 text-left hidden sm:table-cell">Strategy</th>
              <th className="px-4 py-2 text-right">Score</th>
              <th className="px-4 py-2 text-right hidden md:table-cell">Interactions</th>
            </tr>
          </thead>
          <tbody>
            {displayed.map((entry) => (
              <tr
                key={entry.agent_id}
                className="border-t border-surface-200 hover:bg-surface-50 transition-colors"
              >
                <td className="px-4 py-2 text-gray-500 font-mono">
                  {entry.rank}
                </td>
                <td className="px-4 py-2">
                  <div className="flex items-center gap-2">
                    <div
                      className="w-2 h-2 rounded-full"
                      style={{
                        backgroundColor:
                          STRATEGY_COLORS[entry.strategy.toLowerCase().replace(/\s+/g, '_')] ||
                          '#6b7280',
                      }}
                    />
                    <span className="font-medium text-gray-200">{entry.name}</span>
                  </div>
                </td>
                <td className="px-4 py-2 text-gray-400 hidden sm:table-cell">
                  {entry.strategy}
                </td>
                <td className="px-4 py-2 text-right font-mono">
                  <div className="flex items-center justify-end gap-2">
                    <span className="text-gray-200 font-medium">
                      {entry.total_score.toFixed(1)}
                    </span>
                    <div className="w-16 h-1.5 bg-surface-100 rounded-full hidden md:block">
                      <div
                        className="h-1.5 rounded-full bg-arena-500 transition-all"
                        style={{
                          width: `${(entry.total_score / maxScore) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                </td>
                <td className="px-4 py-2 text-right text-gray-500 font-mono hidden md:table-cell">
                  {entry.total_interactions}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}