'use client';

// ============================================================================
// Event Log — scrolling feed of simulation events
// ============================================================================

import React, { useEffect, useRef } from 'react';
import type { MatchResult } from '@/lib/types';
import { ACTION_LABELS } from '@/lib/constants';

interface EventLogProps {
  matches: MatchResult[];
  maxEntries?: number;
}

export default function EventLog({ matches, maxEntries = 50 }: EventLogProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new entries
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [matches]);

  const recentMatches = matches.slice(-maxEntries);

  if (recentMatches.length === 0) {
    return (
      <div className="card">
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
          Event Log
        </h3>
        <p className="text-gray-600 text-xs text-center py-8">
          Events will appear here...
        </p>
      </div>
    );
  }

  return (
    <div className="card">
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
        Event Log
        <span className="ml-2 text-xs font-normal text-gray-600">
          ({recentMatches.length} recent)
        </span>
      </h3>

      <div
        ref={scrollRef}
        className="overflow-y-auto max-h-[300px] -mx-4 -mb-4 space-y-0"
      >
        {recentMatches
          .slice()
          .reverse()
          .map((match, idx) => {
            const aLabel = ACTION_LABELS[match.action_a];
            const bLabel = ACTION_LABELS[match.action_b];
            const isMutualCoop =
              match.action_a === 'cooperate' && match.action_b === 'cooperate';
            const isMutualDefect =
              match.action_a === 'defect' && match.action_b === 'defect';

            return (
              <div
                key={`${match.match_id}-${idx}`}
                className={`px-4 py-2 text-xs border-t border-surface-200 animate-fade-in
                  ${isMutualCoop ? 'bg-green-900/10' : ''}
                  ${isMutualDefect ? 'bg-red-900/10' : ''}
                `}
              >
                <div className="flex items-center justify-between">
                  <span className="text-gray-500 font-mono">
                    R{match.round_number}
                  </span>
                  <span
                    className={`font-mono ${
                      match.payoff_a > match.payoff_b
                        ? 'text-green-400'
                        : match.payoff_a < match.payoff_b
                        ? 'text-red-400'
                        : 'text-gray-400'
                    }`}
                  >
                    {match.payoff_a.toFixed(0)} - {match.payoff_b.toFixed(0)}
                  </span>
                </div>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="text-gray-300">{match.agent_a_id.slice(0, 6)}</span>
                  <span>{aLabel?.emoji}</span>
                  <span className="text-gray-600">vs</span>
                  <span>{bLabel?.emoji}</span>
                  <span className="text-gray-300">{match.agent_b_id.slice(0, 6)}</span>
                </div>
              </div>
            );
          })}
      </div>
    </div>
  );
}