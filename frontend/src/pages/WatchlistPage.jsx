import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Heart, ArrowLeft, Loader } from 'lucide-react';
import { collection, getDocs } from 'firebase/firestore';
import { db } from '../firebase';
import { useAuth } from '../context/AuthContext';
import WatchlistCard from '../components/watchlist/WatchlistCard';

const WatchlistPage = () => {
  const navigate = useNavigate();
  const { user, isLoggedIn } = useAuth();
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch watchlist from Firestore
  useEffect(() => {
    if (!isLoggedIn || !user) {
      setLoading(false);
      return;
    }

    const fetchWatchlist = async () => {
      try {
        const watchlistRef = collection(db, 'users', user.uid, 'watchlist');
        const snapshot = await getDocs(watchlistRef);
        const watchlistStocks = snapshot.docs.map((doc) => ({
          id: doc.id,
          ...doc.data(),
        }));
        setStocks(watchlistStocks);
      } catch (err) {
        console.error('Watchlist fetch error:', err);
      }
      setLoading(false);
    };

    fetchWatchlist();
  }, [isLoggedIn, user]);

  const handleRemove = (symbol) => {
    setStocks((prev) => prev.filter((s) => s.symbol !== symbol));
  };

  // Not logged in
  if (!isLoggedIn) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center">
        <Heart className="w-16 h-16 dark:text-dark-border text-gray-300 mx-auto mb-4" />
        <h2 className="dark:text-dark-text text-gray-900 text-xl font-semibold mb-2">
          Login to view your Watchlist
        </h2>
        <p className="dark:text-dark-muted text-gray-500 text-sm">
          Save stocks to your watchlist and track them here
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <button
          onClick={() => navigate('/')}
          className="p-2 rounded-lg dark:hover:bg-dark-border/50 hover:bg-gray-100 transition-colors"
        >
          <ArrowLeft className="w-5 h-5 dark:text-dark-muted text-gray-500" />
        </button>
        <div className="flex items-center gap-2">
          <Heart className="w-5 h-5 text-red-400" />
          <h2 className="dark:text-dark-text text-gray-900 text-xl font-bold">My Watchlist</h2>
        </div>
        <span className="dark:text-dark-muted text-gray-500 text-sm">
          ({stocks.length} stocks)
        </span>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-20">
          <Loader className="w-8 h-8 dark:text-dark-muted text-gray-400 animate-spin" />
        </div>
      )}

      {/* Empty State */}
      {!loading && stocks.length === 0 && (
        <div className="text-center py-20">
          <Heart className="w-16 h-16 dark:text-dark-border text-gray-300 mx-auto mb-4" />
          <h3 className="dark:text-dark-text text-gray-900 text-lg font-semibold mb-2">
            Your watchlist is empty
          </h3>
          <p className="dark:text-dark-muted text-gray-500 text-sm mb-4">
            Search for stocks and click the ❤️ button to add them here
          </p>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white font-semibold rounded-xl transition-colors text-sm"
          >
            Search Stocks
          </button>
        </div>
      )}

      {/* Watchlist Cards */}
      {!loading && stocks.length > 0 && (
        <div className="space-y-3">
          {stocks.map((stock) => (
            <WatchlistCard
              key={stock.symbol}
              stock={stock}
              onRemove={handleRemove}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default WatchlistPage;