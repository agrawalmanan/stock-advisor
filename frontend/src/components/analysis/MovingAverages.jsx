import React from 'react';
import { formatPrice } from '../../utils/formatters';

const MovingAverages = ({ data }) => {
  if (!data) return null;

  const smaKeys = Object.keys(data).filter(k => k.startsWith('sma_'));
  const emaKeys = Object.keys(data).filter(k => k.startsWith('ema_'));

  const renderRow = (key, ma) => {
    const isAbove = ma.signal === 'Above';
    const signalColor = isAbove ? 'text-profit' : ma.signal === 'Below' ? 'text-loss' : 'dark:text-dark-muted text-gray-500';
    const dotColor = isAbove ? 'bg-profit' : ma.signal === 'Below' ? 'bg-loss' : 'bg-gray-500';

    return (
      <tr key={key} className="border-b dark:border-dark-border/30 border-gray-100 last:border-0">
        <td className="py-2 dark:text-dark-text text-gray-900 text-sm font-medium">{ma.label}</td>
        <td className="py-2 dark:text-dark-text text-gray-900 text-sm text-right">{formatPrice(ma.value)}</td>
        <td className="py-2 text-right">
          <div className="flex items-center justify-end gap-2">
            <div className={`w-2 h-2 rounded-full ${dotColor}`} />
            <span className={`text-sm font-medium ${signalColor}`}>{ma.signal}</span>
          </div>
        </td>
      </tr>
    );
  };

  return (
    <div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="dark:bg-dark-bg/50 bg-gray-50 rounded-lg p-4 border dark:border-dark-border/50 border-gray-200 transition-colors">
          <p className="dark:text-dark-muted text-gray-500 text-xs uppercase tracking-wide mb-2">Simple Moving Average</p>
          <table className="w-full">
            <tbody>{smaKeys.map((key) => renderRow(key, data[key]))}</tbody>
          </table>
        </div>

        <div className="dark:bg-dark-bg/50 bg-gray-50 rounded-lg p-4 border dark:border-dark-border/50 border-gray-200 transition-colors">
          <p className="dark:text-dark-muted text-gray-500 text-xs uppercase tracking-wide mb-2">Exponential Moving Average</p>
          <table className="w-full">
            <tbody>{emaKeys.map((key) => renderRow(key, data[key]))}</tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default MovingAverages;