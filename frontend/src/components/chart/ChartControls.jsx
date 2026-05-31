import React from 'react';

const ChartControls = ({ activePeriod, onPeriodChange }) => {
  const periods = [
    { label: '3M', value: '3mo' },
    { label: '6M', value: '6mo' },
    { label: '1Y', value: '1y' },
  ];

  return (
    <div className="flex gap-2">
      {periods.map((p) => (
        <button
          key={p.value}
          onClick={() => onPeriodChange(p.value)}
          className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
            activePeriod === p.value
              ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
              : 'dark:bg-dark-border/30 bg-gray-100 dark:text-dark-muted text-gray-500 dark:hover:text-dark-text hover:text-gray-700 border border-transparent'
          }`}
        >
          {p.label}
        </button>
      ))}
    </div>
  );
};

export default ChartControls;