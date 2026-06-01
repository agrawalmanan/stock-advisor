import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, Loader } from 'lucide-react';
import { formatPrice } from '../../utils/formatters';
import { getPeers } from '../../utils/api';

const PeerComparison = ({ symbol, sector }) => {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!symbol) return;

    let cancelled = false;

    const load = async () => {
      setIsLoading(true);
      setData(null);

      try {
        const response = await getPeers(symbol);

        if (cancelled) return;

        // Filter valid peers
        const validPeers = (response.peers || []).filter(
          (p) => p && p.current_price !== null && p.current_price !== 'N/A'
        );

        if (validPeers.length > 0) {
          setData({
            peers: validPeers,
            median: response.industry_median || {},
          });
        }
      } catch (err) {
        console.error('Failed to load peers:', err);
      }

      if (!cancelled) setIsLoading(false);
    };

    load();

    return () => {
      cancelled = true;
    };
  }, [symbol]);

  // Loading state
  if (isLoading) {
    return (
      <div className="dark:bg-dark-card bg-white rounded-xl p-6 border dark:border-dark-border border-gray-200">
        <div className="flex items-center gap-2 mb-4">
          <Users className="w-5 h-5 text-blue-400" />
          <h3 className="dark:text-dark-text text-gray-900 font-semibold">Peer Comparison</h3>
        </div>
        <div className="flex items-center justify-center py-10">
          <Loader className="w-6 h-6 text-gray-400 animate-spin" />
          <span className="text-gray-500 text-sm ml-3">Loading peers...</span>
        </div>
      </div>
    );
  }

  // No data
  if (!data || !data.peers || data.peers.length === 0) {
    return null;
  }

  const { peers, median } = data;

  // Helper functions
  const fmt = (val, suffix) => {
    if (val === null || val === undefined || val === 'N/A') return 'N/A';
    return suffix ? `${val}${suffix}` : `${val}`;
  };

  const color = (val, good, avg) => {
    if (val === null || val === undefined || val === 'N/A') return 'dark:text-dark-muted text-gray-500';
    const n = Number(val);
    if (isNaN(n)) return 'dark:text-dark-muted text-gray-500';
    if (n >= good) return 'text-profit';
    if (n >= avg) return 'text-hold';
    return 'text-loss';
  };

  return (
    <div className="dark:bg-dark-card bg-white rounded-xl p-6 border dark:border-dark-border border-gray-200">
      <div className="flex items-center gap-2 mb-4">
        <Users className="w-5 h-5 text-blue-400" />
        <h3 className="dark:text-dark-text text-gray-900 font-semibold">Peer Comparison</h3>
        <span className="dark:text-dark-muted text-gray-500 text-xs">
          ({peers.length} companies • {sector})
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[700px]">
          <thead>
            <tr className="border-b dark:border-dark-border border-gray-200">
              <th className="text-left dark:text-dark-muted text-gray-500 text-xs uppercase py-3 px-2">Company</th>
              <th className="text-right dark:text-dark-muted text-gray-500 text-xs uppercase py-3 px-2">Price</th>
              <th className="text-right dark:text-dark-muted text-gray-500 text-xs uppercase py-3 px-2">Change</th>
              <th className="text-right dark:text-dark-muted text-gray-500 text-xs uppercase py-3 px-2">Mkt Cap</th>
              <th className="text-right dark:text-dark-muted text-gray-500 text-xs uppercase py-3 px-2">P/E</th>
              <th className="text-right dark:text-dark-muted text-gray-500 text-xs uppercase py-3 px-2">ROCE%</th>
              <th className="text-right dark:text-dark-muted text-gray-500 text-xs uppercase py-3 px-2">OPM%</th>
            </tr>
          </thead>
          <tbody>
            {peers.map((peer) => {
              const chg = peer.change_pct;
              const chgNum = (chg !== null && chg !== undefined && chg !== 'N/A') ? Number(chg) : null;
              const isUp = chgNum !== null && chgNum >= 0;

              return (
                <tr
                  key={peer.symbol}
                  onClick={() => navigate(`/stock/${peer.symbol}`)}
                  className="border-b dark:border-dark-border/30 border-gray-100 last:border-0 hover:bg-gray-50 dark:hover:bg-dark-border/30 cursor-pointer group"
                >
                  <td className="py-3 px-2">
                    <p className="dark:text-dark-text text-gray-900 text-sm font-medium group-hover:text-blue-400">
                      {peer.name || peer.symbol}
                    </p>
                    <p className="dark:text-dark-muted text-gray-500 text-xs">
                      {(peer.symbol || '').replace('.NS', '')}
                    </p>
                  </td>
                  <td className="text-right dark:text-dark-text text-gray-900 text-sm font-medium py-3 px-2">
                    {formatPrice(peer.current_price)}
                  </td>
                  <td className={`text-right text-sm font-medium py-3 px-2 ${chgNum !== null ? (isUp ? 'text-profit' : 'text-loss') : 'text-gray-500'}`}>
                    {chgNum !== null ? `${isUp ? '+' : ''}${chg}%` : 'N/A'}
                  </td>
                  <td className="text-right dark:text-dark-text text-gray-900 text-sm py-3 px-2">
                    {peer.market_cap || 'N/A'}
                  </td>
                  <td className="text-right dark:text-dark-text text-gray-900 text-sm py-3 px-2">
                    {fmt(peer.pe_ratio)}
                  </td>
                  <td className={`text-right text-sm font-medium py-3 px-2 ${color(peer.roce_pct, 15, 10)}`}>
                    {fmt(peer.roce_pct, '%')}
                  </td>
                  <td className={`text-right text-sm font-medium py-3 px-2 ${color(peer.opm_pct, 20, 10)}`}>
                    {fmt(peer.opm_pct, '%')}
                  </td>
                </tr>
              );
            })}

            {/* Median Row */}
            {median && Object.keys(median).length > 0 && (
              <tr className="dark:bg-blue-500/5 bg-blue-50 border-t-2 dark:border-blue-500/20 border-blue-200">
                <td className="py-3 px-2"><p className="text-blue-400 text-sm font-bold">Industry Median</p></td>
                <td className="text-right text-blue-400 text-sm font-medium py-3 px-2">{median.current_price ? formatPrice(median.current_price) : '—'}</td>
                <td className="text-right text-blue-400 text-sm font-medium py-3 px-2">{median.change_pct ? `${median.change_pct}%` : '—'}</td>
                <td className="text-right text-blue-400 text-sm font-medium py-3 px-2">—</td>
                <td className="text-right text-blue-400 text-sm font-medium py-3 px-2">{median.pe_ratio || '—'}</td>
                <td className="text-right text-blue-400 text-sm font-medium py-3 px-2">{median.roce_pct ? `${median.roce_pct}%` : '—'}</td>
                <td className="text-right text-blue-400 text-sm font-medium py-3 px-2">{median.opm_pct ? `${median.opm_pct}%` : '—'}</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="flex items-center gap-4 mt-4 text-xs">
        <span className="dark:text-dark-muted text-gray-500">ROCE/OPM:</span>
        <span className="text-profit">● Good (≥15%/≥20%)</span>
        <span className="text-hold">● Average (≥10%)</span>
        <span className="text-loss">● Below avg</span>
      </div>
    </div>
  );
};

export default PeerComparison;