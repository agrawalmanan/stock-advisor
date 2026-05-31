import React from 'react';

const PortfolioFilter = ({ activeFilter, onFilterChange }) => {
  const filters = [
    { label: 'All', value: 'all' },
    { label: 'Long Term', value: 'long' },
    { label: 'Short Term', value: 'short' },
  ];

  return (
    <div className="flex gap-2">
      {filters.map((f) => (
        <button
          key={f.value}
          onClick={() => onFilterChange(f.value)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeFilter === f.value
              ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
              : 'dark:bg-dark-border/30 bg-gray-100 dark:text-dark-muted text-gray-500 dark:hover:text-dark-text hover:text-gray-700 border border-transparent'
          }`}
        >
          {f.label}
        </button>
      ))}
    </div>
  );
};

export default PortfolioFilter;