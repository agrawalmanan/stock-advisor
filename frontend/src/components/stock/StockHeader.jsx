import React from 'react';
import Badge from '../ui/Badge';
import WatchlistBtn from '../watchlist/WatchlistBtn';
import { formatPrice, formatChange } from '../../utils/formatters';

const StockHeader = ({ data }) => {
  const change = formatChange(data.change, data.change_pct);

  return (
    <div className="dark:bg-dark-card bg-white rounded-xl p-6 border dark:border-dark-border border-gray-200 transition-colors">
      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-3 mb-2 flex-wrap">
            <h1 className="text-xl md:text-2xl font-bold dark:text-dark-text text-gray-900">{data.name}</h1>
            <Badge text={data.sector || 'Unknown'} color="blue" />
            <WatchlistBtn
              symbol={data.symbol}
              stockName={data.name}
              sector={data.sector}
            />
          </div>

          <div className="flex items-baseline gap-3">
            <span className="text-3xl md:text-4xl font-bold dark:text-dark-text text-gray-900">
              {formatPrice(data.current_price)}
            </span>
            <span className={`text-lg font-semibold ${change.color}`}>
              {change.arrow} {change.text}
            </span>
          </div>

          <p className="dark:text-dark-muted text-gray-500 text-sm mt-1">
            {data.symbol} • NSE • {data.currency || 'INR'}
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          {data.risk && (
            <Badge text={`Risk: ${data.risk.level}`} color={data.risk.color} />
          )}
          {data.trade_type && (
            <Badge text={data.trade_type.label} color={data.trade_type.color} />
          )}
        </div>
      </div>
    </div>
  );
};

export default StockHeader;