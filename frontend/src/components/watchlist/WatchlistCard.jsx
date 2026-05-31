import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Trash2, TrendingUp, TrendingDown, Loader } from 'lucide-react';
import { doc, deleteDoc } from 'firebase/firestore';
import { db } from '../../firebase';
import { useAuth } from '../../context/AuthContext';
import { getStockData } from '../../utils/api';
import { formatPrice } from '../../utils/formatters';

const WatchlistCard = ({ stock, onRemove }) => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [liveData, setLiveData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [removing, setRemoving] = useState(false);

  // Fetch live price
  useEffect(() => {
    const fetchLive = async () => {
      try {
        const data = await getStockData(stock.symbol);
        setLiveData(data);
      } catch (err) {
        console.error('Live data error:', err);
      }
      setLoading(false);
    };
    fetchLive();
  }, [stock.symbol]);

  const handleRemove = async (e) => {
    e.stopPropagation();
    setRemoving(true);
    try {
      const cleanSymbol = stock.symbol.replace('.NS', '').replace('.', '_');
      await deleteDoc(doc(db, 'users', user.uid, 'watchlist', cleanSymbol));
      onRemove(stock.symbol);
    } catch (err) {
      console.error('Remove error:', err);
      alert('Failed to remove');
    }
    setRemoving(false);
  };

  const isPositive = liveData && liveData.change_pct !== 'N/A' && Number(liveData.change_pct) >= 0;

  return (
    <div
      onClick={() => navigate(`/stock/${stock.symbol}`)}
      className="dark:bg-dark-card bg-white rounded-xl p-4 border dark:border-dark-border border-gray-200 dark:hover:border-blue-500/30 hover:border-blue-500/30 transition-all cursor-pointer group"
    >
      <div className="flex items-center justify-between">
        {/* Left — Stock Info */}
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
            loading ? 'dark:bg-dark-border/50 bg-gray-100' :
            isPositive ? 'bg-green-500/20' : 'bg-red-500/20'
          }`}>
            {loading ? (
              <Loader className="w-4 h-4 dark:text-dark-muted text-gray-400 animate-spin" />
            ) : isPositive ? (
              <TrendingUp className="w-4 h-4 text-profit" />
            ) : (
              <TrendingDown className="w-4 h-4 text-loss" />
            )}
          </div>
          <div>
            <p className="dark:text-dark-text text-gray-900 font-semibold text-sm group-hover:text-blue-400 transition-colors">
              {stock.name}
            </p>
            <p className="dark:text-dark-muted text-gray-500 text-xs">
              {stock.symbol.replace('.NS', '')} • {stock.sector}
            </p>
          </div>
        </div>

        {/* Right — Price + Remove */}
        <div className="flex items-center gap-4">
          {loading ? (
            <div className="text-right">
              <div className="skeleton h-5 w-20 mb-1" />
              <div className="skeleton h-4 w-16" />
            </div>
          ) : liveData ? (
            <div className="text-right">
              <p className="dark:text-dark-text text-gray-900 font-bold text-sm">
                {formatPrice(liveData.current_price)}
              </p>
              <p className={`text-xs font-medium ${isPositive ? 'text-profit' : 'text-loss'}`}>
                {isPositive ? '+' : ''}{liveData.change_pct}%
              </p>
            </div>
          ) : (
            <p className="dark:text-dark-muted text-gray-500 text-xs">No data</p>
          )}

          <button
            onClick={handleRemove}
            disabled={removing}
            className="p-2 rounded-lg dark:hover:bg-red-500/20 hover:bg-red-50 transition-colors opacity-0 group-hover:opacity-100"
            title="Remove from Watchlist"
          >
            <Trash2 className={`w-4 h-4 ${removing ? 'text-gray-400' : 'text-loss'}`} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default WatchlistCard;