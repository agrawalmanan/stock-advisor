import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { Activity } from 'lucide-react';
import { AuthProvider, useAuth } from './context/AuthContext';
import ThemeToggle from './components/ui/ThemeToggle';
import UserMenu from './components/auth/UserMenu';
import LoginModal from './components/auth/LoginModal';
import RegisterModal from './components/auth/RegisterModal';
import SearchBar from './components/search/SearchBar';
import HomePage from './pages/HomePage';
import StockPage from './pages/StockPage';
import WatchlistPage from './pages/WatchlistPage';
import PortfolioPage from './pages/PortfolioPage';

// Header component with nav
const Header = () => {
  const navigate = useNavigate();
  const { isLoggedIn } = useAuth();
  const [showLogin, setShowLogin] = useState(false);
  const [showRegister, setShowRegister] = useState(false);

  const handleStockSelect = (symbol) => {
    navigate(`/stock/${symbol}`);
  };

  return (
    <>
      <header className="border-b dark:border-dark-border border-gray-200 dark:bg-dark-card/50 bg-white/80 backdrop-blur-sm sticky top-0 z-40 transition-colors">
        <div className="max-w-6xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-3 hover:opacity-80 transition-opacity"
            >
              <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <Activity className="w-5 h-5 text-blue-400" />
              </div>
              <h1 className="text-xl font-bold dark:text-dark-text text-gray-900">
                Stock<span className="text-blue-400">Advisor</span>
              </h1>
              <span className="dark:text-dark-muted text-gray-500 text-xs dark:bg-dark-border/50 bg-gray-200 px-2 py-0.5 rounded hidden md:block">
                NSE India
              </span>
            </button>

            {/* Search Bar (compact in header) */}
            <div className="flex-1 max-w-md mx-4 hidden md:block">
              <SearchBar onStockSelect={handleStockSelect} />
            </div>

            {/* Right side */}
            <div className="flex items-center gap-2">
              <ThemeToggle />
              {isLoggedIn ? (
                <UserMenu />
              ) : (
                <button
                  onClick={() => setShowLogin(true)}
                  className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white text-sm font-semibold rounded-xl transition-colors"
                >
                  Login
                </button>
              )}
            </div>
          </div>

          {/* Mobile search */}
          <div className="mt-3 md:hidden">
            <SearchBar onStockSelect={handleStockSelect} />
          </div>
        </div>
      </header>

      {/* Auth Modals */}
      <LoginModal
        isOpen={showLogin}
        onClose={() => setShowLogin(false)}
        onSwitchToRegister={() => { setShowLogin(false); setShowRegister(true); }}
      />
      <RegisterModal
        isOpen={showRegister}
        onClose={() => setShowRegister(false)}
        onSwitchToLogin={() => { setShowRegister(false); setShowLogin(true); }}
      />
    </>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen dark:bg-dark-bg bg-light-bg transition-colors duration-300">
          <Header />
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/stock/:symbol" element={<StockPage />} />
            <Route path="/watchlist" element={<WatchlistPage />} />
            <Route path="/portfolio" element={<PortfolioPage />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;