import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Briefcase, ArrowLeft, Plus, Loader } from 'lucide-react';
import { collection, getDocs, addDoc, deleteDoc, doc } from 'firebase/firestore';
import { db } from '../firebase';
import { useAuth } from '../context/AuthContext';
import { getStockData, createAlert } from '../utils/api';
import PortfolioSummary from '../components/portfolio/PortfolioSummary';
import PortfolioFilter from '../components/portfolio/PortfolioFilter';
import PortfolioTable from '../components/portfolio/PortfolioTable';
import AddStockModal from '../components/portfolio/AddStockModal';

const PortfolioPage = () => {
  const navigate = useNavigate();
  const { user, isLoggedIn } = useAuth();
  const [holdings, setHoldings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [showAddModal, setShowAddModal] = useState(false);

  // Fetch portfolio from Firestore
  useEffect(() => {
    if (!isLoggedIn || !user) {
      setLoading(false);
      return;
    }

    const fetchPortfolio = async () => {
      try {
        const portfolioRef = collection(db, 'users', user.uid, 'portfolio');
        const snapshot = await getDocs(portfolioRef);
        const rawHoldings = snapshot.docs.map((d) => ({
          id: d.id,
          ...d.data(),
        }));

        // Fetch live prices for each holding
        const withPrices = await Promise.all(
          rawHoldings.map(async (h) => {
            try {
              const data = await getStockData(h.symbol);
              return { ...h, livePrice: data.current_price };
            } catch (err) {
              return { ...h, livePrice: null };
            }
          })
        );

        setHoldings(withPrices);
      } catch (err) {
        console.error('Portfolio fetch error:', err);
      }
      setLoading(false);
    };

    fetchPortfolio();
  }, [isLoggedIn, user]);

  // Add stock to portfolio
  const handleAddStock = async (holding) => {
    try {
      const portfolioRef = collection(db, 'users', user.uid, 'portfolio');
      const docRef = await addDoc(portfolioRef, holding);

      // Fetch live price
      let livePrice = null;
      try {
        const data = await getStockData(holding.symbol);
        livePrice = data.current_price;
      } catch (err) {
        console.error('Live price error:', err);
      }

      // If target price set, create alert
      if (holding.targetPrice) {
        try {
          await createAlert({
            symbol: holding.symbol,
            stock_name: holding.name,
            target_price: holding.targetPrice,
            alert_type: 'above',
            user_id: user.uid,
          });
        } catch (err) {
          console.error('Alert creation error:', err);
        }
      }

      setHoldings((prev) => [
        ...prev,
        { ...holding, id: docRef.id, livePrice },
      ]);
    } catch (err) {
      console.error('Add stock error:', err);
      alert('Failed to add stock');
    }
  };

  // Delete stock from portfolio
  const handleDeleteStock = async (index) => {
    const holding = holdings[index];
    if (!holding) return;

    if (!window.confirm(`Remove ${holding.name} from portfolio?`)) return;

    try {
      await deleteDoc(doc(db, 'users', user.uid, 'portfolio', holding.id));
      setHoldings((prev) => prev.filter((_, i) => i !== index));
    } catch (err) {
      console.error('Delete error:', err);
      alert('Failed to remove stock');
    }
  };

  // Filter holdings
  const filteredHoldings = holdings.filter((h) => {
    if (filter === 'all') return true;
    if (filter === 'long') return h.holdingType === 'long';
    if (filter === 'short') return h.holdingType === 'short';
    return true;
  });

  // Not logged in
  if (!isLoggedIn) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center">
        <Briefcase className="w-16 h-16 dark:text-dark-border text-gray-300 mx-auto mb-4" />
        <h2 className="dark:text-dark-text text-gray-900 text-xl font-semibold mb-2">
          Login to view your Portfolio
        </h2>
        <p className="dark:text-dark-muted text-gray-500 text-sm">
          Track your investments and P&L here
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/')}
            className="p-2 rounded-lg dark:hover:bg-dark-border/50 hover:bg-gray-100 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 dark:text-dark-muted text-gray-500" />
          </button>
          <div className="flex items-center gap-2">
            <Briefcase className="w-5 h-5 text-green-400" />
            <h2 className="dark:text-dark-text text-gray-900 text-xl font-bold">My Portfolio</h2>
          </div>
          <span className="dark:text-dark-muted text-gray-500 text-sm">
            ({holdings.length} holdings)
          </span>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white font-semibold rounded-xl transition-colors text-sm"
        >
          <Plus className="w-4 h-4" />
          Add Stock
        </button>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-20">
          <Loader className="w-8 h-8 dark:text-dark-muted text-gray-400 animate-spin" />
        </div>
      )}

      {/* Empty State */}
      {!loading && holdings.length === 0 && (
        <div className="text-center py-20">
          <Briefcase className="w-16 h-16 dark:text-dark-border text-gray-300 mx-auto mb-4" />
          <h3 className="dark:text-dark-text text-gray-900 text-lg font-semibold mb-2">
            No stocks in portfolio
          </h3>
          <p className="dark:text-dark-muted text-gray-500 text-sm mb-4">
            Add stocks to track your investments and P&L
          </p>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white font-semibold rounded-xl transition-colors text-sm"
          >
            Add Your First Stock
          </button>
        </div>
      )}

      {/* Portfolio Content */}
      {!loading && holdings.length > 0 && (
        <>
          {/* Summary Cards */}
          <PortfolioSummary holdings={filteredHoldings} />

          {/* Filter Bar */}
          <div className="flex items-center justify-between mb-4">
            <PortfolioFilter activeFilter={filter} onFilterChange={setFilter} />
            <span className="dark:text-dark-muted text-gray-500 text-sm">
              Showing {filteredHoldings.length} of {holdings.length}
            </span>
          </div>

          {/* Holdings Table */}
          <PortfolioTable
            holdings={filteredHoldings}
            onDelete={handleDeleteStock}
          />
        </>
      )}

      {/* Add Stock Modal */}
      <AddStockModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onAdd={handleAddStock}
      />
    </div>
  );
};

export default PortfolioPage;