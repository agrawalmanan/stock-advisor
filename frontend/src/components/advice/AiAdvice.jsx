import React from 'react';
import { Bot, Target, LogOut, ShieldAlert } from 'lucide-react';
import ReasonsList from './ReasonsList';
import { formatPrice, getActionColor } from '../../utils/formatters';

const AiAdvice = ({ advice }) => {
  if (!advice) return null;

  const actionColor = getActionColor(advice.action);

  return (
    <div className="dark:bg-dark-card bg-white rounded-xl p-6 border dark:border-dark-border border-gray-200 transition-colors">
      <div className="flex items-center gap-2 mb-4">
        <Bot className="w-5 h-5 text-blue-400" />
        <h3 className="dark:text-dark-text text-gray-900 font-semibold text-lg">AI Advisor</h3>
        <span className="dark:text-dark-muted text-gray-500 text-xs">(Powered by Llama AI)</span>
      </div>

      <div className="flex items-center gap-4 mb-4">
        <div className={`px-6 py-3 rounded-xl border-2 ${actionColor.bg} ${actionColor.border}`}>
          <span className={`text-3xl font-black ${actionColor.text}`}>{advice.action}</span>
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="dark:text-dark-muted text-gray-500 text-sm">Confidence</span>
            <span className="dark:text-dark-text text-gray-900 font-bold text-lg">{advice.confidence}%</span>
          </div>
          <div className="w-32 h-2 dark:bg-dark-border bg-gray-200 rounded-full mt-1">
            <div
              className={`h-full rounded-full ${
                advice.confidence >= 70 ? 'bg-profit' : advice.confidence >= 50 ? 'bg-hold' : 'bg-loss'
              }`}
              style={{ width: `${advice.confidence}%` }}
            />
          </div>
        </div>
      </div>

      {advice.summary && (
        <p className="dark:text-dark-muted text-gray-500 text-sm mb-4 italic">"{advice.summary}"</p>
      )}

      {(advice.entry_point !== 'N/A' || advice.exit_point !== 'N/A') && (
        <div className="grid grid-cols-3 gap-3 mb-4">
          <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-3 text-center">
            <div className="flex items-center justify-center gap-1 mb-1">
              <Target className="w-3 h-3 text-green-400" />
              <span className="text-green-400 text-xs font-semibold">Entry</span>
            </div>
            <span className="text-green-400 font-bold text-sm">{formatPrice(advice.entry_point)}</span>
          </div>
          <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3 text-center">
            <div className="flex items-center justify-center gap-1 mb-1">
              <LogOut className="w-3 h-3 text-blue-400" />
              <span className="text-blue-400 text-xs font-semibold">Exit</span>
            </div>
            <span className="text-blue-400 font-bold text-sm">{formatPrice(advice.exit_point)}</span>
          </div>
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 text-center">
            <div className="flex items-center justify-center gap-1 mb-1">
              <ShieldAlert className="w-3 h-3 text-red-400" />
              <span className="text-red-400 text-xs font-semibold">Stop Loss</span>
            </div>
            <span className="text-red-400 font-bold text-sm">{formatPrice(advice.stop_loss)}</span>
          </div>
        </div>
      )}

      <ReasonsList reasons={advice.reasons || []} />
    </div>
  );
};

export default AiAdvice;