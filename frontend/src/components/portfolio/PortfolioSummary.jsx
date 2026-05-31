import React from 'react';
import { TrendingUp, TrendingDown, Briefcase } from 'lucide-react';
import { formatPrice } from '../../utils/formatters';

const PortfolioSummary = ({ holdings }) => {
  if (!holdings || holdings.length === 0) return null;

  let totalInvested = 0;
  let totalCurrent = 0;

  holdings.forEach((h) => {
    if (h.buyPrice && h.qty && h.livePrice) {
      totalInvested += h.buyPrice * h.qty;
      totalCurrent += h.livePrice * h.qty;
    }
  });

  const totalPnL = totalCurrent - totalInvested;
  const totalPnLPct = totalInvested > 0 ? ((totalPnL / totalInvested) * 100) : 0;
  const isProfit = totalPnL >= 0;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      {/* Total Investment */}
      <div className="dark:bg-dark-card bg-white rounded-xl p-5 border dark:border-dark-border border-gray-200 transition-colors">
        <div className="flex items-center gap-2 mb-2">
          <Briefcase className="w-4 h-4 text-blue-400" />
          <span className="dark:text-dark-muted text-gray-500 text-sm">Total Invested</span>
        </div>
        <p className="dark:text-dark-text text-gray-900 font-bold text-2xl">
          {formatPrice(totalInvested.toFixed(2))}
        </p>
        <p className="dark:text-dark-muted text-gray-500 text-xs mt-1">
          {holdings.length} stock{holdings.length > 1 ? 's' : ''}
        </p>
      </div>

      {/* Current Value */}
      <div className="dark:bg-dark-card bg-white rounded-xl p-5 border dark:border-dark-border border-gray-200 transition-colors">
        <div className="flex items-center gap-2 mb-2">
          {isProfit ? (
            <TrendingUp className="w-4 h-4 text-profit" />
          ) : (
            <TrendingDown className="w-4 h-4 text-loss" />
          )}
          <span className="dark:text-dark-muted text-gray-500 text-sm">Current Value</span>
        </div>
        <p className="dark:text-dark-text text-gray-900 font-bold text-2xl">
          {formatPrice(totalCurrent.toFixed(2))}
        </p>
      </div>

      {/* Total P&L */}
      <div className={`rounded-xl p-5 border transition-colors ${
        isProfit
          ? 'bg-green-500/5 border-green-500/20'
          : 'bg-red-500/5 border-red-500/20'
      }`}>
        <div className="flex items-center gap-2 mb-2">
          <span className={`text-sm ${isProfit ? 'text-profit' : 'text-loss'}`}>
            {isProfit ? '▲' : '▼'}
          </span>
          <span className={`text-sm ${isProfit ? 'text-profit' : 'text-loss'}`}>
            Total P&L
          </span>
        </div>
        <p className={`font-bold text-2xl ${isProfit ? 'text-profit' : 'text-loss'}`}>
          {isProfit ? '+' : ''}{formatPrice(totalPnL.toFixed(2))}
        </p>
        <p className={`text-xs mt-1 ${isProfit ? 'text-profit' : 'text-loss'}`}>
          {isProfit ? '+' : ''}{totalPnLPct.toFixed(2)}%
        </p>
      </div>
    </div>
  );
};

export default PortfolioSummary;