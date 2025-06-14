import {
    ArrowTrendingDownIcon,
    ArrowTrendingUpIcon,
    ChartBarIcon,
    InformationCircleIcon,
    MagnifyingGlassIcon
} from '@heroicons/react/24/outline';
import axios from 'axios';
import { motion } from 'framer-motion';
import { useState } from 'react';
import toast from 'react-hot-toast';
import { useQuery } from 'react-query';

const API_BASE_URL = 'http://localhost:8001';

interface StockAnalysis {
  symbol: string;
  company_name: string;
  current_price: number;
  previous_close: number;
  change: number;
  change_percent: number;
  volume: number;
  market_cap?: number;
  pe_ratio?: number;
  technical_indicators: {
    ma_20: number;
    ma_50?: number;
    rsi: number;
    high_52w: number;
    low_52w: number;
  };
  ai_analysis: {
    trend: string;
    signal: string;
    confidence: number;
  };
  last_updated: string;
}

interface TrendingStock {
  symbol: string;
  name: string;
  price: number;
  change_percent: number;
  volume: number;
}

interface FallingStock {
  symbol: string;
  current_price: number;
  previous_close: number;
  change_percent: number;
  change_amount: number;
  timestamp: string;
  severity: 'high' | 'medium' | 'low';
}

interface FallingStocksData {
  status: string;
  timestamp: string;
  update_info: {
    last_updated: string | null;
    minutes_since_update: number;
    next_update_in: number;
    notification_count: number;
  };
  summary: {
    total_falling: number;
    severe_falls: number;
    moderate_falls: number;
    minor_falls: number;
  };
  falling_stocks: {
    severe: FallingStock[];
    moderate: FallingStock[];
    minor: FallingStock[];
    all: FallingStock[];
  };
  alert_level: 'high' | 'medium' | 'low' | 'none';
}

const Stocks = () => {
  const [searchSymbol, setSearchSymbol] = useState('');
  const [selectedStock, setSelectedStock] = useState<string | null>(null);

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

  // Fetch falling stocks (updates every 2 minutes)
  const { data: fallingData, isLoading: fallingLoading } = useQuery<FallingStocksData>(
    'falling-stocks',
    async () => {
      const response = await axios.get(`${API_BASE_URL}/api/stocks/falling`);
      return response.data;
    },
    {
      refetchInterval: 120000, // Refresh every 2 minutes to match backend
      onError: () => toast.error('Failed to fetch falling stocks')
    }
  );

  // Fetch individual stock analysis
  const { data: stockData, isLoading: stockLoading } = useQuery<StockAnalysis>(
    ['stock-analysis', selectedStock],
    async () => {
      if (!selectedStock) return null;
      const response = await axios.post(`${API_BASE_URL}/api/stocks/analyze`, {
        symbol: selectedStock,
        period: '1y'
      });
      return response.data;
    },
    {
      enabled: !!selectedStock,
      onError: () => toast.error('Failed to analyze stock')
    }
  );

  const handleSearch = () => {
    if (searchSymbol.trim()) {
      setSelectedStock(searchSymbol.trim().toUpperCase());
      toast.success(`Analyzing ${searchSymbol.toUpperCase()}...`);
    }
  };

  const handleStockSelect = (symbol: string) => {
    setSelectedStock(symbol);
    setSearchSymbol(symbol);
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'BULLISH': return 'text-green-400';
      case 'BEARISH': return 'text-red-400';
      default: return 'text-yellow-400';
    }
  };

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'BUY': return 'text-green-400';
      case 'SELL': return 'text-red-400';
      default: return 'text-yellow-400';
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h1 className="text-4xl font-bold text-primary-50 mb-2">
          Stock Analytics
        </h1>
        <p className="text-lg text-primary-100/80">
          Real-time stock analysis with AI-powered insights and technical indicators
        </p>
      </motion.div>

      {/* Search Section */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-card-gradient rounded-xl p-6 border border-primary-800/30 shadow-lg"
      >
        <h2 className="text-2xl font-semibold text-primary-50 mb-4 flex items-center">
          <MagnifyingGlassIcon className="h-6 w-6 mr-2 text-accent-emerald" />
          Stock Search & Analysis
        </h2>
        
        <div className="flex gap-4 mb-4">
          <input
            type="text"
            placeholder="Enter stock symbol (e.g., AAPL, GOOGL, TSLA)"
            value={searchSymbol}
            onChange={(e) => setSearchSymbol(e.target.value.toUpperCase())}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            className="flex-1 px-4 py-3 bg-primary-900/50 border border-primary-800/30 rounded-lg text-primary-50 placeholder-primary-400 focus:border-accent-emerald focus:outline-none"
          />
          <button
            onClick={handleSearch}
            disabled={!searchSymbol.trim() || stockLoading}
            className="px-6 py-3 bg-accent-emerald hover:bg-primary-500 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            <MagnifyingGlassIcon className="h-5 w-5 mr-2" />
            {stockLoading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>

        {/* Quick Select Popular Stocks */}
        <div className="flex flex-wrap gap-2">
          {['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX'].map((symbol) => (
            <button
              key={symbol}
              onClick={() => handleStockSelect(symbol)}
              className="px-3 py-1 bg-primary-900/30 hover:bg-primary-800/50 text-primary-200 rounded-lg text-sm transition-colors border border-primary-800/20 hover:border-accent-emerald/30"
            >
              {symbol}
            </button>
          ))}
        </div>
      </motion.section>

      {/* Stock Analysis Results */}
      {stockData && (
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-card-gradient rounded-xl p-6 border border-primary-800/30 shadow-lg"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-semibold text-primary-50 flex items-center">
              <ChartBarIcon className="h-6 w-6 mr-2 text-accent-emerald" />
              {stockData.symbol} Analysis
            </h2>
            <div className={`px-3 py-1 rounded-full text-sm font-medium ${getTrendColor(stockData.ai_analysis.trend)}`}>
              {stockData.ai_analysis.trend}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Price Information */}
            <div className="bg-primary-900/50 rounded-lg p-5 border border-primary-800/20">
              <h3 className="text-lg font-semibold text-primary-50 mb-3">Price Information</h3>
              <div className="space-y-3">
                <div>
                  <p className="text-primary-400 text-sm">Company</p>
                  <p className="text-primary-50 font-semibold">{stockData.company_name}</p>
                </div>
                <div>
                  <p className="text-primary-400 text-sm">Current Price</p>
                  <p className="text-2xl font-bold text-white">${stockData.current_price.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-primary-400 text-sm">Change</p>
                  <div className={`flex items-center ${stockData.change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {stockData.change >= 0 ? (
                      <ArrowTrendingUpIcon className="h-4 w-4 mr-1" />
                    ) : (
                      <ArrowTrendingDownIcon className="h-4 w-4 mr-1" />
                    )}
                    <span className="font-semibold">
                      {stockData.change > 0 ? '+' : ''}{stockData.change.toFixed(2)} 
                      ({stockData.change_percent > 0 ? '+' : ''}{stockData.change_percent.toFixed(2)}%)
                    </span>
                  </div>
                </div>
                <div>
                  <p className="text-primary-400 text-sm">Volume</p>
                  <p className="text-primary-50 font-semibold">{stockData.volume.toLocaleString()}</p>
                </div>
                {stockData.market_cap && (
                  <div>
                    <p className="text-primary-400 text-sm">Market Cap</p>
                    <p className="text-primary-50 font-semibold">${(stockData.market_cap / 1e9).toFixed(1)}B</p>
                  </div>
                )}
                {stockData.pe_ratio && (
                  <div>
                    <p className="text-primary-400 text-sm">P/E Ratio</p>
                    <p className="text-primary-50 font-semibold">{stockData.pe_ratio.toFixed(2)}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Technical Indicators */}
            <div className="bg-primary-900/50 rounded-lg p-5 border border-primary-800/20">
              <h3 className="text-lg font-semibold text-primary-50 mb-3">Technical Indicators</h3>
              <div className="space-y-3">
                <div>
                  <p className="text-primary-400 text-sm">20-Day MA</p>
                  <p className="text-primary-50 font-semibold">${stockData.technical_indicators.ma_20.toFixed(2)}</p>
                </div>
                {stockData.technical_indicators.ma_50 && (
                  <div>
                    <p className="text-primary-400 text-sm">50-Day MA</p>
                    <p className="text-primary-50 font-semibold">${stockData.technical_indicators.ma_50.toFixed(2)}</p>
                  </div>
                )}
                <div>
                  <p className="text-primary-400 text-sm">RSI</p>
                  <div className="flex items-center">
                    <p className="text-primary-50 font-semibold mr-2">{stockData.technical_indicators.rsi.toFixed(1)}</p>
                    <div className={`px-2 py-1 rounded text-xs font-medium ${
                      stockData.technical_indicators.rsi < 30 ? 'bg-green-500/20 text-green-400' :
                      stockData.technical_indicators.rsi > 70 ? 'bg-red-500/20 text-red-400' :
                      'bg-yellow-500/20 text-yellow-400'
                    }`}>
                      {stockData.technical_indicators.rsi < 30 ? 'Oversold' :
                       stockData.technical_indicators.rsi > 70 ? 'Overbought' : 'Neutral'}
                    </div>
                  </div>
                </div>
                <div>
                  <p className="text-primary-400 text-sm">52W High</p>
                  <p className="text-primary-50 font-semibold">${stockData.technical_indicators.high_52w.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-primary-400 text-sm">52W Low</p>
                  <p className="text-primary-50 font-semibold">${stockData.technical_indicators.low_52w.toFixed(2)}</p>
                </div>
              </div>
            </div>

            {/* AI Analysis */}
            <div className="bg-primary-900/50 rounded-lg p-5 border border-primary-800/20">
              <h3 className="text-lg font-semibold text-primary-50 mb-3 flex items-center">
                <InformationCircleIcon className="h-5 w-5 mr-2 text-accent-emerald" />
                AI Analysis
              </h3>
              <div className="space-y-4">
                <div>
                  <p className="text-primary-400 text-sm">Market Trend</p>
                  <p className={`font-semibold text-lg ${getTrendColor(stockData.ai_analysis.trend)}`}>
                    {stockData.ai_analysis.trend}
                  </p>
                </div>
                <div>
                  <p className="text-primary-400 text-sm">Trading Signal</p>
                  <p className={`font-semibold text-lg ${getSignalColor(stockData.ai_analysis.signal)}`}>
                    {stockData.ai_analysis.signal}
                  </p>
                </div>
                <div>
                  <p className="text-primary-400 text-sm">Confidence Level</p>
                  <div className="flex items-center">
                    <div className="flex-1 bg-primary-800 rounded-full h-2 mr-3">
                      <div 
                        className="bg-accent-emerald h-2 rounded-full transition-all duration-500"
                        style={{ width: `${stockData.ai_analysis.confidence * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-primary-50 font-semibold">
                      {Math.round(stockData.ai_analysis.confidence * 100)}%
                    </span>
                  </div>
                </div>
                <div className="pt-3 border-t border-primary-800/20">
                  <p className="text-primary-400 text-xs">
                    Last Updated: {new Date(stockData.last_updated).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </motion.section>
      )}

      {/* Trending Stocks */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-card-gradient rounded-xl p-6 border border-primary-800/30 shadow-lg"
      >
        <h2 className="text-2xl font-semibold text-primary-50 mb-6 flex items-center">
          <ArrowTrendingUpIcon className="h-6 w-6 mr-2 text-accent-emerald" />
          Trending Stocks
        </h2>
        
        {trendingLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="bg-primary-900/30 rounded-lg p-4 animate-pulse">
                <div className="h-4 bg-primary-800 rounded mb-2"></div>
                <div className="h-6 bg-primary-800 rounded mb-2"></div>
                <div className="h-4 bg-primary-800 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {trendingData?.trending_stocks?.map((stock) => {
              const isPositive = stock.change_percent >= 0;
              return (
                <motion.div
                  key={stock.symbol}
                  whileHover={{ scale: 1.02 }}
                  onClick={() => handleStockSelect(stock.symbol)}
                  className="bg-primary-900/30 rounded-lg p-4 border border-primary-800/20 hover:border-accent-emerald/30 transition-all cursor-pointer"
                >
                  <h4 className="text-primary-50 font-semibold text-lg">{stock.symbol}</h4>
                  <p className="text-primary-200 text-sm mb-2">{stock.name}</p>
                  <p className="text-white font-bold text-xl">${stock.price.toFixed(2)}</p>
                  <div className={`flex items-center text-sm ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                    {isPositive ? (
                      <ArrowTrendingUpIcon className="h-4 w-4 mr-1" />
                    ) : (
                      <ArrowTrendingDownIcon className="h-4 w-4 mr-1" />
                    )}
                    {stock.change_percent > 0 ? '+' : ''}{stock.change_percent.toFixed(2)}%
                  </div>
                  <p className="text-primary-400 text-xs mt-1">
                    Vol: {stock.volume.toLocaleString()}
                  </p>
                </motion.div>
              );
            })}
          </div>
        )}
      </motion.section>

      {/* Falling Stocks Monitor */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-card-gradient rounded-xl p-6 border border-primary-800/30 shadow-lg"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-semibold text-primary-50 flex items-center">
            <ArrowTrendingDownIcon className="h-6 w-6 mr-2 text-red-400" />
            Falling Stocks Monitor
            <span className="ml-3 text-sm bg-red-500/20 text-red-400 px-2 py-1 rounded-full">
              Live • Updates every 2min
            </span>
          </h2>
          {fallingData?.update_info && (
            <div className="text-right">
              <p className="text-primary-400 text-sm">
                Next update in: {Math.ceil(fallingData.update_info.next_update_in)}min
              </p>
              <p className="text-primary-400 text-xs">
                Checks: #{fallingData.update_info.notification_count}
              </p>
            </div>
          )}
        </div>

        {/* Alert Summary */}
        {fallingData?.summary && (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 text-center">
              <p className="text-red-400 text-2xl font-bold">{fallingData.summary.severe_falls}</p>
              <p className="text-red-300 text-sm">Severe Falls</p>
              <p className="text-red-400 text-xs">(&gt; -5%)</p>
            </div>
            <div className="bg-orange-500/10 border border-orange-500/20 rounded-lg p-3 text-center">
              <p className="text-orange-400 text-2xl font-bold">{fallingData.summary.moderate_falls}</p>
              <p className="text-orange-300 text-sm">Moderate Falls</p>
              <p className="text-orange-400 text-xs">(-3% to -5%)</p>
            </div>
            <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3 text-center">
              <p className="text-yellow-400 text-2xl font-bold">{fallingData.summary.minor_falls}</p>
              <p className="text-yellow-300 text-sm">Minor Falls</p>
              <p className="text-yellow-400 text-xs">(-1% to -3%)</p>
            </div>
            <div className={`border rounded-lg p-3 text-center ${
              fallingData.alert_level === 'high' ? 'bg-red-500/10 border-red-500/20' :
              fallingData.alert_level === 'medium' ? 'bg-orange-500/10 border-orange-500/20' :
              fallingData.alert_level === 'low' ? 'bg-yellow-500/10 border-yellow-500/20' :
              'bg-green-500/10 border-green-500/20'
            }`}>
              <p className={`text-2xl font-bold ${
                fallingData.alert_level === 'high' ? 'text-red-400' :
                fallingData.alert_level === 'medium' ? 'text-orange-400' :
                fallingData.alert_level === 'low' ? 'text-yellow-400' :
                'text-green-400'
              }`}>
                {fallingData.alert_level.toUpperCase()}
              </p>
              <p className={`text-sm ${
                fallingData.alert_level === 'high' ? 'text-red-300' :
                fallingData.alert_level === 'medium' ? 'text-orange-300' :
                fallingData.alert_level === 'low' ? 'text-yellow-300' :
                'text-green-300'
              }`}>
                Alert Level
              </p>
            </div>
          </div>
        )}

        {/* Falling Stocks Grid */}
        {fallingLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-primary-900/30 rounded-lg p-4 animate-pulse">
                <div className="h-4 bg-primary-800 rounded mb-2"></div>
                <div className="h-6 bg-primary-800 rounded mb-2"></div>
                <div className="h-4 bg-primary-800 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        ) : (fallingData?.falling_stocks?.all?.length || 0) > 0 ? (
          <div className="space-y-4">
            {/* Severe Falls */}
            {(fallingData?.falling_stocks?.severe?.length || 0) > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-red-400 mb-3 flex items-center">
                  ⚠️ Severe Falls (More than -5%)
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
                  {fallingData?.falling_stocks?.severe?.slice(0, 6).map((stock) => (
                    <motion.div
                      key={stock.symbol}
                      whileHover={{ scale: 1.02 }}
                      onClick={() => handleStockSelect(stock.symbol)}
                      className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 cursor-pointer hover:border-red-400/50 transition-all"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="text-primary-50 font-semibold text-lg">{stock.symbol}</h4>
                        <span className="bg-red-500/20 text-red-400 px-2 py-1 rounded text-xs font-medium">
                          SEVERE
                        </span>
                      </div>
                      <p className="text-white font-bold text-xl">${stock.current_price.toFixed(2)}</p>
                      <div className="flex items-center text-red-400 text-sm">
                        <ArrowTrendingDownIcon className="h-4 w-4 mr-1" />
                        {stock.change_percent.toFixed(2)}% (${stock.change_amount.toFixed(2)})
                      </div>
                      <p className="text-primary-400 text-xs mt-1">
                        Previous: ${stock.previous_close.toFixed(2)}
                      </p>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {/* Moderate Falls */}
            {(fallingData?.falling_stocks?.moderate?.length || 0) > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-orange-400 mb-3 flex items-center">
                  📉 Moderate Falls (-3% to -5%)
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
                  {fallingData?.falling_stocks?.moderate?.slice(0, 12).map((stock) => (
                    <motion.div
                      key={stock.symbol}
                      whileHover={{ scale: 1.02 }}
                      onClick={() => handleStockSelect(stock.symbol)}
                      className="bg-orange-500/10 border border-orange-500/30 rounded-lg p-4 cursor-pointer hover:border-orange-400/50 transition-all"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="text-primary-50 font-semibold">{stock.symbol}</h4>
                        <span className="bg-orange-500/20 text-orange-400 px-2 py-1 rounded text-xs">
                          MOD
                        </span>
                      </div>
                      <p className="text-white font-bold">${stock.current_price.toFixed(2)}</p>
                      <div className="flex items-center text-orange-400 text-sm">
                        <ArrowTrendingDownIcon className="h-4 w-4 mr-1" />
                        {stock.change_percent.toFixed(2)}%
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {/* Minor Falls */}
            {(fallingData?.falling_stocks?.minor?.length || 0) > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-yellow-400 mb-3 flex items-center">
                  📊 Minor Falls (-1% to -3%)
                </h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-3">
                  {fallingData?.falling_stocks?.minor?.slice(0, 16).map((stock) => (
                    <motion.div
                      key={stock.symbol}
                      whileHover={{ scale: 1.02 }}
                      onClick={() => handleStockSelect(stock.symbol)}
                      className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3 cursor-pointer hover:border-yellow-400/50 transition-all"
                    >
                      <h4 className="text-primary-50 font-semibold text-sm">{stock.symbol}</h4>
                      <p className="text-white font-bold text-sm">${stock.current_price.toFixed(2)}</p>
                      <div className="flex items-center text-yellow-400 text-xs">
                        <ArrowTrendingDownIcon className="h-3 w-3 mr-1" />
                        {stock.change_percent.toFixed(1)}%
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-8">
            <div className="text-green-400 mb-2">✅</div>
            <p className="text-primary-200">No significant stock falls detected</p>
            <p className="text-primary-400 text-sm">All monitored stocks are performing well</p>
          </div>
        )}
      </motion.section>
    </div>
  );
};

export default Stocks; 