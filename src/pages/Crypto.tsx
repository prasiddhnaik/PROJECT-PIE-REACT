import {
    ArrowTrendingDownIcon,
    ArrowTrendingUpIcon,
    CubeIcon,
    FireIcon,
    InformationCircleIcon,
    MagnifyingGlassIcon
} from '@heroicons/react/24/outline';
import axios from 'axios';
import { motion } from 'framer-motion';
import { useState } from 'react';
import toast from 'react-hot-toast';
import { useQuery } from 'react-query';

const API_BASE_URL = 'http://localhost:8001';

interface CryptoAnalysis {
  symbol: string;
  current_price: number;
  market_cap: number;
  volume_24h: number;
  change_24h: number;
  volatility: number;
  ai_analysis: {
    trend: string;
    signal: string;
    confidence: number;
  };
  last_updated: string;
}

interface TrendingCrypto {
  id: string;
  name: string;
  symbol: string;
  market_cap_rank?: number;
  thumb?: string;
}

const Crypto = () => {
  const [searchSymbol, setSearchSymbol] = useState('');
  const [selectedCrypto, setSelectedCrypto] = useState<string | null>(null);

  // Fetch trending crypto
  const { data: trendingData, isLoading: trendingLoading } = useQuery<{trending_crypto: TrendingCrypto[]}>(
    'trending-crypto',
    async () => {
      const response = await axios.get(`${API_BASE_URL}/api/crypto/trending`);
      return response.data;
    },
    {
      refetchInterval: 120000, // Refresh every 2 minutes
      onError: () => toast.error('Failed to fetch trending cryptocurrencies')
    }
  );

  // Fetch individual crypto analysis
  const { data: cryptoData, isLoading: cryptoLoading } = useQuery<CryptoAnalysis>(
    ['crypto-analysis', selectedCrypto],
    async () => {
      if (!selectedCrypto) return null;
      const response = await axios.post(`${API_BASE_URL}/api/crypto/analyze`, {
        symbol: selectedCrypto.toLowerCase(),
        currency: 'usd'
      });
      return response.data;
    },
    {
      enabled: !!selectedCrypto,
      onError: () => toast.error('Failed to analyze cryptocurrency')
    }
  );

  const handleSearch = () => {
    if (searchSymbol.trim()) {
      // Convert common symbols to their CoinGecko IDs
      const symbolMap: { [key: string]: string } = {
        'POLYGON': 'polygon-ecosystem-token',
        'MATIC': 'polygon-ecosystem-token',
        'BTC': 'bitcoin',
        'ETH': 'ethereum', 
        'ADA': 'cardano',
        'SOL': 'solana',
        'DOT': 'polkadot',
        'LINK': 'chainlink',
        'AVAX': 'avalanche-2'
      };
      
      const searchTerm = searchSymbol.trim().toUpperCase();
      const cryptoId = symbolMap[searchTerm] || searchSymbol.trim().toLowerCase();
      
      setSelectedCrypto(cryptoId);
      toast.success(`Analyzing ${searchTerm}...`);
    }
  };

  const handleCryptoSelect = (cryptoId: string) => {
    setSelectedCrypto(cryptoId);
    setSearchSymbol(cryptoId.toUpperCase());
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

  const formatMarketCap = (marketCap: number) => {
    if (marketCap >= 1e12) return `$${(marketCap / 1e12).toFixed(1)}T`;
    if (marketCap >= 1e9) return `$${(marketCap / 1e9).toFixed(1)}B`;
    if (marketCap >= 1e6) return `$${(marketCap / 1e6).toFixed(1)}M`;
    return `$${marketCap.toFixed(0)}`;
  };

  const formatVolume = (volume: number) => {
    if (volume >= 1e9) return `$${(volume / 1e9).toFixed(1)}B`;
    if (volume >= 1e6) return `$${(volume / 1e6).toFixed(1)}M`;
    if (volume >= 1e3) return `$${(volume / 1e3).toFixed(1)}K`;
    return `$${volume.toFixed(0)}`;
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
          Cryptocurrency Hub
        </h1>
        <p className="text-lg text-primary-100/80">
          Real-time crypto analytics with AI-powered market insights
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
          Cryptocurrency Search & Analysis
        </h2>
        
        <div className="flex gap-4 mb-4">
          <input
            type="text"
            placeholder="Enter crypto ID (e.g., bitcoin, ethereum, cardano)"
            value={searchSymbol}
            onChange={(e) => setSearchSymbol(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            className="flex-1 px-4 py-3 bg-primary-900/50 border border-primary-800/30 rounded-lg text-primary-50 placeholder-primary-400 focus:border-accent-emerald focus:outline-none"
          />
          <button
            onClick={handleSearch}
            disabled={!searchSymbol.trim() || cryptoLoading}
            className="px-6 py-3 bg-accent-emerald hover:bg-primary-500 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            <MagnifyingGlassIcon className="h-5 w-5 mr-2" />
            {cryptoLoading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>

        {/* Quick Select Popular Cryptos */}
        <div className="flex flex-wrap gap-2">
          {[
            { id: 'bitcoin', symbol: 'BTC' },
            { id: 'ethereum', symbol: 'ETH' },
            { id: 'cardano', symbol: 'ADA' },
            { id: 'solana', symbol: 'SOL' },
            { id: 'polkadot', symbol: 'DOT' },
            { id: 'chainlink', symbol: 'LINK' },
            { id: 'polygon', symbol: 'MATIC' },
            { id: 'avalanche-2', symbol: 'AVAX' }
          ].map((crypto) => (
            <button
              key={crypto.id}
              onClick={() => handleCryptoSelect(crypto.id)}
              className="px-3 py-1 bg-primary-900/30 hover:bg-primary-800/50 text-primary-200 rounded-lg text-sm transition-colors border border-primary-800/20 hover:border-accent-emerald/30"
            >
              {crypto.symbol}
            </button>
          ))}
        </div>
      </motion.section>

      {/* Crypto Analysis Results */}
      {cryptoData && (
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-card-gradient rounded-xl p-6 border border-primary-800/30 shadow-lg"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-semibold text-primary-50 flex items-center">
              <CubeIcon className="h-6 w-6 mr-2 text-accent-emerald" />
              {cryptoData.symbol.toUpperCase()} Analysis
            </h2>
            <div className={`px-3 py-1 rounded-full text-sm font-medium ${getTrendColor(cryptoData.ai_analysis.trend)}`}>
              {cryptoData.ai_analysis.trend}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Price Information */}
            <div className="bg-primary-900/50 rounded-lg p-5 border border-primary-800/20">
              <h3 className="text-lg font-semibold text-primary-50 mb-3">Price Information</h3>
              <div className="space-y-3">
                <div>
                  <p className="text-primary-400 text-sm">Current Price</p>
                  <p className="text-2xl font-bold text-white">${cryptoData.current_price.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-primary-400 text-sm">24h Change</p>
                  <div className={`flex items-center ${cryptoData.change_24h >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {cryptoData.change_24h >= 0 ? (
                      <ArrowTrendingUpIcon className="h-4 w-4 mr-1" />
                    ) : (
                      <ArrowTrendingDownIcon className="h-4 w-4 mr-1" />
                    )}
                    <span className="font-semibold">
                      {cryptoData.change_24h > 0 ? '+' : ''}{cryptoData.change_24h.toFixed(2)}%
                    </span>
                  </div>
                </div>
                <div>
                  <p className="text-primary-400 text-sm">Market Cap</p>
                  <p className="text-primary-50 font-semibold">{formatMarketCap(cryptoData.market_cap)}</p>
                </div>
                <div>
                  <p className="text-primary-400 text-sm">24h Volume</p>
                  <p className="text-primary-50 font-semibold">{formatVolume(cryptoData.volume_24h)}</p>
                </div>
                <div>
                  <p className="text-primary-400 text-sm">Volatility</p>
                  <div className="flex items-center">
                    <p className="text-primary-50 font-semibold mr-2">{cryptoData.volatility.toFixed(1)}%</p>
                    <div className={`px-2 py-1 rounded text-xs font-medium ${
                      cryptoData.volatility > 20 ? 'bg-red-500/20 text-red-400' :
                      cryptoData.volatility > 10 ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-green-500/20 text-green-400'
                    }`}>
                      {cryptoData.volatility > 20 ? 'High' :
                       cryptoData.volatility > 10 ? 'Medium' : 'Low'}
                    </div>
                  </div>
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
                  <p className={`font-semibold text-lg ${getTrendColor(cryptoData.ai_analysis.trend)}`}>
                    {cryptoData.ai_analysis.trend}
                  </p>
                </div>
                <div>
                  <p className="text-primary-400 text-sm">Trading Signal</p>
                  <p className={`font-semibold text-lg ${getSignalColor(cryptoData.ai_analysis.signal)}`}>
                    {cryptoData.ai_analysis.signal}
                  </p>
                </div>
                <div>
                  <p className="text-primary-400 text-sm">Confidence Level</p>
                  <div className="flex items-center">
                    <div className="flex-1 bg-primary-800 rounded-full h-2 mr-3">
                      <div 
                        className="bg-accent-emerald h-2 rounded-full transition-all duration-500"
                        style={{ width: `${cryptoData.ai_analysis.confidence * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-primary-50 font-semibold">
                      {Math.round(cryptoData.ai_analysis.confidence * 100)}%
                    </span>
                  </div>
                </div>
                <div className="pt-3 border-t border-primary-800/20">
                  <p className="text-primary-400 text-xs">
                    Last Updated: {new Date(cryptoData.last_updated).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>

            {/* Market Insights */}
            <div className="bg-primary-900/50 rounded-lg p-5 border border-primary-800/20">
              <h3 className="text-lg font-semibold text-primary-50 mb-3">Market Insights</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-primary-800/30 rounded-lg">
                  <span className="text-primary-200">Risk Level</span>
                  <span className={`font-semibold ${
                    cryptoData.volatility > 20 ? 'text-red-400' :
                    cryptoData.volatility > 10 ? 'text-yellow-400' : 'text-green-400'
                  }`}>
                    {cryptoData.volatility > 20 ? 'HIGH' :
                     cryptoData.volatility > 10 ? 'MEDIUM' : 'LOW'}
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 bg-primary-800/30 rounded-lg">
                  <span className="text-primary-200">Market Sentiment</span>
                  <span className={getTrendColor(cryptoData.ai_analysis.trend)}>
                    {cryptoData.ai_analysis.trend}
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 bg-primary-800/30 rounded-lg">
                  <span className="text-primary-200">Recommendation</span>
                  <span className={getSignalColor(cryptoData.ai_analysis.signal)}>
                    {cryptoData.ai_analysis.signal}
                  </span>
                </div>
                <div className="p-3 bg-accent-emerald/10 border border-accent-emerald/20 rounded-lg">
                  <p className="text-primary-200 text-sm">
                    💡 <strong>AI Tip:</strong> {
                      cryptoData.ai_analysis.signal === 'BUY' ? 'Strong buying opportunity detected.' :
                      cryptoData.ai_analysis.signal === 'SELL' ? 'Consider taking profits.' :
                      'Monitor for better entry/exit points.'
                    }
                  </p>
                </div>
              </div>
            </div>
          </div>
        </motion.section>
      )}

      {/* Trending Crypto */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-card-gradient rounded-xl p-6 border border-primary-800/30 shadow-lg"
      >
        <h2 className="text-2xl font-semibold text-primary-50 mb-6 flex items-center">
          <FireIcon className="h-6 w-6 mr-2 text-accent-emerald" />
          Trending Cryptocurrencies
        </h2>
        
        {trendingLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {[...Array(10)].map((_, i) => (
              <div key={i} className="bg-primary-900/30 rounded-lg p-4 animate-pulse">
                <div className="h-4 bg-primary-800 rounded mb-2"></div>
                <div className="h-6 bg-primary-800 rounded mb-2"></div>
                <div className="h-4 bg-primary-800 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {trendingData?.trending_crypto?.map((crypto, index) => (
              <motion.div
                key={crypto.id}
                whileHover={{ scale: 1.02 }}
                onClick={() => handleCryptoSelect(crypto.id)}
                className="bg-primary-900/30 rounded-lg p-4 border border-primary-800/20 hover:border-accent-emerald/30 transition-all cursor-pointer"
              >
                <div className="flex items-center mb-2">
                  <span className="text-accent-emerald font-bold text-sm mr-2">#{index + 1}</span>
                  {crypto.thumb && (
                    <img src={crypto.thumb} alt={crypto.name} className="w-6 h-6 mr-2" />
                  )}
                </div>
                <h4 className="text-primary-50 font-semibold text-sm">{crypto.name}</h4>
                <p className="text-primary-200 text-xs">{crypto.symbol?.toUpperCase()}</p>
                {crypto.market_cap_rank && (
                  <p className="text-primary-400 text-xs mt-1">
                    Rank: #{crypto.market_cap_rank}
                  </p>
                )}
              </motion.div>
            ))}
          </div>
        )}
      </motion.section>
    </div>
  );
};

export default Crypto; 