import React, { useState, useRef, useEffect } from 'react';
import { Search, X } from 'lucide-react';
import AutocompleteDropdown from './AutocompleteDropdown';
import { searchStocks } from '../../utils/api';

const SearchBar = ({ onStockSelect }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const inputRef = useRef(null);
  const wrapperRef = useRef(null);
  const debounceRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearch = async (value) => {
    setQuery(value);

    if (value.length < 1) {
      setResults([]);
      setIsOpen(false);
      return;
    }

    if (debounceRef.current) clearTimeout(debounceRef.current);

    debounceRef.current = setTimeout(async () => {
      setIsLoading(true);
      try {
        const data = await searchStocks(value);
        setResults(data.results || []);
        setIsOpen(true);
      } catch (err) {
        console.error('Search error:', err);
        setResults([]);
      }
      setIsLoading(false);
    }, 300);
  };

  const handleSelect = (stock) => {
    setQuery(stock.name);
    setIsOpen(false);
    setResults([]);
    onStockSelect(stock.symbol);
  };

  const handleClear = () => {
    setQuery('');
    setResults([]);
    setIsOpen(false);
    inputRef.current?.focus();
  };

  return (
    <div ref={wrapperRef} className="relative w-full max-w-2xl mx-auto">
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 dark:text-dark-muted text-light-muted" />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => handleSearch(e.target.value)}
          placeholder="Search stocks... (e.g. Reliance, TCS, HDFC)"
          className="w-full pl-12 pr-10 py-4 dark:bg-dark-card dark:border-dark-border dark:text-dark-text dark:placeholder:text-dark-muted bg-white border-gray-300 text-gray-900 placeholder:text-gray-400 border rounded-xl focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 transition-all text-base"
        />
        {query && (
          <button
            onClick={handleClear}
            className="absolute right-4 top-1/2 -translate-y-1/2 dark:text-dark-muted dark:hover:text-dark-text text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {isOpen && (
        <AutocompleteDropdown
          results={results}
          isLoading={isLoading}
          onSelect={handleSelect}
        />
      )}
    </div>
  );
};

export default SearchBar;