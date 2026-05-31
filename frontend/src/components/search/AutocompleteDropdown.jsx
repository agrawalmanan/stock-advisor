import React from 'react';
import { TrendingUp } from 'lucide-react';

const AutocompleteDropdown = ({ results, isLoading, onSelect }) => {
  if (isLoading) {
    return (
      <div className="absolute top-full left-0 right-0 mt-2 dark:bg-dark-card dark:border-dark-border bg-white border-gray-200 border rounded-xl shadow-2xl z-50 p-4">
        <div className="flex items-center gap-2 dark:text-dark-muted text-gray-500 text-sm">
          <div className="w-4 h-4 border-2 dark:border-dark-muted border-gray-400 border-t-blue-500 rounded-full animate-spin" />
          Searching...
        </div>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="absolute top-full left-0 right-0 mt-2 dark:bg-dark-card dark:border-dark-border bg-white border-gray-200 border rounded-xl shadow-2xl z-50 p-4">
        <p className="dark:text-dark-muted text-gray-500 text-sm text-center">No stocks found</p>
      </div>
    );
  }

  return (
    <div className="absolute top-full left-0 right-0 mt-2 dark:bg-dark-card dark:border-dark-border bg-white border-gray-200 border rounded-xl shadow-2xl z-50 overflow-hidden max-h-80 overflow-y-auto">
      {results.map((stock, index) => (
        <button
          key={stock.symbol}
          onClick={() => onSelect(stock)}
          className={`w-full flex items-center gap-3 px-4 py-3 dark:hover:bg-dark-border/50 hover:bg-gray-100 transition-colors text-left ${
            index !== results.length - 1 ? 'border-b dark:border-dark-border/50 border-gray-100' : ''
          }`}
        >
          <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
            <TrendingUp className="w-4 h-4 text-blue-400" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="dark:text-dark-text text-gray-900 text-sm font-medium truncate">{stock.name}</p>
            <p className="dark:text-dark-muted text-gray-500 text-xs">{stock.symbol.replace('.NS', '')} • {stock.sector}</p>
          </div>
        </button>
      ))}
    </div>
  );
};

export default AutocompleteDropdown;