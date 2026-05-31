import React, { useState } from 'react';
import { Info } from 'lucide-react';
import MovingAverages from './MovingAverages';
import SupportResistance from './SupportResistance';
import TrendBadge from './TrendBadge';
import IndicatorModal from './IndicatorModal';
import Badge from '../ui/Badge';

const IndicatorCard = ({ title, value, signal, description, onInfoClick }) => {
  const signalColor = {
    Bullish: 'green',
    Bearish: 'red',
    Neutral: 'yellow',
    Overbought: 'red',
    Oversold: 'green',
  };

  return (
    <div className="dark:bg-dark-bg/50 bg-gray-50 rounded-lg p-4 border dark:border-dark-border/50 border-gray-200 transition-colors">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-1.5">
          <span className="dark:text-dark-muted text-gray-500 text-sm">{title}</span>
          {onInfoClick && (
            <button
              onClick={onInfoClick}
              className="p-0.5 rounded dark:hover:bg-dark-border/50 hover:bg-gray-200 transition-colors"
              title="Learn about this indicator"
            >
              <Info className="w-3.5 h-3.5 text-blue-400" />
            </button>
          )}
        </div>
        <Badge text={signal} color={signalColor[signal] || 'gray'} size="xs" />
      </div>
      <p className="dark:text-dark-text text-gray-900 font-bold text-lg">{value}</p>
      {description && (
        <p className="dark:text-dark-muted text-gray-500 text-xs mt-1">{description}</p>
      )}
    </div>
  );
};

const TechnicalAnalysis = ({ analysis, period, onPeriodChange, symbol }) => {
  const [showModal, setShowModal] = useState(false);
  const [modalTab, setModalTab] = useState('sma');

  if (!analysis) return null;

  const openModal = (tab) => {
    setModalTab(tab);
    setShowModal(true);
  };

  return (
    <div className="space-y-4">
      <div className="dark:bg-dark-card bg-white rounded-xl p-6 border dark:border-dark-border border-gray-200 transition-colors">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <h3 className="dark:text-dark-text text-gray-900 font-semibold text-lg">Technical Analysis</h3>
            <button
              onClick={() => openModal('sma')}
              className="p-1 rounded-lg dark:hover:bg-dark-border/50 hover:bg-gray-100 transition-colors"
              title="Learn about indicators"
            >
              <Info className="w-4 h-4 text-blue-400" />
            </button>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex gap-2">
              {['3mo', '6mo'].map((p) => (
                <button
                  key={p}
                  onClick={() => onPeriodChange(p)}
                  className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
                    period === p
                      ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                      : 'dark:bg-dark-border/30 bg-gray-100 dark:text-dark-muted text-gray-500 dark:hover:text-dark-text hover:text-gray-700 border border-transparent'
                  }`}
                >
                  {p === '3mo' ? '3 Months' : '6 Months'}
                </button>
              ))}
            </div>
            {analysis.trend && <TrendBadge trend={analysis.trend} />}
          </div>
        </div>

        {/* Indicator Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <IndicatorCard
            title="RSI (14)"
            value={analysis.rsi?.value || 'N/A'}
            signal={analysis.rsi?.signal || 'N/A'}
            description={analysis.rsi?.description}
            onInfoClick={() => openModal('rsi')}
          />
          <IndicatorCard
            title="MACD"
            value={analysis.macd?.macd || 'N/A'}
            signal={analysis.macd?.trend || 'N/A'}
            description={analysis.macd?.description}
            onInfoClick={() => openModal('macd')}
          />
          <IndicatorCard
            title="Bollinger Bands"
            value={`${analysis.bollinger_bands?.middle || 'N/A'}`}
            signal={analysis.bollinger_bands?.signal || 'N/A'}
            description={`Upper: ${analysis.bollinger_bands?.upper || 'N/A'} | Lower: ${analysis.bollinger_bands?.lower || 'N/A'}`}
            onInfoClick={() => openModal('bollinger')}
          />
        </div>

        {/* Moving Averages with info button */}
        <div className="flex items-center gap-2 mb-3">
          <h4 className="dark:text-dark-text text-gray-900 font-semibold">Moving Averages</h4>
          <button
            onClick={() => openModal('sma')}
            className="p-0.5 rounded dark:hover:bg-dark-border/50 hover:bg-gray-200 transition-colors"
            title="Learn about Moving Averages"
          >
            <Info className="w-3.5 h-3.5 text-blue-400" />
          </button>
        </div>
        <MovingAverages data={analysis.moving_averages} />
      </div>

      {/* Support & Resistance with info button */}
      <div className="relative">
        <SupportResistance
          data={analysis.support_resistance}
          onInfoClick={() => openModal('support_resistance')}
        />
      </div>

      {/* Indicator Info Modal */}
      <IndicatorModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        symbol={symbol || analysis.symbol}
        period={period}
        initialTab={modalTab}
      />
    </div>
  );
};

export default TechnicalAnalysis;