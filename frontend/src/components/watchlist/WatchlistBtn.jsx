import React, { useState, useEffect } from 'react';
import { Heart } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { doc, setDoc, deleteDoc, getDoc } from 'firebase/firestore';
import { db } from '../../firebase';

const WatchlistBtn = ({ symbol, stockName, sector }) => {
  const { user, isLoggedIn } = useAuth();
  const [isWatchlisted, setIsWatchlisted] = useState(false);
  const [loading, setLoading] = useState(false);

  // Check if stock is in watchlist
  useEffect(() => {
    if (!isLoggedIn || !user) return;

    const checkWatchlist = async () => {
      try {
        const cleanSymbol = symbol.replace('.NS', '').replace('.', '_');
        const docRef = doc(db, 'users', user.uid, 'watchlist', cleanSymbol);
        const docSnap = await getDoc(docRef);
        setIsWatchlisted(docSnap.exists());
      } catch (err) {
        console.error('Watchlist check error:', err);
      }
    };

    checkWatchlist();
  }, [isLoggedIn, user, symbol]);

  const toggleWatchlist = async () => {
    if (!isLoggedIn) {
      alert('Please login to add stocks to your watchlist');
      return;
    }

    setLoading(true);
    const cleanSymbol = symbol.replace('.NS', '').replace('.', '_');
    const docRef = doc(db, 'users', user.uid, 'watchlist', cleanSymbol);

    try {
      if (isWatchlisted) {
        await deleteDoc(docRef);
        setIsWatchlisted(false);
      } else {
        await setDoc(docRef, {
          symbol: symbol,
          name: stockName,
          sector: sector || 'Unknown',
          addedAt: new Date().toISOString(),
        });
        setIsWatchlisted(true);
      }
    } catch (err) {
      console.error('Watchlist toggle error:', err);
      alert('Failed to update watchlist');
    }
    setLoading(false);
  };

  return (
    <button
      onClick={toggleWatchlist}
      disabled={loading}
      className={`flex items-center gap-2 px-4 py-2 rounded-xl border transition-all ${
        isWatchlisted
          ? 'bg-red-500/20 border-red-500/30 text-red-400 hover:bg-red-500/30'
          : 'dark:bg-dark-border/30 bg-gray-100 dark:border-dark-border border-gray-200 dark:text-dark-muted text-gray-500 dark:hover:border-red-500/30 hover:border-red-500/30 hover:text-red-400'
      } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
      title={isWatchlisted ? 'Remove from Watchlist' : 'Add to Watchlist'}
    >
      <Heart
        className={`w-4 h-4 ${isWatchlisted ? 'fill-red-400' : ''}`}
      />
      <span className="text-sm font-medium">
        {loading ? '...' : isWatchlisted ? 'Watchlisted' : 'Watchlist'}
      </span>
    </button>
  );
};

export default WatchlistBtn;