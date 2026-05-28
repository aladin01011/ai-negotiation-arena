'use client';

// ============================================================================
// Strategy Distribution — pie/donut chart
// ============================================================================

import React, { useMemo } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';
import type { StandingsEntry } from '@/lib/types';
import { STRATEGY_COLORS } from '@/lib/constants';

interface StrategyDistributionProps {
  standings: StandingsEntry[];
}

export default function StrategyDistribution({
  standings,
}: StrategyDistributionProps) {
  const data = useMemo(() => {
    const counts = new Map<string, { count: number; totalScore: number }>();

    standings.forEach((entry) => {
      const key = entry.strategy;
      const current = counts.get(key) || { count: 0, totalScore: 0 };
      current.count += 1;
      current.totalScore += entry.total_score;
      counts.set(key, current);
    });

    return Array.from(counts.entries())
      .map(([name, stats]) => ({
        name,
        value: stats.count,
        totalScore: stats.totalScore,
        avgScore: stats.count > 0 ? stats.totalScore / stats.count : 0,
        color:
          STRATEGY_COLORS[name.toLowerCase().replace(/\s+/g, '_')] || '#6b7280',
      }))
      .sort((a, b) => b.value - a.value);
  }, [standings]);

  if (data.length === 0) {
    return (
      <div className="card">
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
          Strategy Distribution
        </h3>
        <p className="text-gray-600 text-sm text-center py-8">
          No data yet.
        </p>
      </div>
    );
  }

  return (
    <div className="card">
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
        Strategy Distribution
      </h3>

      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={50}
            outerRadius={80}
            paddingAngle={2}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: '#1a1d27',
              border: '1px solid #2e3140',
              borderRadius: '8px',
              fontSize: '12px',
            }}
            formatter={(_: any, name: string, props: any) => [
              `${props.payload.value} agents (avg score: ${props.payload.avgScore.toFixed(1)})`,
              name,
            ]}
          />
        </PieChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div className="mt-2 space-y-1">
        {data.map((entry) => (
          <div
            key={entry.name}
            className="flex items-center justify-between text-xs px-1"
          >
            <div className="flex items-center gap-2">
              <span
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-gray-400">{entry.name}</span>
            </div>
            <span className="text-gray-500 font-mono">
              {entry.value} ({entry.avgScore.toFixed(1)} avg)
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}