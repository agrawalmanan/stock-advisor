import React from 'react';
import { Shield } from 'lucide-react';

const RiskMeter = ({ risk }) => {
  if (!risk) return null;

  const { score, level, max_score } = risk;
  const percentage = (score / (max_score || 100)) * 100;

  const colorMap = {
    Low: { bar: 'bg-profit', text: 'text-profit' },
    Medium: { bar: 'bg-hold', text: 'text-hold' },
    High: { bar: 'bg-loss', text: 'text-loss' },
  };

  const colors = colorMap[level] || colorMap.Medium;

  return (
    <div className="dark:bg-dark-card bg-white rounded-xl p-6 border dark:border-dark-border border-gray-200 transition-colors">
      <div className="flex items-center gap-2 mb-4">
        <Shield className="w-5 h-5 text-blue-400" />
        <h3 className="dark:text-dark-text text-gray-900 font-semibold">Risk Assessment</h3>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex-1">
          <div className="flex items-center justify-between mb-2">
            <span className="dark:text-dark-muted text-gray-500 text-sm">Risk Score</span>
            <span className={`font-bold text-lg ${colors.text}`}>{score}/{max_score || 100}</span>
          </div>

          <div className="w-full h-3 dark:bg-dark-border bg-gray-200 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full ${colors.bar} transition-all duration-500`}
              style={{ width: `${percentage}%` }}
            />
          </div>

          <div className="flex justify-between mt-1">
            <span className="text-profit text-xs">Low</span>
            <span className="text-hold text-xs">Medium</span>
            <span className="text-loss text-xs">High</span>
          </div>
        </div>

        <div className={`px-4 py-3 rounded-xl border ${
          level === 'Low' ? 'bg-green-500/10 border-green-500/20' :
          level === 'Medium' ? 'bg-yellow-500/10 border-yellow-500/20' :
          'bg-red-500/10 border-red-500/20'
        }`}>
          <span className={`font-bold text-xl ${colors.text}`}>{level}</span>
        </div>
      </div>
    </div>
  );
};

export default RiskMeter;