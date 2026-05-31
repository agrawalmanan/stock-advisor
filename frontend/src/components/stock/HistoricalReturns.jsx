import React from 'react';

const HistoricalReturns = ({ returns }) => {
  if (!returns) return null;

  const periods = ['1M', '3M', '6M', '1Y', '5Y'];

  return (
    <div className="dark:bg-dark-card bg-white rounded-xl p-6 border dark:border-dark-border border-gray-200 transition-colors">
      <h3 className="dark:text-dark-text text-gray-900 font-semibold mb-4">Historical Returns</h3>
      <div className="flex flex-wrap gap-3">
        {periods.map((period) => {
          const value = returns[period];
          const isPositive = value !== 'N/A' && Number(value) >= 0;
          const color = value === 'N/A'
            ? 'bg-gray-500/20 text-gray-400 border-gray-500/30'
            : isPositive
              ? 'bg-green-500/20 text-green-400 border-green-500/30'
              : 'bg-red-500/20 text-red-400 border-red-500/30';

          return (
            <div key={period} className={`flex flex-col items-center px-4 py-3 rounded-lg border ${color}`}>
              <span className="text-xs opacity-70 mb-1">{period}</span>
              <span className="font-bold text-sm">
                {value === 'N/A' ? 'N/A' : `${Number(value) >= 0 ? '+' : ''}${value}%`}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default HistoricalReturns;