import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, Loader, ArrowUpDown } from 'lucide-react';
import { formatPrice } from '../../utils/formatters';
import { getPeers } from '../../utils/api';

const safeNum = (val) => {
  if (val === null || val === undefined || val === 'N/A') return null;
  const n = Number(val);
  return isNaN(n) ? null : n;
};

const PeerComparison = ({ symbol, sector }) => {
  const navigate = useNavigate();
  const [peers, setPeers] = useState([]);
  const [industryMedian, setIndustryMedian] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [sortKey, setSortKey] = useState(null);
  const [sortAsc, setSortAsc] = useState(true);

  useEffect(() => {
    if (!symbol) {
      setPeers([]);
      setIndustryMedian({});
      setLoading(false);
      return;
    }

    const fetchPeers = async () => {
      setLoading(true);
      setError(false);

      try {
        const data = await getPeers(symbol);

        const validPeers = (data?.peers || []).filter(
          (p) => p && p.current_price && p.current_price !== 'N/A'
        );

        setPeers(validPeers);
        setIndustryMedian(data?.industry_median || {});
      } catch (err) {
        console.error('Peer fetch error:', err);
        setPeers([]);
        setIndustryMedian({});
        setError(true);
      } finally {
        setLoading(false);
      }
    };

    fetchPeers();
  }, [symbol]);

  const handleSort = (key) => {
    if (sortKey === key) {
      setSortAsc(!sortAsc);
    } else {
      setSortKey(key);
      setSortAsc(true);
    }
  };

  const sortedPeers = [...peers].sort((a, b) => {
    if (!sortKey) return 0;

    const aVal = safeNum(a?.[sortKey]) ?? -Infinity;
    const bVal = safeNum(b?.[sortKey]) ?? -Infinity;

    return sortAsc ? aVal - bVal : bVal - aVal;
  });

  const SortHeader = ({ label, keyName }) => (
    <th
      onClick={() => handleSort(keyName)}
      className="text-right dark:text-dark-muted text-gray-500 text-xs uppercase tracking-wide py-3 px-2 cursor-pointer hover:text-blue-400 transition-colors select-none"
    >
      <div className="flex items-center justify-end gap-1">
        {label}
        <ArrowUpDown className="w-3 h-3" />
      </div>
    </th>
  );

  const formatMetric = (val, suffix = '') => {
    const n = safeNum(val);
    if (n === null) return 'N/A';
    return `${n}${suffix}`;
  };

  const metricColor = (val, goodThreshold, avgThreshold) => {
    const n = safeNum(val);
    if (n === null) return 'dark:text-dark-muted text-gray-500';
    if (n >= goodThreshold) return 'text-profit';
    if (n >= avgThreshold) return 'text-hold';
    return 'text-loss';
  };

  if (loading) {
    return (
      <div className="dark:bg-dark-card bg-white rounded-xl p-6 border dark:border-dark-border border-gray-200 transition-colors">
        <div className="flex items-center gap-2 mb-4">
          <Users className="w-5 h-5 text-blue-400" />
          <h3 className="dark:text-dark-text text-gray-900 font-semibold">Peer Comparison</h3>
        </div>
        <div className="flex items-center justify-center py-10">
          <Loader className="w-6 h-6 dark:text-dark-muted text-gray-400 animate-spin" />
          <span className="dark:text-dark-muted text-gray-500 text-sm ml-3">Loading peer data...</span>
        </div>
      </div>
    );
  }

  if (error || peers.length === 0) {
    return null;
  }

  return (
    <div className="dark:bg-dark-card bg-white rounded-xl p-6 border dark:border-dark-border border-gray-200 transition-colors">
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
              <th className="text-left dark:text-dark-muted text-gray-500 text-xs uppercase tracking-wide py-3 px-2">
                Company
              </th>
              <SortHeader label="Price" keyName="current_price" />
              <SortHeader label="Change" keyName="change_pct" />
              <th className="text-right dark:text-dark-muted text-gray-500 text-xs uppercase tracking-wide py-3 px-2">
                Mkt Cap
              </th>
              <SortHeader label="P/E" keyName="pe_ratio" />
              <SortHeader label="ROCE%" keyName="roce_pct" />
              <SortHeader label="OPM%" keyName="opm_pct" />
            </tr>
          </thead>
          <tbody>
            {sortedPeers.map((peer, i) => {
              const changeNum = safeNum(peer?.change_pct);
              const isPositive = changeNum !== null && changeNum >= 0;

              return (
                <tr
                  key={peer.symbol || i}
                  onClick={() => navigate(`/stock/${peer.symbol}`)}
                  className="border-b dark:border-dark-border/30 border-gray-100 last:border-0 dark:hover:bg-dark-border/30 hover:bg-gray-50 cursor-pointer transition-colors group"
                >
                  <td className="py-3 px-2">
                    <p className="dark:text-dark-text text-gray-900 text-sm font-medium group-hover:text-blue-400 transition-colors">
                      {peer.name || peer.symbol}
                    </p>
                    <p className="dark:text-dark-muted text-gray-500 text-xs">
                      {peer.symbol?.replace('.NS', '')}
                    </p>
                  </td>
                  <td className="text-right dark:text-dark-text text-gray-900 text-sm font-medium py-3 px-2">
                    {formatPrice(peer.current_price)}
                  </td>
                  <td
                    className={`text-right text-sm font-medium py-3 px-2 ${
                      changeNum !== null
                        ? isPositive
                          ? 'text-profit'
                          : 'text-loss'
                        : 'dark:text-dark-muted text-gray-500'
                    }`}
                  >
                    {changeNum !== null ? `${isPositive ? '+' : ''}${peer.change_pct}%` : 'N/A'}
                  </td>
                  <td className="text-right dark:text-dark-text text-gray-900 text-sm py-3 px-2">
                    {peer.market_cap || 'N/A'}
                  </td>
                  <td className="text-right dark:text-dark-text text-gray-900 text-sm py-3 px-2">
                    {formatMetric(peer.pe_ratio)}
                  </td>
                  <td className={`text-right text-sm font-medium py-3 px-2 ${metricColor(peer.roce_pct, 15, 10)}`}>
                    {formatMetric(peer.roce_pct, '%')}
                  </td>
                  <td className={`text-right text-sm font-medium py-3 px-2 ${metricColor(peer.opm_pct, 20, 10)}`}>
                    {formatMetric(peer.opm_pct, '%')}
                  </td>
                </tr>
              );
            })}

            {industryMedian && Object.keys(industryMedian).length > 0 && (
              <tr className="dark:bg-blue-500/5 bg-blue-50 border-t-2 dark:border-blue-500/20 border-blue-200">
                <td className="py-3 px-2">
                  <p className="text-blue-400 text-sm font-bold">Industry Median</p>
                </td>
                <td className="text-right text-blue-400 text-sm font-medium py-3 px-2">
                  {safeNum(industryMedian.current_price) !== null ? formatPrice(industryMedian.current_price) : '—'}
                </td>
                <td className="text-right text-blue-400 text-sm font-medium py-3 px-2">
                  {safeNum(industryMedian.change_pct) !== null ? `${industryMedian.change_pct}%` : '—'}
                </td>
                <td className="text-right text-blue-400 text-sm font-medium py-3 px-2">—</td>
                <td className="text-right text-blue-400 text-sm font-medium py-3 px-2">
                  {safeNum(industryMedian.pe_ratio) !== null ? industryMedian.pe_ratio : '—'}
                </td>
                <td className="text-right text-blue-400 text-sm font-medium py-3 px-2">
                  {safeNum(industryMedian.roce_pct) !== null ? `${industryMedian.roce_pct}%` : '—'}
                </td>
                <td className="text-right text-blue-400 text-sm font-medium py-3 px-2">
                  {safeNum(industryMedian.opm_pct) !== null ? `${industryMedian.opm_pct}%` : '—'}
                </td>
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