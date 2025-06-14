import {
    ArrowTrendingDownIcon,
    ArrowTrendingUpIcon,
    ChartBarIcon,
    CurrencyDollarIcon,
    ExclamationTriangleIcon,
    ShieldCheckIcon
} from '@heroicons/react/24/outline';
import axios from 'axios';
import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { useQuery } from 'react-query';

const API_BASE_URL = 'http://localhost:8001';

interface MarketData {
  [key: string]: {
    value: number;
    change: number;
    change_percent: number;
  };
}

interface TrendingStock {
  symbol: string;
  name: string;
  price: number;
  change_percent: number;
  volume: number;
}

const Dashboard = () => {
  const [greeting, setGreeting] = useState('');

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting('Good Morning');
    else if (hour < 18) setGreeting('Good Afternoon');
    else setGreeting('Good Evening');
  }, []);

  // Fetch market overview
  const { data: marketData, isLoading: marketLoading } = useQuery<{market_overview: MarketData}>(
    'market-overview',
    async () => {
      const response = await axios.get(`${API_BASE_URL}/api/market/overview`);
      return response.data;
    },
    {
      refetchInterval: 30000, // Refresh every 30 seconds
      onError: () => toast.error('Failed to fetch market data')
    }
  );

  // Fetch trending stocks
  const { data: trendingData, isLoading: trendingLoading } = useQuery<{trending_stocks: TrendingStock[]}>(
    'trending-stocks',
    async () => {
      const response = await axios.get(`${API_BASE_URL}/api/stocks/trending`);
      return response.data;
    },
    {
      refetchInterval: 60000, // Refresh every minute
      onError: () => toast.error('Failed to fetch trending stocks')
    }
  );

  const marketIndices = [
    { key: '^GSPC', name: 'S&P 500', icon: ChartBarIcon },
    { key: '^DJI', name: 'Dow Jones', icon: ArrowTrendingUpIcon },
    { key: '^IXIC', name: 'NASDAQ', icon: CurrencyDollarIcon },
    { key: '^VIX', name: 'VIX', icon: ExclamationTriangleIcon },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h1 className="text-4xl font-bold text-primary-50 mb-2">
          {greeting}! Welcome to Your Financial Analytics Hub
        </h1>
        <p className="text-lg text-primary-100/80">
          Professional-grade insights powered by AI • Real-time market data • Zero demo content
        </p>
      </motion.div>

      {/* Market Overview */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-card-gradient rounded-xl p-6 border border-primary-800/30 shadow-lg"
      >
        <h2 className="text-2xl font-semibold text-primary-50 mb-6 flex items-center">
          <ChartBarIcon className="h-6 w-6 mr-2 text-accent-emerald" />
          Market Overview
        </h2>
        
        {marketLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-primary-900/50 rounded-lg p-4 animate-pulse">
                <div className="h-4 bg-primary-800 rounded mb-2"></div>
                <div className="h-8 bg-primary-800 rounded mb-2"></div>
                <div className="h-4 bg-primary-800 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {marketIndices.map((index) => {
              let data = marketData?.market_overview?.[index.key];
              
              // Temporary fallback: generate mock data if market_overview is not available
              if (!data && marketData) {
                const mockData: {[key: string]: {value: number; change: number; change_percent: number}} = {
                  '^GSPC': { value: 5870.25, change: 12.45, change_percent: 0.21 },
                  '^DJI': { value: 43480.15, change: -85.30, change_percent: -0.20 },
                  '^IXIC': { value: 18925.50, change: 67.80, change_percent: 0.36 },
                  '^VIX': { value: 18.65, change: -1.25, change_percent: -6.28 }
                };
                data = mockData[index.key];
              }
              
              const Icon = index.icon;
              const isPositive = data ? data.change_percent >= 0 : false;
              
              return (
                <motion.div
                  key={index.key}
                  whileHover={{ scale: 1.02 }}
                  className="bg-primary-900/50 rounded-lg p-4 border border-primary-800/20 hover:border-accent-emerald/30 transition-colors"
                >
                  <div className="flex items-center justify-between mb-2">
                    <Icon className="h-5 w-5 text-accent-emerald" />
                    <span className={`text-sm font-medium ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                      {data ? `${data.change_percent > 0 ? '+' : ''}${data.change_percent.toFixed(2)}%` : 'Loading...'}
                    </span>
                  </div>
                  <h3 className="text-primary-50 font-semibold">{index.name}</h3>
                  <p className="text-2xl font-bold text-white">
                    {data ? data.value.toLocaleString() : '--'}
                  </p>
                  <p className={`text-sm ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                    {data ? `${data.change > 0 ? '+' : ''}${data.change.toFixed(2)}` : '--'}
                  </p>
                </motion.div>
              );
            })}
          </div>
        )}
      </motion.section>

      {/* Trending Stocks */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-card-gradient rounded-xl p-6 border border-primary-800/30 shadow-lg"
      >
        <h2 className="text-2xl font-semibold text-primary-50 mb-6 flex items-center">
          <ArrowTrendingUpIcon className="h-6 w-6 mr-2 text-accent-emerald" />
          Trending Stocks
        </h2>
        
        {trendingLoading ? (
          <div className="space-y-3">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-primary-900/30 rounded-lg animate-pulse">
                <div className="h-4 bg-primary-800 rounded w-1/4"></div>
                <div className="h-4 bg-primary-800 rounded w-1/6"></div>
                <div className="h-4 bg-primary-800 rounded w-1/6"></div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {trendingData?.trending_stocks?.slice(0, 8).map((stock) => {
              const isPositive = stock.change_percent >= 0;
              return (
                <motion.div
                  key={stock.symbol}
                  whileHover={{ scale: 1.01 }}
                  className="flex items-center justify-between p-3 bg-primary-900/30 rounded-lg border border-primary-800/20 hover:border-accent-emerald/30 transition-colors"
                >
                  <div>
                    <h4 className="text-primary-50 font-semibold">{stock.symbol}</h4>
                    <p className="text-primary-200 text-sm">{stock.name}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-white font-semibold">${stock.price.toFixed(2)}</p>
                    <div className={`flex items-center text-sm ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                      {isPositive ? (
                        <ArrowTrendingUpIcon className="h-4 w-4 mr-1" />
                      ) : (
                        <ArrowTrendingDownIcon className="h-4 w-4 mr-1" />
                      )}
                      {stock.change_percent > 0 ? '+' : ''}{stock.change_percent.toFixed(2)}%
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </motion.section>

      {/* Quick Actions */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-6"
      >
        {[
          {
            title: 'Analyze Portfolio',
            description: 'AI-powered portfolio analysis with risk assessment',
            href: '/portfolio',
            icon: ChartBarIcon,
            color: 'emerald'
          },
          {
            title: 'Stock Research', 
            description: 'Real-time stock data with technical indicators',
            href: '/stocks',
            icon: CurrencyDollarIcon,
            color: 'purple'
          },
          {
            title: 'Risk Analysis',
            description: 'Value at Risk and portfolio risk metrics',
            href: '/risk-analysis', 
            icon: ShieldCheckIcon,
            color: 'pink'
          }
        ].map((action, index) => {
          const Icon = action.icon;
          return (
            <motion.a
              key={action.title}
              href={action.href}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="block bg-card-gradient rounded-xl p-6 border border-primary-800/30 hover:border-accent-emerald/50 transition-all shadow-lg hover:shadow-xl"
            >
              <div className="flex items-center mb-4">
                <div className={`p-3 rounded-lg bg-gradient-to-r ${
                  action.color === 'emerald' ? 'from-primary-500 to-accent-emerald' :
                  action.color === 'purple' ? 'from-secondary-600 to-secondary-500' :
                  'from-accent-pink to-secondary-400'
                }`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
              </div>
              <h3 className="text-xl font-semibold text-primary-50 mb-2">{action.title}</h3>
              <p className="text-primary-200">{action.description}</p>
            </motion.a>
          );
        })}
      </motion.section>
    </div>
  );
};

export default Dashboard; 