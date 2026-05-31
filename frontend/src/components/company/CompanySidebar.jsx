import React, { useState, useEffect } from 'react';
import { Building2, BarChart3, Loader } from 'lucide-react';
import { getCompanyInfo } from '../../utils/api';
import AboutTab from './AboutTab';
import KeyPointsTab from './KeyPointsTab';
import PriceAlertForm from '../alerts/PriceAlertForm';

const CompanySidebar = ({ symbol, currentPrice, stockName }) => {
  const [activeTab, setActiveTab] = useState('about');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!symbol) return;

    const fetchCompanyInfo = async () => {
      setLoading(true);
      try {
        const info = await getCompanyInfo(symbol);
        setData(info);
      } catch (err) {
        console.error('Company info error:', err);
      }
      setLoading(false);
    };

    fetchCompanyInfo();
  }, [symbol]);

  return (
    <div className="space-y-4">
      {/* Company Info Card */}
      <div className="dark:bg-dark-card bg-white rounded-xl border dark:border-dark-border border-gray-200 transition-colors overflow-hidden">
        {/* Tabs */}
        <div className="flex border-b dark:border-dark-border border-gray-200">
          <button
            onClick={() => setActiveTab('about')}
            className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === 'about'
                ? 'dark:text-blue-400 text-blue-500 border-b-2 border-blue-400 dark:bg-dark-bg/30 bg-blue-50/50'
                : 'dark:text-dark-muted text-gray-500 dark:hover:text-dark-text hover:text-gray-700'
            }`}
          >
            <Building2 className="w-4 h-4" />
            About
          </button>
          <button
            onClick={() => setActiveTab('keypoints')}
            className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === 'keypoints'
                ? 'dark:text-blue-400 text-blue-500 border-b-2 border-blue-400 dark:bg-dark-bg/30 bg-blue-50/50'
                : 'dark:text-dark-muted text-gray-500 dark:hover:text-dark-text hover:text-gray-700'
            }`}
          >
            <BarChart3 className="w-4 h-4" />
            Key Points
          </button>
        </div>

        {/* Tab Content */}
        <div className="p-5">
          {loading ? (
            <div className="flex items-center justify-center py-10">
              <Loader className="w-5 h-5 dark:text-dark-muted text-gray-400 animate-spin" />
            </div>
          ) : (
            <>
              {activeTab === 'about' && <AboutTab data={data} />}
              {activeTab === 'keypoints' && <KeyPointsTab data={data} />}
            </>
          )}
        </div>
      </div>

      {/* Price Alert Form */}
      <PriceAlertForm
        symbol={symbol}
        stockName={stockName || symbol}
        currentPrice={currentPrice}
      />
    </div>
  );
};

export default CompanySidebar;