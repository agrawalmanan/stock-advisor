import React, { useState } from 'react';
import { Activity, Heart, Briefcase, TrendingUp, Search } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import SearchBar from '../components/search/SearchBar';

const HomePage = () => {
  const navigate = useNavigate();
  const { isLoggedIn } = useAuth();

  const handleStockSelect = (symbol) => {
    navigate(`/stock/${symbol}`);
  };

  // Recent searches from localStorage
  const getRecentSearches = () => {
    try {
      return JSON.parse(localStorage.getItem('recentSearches') || '[]');
    } catch {
      return [];
    }
  };

  const recentSearches = getRecentSearches();

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      {/* Hero Section */}
      <div className="text-center mb-10">
        <div className="w-16 h-16 bg-blue-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <Activity className="w-8 h-8 text-blue-400" />
        </div>
        <h1 className="text-3xl md:text-4xl font-bold dark:text-dark-text text-gray-900 mb-3">
          Stock<span className="text-blue-400">Advisor</span>
        </h1>
        <p className="dark:text-dark-muted text-gray-500 text-lg mb-8">
          Live stock data, technical analysis & AI-powered advice for NSE India
        </p>

        {/* Search Bar */}
        <SearchBar onStockSelect={handleStockSelect} />
      </div>

      {/* Recent Searches */}
      {recentSearches.length > 0 && (
        <div className="mb-8">
          <p className="dark:text-dark-muted text-gray-500 text-sm mb-3 text-center">Recent Searches</p>
          <div className="flex flex-wrap justify-center gap-2">
            {recentSearches.map((stock, i) => (
              <button
                key={i}
                onClick={() => handleStockSelect(stock.symbol)}
                className="flex items-center gap-2 px-4 py-2 dark:bg-dark-card bg-white border dark:border-dark-border border-gray-200 rounded-xl dark:hover:border-blue-500/30 hover:border-blue-500/30 transition-colors"
              >
                <TrendingUp className="w-3 h-3 text-blue-400" />
                <span className="dark:text-dark-text text-gray-900 text-sm font-medium">
                  {stock.name?.split(' ')[0] || stock.symbol.replace('.NS', '')}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Quick Access Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-xl mx-auto">
        <button
          onClick={() => {
            if (isLoggedIn) navigate('/watchlist');
            else alert('Please login to view watchlist');
          }}
          className="flex items-center gap-4 p-5 dark:bg-dark-card bg-white border dark:border-dark-border border-gray-200 rounded-xl dark:hover:border-red-500/30 hover:border-red-500/30 transition-colors text-left group"
        >
          <div className="w-10 h-10 bg-red-500/20 rounded-xl flex items-center justify-center">
            <Heart className="w-5 h-5 text-red-400" />
          </div>
          <div>
            <p className="dark:text-dark-text text-gray-900 font-semibold group-hover:text-red-400 transition-colors">
              My Watchlist
            </p>
            <p className="dark:text-dark-muted text-gray-500 text-sm">Saved stocks</p>
          </div>
        </button>

        <button
          onClick={() => {
            if (isLoggedIn) navigate('/portfolio');
            else alert('Please login to view portfolio');
          }}
          className="flex items-center gap-4 p-5 dark:bg-dark-card bg-white border dark:border-dark-border border-gray-200 rounded-xl dark:hover:border-green-500/30 hover:border-green-500/30 transition-colors text-left group"
        >
          <div className="w-10 h-10 bg-green-500/20 rounded-xl flex items-center justify-center">
            <Briefcase className="w-5 h-5 text-green-400" />
          </div>
          <div>
            <p className="dark:text-dark-text text-gray-900 font-semibold group-hover:text-green-400 transition-colors">
              My Portfolio
            </p>
            <p className="dark:text-dark-muted text-gray-500 text-sm">Track investments</p>
          </div>
        </button>
      </div>

      {/* Features Grid */}
      <div className="mt-12 grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { icon: '📊', title: 'Live Data', desc: '2136 NSE stocks' },
          { icon: '📈', title: 'Charts', desc: 'Candlestick & line' },
          { icon: '🤖', title: 'AI Advice', desc: 'Buy/Sell/Hold' },
          { icon: '📰', title: 'News', desc: 'Latest updates' },
        ].map((feature, i) => (
          <div
            key={i}
            className="text-center p-4 dark:bg-dark-card bg-white border dark:border-dark-border border-gray-200 rounded-xl"
          >
            <span className="text-2xl mb-2 block">{feature.icon}</span>
            <p className="dark:text-dark-text text-gray-900 font-semibold text-sm">{feature.title}</p>
            <p className="dark:text-dark-muted text-gray-500 text-xs">{feature.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default HomePage;