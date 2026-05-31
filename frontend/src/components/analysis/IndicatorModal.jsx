import React, { useState, useEffect } from 'react';
import { X, BookOpen, Bot, Loader } from 'lucide-react';
import { getInterpretation } from '../../utils/api';

const IndicatorModal = ({ isOpen, onClose, symbol, period, initialTab = 'sma' }) => {
  const [activeIndicator, setActiveIndicator] = useState(initialTab);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isOpen || !symbol) return;

    const fetchInterpretation = async () => {
      setLoading(true);
      try {
        const result = await getInterpretation(symbol, period);
        setData(result);
      } catch (err) {
        console.error('Interpretation error:', err);
      }
      setLoading(false);
    };

    fetchInterpretation();
  }, [isOpen, symbol, period]);

  useEffect(() => {
    setActiveIndicator(initialTab);
  }, [initialTab]);

  if (!isOpen) return null;

  const indicators = [
    { key: 'sma', label: 'SMA' },
    { key: 'ema', label: 'EMA' },
    { key: 'rsi', label: 'RSI' },
    { key: 'macd', label: 'MACD' },
    { key: 'bollinger', label: 'Bollinger' },
    { key: 'support_resistance', label: 'S & R' },
  ];

  const staticInfo = data?.static?.[activeIndicator];
  const dynamicKey = `${activeIndicator}_interpretation`;
  const dynamicText = data?.dynamic?.[dynamicKey];
  const overallSummary = data?.dynamic?.overall_summary;

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="dark:bg-dark-card bg-white rounded-2xl border dark:border-dark-border border-gray-200 w-full max-w-2xl max-h-[85vh] overflow-hidden relative flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b dark:border-dark-border border-gray-200">
          <div className="flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-blue-400" />
            <h2 className="text-lg font-bold dark:text-dark-text text-gray-900">
              Understanding Indicators
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg dark:hover:bg-dark-border/50 hover:bg-gray-100 transition-colors"
          >
            <X className="w-5 h-5 dark:text-dark-muted text-gray-500" />
          </button>
        </div>

        {/* Indicator Tabs */}
        <div className="flex overflow-x-auto border-b dark:border-dark-border border-gray-200 px-2">
          {indicators.map((ind) => (
            <button
              key={ind.key}
              onClick={() => setActiveIndicator(ind.key)}
              className={`px-4 py-3 text-sm font-medium whitespace-nowrap transition-colors ${
                activeIndicator === ind.key
                  ? 'text-blue-400 border-b-2 border-blue-400'
                  : 'dark:text-dark-muted text-gray-500 dark:hover:text-dark-text hover:text-gray-700'
              }`}
            >
              {ind.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="p-5 overflow-y-auto flex-1">
          {loading ? (
            <div className="flex items-center justify-center py-16">
              <Loader className="w-6 h-6 dark:text-dark-muted text-gray-400 animate-spin" />
              <span className="dark:text-dark-muted text-gray-500 text-sm ml-3">
                Generating interpretation...
              </span>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Static Explanation */}
              {staticInfo && (
                <div>
                  <h3 className="dark:text-dark-text text-gray-900 font-bold text-base mb-2">
                    {staticInfo.title}
                  </h3>

                  {/* What is it */}
                  <div className="dark:bg-dark-bg/50 bg-gray-50 rounded-lg p-4 border dark:border-dark-border/50 border-gray-200 mb-4">
                    <p className="dark:text-dark-muted text-gray-500 text-xs uppercase tracking-wide font-semibold mb-2">
                      What is it?
                    </p>
                    <p className="dark:text-dark-text text-gray-700 text-sm leading-relaxed">
                      {staticInfo.what}
                    </p>
                  </div>

                  {/* How to read */}
                  <div className="dark:bg-dark-bg/50 bg-gray-50 rounded-lg p-4 border dark:border-dark-border/50 border-gray-200 mb-4">
                    <p className="dark:text-dark-muted text-gray-500 text-xs uppercase tracking-wide font-semibold mb-2">
                      How to read it
                    </p>
                    <ul className="space-y-1.5">
                      {staticInfo.how_to_read.map((item, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="text-blue-400 mt-0.5 text-sm">→</span>
                          <span className="dark:text-dark-text text-gray-700 text-sm">{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {/* AI Dynamic Interpretation */}
              {dynamicText && (
                <div className="bg-blue-500/5 border border-blue-500/20 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Bot className="w-4 h-4 text-blue-400" />
                    <p className="text-blue-400 text-xs uppercase tracking-wide font-semibold">
                      AI Analysis for {symbol.replace('.NS', '')}
                    </p>
                  </div>
                  <p className="dark:text-dark-text text-gray-700 text-sm leading-relaxed">
                    {dynamicText}
                  </p>
                </div>
              )}

              {/* Overall Summary (show on all tabs) */}
              {overallSummary && (
                <div className="bg-purple-500/5 border border-purple-500/20 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Bot className="w-4 h-4 text-purple-400" />
                    <p className="text-purple-400 text-xs uppercase tracking-wide font-semibold">
                      Overall Summary
                    </p>
                  </div>
                  <p className="dark:text-dark-text text-gray-700 text-sm leading-relaxed">
                    {overallSummary}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default IndicatorModal;