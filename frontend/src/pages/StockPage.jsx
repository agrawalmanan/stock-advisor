import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import StockHeader from '../components/stock/StockHeader';
import StockDetails from '../components/stock/StockDetails';
import HistoricalReturns from '../components/stock/HistoricalReturns';
import DeliveryTag from '../components/stock/DeliveryTag';
import PriceChart from '../components/chart/PriceChart';
import TechnicalAnalysis from '../components/analysis/TechnicalAnalysis';
import AiAdvice from '../components/advice/AiAdvice';
import NewsSection from '../components/advice/NewsSection';
import PeerComparison from '../components/peers/PeerComparison';
import RiskMeter from '../components/risk/RiskMeter';
import Disclaimer from '../components/ui/Disclaimer';
import ErrorMessage from '../components/ui/ErrorMessage';
import CompanySidebar from '../components/company/CompanySidebar';

import {
  StockHeaderSkeleton,
  StockDetailsSkeleton,
  ChartSkeleton,
  AnalysisSkeleton,
  AdviceSkeleton,
} from '../components/ui/SkeletonLoader';
import { getStockData, getAnalysis, getAdvice, getNews } from '../utils/api';

const StockPage = () => {
  const { symbol } = useParams();
  const [stockData, setStockData] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [advice, setAdvice] = useState(null);
  const [news, setNews] = useState(null);
  const [analysisPeriod, setAnalysisPeriod] = useState('3mo');

  const [loadingStock, setLoadingStock] = useState(true);
  const [loadingAnalysis, setLoadingAnalysis] = useState(true);
  const [loadingAdvice, setLoadingAdvice] = useState(true);
  const [loadingNews, setLoadingNews] = useState(true);

  const [error, setError] = useState(null);

  // Save to recent searches
  const saveRecentSearch = (data) => {
    try {
      const recent = JSON.parse(localStorage.getItem('recentSearches') || '[]');
      const filtered = recent.filter((s) => s.symbol !== symbol);
      filtered.unshift({ symbol, name: data.name });
      localStorage.setItem('recentSearches', JSON.stringify(filtered.slice(0, 5)));
    } catch (e) {
      console.error('Error saving recent search:', e);
    }
  };

  // Fetch all data
  useEffect(() => {
    if (!symbol) return;

    const fetchAll = async () => {
      // Reset
      setStockData(null);
      setAnalysis(null);
      setAdvice(null);
      setNews(null);
      setError(null);

      // Stock data
      setLoadingStock(true);
      const fetchWithRetry = async (retries = 3) => {
          for (let i = 0; i < retries; i++) {
              try {
                  const data = await getStockData(symbol);
                  return data;
              } catch (err) {
                  const msg = err.response?.data?.detail || err.message || '';
                  if (msg.includes('Rate') || msg.includes('Too Many') || msg.includes('429')) {
                      console.log(`Rate limited, retrying in ${(i + 1) * 3}s...`);
                      await new Promise(r => setTimeout(r, (i + 1) * 3000));
                  } else {
                      throw err;
                  }
              }
          }
          throw new Error('Rate limited. Please wait a moment and try again.');
      };

      try {
          const data = await fetchWithRetry();
          setStockData(data);
      } catch (err) {
          setError(err.response?.data?.detail || err.message || 'Failed to fetch stock data');
          setLoadingStock(false);
          return;
      }
      setLoadingStock(false); 

      // Analysis
      setLoadingAnalysis(true);
      try {
        const analysisData = await getAnalysis(symbol, analysisPeriod);
        setAnalysis(analysisData);
      } catch (err) {
        console.error('Analysis error:', err);
      }
      setLoadingAnalysis(false);

      // News
      setLoadingNews(true);
      getNews(symbol)
        .then((newsData) => setNews(newsData.articles || []))
        .catch((err) => console.error('News error:', err))
        .finally(() => setLoadingNews(false));

      // AI Advice
      setLoadingAdvice(true);
      getAdvice(symbol)
        .then((adviceData) => setAdvice(adviceData))
        .catch((err) => console.error('Advice error:', err))
        .finally(() => setLoadingAdvice(false));
    };

    fetchAll();
  }, [symbol]);

  // Period change
  const handlePeriodChange = async (newPeriod) => {
    setAnalysisPeriod(newPeriod);
    setLoadingAnalysis(true);
    try {
      const analysisData = await getAnalysis(symbol, newPeriod);
      setAnalysis(analysisData);
    } catch (err) {
      console.error('Analysis error:', err);
    }
    setLoadingAnalysis(false);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      {/* Error */}
      {error && (
        <ErrorMessage
          message={error}
          onRetry={() => window.location.reload()}
        />
      )}

      {/* Stock Header - Full Width */}
      {loadingStock && <StockHeaderSkeleton />}
      {stockData && <StockHeader data={stockData} />}

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-4 mt-4">
        {/* Left Sidebar */}
        <div className="space-y-4">
          {/* Company Info */}
          {symbol && (
            <CompanySidebar
              symbol={symbol}
              currentPrice={stockData?.current_price}
              stockName={stockData?.name}
            />
          )}  
        </div>

        {/* Right Main Content */}
        <div className="space-y-4">
          {/* Details + Returns */}
          {loadingStock && <StockDetailsSkeleton />}
          {stockData && (
            <>
              <StockDetails data={stockData} />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <HistoricalReturns returns={stockData.historical_returns} />
                <div className="space-y-4">
                  <DeliveryTag tradeType={stockData.trade_type} />
                  <RiskMeter risk={stockData.risk} />
                </div>
              </div>
            </>
          )}

          {/* Chart */}
          {loadingStock && <ChartSkeleton />}
          {symbol && !loadingStock && <PriceChart symbol={symbol} />}

          {/* Technical Analysis */}
          {loadingAnalysis && <AnalysisSkeleton />}
          {analysis && (
            <TechnicalAnalysis
              analysis={analysis}
              period={analysisPeriod}
              onPeriodChange={handlePeriodChange}
              symbol={symbol}
            />
          )}

          {/* AI Advice */}
          {loadingAdvice && <AdviceSkeleton />}
          {advice && <AiAdvice advice={advice.advice} />}

          {/* News */}
          {loadingNews && <AnalysisSkeleton />}
          {!loadingNews && <NewsSection news={news} />}

          {/* Peers */}
          {stockData && (
            <PeerComparison
              symbol={stockData.symbol}
              sector={stockData.sector}
            />
          )}

          {/* Disclaimer */}
          <Disclaimer />
        </div>
      </div>
    </div>
  );
};

export default StockPage;