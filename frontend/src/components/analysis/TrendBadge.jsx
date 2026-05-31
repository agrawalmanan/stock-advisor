import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

const TrendBadge = ({ trend }) => {
  if (!trend) return null;

  const config = {
    Bullish: {
      icon: <TrendingUp className="w-4 h-4" />,
      color: 'bg-green-500/20 text-green-400 border-green-500/30',
    },
    Bearish: {
      icon: <TrendingDown className="w-4 h-4" />,
      color: 'bg-red-500/20 text-red-400 border-red-500/30',
    },
    Neutral: {
      icon: <Minus className="w-4 h-4" />,
      color: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    },
  };

  const c = config[trend.trend] || config.Neutral;

  return (
    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border ${c.color}`}>
      {c.icon}
      <span className="text-sm font-semibold">{trend.trend}</span>
      <span className="text-xs opacity-70">({trend.score}%)</span>
    </div>
  );
};

export default TrendBadge;