'use client';

// ============================================================================
// Cooperation Rate Over Time — live line chart
// ============================================================================

import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import type { MatchResult } from '@/lib/types';

interface CooperationChartProps {
  matches: MatchResult[];
  roundsCompleted: number;
}

interface DataPoint {
  round: number;
  cooperationRate: number;
  mutualCooperation: number;
  mutualDefection: number;
  oneSided: number;
}

export default function CooperationChart({
  matches,
  roundsCompleted,
}: CooperationChartProps) {
  const data = useMemo(() => {
    if (!matches.length) return [];

    // Group matches by round
    const roundMap = new Map<number, MatchResult[]>();
    matches.forEach((m) => {
      const existing = roundMap.get(m.round_number) || [];
      existing.push(m);
      roundMap.set(m.round_number, existing);
    });

    const points: DataPoint[] = [];
    let cumulativeCoop = 0;
    let cumulativeTotal = 0;

    // If we have many rounds, aggregate into bins
    const entries = Array.from(roundMap.entries()).sort(([a], [b]) => a - b);
    
    for (const [round, roundMatches] of entries) {
      const total = roundMatches.length;
      const coop = roundMatches.filter(
        (m) => m.action_a === 'cooperate' && m.action_b === 'cooperate'
      ).length;
      const mutualDefect = roundMatches.filter(
        (m) => m.action_a === 'defect' && m.action_b === 'defect'
      ).length;
      const oneSided = total - coop - mutualDefect;

      cumulativeCoop += coop;
      cumulativeTotal += total;

      points.push({
        round,
        cooperationRate: total > 0 ? coop / total : 0,
        mutualCooperation: total > 0 ? coop / total : 0,
        mutualDefection: total > 0 ? mutualDefect / total : 0,
        oneSided: total > 0 ? oneSided / total : 0,
      });
    }

    return points;
  }, [matches]);

  if (data.length === 0) {
    return (
      <div className="card">
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
          Cooperation Rate
        </h3>
        <p className="text-gray-600 text-sm text-center py-8">
          Waiting for data...
        </p>
      </div>
    );
  }

  const latestRate = data[data.length - 1]?.cooperationRate ?? 0;

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
          Cooperation Rate
        </h3>
        <div className="flex items-center gap-3 text-xs">
          <span className="text-gray-500">
            Round {roundsCompleted}
          </span>
          <span
            className={`font-mono font-bold ${
              latestRate > 0.5 ? 'text-green-400' : 'text-red-400'
            }`}
          >
            {(latestRate * 100).toFixed(1)}%
          </span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2e3140" />
          <XAxis
            dataKey="round"
            stroke="#6b7280"
            tick={{ fill: '#6b7280', fontSize: 11 }}
            tickLine={false}
            label={{ value: 'Round', position: 'insideBottom', offset: -5, fill: '#6b7280', fontSize: 11 }}
          />
          <YAxis
            domain={[0, 1]}
            stroke="#6b7280"
            tick={{ fill: '#6b7280', fontSize: 11 }}
            tickLine={false}
            tickFormatter={(v: number) => `${(v * 100).toFixed(0)}%`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1a1d27',
              border: '1px solid #2e3140',
              borderRadius: '8px',
              fontSize: '12px',
            }}
            formatter={(value: number) => [`${(value * 100).toFixed(1)}%`]}
          />
          <ReferenceLine
            y={0.5}
            stroke="#4ade80"
            strokeDasharray="4 4"
            strokeOpacity={0.3}
            label={{
              value: '50%',
              position: 'right',
              fill: '#4ade80',
              fontSize: 10,
              opacity: 0.5,
            }}
          />
          <Line
            type="monotone"
            dataKey="cooperationRate"
            stroke="#22c55e"
            strokeWidth={2}
            dot={false}
            animationDuration={300}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}