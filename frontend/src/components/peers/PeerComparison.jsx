import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, Loader, ArrowUpDown } from 'lucide-react';
import { formatPrice } from '../../utils/formatters';
import { getPeers } from '../../utils/api';

const PeerComparison = ({ symbol, sector }) => {
  console.log('PeerComparison mounted with:', symbol, sector);
  
  const navigate = useNavigate();
  const [peers, setPeers] = useState([]);
  const [industryMedian, setIndustryMedian] = useState({});
  const [loading, setLoading] = useState(true);
  const [sortKey, setSortKey] = useState(null);
  const [sortAsc, setSortAsc] = useState(true);

  useEffect(() => {
      
      const fetchPeers = async () => {
        setLoading(true);
        setError(false);
        try {
          const data = await getPeers(symbol);
          const validPeers = (data.peers || []).filter(
            (p) => p && p.current_price && p.current_price !== 'N/A'
          );
          setPeers(validPeers);
          setIndustryMedian(data.industry_median || {});
        } catch (err) {
          setPeers([]);
          setError(true);
        }
        setLoading(false);
      };

      fetchPeers();
    }, [symbol]);
  // Sorting
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
    let aVal = a[sortKey];
    let bVal = b[sortKey];
    if (aVal === 'N/A') aVal = -Infinity;
    if (bVal === 'N/A') bVal = -Infinity;
    aVal = Number(aVal) || 0;
    bVal = Number(bVal) || 0;
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

  if (peers.length === 0) return null;

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
            {/* Peer Rows */}
            {sortedPeers.map((peer, i) => {
              const isPositive = peer.change_pct !== 'N/A' && Number(peer.change_pct) >= 0;
              return (
                <tr
                  key={i}
                  onClick={() => navigate(`/stock/${peer.symbol}`)}
                  className="border-b dark:border-dark-border/30 border-gray-100 last:border-0 dark:hover:bg-dark-border/30 hover:bg-gray-50 cursor-pointer transition-colors group"
                >
                  <td className="py-3 px-2">
                    <p className="dark:text-dark-text text-gray-900 text-sm font-medium group-hover:text-blue-400 transition-colors">
                      {peer.name}
                    </p>
                    <p className="dark:text-dark-muted text-gray-500 text-xs">
                      {peer.symbol.replace('.NS', '')}
                    </p>
                  </td>
                  <td className="text-right dark:text-dark-text text-gray-900 text-sm font-medium py-3 px-2">
                    {formatPrice(peer.current_price)}
                  </td>
                  <td className={`text-right text-sm font-medium py-3 px-2 ${isPositive ? 'text-profit' : 'text-loss'}`}>
                    {peer.change_pct !== 'N/A' ? `${isPositive ? '+' : ''}${peer.change_pct}%` : 'N/A'}
                  </td>
                  <td className="text-right dark:text-dark-text text-gray-900 text-sm py-3 px-2">
                    {peer.market_cap || 'N/A'}
                  </td>
                  <td className="text-right dark:text-dark-text text-gray-900 text-sm py-3 px-2">
                    {peer.pe_ratio !== 'N/A' ? peer.pe_ratio : 'N/A'}
                  </td>
                  <td className="text-right text-sm font-medium py-3 px-2">
                    <span className={
                      peer.roce_pct !== 'N/A' && Number(peer.roce_pct) >= 15
                        ? 'text-profit'
                        : peer.roce_pct !== 'N/A' && Number(peer.roce_pct) >= 10
                          ? 'text-hold'
                          : peer.roce_pct !== 'N/A'
                            ? 'text-loss'
                            : 'dark:text-dark-muted text-gray-500'
                    }>
                      {peer.roce_pct !== 'N/A' ? `${peer.roce_pct}%` : 'N/A'}
                    </span>
                  </td>
                  <td className="text-right text-sm font-medium py-3 px-2">
                    <span className={
                      peer.opm_pct !== 'N/A' && Number(peer.opm_pct) >= 20
                        ? 'text-profit'
                        : peer.opm_pct !== 'N/A' && Number(peer.opm_pct) >= 10
                          ? 'text-hold'
                          : peer.opm_pct !== 'N/A'
                            ? 'text-loss'
                            : 'dark:text-dark-muted text-gray-500'
                    }>
                      {peer.opm_pct !== 'N/A' ? `${peer.opm_pct}%` : 'N/A'}
                    </span>
                  </td>
                </tr>
              );
            })}

            {/* Industry Median Row */}
            {industryMedian && Object.keys(industryMedian).length > 0 && (
              <tr className="dark:bg-blue-500/5 bg-blue-50 border-t-2 dark:border-blue-500/20 border-blue-200">
                <td className="py-3 px-2">
                  <p className="text-blue-400 text-sm font-bold">Industry Median</p>
                </td>
                <td className="text-right text-blue-400 text-sm font-medium py-3 px-2">
                  {industryMedian.current_price !== 'N/A' ? formatPrice(industryMedian.current_price) : 'N/A'}
                </td>
                <td className="text-right text-blue-400 text-sm font-medium py-3 px-2">
                  {industryMedian.change_pct !== 'N/A' ? `${industryMedian.change_pct}%` : 'N/A'}
                </td>
                <td className="text-right text-blue-400 text-sm font-medium py-3 px-2">
                  —
                </td>
                <td className="text-right text-blue-400 text-sm font-medium py-3 px-2">
                  {industryMedian.pe_ratio !== 'N/A' ? industryMedian.pe_ratio : 'N/A'}
                </td>
                <td className="text-right text-blue-400 text-sm font-medium py-3 px-2">
                  {industryMedian.roce_pct !== 'N/A' ? `${industryMedian.roce_pct}%` : 'N/A'}
                </td>
                <td className="text-right text-blue-400 text-sm font-medium py-3 px-2">
                  {industryMedian.opm_pct !== 'N/A' ? `${industryMedian.opm_pct}%` : 'N/A'}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Legend */}
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