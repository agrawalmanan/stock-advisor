import React, { useState } from 'react';
import { X, Search, Plus, Loader } from 'lucide-react';
import { searchStocks } from '../../utils/api';

const AddStockModal = ({ isOpen, onClose, onAdd }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [selected, setSelected] = useState(null);
  const [qty, setQty] = useState('');
  const [buyPrice, setBuyPrice] = useState('');
  const [buyDate, setBuyDate] = useState('');
  const [holdingType, setHoldingType] = useState('long');
  const [targetPrice, setTargetPrice] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSearch = async (value) => {
    setQuery(value);
    if (value.length < 1) {
      setResults([]);
      return;
    }

    setSearching(true);
    try {
      const data = await searchStocks(value);
      setResults(data.results || []);
    } catch (err) {
      console.error('Search error:', err);
    }
    setSearching(false);
  };

  const handleSelect = (stock) => {
    setSelected(stock);
    setQuery(stock.name);
    setResults([]);
  };

  const handleAdd = () => {
    if (!selected) {
      setError('Please select a stock');
      return;
    }
    if (!qty || Number(qty) <= 0) {
      setError('Enter valid quantity');
      return;
    }
    if (!buyPrice || Number(buyPrice) <= 0) {
      setError('Enter valid buy price');
      return;
    }

    setLoading(true);
    setError('');

    const holding = {
      symbol: selected.symbol,
      name: selected.name,
      sector: selected.sector,
      qty: Number(qty),
      buyPrice: Number(buyPrice),
      buyDate: buyDate || new Date().toISOString().split('T')[0],
      holdingType: holdingType,
      targetPrice: targetPrice ? Number(targetPrice) : null,
      addedAt: new Date().toISOString(),
    };

    onAdd(holding);
    setLoading(false);

    // Reset
    setSelected(null);
    setQuery('');
    setQty('');
    setBuyPrice('');
    setBuyDate('');
    setTargetPrice('');
    setHoldingType('long');
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="dark:bg-dark-card bg-white rounded-2xl border dark:border-dark-border border-gray-200 w-full max-w-md p-6 relative">
        {/* Close */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 dark:text-dark-muted text-gray-400 hover:text-gray-600 dark:hover:text-dark-text"
        >
          <X className="w-5 h-5" />
        </button>

        <h2 className="text-lg font-bold dark:text-dark-text text-gray-900 mb-4">Add Stock to Portfolio</h2>

        <div className="space-y-4">
          {/* Stock Search */}
          <div className="relative">
            <label className="dark:text-dark-muted text-gray-500 text-xs mb-1 block">Stock</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 dark:text-dark-muted text-gray-400" />
              <input
                type="text"
                value={query}
                onChange={(e) => handleSearch(e.target.value)}
                placeholder="Search stock..."
                className="w-full pl-10 pr-4 py-2.5 dark:bg-dark-bg dark:border-dark-border dark:text-dark-text bg-gray-50 border-gray-300 text-gray-900 border rounded-xl focus:outline-none focus:border-blue-500/50 text-sm"
              />
            </div>

            {/* Search Results */}
            {results.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-1 dark:bg-dark-card bg-white border dark:border-dark-border border-gray-200 rounded-xl shadow-xl z-10 max-h-40 overflow-y-auto">
                {results.map((stock) => (
                  <button
                    key={stock.symbol}
                    onClick={() => handleSelect(stock)}
                    className="w-full px-4 py-2 text-left dark:hover:bg-dark-border/50 hover:bg-gray-50 text-sm"
                  >
                    <span className="dark:text-dark-text text-gray-900 font-medium">{stock.name}</span>
                    <span className="dark:text-dark-muted text-gray-500 text-xs ml-2">
                      {stock.symbol.replace('.NS', '')}
                    </span>
                  </button>
                ))}
              </div>
            )}

            {selected && (
              <p className="text-profit text-xs mt-1">✓ Selected: {selected.name}</p>
            )}
          </div>

          {/* Qty + Buy Price */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="dark:text-dark-muted text-gray-500 text-xs mb-1 block">Quantity</label>
              <input
                type="number"
                value={qty}
                onChange={(e) => setQty(e.target.value)}
                placeholder="e.g. 10"
                className="w-full px-3 py-2.5 dark:bg-dark-bg dark:border-dark-border dark:text-dark-text bg-gray-50 border-gray-300 text-gray-900 border rounded-xl focus:outline-none focus:border-blue-500/50 text-sm"
              />
            </div>
            <div>
              <label className="dark:text-dark-muted text-gray-500 text-xs mb-1 block">Buy Price (₹)</label>
              <input
                type="number"
                value={buyPrice}
                onChange={(e) => setBuyPrice(e.target.value)}
                placeholder="e.g. 1350"
                className="w-full px-3 py-2.5 dark:bg-dark-bg dark:border-dark-border dark:text-dark-text bg-gray-50 border-gray-300 text-gray-900 border rounded-xl focus:outline-none focus:border-blue-500/50 text-sm"
              />
            </div>
          </div>

          {/* Buy Date */}
          <div>
            <label className="dark:text-dark-muted text-gray-500 text-xs mb-1 block">Buy Date</label>
            <input
              type="date"
              value={buyDate}
              onChange={(e) => setBuyDate(e.target.value)}
              className="w-full px-3 py-2.5 dark:bg-dark-bg dark:border-dark-border dark:text-dark-text bg-gray-50 border-gray-300 text-gray-900 border rounded-xl focus:outline-none focus:border-blue-500/50 text-sm"
            />
          </div>

          {/* Holding Type */}
          <div>
            <label className="dark:text-dark-muted text-gray-500 text-xs mb-1 block">Holding Type</label>
            <div className="flex gap-2">
              <button
                onClick={() => setHoldingType('long')}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                  holdingType === 'long'
                    ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                    : 'dark:bg-dark-border/30 bg-gray-100 dark:text-dark-muted text-gray-500 border border-transparent'
                }`}
              >
                📈 Long Term
              </button>
              <button
                onClick={() => setHoldingType('short')}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                  holdingType === 'short'
                    ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30'
                    : 'dark:bg-dark-border/30 bg-gray-100 dark:text-dark-muted text-gray-500 border border-transparent'
                }`}
              >
                ⚡ Short Term
              </button>
            </div>
          </div>

          {/* Target Price (Optional) */}
          <div>
            <label className="dark:text-dark-muted text-gray-500 text-xs mb-1 block">
              Target Price ₹ (Optional — sets alert)
            </label>
            <input
              type="number"
              value={targetPrice}
              onChange={(e) => setTargetPrice(e.target.value)}
              placeholder="e.g. 1500"
              className="w-full px-3 py-2.5 dark:bg-dark-bg dark:border-dark-border dark:text-dark-text bg-gray-50 border-gray-300 text-gray-900 border rounded-xl focus:outline-none focus:border-blue-500/50 text-sm"
            />
          </div>

          {/* Error */}
          {error && <p className="text-loss text-xs">{error}</p>}

          {/* Add Button */}
          <button
            onClick={handleAdd}
            disabled={loading}
            className="w-full py-3 bg-blue-500 hover:bg-blue-600 text-white font-semibold rounded-xl transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? (
              <Loader className="w-4 h-4 animate-spin" />
            ) : (
              <Plus className="w-4 h-4" />
            )}
            Add to Portfolio
          </button>
        </div>
      </div>
    </div>
  );
};

export default AddStockModal;