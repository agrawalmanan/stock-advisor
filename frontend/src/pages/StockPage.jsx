import React, { useState, useEffect, useRef } from 'react';
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
import CompanySidebar from '../components/company/CompanySidebar';
import Disclaimer from '../components/ui/Disclaimer';
import ErrorMessage from '../components/ui/ErrorMessage';
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
  const fetchedRef = useRef(null);

  const saveRecentSearch = (data) => {
    try {
      const recent = JSON.parse(localStorage.getItem('recentSearches') || '[]');
      const filtered = recent.filter((s) => s.symbol !== symbol);
      filtered.unshift({ symbol, name: data.name });
      localStorage.setItem('recentSearches', JSON.stringify(filtered.slice(0, 5)));
    } catch (e) {}
  };

  useEffect(() => {
    // Prevent double fetch
    if (fetchedRef.current === symbol) return;
    fetchedRef.current = symbol;

    if (!symbol) return;

    setStockData(null);
    setAnalysis(null);
    setAdvice(null);
    setNews(null);
    setError(null);
    setLoadingStock(true);
    setLoadingAnalysis(true);
    setLoadingAdvice(true);
    setLoadingNews(true);

    const fetchAll = async () => {
      // Stock data
      try {
        const data = await getStockData(symbol);
        setStockData(data);
        saveRecentSearch(data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to fetch stock data');
        setLoadingStock(false);
        setLoadingAnalysis(false);
        setLoadingAdvice(false);
        setLoadingNews(false);
        return;
      }
      setLoadingStock(false);

      // Analysis
      try {
        const analysisData = await getAnalysis(symbol, analysisPeriod);
        setAnalysis(analysisData);
      } catch (err) {
        console.error('Analysis error:', err);
      }
      setLoadingAnalysis(false);

      // News
      getNews(symbol)
        .then((newsData) => setNews(newsData.articles || []))
        .catch((err) => console.error('News error:', err))
        .finally(() => setLoadingNews(false));

      // AI Advice
      getAdvice(symbol)
        .then((adviceData) => setAdvice(adviceData))
        .catch((err) => console.error('Advice error:', err))
        .finally(() => setLoadingAdvice(false));
    };

    fetchAll();
  }, [symbol]);

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
      {error && (
        <ErrorMessage
          message={error}
          onRetry={() => window.location.reload()}
        />
      )}

      {/* Stock Header - Full Width */}
      {loadingStock && <StockHeaderSkeleton />}
      {stockData && !loadingStock && <StockHeader data={stockData} />}

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-4 mt-4">

        {/* Left Sidebar */}
        <div className="space-y-4">
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

          {/* Stock Details */}
          {loadingStock && <StockDetailsSkeleton />}
          {stockData && !loadingStock && (
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
          {symbol && !loadingStock && (
            <PriceChart symbol={symbol} />
          )}

          {/* Technical Analysis */}
          {loadingAnalysis && <AnalysisSkeleton />}
          {!loadingAnalysis && analysis && (
            <TechnicalAnalysis
              analysis={analysis}
              period={analysisPeriod}
              onPeriodChange={handlePeriodChange}
              symbol={symbol}
            />
          )}

          {/* AI Advice */}
          {loadingAdvice && <AdviceSkeleton />}
          {!loadingAdvice && advice && (
            <AiAdvice advice={advice.advice} />
          )}

          {/* News */}
          {loadingNews && <AnalysisSkeleton />}
          {!loadingNews && (
            <NewsSection news={news || []} />
          )}

          {/* Peer Comparison */}
          {stockData && !loadingStock && (
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