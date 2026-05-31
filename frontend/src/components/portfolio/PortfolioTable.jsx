import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Trash2, Bell, Loader } from 'lucide-react';
import { formatPrice } from '../../utils/formatters';

const PortfolioTable = ({ holdings, onDelete }) => {
  const navigate = useNavigate();

  if (!holdings || holdings.length === 0) return null;

  return (
    <div className="dark:bg-dark-card bg-white rounded-xl border dark:border-dark-border border-gray-200 overflow-hidden transition-colors">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[800px]">
          <thead>
            <tr className="border-b dark:border-dark-border border-gray-200 dark:bg-dark-bg/50 bg-gray-50">
              <th className="text-left dark:text-dark-muted text-gray-500 text-xs uppercase tracking-wide py-3 px-4">Stock</th>
              <th className="text-center dark:text-dark-muted text-gray-500 text-xs uppercase tracking-wide py-3 px-2">Type</th>
              <th className="text-right dark:text-dark-muted text-gray-500 text-xs uppercase tracking-wide py-3 px-2">Qty</th>
              <th className="text-right dark:text-dark-muted text-gray-500 text-xs uppercase tracking-wide py-3 px-2">Buy Price</th>
              <th className="text-right dark:text-dark-muted text-gray-500 text-xs uppercase tracking-wide py-3 px-2">Current</th>
              <th className="text-right dark:text-dark-muted text-gray-500 text-xs uppercase tracking-wide py-3 px-2">P&L</th>
              <th className="text-right dark:text-dark-muted text-gray-500 text-xs uppercase tracking-wide py-3 px-2">P&L %</th>
              <th className="text-right dark:text-dark-muted text-gray-500 text-xs uppercase tracking-wide py-3 px-2">Target</th>
              <th className="text-center dark:text-dark-muted text-gray-500 text-xs uppercase tracking-wide py-3 px-2"></th>
            </tr>
          </thead>
          <tbody>
            {holdings.map((h, i) => {
              const pnl = h.livePrice ? (h.livePrice - h.buyPrice) * h.qty : 0;
              const pnlPct = h.buyPrice > 0 ? ((h.livePrice - h.buyPrice) / h.buyPrice) * 100 : 0;
              const isProfit = pnl >= 0;

              return (
                <tr
                  key={i}
                  className="border-b dark:border-dark-border/30 border-gray-100 last:border-0 dark:hover:bg-dark-border/20 hover:bg-gray-50 transition-colors"
                >
                  {/* Stock Name */}
                  <td className="py-3 px-4">
                    <button
                      onClick={() => navigate(`/stock/${h.symbol}`)}
                      className="text-left group"
                    >
                      <p className="dark:text-dark-text text-gray-900 text-sm font-medium group-hover:text-blue-400 transition-colors">
                        {h.name}
                      </p>
                      <p className="dark:text-dark-muted text-gray-500 text-xs">
                        {h.symbol.replace('.NS', '')} • {h.buyDate}
                      </p>
                    </button>
                  </td>

                  {/* Type */}
                  <td className="text-center py-3 px-2">
                    <span className={`text-xs px-2 py-1 rounded-md font-medium ${
                      h.holdingType === 'long'
                        ? 'bg-blue-500/20 text-blue-400'
                        : 'bg-orange-500/20 text-orange-400'
                    }`}>
                      {h.holdingType === 'long' ? 'Long' : 'Short'}
                    </span>
                  </td>

                  {/* Qty */}
                  <td className="text-right dark:text-dark-text text-gray-900 text-sm py-3 px-2">
                    {h.qty}
                  </td>

                  {/* Buy Price */}
                  <td className="text-right dark:text-dark-text text-gray-900 text-sm py-3 px-2">
                    {formatPrice(h.buyPrice)}
                  </td>

                  {/* Current Price */}
                  <td className="text-right py-3 px-2">
                    {h.livePrice ? (
                      <span className="dark:text-dark-text text-gray-900 text-sm font-medium">
                        {formatPrice(h.livePrice)}
                      </span>
                    ) : (
                      <Loader className="w-4 h-4 dark:text-dark-muted text-gray-400 animate-spin ml-auto" />
                    )}
                  </td>

                  {/* P&L */}
                  <td className={`text-right text-sm font-medium py-3 px-2 ${isProfit ? 'text-profit' : 'text-loss'}`}>
                    {h.livePrice ? `${isProfit ? '+' : ''}${formatPrice(pnl.toFixed(2))}` : '—'}
                  </td>

                  {/* P&L % */}
                  <td className={`text-right text-sm font-medium py-3 px-2 ${isProfit ? 'text-profit' : 'text-loss'}`}>
                    {h.livePrice ? `${isProfit ? '+' : ''}${pnlPct.toFixed(2)}%` : '—'}
                  </td>

                  {/* Target */}
                  <td className="text-right dark:text-dark-muted text-gray-500 text-sm py-3 px-2">
                    {h.targetPrice ? (
                      <div className="flex items-center justify-end gap-1">
                        <Bell className="w-3 h-3 text-yellow-400" />
                        <span>{formatPrice(h.targetPrice)}</span>
                      </div>
                    ) : '—'}
                  </td>

                  {/* Delete */}
                  <td className="text-center py-3 px-2">
                    <button
                      onClick={() => onDelete(i)}
                      className="p-1.5 rounded dark:hover:bg-red-500/20 hover:bg-red-50 transition-colors"
                    >
                      <Trash2 className="w-4 h-4 text-loss" />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PortfolioTable;