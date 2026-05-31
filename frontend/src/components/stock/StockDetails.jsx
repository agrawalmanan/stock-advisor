import React from 'react';
import { formatPrice, formatVolume } from '../../utils/formatters';

const DetailItem = ({ label, value }) => (
  <div>
    <p className="dark:text-dark-muted text-gray-500 text-xs uppercase tracking-wide mb-1">{label}</p>
    <p className="dark:text-dark-text text-gray-900 font-semibold text-sm">{value}</p>
  </div>
);

const StockDetails = ({ data }) => {
  return (
    <div className="dark:bg-dark-card bg-white rounded-xl p-6 border dark:border-dark-border border-gray-200 transition-colors">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-y-4 gap-x-6">
        <DetailItem label="Prev Close" value={formatPrice(data.prev_close)} />
        <DetailItem label="Volume" value={data.volume_formatted || formatVolume(data.volume)} />
        <DetailItem label="Day High" value={formatPrice(data.day_high)} />
        <DetailItem label="Day Low" value={formatPrice(data.day_low)} />
        <DetailItem label="52W High" value={formatPrice(data.week_52_high)} />
        <DetailItem label="52W Low" value={formatPrice(data.week_52_low)} />
        <DetailItem label="Mkt Cap" value={data.market_cap || 'N/A'} />
        <DetailItem label="P/E Ratio" value={data.pe_ratio || 'N/A'} />
        <DetailItem label="P/B Ratio" value={data.pb_ratio || 'N/A'} />
        <DetailItem label="EPS" value={data.eps ? `₹${data.eps}` : 'N/A'} />
        <DetailItem label="Beta" value={data.beta || 'N/A'} />
        <DetailItem
          label="Div Yield"
          value={data.dividend_yield ? `${(data.dividend_yield * 100).toFixed(2)}%` : 'N/A'}
        />
      </div>
    </div>
  );
};

export default StockDetails;