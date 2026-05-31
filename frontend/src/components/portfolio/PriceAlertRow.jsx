import React from 'react'

function PriceAlertRow({ symbol = 'RELIANCE', currentPrice = '2,415.80', targetPrice = '2,500.00', direction = 'above' }) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-900">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">{symbol}</p>
          <p className="text-xl font-semibold mt-1">Current ₹{currentPrice}</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-slate-500 dark:text-slate-400">Alert when</p>
          <p className="text-lg font-semibold text-blue-600">{direction === 'above' ? 'Above' : 'Below'} ₹{targetPrice}</p>
        </div>
      </div>
    </div>
  )
}

export default PriceAlertRow
