import React, { useState } from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import ReadMoreModal from './ReadMoreModal';

const KeyPointItem = ({ label, value, type = 'neutral' }) => {
  const colorMap = {
    good: 'text-profit',
    bad: 'text-loss',
    neutral: 'dark:text-dark-text text-gray-900',
    muted: 'dark:text-dark-muted text-gray-500',
  };

  return (
    <div className="flex items-center justify-between py-1.5">
      <span className="dark:text-dark-muted text-gray-500 text-xs">{label}</span>
      <span className={`text-sm font-semibold ${colorMap[type]}`}>{value}</span>
    </div>
  );
};

const KeyPointsTab = ({ data }) => {
  const [showModal, setShowModal] = useState(false);

  if (!data) return null;

  const kp = data.key_points || {};

  // Determine good/bad for color coding
  const getType = (label, value) => {
    if (value === 'N/A') return 'muted';
    const num = parseFloat(value);
    if (isNaN(num)) return 'neutral';

    switch (label) {
      case 'ROE':
      case 'Revenue Growth':
      case 'Earnings Growth':
        return num > 0 ? 'good' : 'bad';
      case 'Debt to Equity':
        return num < 1 ? 'good' : num < 2 ? 'neutral' : 'bad';
      case 'Profit Margins':
        return num > 10 ? 'good' : num > 5 ? 'neutral' : 'bad';
      default:
        return 'neutral';
    }
  };

  const keyMetrics = [
    { label: 'Promoter Holding', value: kp.promoter_holding !== 'N/A' ? `${kp.promoter_holding}%` : 'N/A' },
    { label: 'FII Holding', value: kp.fii_holding !== 'N/A' ? `${kp.fii_holding}%` : 'N/A' },
    { label: 'P/E Ratio', value: kp.pe_ratio || 'N/A' },
    { label: 'ROE', value: kp.roe || 'N/A' },
    { label: 'Debt to Equity', value: kp.debt_to_equity || 'N/A' },
  ];

  return (
    <>
      <div className="space-y-3">
        {/* Key Metrics */}
        <div>
          {keyMetrics.map((item, i) => (
            <KeyPointItem
              key={i}
              label={item.label}
              value={item.value}
              type={getType(item.label, item.value)}
            />
          ))}
          <button
            onClick={() => setShowModal(true)}
            className="text-blue-400 hover:text-blue-300 text-sm font-medium mt-2"
          >
            View all key points...
          </button>
        </div>

        {/* Strengths Preview */}
        {data.strengths && data.strengths.length > 0 && (
          <div>
            <p className="dark:text-dark-muted text-gray-500 text-xs uppercase tracking-wide font-semibold mb-1.5">
              Strengths
            </p>
            {data.strengths.slice(0, 2).map((s, i) => (
              <div key={i} className="flex items-start gap-1.5 mb-1">
                <TrendingUp className="w-3 h-3 text-profit mt-0.5 flex-shrink-0" />
                <span className="dark:text-dark-text text-gray-700 text-xs">{s}</span>
              </div>
            ))}
          </div>
        )}

        {/* Risks Preview */}
        {data.risks && data.risks.length > 0 && (
          <div>
            <p className="dark:text-dark-muted text-gray-500 text-xs uppercase tracking-wide font-semibold mb-1.5">
              Risks
            </p>
            {data.risks.slice(0, 2).map((r, i) => (
              <div key={i} className="flex items-start gap-1.5 mb-1">
                <TrendingDown className="w-3 h-3 text-loss mt-0.5 flex-shrink-0" />
                <span className="dark:text-dark-text text-gray-700 text-xs">{r}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Full Key Points Modal */}
      <ReadMoreModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title={`Key Points — ${data.name}`}
      >
        <div className="space-y-6">
          {/* All Financial Metrics */}
          <div>
            <h4 className="dark:text-dark-text text-gray-900 font-semibold mb-3">Financial Metrics</h4>
            <div className="dark:bg-dark-bg/50 bg-gray-50 rounded-lg p-4 space-y-2">
              <KeyPointItem label="Promoter Holding" value={kp.promoter_holding !== 'N/A' ? `${kp.promoter_holding}%` : 'N/A'} type={getType('Promoter', kp.promoter_holding)} />
              <KeyPointItem label="FII Holding" value={kp.fii_holding !== 'N/A' ? `${kp.fii_holding}%` : 'N/A'} type="neutral" />
              <KeyPointItem label="P/E Ratio" value={kp.pe_ratio || 'N/A'} type="neutral" />
              <KeyPointItem label="P/B Ratio" value={kp.pb_ratio || 'N/A'} type="neutral" />
              <KeyPointItem label="Beta" value={kp.beta || 'N/A'} type="neutral" />
              <KeyPointItem label="Dividend Yield" value={kp.dividend_yield || 'N/A'} type="neutral" />
              <KeyPointItem label="Debt to Equity" value={kp.debt_to_equity || 'N/A'} type={getType('Debt to Equity', kp.debt_to_equity)} />
              <KeyPointItem label="Revenue Growth" value={kp.revenue_growth || 'N/A'} type={getType('Revenue Growth', kp.revenue_growth)} />
              <KeyPointItem label="Earnings Growth" value={kp.earnings_growth || 'N/A'} type={getType('Earnings Growth', kp.earnings_growth)} />
              <KeyPointItem label="Profit Margins" value={kp.profit_margins || 'N/A'} type={getType('Profit Margins', kp.profit_margins)} />
              <KeyPointItem label="ROE" value={kp.roe || 'N/A'} type={getType('ROE', kp.roe)} />
            </div>
          </div>

          {/* Strengths */}
          {data.strengths && data.strengths.length > 0 && (
            <div>
              <h4 className="dark:text-dark-text text-gray-900 font-semibold mb-3">Key Strengths</h4>
              <div className="space-y-2">
                {data.strengths.map((s, i) => (
                  <div key={i} className="flex items-start gap-2 p-3 bg-green-500/5 border border-green-500/20 rounded-lg">
                    <TrendingUp className="w-4 h-4 text-profit mt-0.5 flex-shrink-0" />
                    <span className="dark:text-dark-text text-gray-700 text-sm">{s}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Risks */}
          {data.risks && data.risks.length > 0 && (
            <div>
              <h4 className="dark:text-dark-text text-gray-900 font-semibold mb-3">Key Risks</h4>
              <div className="space-y-2">
                {data.risks.map((r, i) => (
                  <div key={i} className="flex items-start gap-2 p-3 bg-red-500/5 border border-red-500/20 rounded-lg">
                    <TrendingDown className="w-4 h-4 text-loss mt-0.5 flex-shrink-0" />
                    <span className="dark:text-dark-text text-gray-700 text-sm">{r}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </ReadMoreModal>
    </>
  );
};

export default KeyPointsTab;