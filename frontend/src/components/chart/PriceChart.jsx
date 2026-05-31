import React, { useEffect, useRef, useState } from 'react';
import { createChart, CandlestickSeries } from 'lightweight-charts';
import { getChartData } from '../../utils/api';
import ChartControls from './ChartControls';

const PriceChart = ({ symbol }) => {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const seriesRef = useRef(null);
  const [period, setPeriod] = useState('3mo');
  const [loading, setLoading] = useState(true);
  const [isDark, setIsDark] = useState(true);

  // Detect theme changes
  useEffect(() => {
    const observer = new MutationObserver(() => {
      const dark = document.documentElement.classList.contains('dark');
      setIsDark(dark);
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    setIsDark(document.documentElement.classList.contains('dark'));
    return () => observer.disconnect();
  }, []);

  // Update chart colors when theme changes
  useEffect(() => {
    if (!chartRef.current) return;
    chartRef.current.applyOptions({
      layout: {
        background: { color: isDark ? '#1a1d29' : '#ffffff' },
        textColor: isDark ? '#8b8fa3' : '#718096',
      },
      grid: {
        vertLines: { color: isDark ? '#2a2d3a' : '#e2e8f0' },
        horzLines: { color: isDark ? '#2a2d3a' : '#e2e8f0' },
      },
      timeScale: { borderColor: isDark ? '#2a2d3a' : '#e2e8f0' },
      rightPriceScale: { borderColor: isDark ? '#2a2d3a' : '#e2e8f0' },
    });
  }, [isDark]);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: isDark ? '#1a1d29' : '#ffffff' },
        textColor: isDark ? '#8b8fa3' : '#718096',
      },
      grid: {
        vertLines: { color: isDark ? '#2a2d3a' : '#e2e8f0' },
        horzLines: { color: isDark ? '#2a2d3a' : '#e2e8f0' },
      },
      width: chartContainerRef.current.clientWidth,
      height: 400,
      timeScale: {
        borderColor: isDark ? '#2a2d3a' : '#e2e8f0',
        timeVisible: false,
      },
      rightPriceScale: {
        borderColor: isDark ? '#2a2d3a' : '#e2e8f0',
      },
      crosshair: {
        mode: 0,
        vertLine: {
          color: isDark ? '#4a4d5a' : '#cbd5e0',
          labelBackgroundColor: isDark ? '#2a2d3a' : '#e2e8f0',
        },
        horzLine: {
          color: isDark ? '#4a4d5a' : '#cbd5e0',
          labelBackgroundColor: isDark ? '#2a2d3a' : '#e2e8f0',
        },
      },
    });

    const series = chart.addSeries(CandlestickSeries, {
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderDownColor: '#ef4444',
      borderUpColor: '#22c55e',
      wickDownColor: '#ef4444',
      wickUpColor: '#22c55e',
    });

    chartRef.current = chart;
    seriesRef.current = series;

    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      if (!symbol || !seriesRef.current) return;

      setLoading(true);
      try {
        const data = await getChartData(symbol, period);
        if (data.candles && data.candles.length > 0) {
          seriesRef.current.setData(data.candles);
          chartRef.current?.timeScale().fitContent();
        }
      } catch (err) {
        console.error('Chart data error:', err);
      }
      setLoading(false);
    };

    fetchData();
  }, [symbol, period]);

  return (
    <div className="dark:bg-dark-card bg-white rounded-xl p-6 border dark:border-dark-border border-gray-200 transition-colors">
      <div className="flex items-center justify-between mb-4">
        <h3 className="dark:text-dark-text text-gray-900 font-semibold">Price Chart</h3>
        <ChartControls activePeriod={period} onPeriodChange={setPeriod} />
      </div>

      <div className="relative">
        {loading && (
          <div className="absolute inset-0 dark:bg-dark-card/80 bg-white/80 flex items-center justify-center z-10 rounded-lg">
            <div className="w-6 h-6 border-2 dark:border-dark-muted border-gray-300 border-t-blue-500 rounded-full animate-spin" />
          </div>
        )}
        <div ref={chartContainerRef} className="rounded-lg overflow-hidden" />
      </div>
    </div>
  );
};

export default PriceChart;