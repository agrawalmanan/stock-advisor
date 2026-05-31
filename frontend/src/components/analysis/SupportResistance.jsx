import React from 'react';
import { Info } from 'lucide-react';
import { formatPrice } from '../../utils/formatters';

const SupportResistance = ({ data, onInfoClick }) => {
  if (!data) return null;

  const { support = [], resistance = [], current_price } = data;

  return (
    <div className="dark:bg-dark-card bg-white rounded-xl p-6 border dark:border-dark-border border-gray-200 transition-colors">
      <div className="flex items-center gap-2 mb-4">
        <h3 className="dark:text-dark-text text-gray-900 font-semibold">Support & Resistance</h3>
        {onInfoClick && (
          <button
            onClick={onInfoClick}
            className="p-0.5 rounded dark:hover:bg-dark-border/50 hover:bg-gray-200 transition-colors"
            title="Learn about Support & Resistance"
          >
            <Info className="w-3.5 h-3.5 text-blue-400" />
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-green-500/5 rounded-lg p-4 border border-green-500/20">
          <p className="text-green-400 text-xs uppercase tracking-wide font-semibold mb-3">Support Levels</p>
          <div className="space-y-2">
            {support.length > 0 ? support.map((level, i) => (
              <div key={i} className="flex items-center justify-between">
                <span className="dark:text-dark-muted text-gray-500 text-sm">S{i + 1}</span>
                <span className="text-green-400 font-semibold text-sm">{formatPrice(level)}</span>
              </div>
            )) : (
              <p className="dark:text-dark-muted text-gray-500 text-sm">No levels found</p>
            )}
          </div>
        </div>

        <div className="bg-blue-500/5 rounded-lg p-4 border border-blue-500/20 flex flex-col items-center justify-center">
          <p className="text-blue-400 text-xs uppercase tracking-wide font-semibold mb-2">Current Price</p>
          <span className="text-blue-400 font-bold text-2xl">{formatPrice(current_price)}</span>
        </div>

        <div className="bg-red-500/5 rounded-lg p-4 border border-red-500/20">
          <p className="text-red-400 text-xs uppercase tracking-wide font-semibold mb-3">Resistance Levels</p>
          <div className="space-y-2">
            {resistance.length > 0 ? resistance.map((level, i) => (
              <div key={i} className="flex items-center justify-between">
                <span className="dark:text-dark-muted text-gray-500 text-sm">R{i + 1}</span>
                <span className="text-red-400 font-semibold text-sm">{formatPrice(level)}</span>
              </div>
            )) : (
              <p className="dark:text-dark-muted text-gray-500 text-sm">No levels found</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SupportResistance;