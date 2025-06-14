import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useQuery } from 'react-query';
import toast from 'react-hot-toast';
import { ChartBarIcon, PlusIcon, TrashIcon } from '@heroicons/react/24/outline';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001';

interface Fund {
  symbol: string;
  name: string;
  allocation?: number;
}

interface PortfolioAnalysis {
  [symbol: string]: {
    symbol: string;
    name: string;
    start_price: number;
    end_price: number;
    total_return: number;
    volatility: number;
    sharpe_ratio: number;
    risk_level: string;
    ai_recommendation: string;
    last_updated: string;
  };
}

interface MarketSentiment {
  fear_greed_index: {
    value: number;
    classification: string;
    description: string;
    last_updated: string;
  };
  vix_index: {
    value: number;
    level: string;
    description: string;
  };
  put_call_ratio: {
    value: number;
    sentiment: string;
    description: string;
  };
  market_breadth: {
    advancing: number;
    declining: number;
    ratio: number;
    sentiment: string;
  };
  treasury_yield: {
    ten_year: number;
    two_year: number;
    spread: number;
    curve_status: string;
  };
}

const Portfolio = () => {
  const [funds, setFunds] = useState<Fund[]>([
    { symbol: 'AAPL', name: 'Apple Inc.', allocation: 30 },
    { symbol: 'GOOGL', name: 'Alphabet Inc.', allocation: 25 },
    { symbol: 'MSFT', name: 'Microsoft Corp.', allocation: 25 },
    { symbol: 'TSLA', name: 'Tesla Inc.', allocation: 20 }
  ]);
  
  const [startDate, setStartDate] = useState('2023-01-01');
  const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0]);
  const [newFund, setNewFund] = useState({ symbol: '', name: '', allocation: 0 });

  const { data: portfolioData, isLoading, refetch } = useQuery<{portfolio_analysis: PortfolioAnalysis}>(
    ['portfolio-analysis', funds, startDate, endDate],
    async () => {
      const response = await axios.post(`${API_BASE_URL}/api/portfolio/analyze`, {
        funds,
        start_date: startDate,
        end_date: endDate
      });
      return response.data;
    },
    {
      enabled: funds.length > 0,
      onError: () => toast.error('Failed to analyze portfolio')
    }
  );

  const { data: marketSentiment } = useQuery<MarketSentiment>(
    'market-sentiment',
    async () => {
      const response = await axios.get(`${API_BASE_URL}/api/market/sentiment`);
      return response.data;
    },
    {
      refetchInterval: 5 * 60 * 1000, // Refresh every 5 minutes
      onError: () => toast.error('Failed to fetch market sentiment')
    }
  );

  const addFund = () => {
    if (newFund.symbol && newFund.name) {
      setFunds([...funds, { ...newFund }]);
      setNewFund({ symbol: '', name: '', allocation: 0 });
      toast.success('Fund added to portfolio');
    }
  };

  const removeFund = (index: number) => {
    setFunds(funds.filter((_, i) => i !== index));
    toast.success('Fund removed from portfolio');
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'LOW': return 'text-green-400';
      case 'MEDIUM': return 'text-yellow-400';
      case 'HIGH': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation) {
      case 'STRONG BUY': 
      case 'BUY': return 'text-green-400';
      case 'HOLD': return 'text-yellow-400';
      case 'SELL': return 'text-red-400';
      default: return 'text-gray-400';
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
          Portfolio Analysis
        </h1>
        <p className="text-lg text-primary-100/80">
          AI-powered portfolio insights with professional risk assessment
        </p>
      </motion.div>

      {/* Portfolio Configuration */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-card-gradient rounded-xl p-6 border border-primary-800/30 shadow-lg"
      >
        <h2 className="text-2xl font-semibold text-primary-50 mb-6 flex items-center">
          <ChartBarIcon className="h-6 w-6 mr-2 text-accent-emerald" />
          Portfolio Configuration
        </h2>
        
        {/* Date Range */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-primary-200 text-sm font-medium mb-2">
              Start Date
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-3 py-2 bg-primary-900/50 border border-primary-800/30 rounded-lg text-primary-50 focus:border-accent-emerald focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-primary-200 text-sm font-medium mb-2">
              End Date
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full px-3 py-2 bg-primary-900/50 border border-primary-800/30 rounded-lg text-primary-50 focus:border-accent-emerald focus:outline-none"
            />
          </div>
        </div>

        {/* Add Fund */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <input
            type="text"
            placeholder="Symbol (e.g., AAPL)"
            value={newFund.symbol}
            onChange={(e) => setNewFund({...newFund, symbol: e.target.value.toUpperCase()})}
            className="px-3 py-2 bg-primary-900/50 border border-primary-800/30 rounded-lg text-primary-50 placeholder-primary-400 focus:border-accent-emerald focus:outline-none"
          />
          <input
            type="text"
            placeholder="Fund Name"
            value={newFund.name}
            onChange={(e) => setNewFund({...newFund, name: e.target.value})}
            className="px-3 py-2 bg-primary-900/50 border border-primary-800/30 rounded-lg text-primary-50 placeholder-primary-400 focus:border-accent-emerald focus:outline-none"
          />
          <input
            type="number"
            placeholder="Allocation %"
            value={newFund.allocation || ''}
            onChange={(e) => setNewFund({...newFund, allocation: Number(e.target.value)})}
            className="px-3 py-2 bg-primary-900/50 border border-primary-800/30 rounded-lg text-primary-50 placeholder-primary-400 focus:border-accent-emerald focus:outline-none"
          />
          <button
            onClick={addFund}
            className="px-4 py-2 bg-accent-emerald hover:bg-primary-500 text-white rounded-lg transition-colors flex items-center justify-center"
          >
            <PlusIcon className="h-5 w-5 mr-1" />
            Add Fund
          </button>
        </div>

        {/* Current Funds */}
        <div className="space-y-2">
          {funds.map((fund, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-primary-900/30 rounded-lg border border-primary-800/20">
              <div>
                <span className="text-primary-50 font-semibold">{fund.symbol}</span>
                <span className="text-primary-200 ml-2">{fund.name}</span>
                {fund.allocation && (
                  <span className="text-accent-emerald ml-2">({fund.allocation}%)</span>
                )}
              </div>
              <button
                onClick={() => removeFund(index)}
                className="p-1 text-red-400 hover:text-red-300 transition-colors"
              >
                <TrashIcon className="h-5 w-5" />
              </button>
            </div>
          ))}
        </div>

        <button
          onClick={() => refetch()}
          disabled={isLoading || funds.length === 0}
          className="mt-4 w-full px-4 py-2 bg-emerald-purple hover:opacity-90 text-white rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Analyzing...' : 'Analyze Portfolio'}
        </button>
      </motion.section>

      {/* Market Sentiment & Fear & Greed Index */}
      {marketSentiment && (
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="bg-card-gradient rounded-xl p-6 border border-primary-800/30 shadow-lg"
        >
          <h2 className="text-2xl font-semibold text-primary-50 mb-6">
            Market Sentiment Analysis
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Fear & Greed Index */}
            <div className="bg-primary-900/50 rounded-lg p-5 border border-primary-800/20">
              <h3 className="text-lg font-semibold text-primary-50 mb-3">Fear & Greed Index</h3>
              <div className="text-center">
                <div className={`text-4xl font-bold mb-2 ${
                  marketSentiment.fear_greed_index.value >= 75 ? 'text-red-400' :
                  marketSentiment.fear_greed_index.value >= 55 ? 'text-yellow-400' :
                  marketSentiment.fear_greed_index.value >= 45 ? 'text-blue-400' :
                  marketSentiment.fear_greed_index.value >= 25 ? 'text-orange-400' :
                  'text-red-500'
                }`}>
                  {marketSentiment.fear_greed_index.value}
                </div>
                <div className={`text-sm font-medium mb-2 ${
                  marketSentiment.fear_greed_index.classification === 'Extreme Greed' ? 'text-red-400' :
                  marketSentiment.fear_greed_index.classification === 'Greed' ? 'text-yellow-400' :
                  marketSentiment.fear_greed_index.classification === 'Neutral' ? 'text-blue-400' :
                  marketSentiment.fear_greed_index.classification === 'Fear' ? 'text-orange-400' :
                  'text-red-500'
                }`}>
                  {marketSentiment.fear_greed_index.classification}
                </div>
                <p className="text-primary-300 text-xs">
                  {marketSentiment.fear_greed_index.description}
                </p>
              </div>
            </div>

            {/* VIX Index */}
            <div className="bg-primary-900/50 rounded-lg p-5 border border-primary-800/20">
              <h3 className="text-lg font-semibold text-primary-50 mb-3">VIX (Volatility Index)</h3>
              <div className="text-center">
                <div className={`text-3xl font-bold mb-2 ${
                  marketSentiment.vix_index.value >= 30 ? 'text-red-400' :
                  marketSentiment.vix_index.value >= 20 ? 'text-yellow-400' :
                  'text-green-400'
                }`}>
                  {marketSentiment.vix_index.value.toFixed(2)}
                </div>
                <div className="text-sm font-medium text-primary-200 mb-2">
                  {marketSentiment.vix_index.level}
                </div>
                <p className="text-primary-300 text-xs">
                  {marketSentiment.vix_index.description}
                </p>
              </div>
            </div>

            {/* Put/Call Ratio */}
            <div className="bg-primary-900/50 rounded-lg p-5 border border-primary-800/20">
              <h3 className="text-lg font-semibold text-primary-50 mb-3">Put/Call Ratio</h3>
              <div className="text-center">
                <div className={`text-3xl font-bold mb-2 ${
                  marketSentiment.put_call_ratio.sentiment === 'Bearish' ? 'text-red-400' :
                  marketSentiment.put_call_ratio.sentiment === 'Neutral' ? 'text-yellow-400' :
                  'text-green-400'
                }`}>
                  {marketSentiment.put_call_ratio.value.toFixed(2)}
                </div>
                <div className="text-sm font-medium text-primary-200 mb-2">
                  {marketSentiment.put_call_ratio.sentiment}
                </div>
                <p className="text-primary-300 text-xs">
                  {marketSentiment.put_call_ratio.description}
                </p>
              </div>
            </div>

            {/* Market Breadth */}
            <div className="bg-primary-900/50 rounded-lg p-5 border border-primary-800/20">
              <h3 className="text-lg font-semibold text-primary-50 mb-3">Market Breadth</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-primary-300 text-sm">Advancing:</span>
                  <span className="text-green-400 font-semibold">{marketSentiment.market_breadth.advancing}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-primary-300 text-sm">Declining:</span>
                  <span className="text-red-400 font-semibold">{marketSentiment.market_breadth.declining}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-primary-300 text-sm">Ratio:</span>
                  <span className="text-primary-50 font-semibold">{marketSentiment.market_breadth.ratio.toFixed(2)}</span>
                </div>
                <div className={`text-center text-sm font-medium ${
                  marketSentiment.market_breadth.sentiment === 'Bullish' ? 'text-green-400' :
                  marketSentiment.market_breadth.sentiment === 'Neutral' ? 'text-yellow-400' :
                  'text-red-400'
                }`}>
                  {marketSentiment.market_breadth.sentiment}
                </div>
              </div>
            </div>

            {/* Treasury Yield Curve */}
            <div className="bg-primary-900/50 rounded-lg p-5 border border-primary-800/20">
              <h3 className="text-lg font-semibold text-primary-50 mb-3">Treasury Yield Curve</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-primary-300 text-sm">10-Year:</span>
                  <span className="text-primary-50 font-semibold">{marketSentiment.treasury_yield.ten_year.toFixed(2)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-primary-300 text-sm">2-Year:</span>
                  <span className="text-primary-50 font-semibold">{marketSentiment.treasury_yield.two_year.toFixed(2)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-primary-300 text-sm">Spread:</span>
                  <span className={`font-semibold ${
                    marketSentiment.treasury_yield.spread >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {marketSentiment.treasury_yield.spread > 0 ? '+' : ''}{marketSentiment.treasury_yield.spread.toFixed(2)}%
                  </span>
                </div>
                <div className={`text-center text-sm font-medium ${
                  marketSentiment.treasury_yield.curve_status === 'Normal' ? 'text-green-400' :
                  marketSentiment.treasury_yield.curve_status === 'Flat' ? 'text-yellow-400' :
                  'text-red-400'
                }`}>
                  {marketSentiment.treasury_yield.curve_status}
                </div>
              </div>
            </div>

            {/* Overall Market Sentiment Summary */}
            <div className="bg-primary-900/50 rounded-lg p-5 border border-primary-800/20">
              <h3 className="text-lg font-semibold text-primary-50 mb-3">Overall Sentiment</h3>
              <div className="text-center">
                <div className="text-2xl font-bold text-accent-emerald mb-2">
                  {(() => {
                    const fearGreed = marketSentiment.fear_greed_index.value;
                    const vix = marketSentiment.vix_index.value;
                    
                    if (fearGreed >= 60 && vix < 20) return "🚀 BULLISH";
                    if (fearGreed <= 40 && vix > 25) return "🐻 BEARISH";
                    if (fearGreed >= 45 && fearGreed <= 55) return "⚖️ NEUTRAL";
                    if (fearGreed > 55) return "⚠️ CAUTIOUS";
                    return "📊 MIXED";
                  })()}
                </div>
                <p className="text-primary-300 text-xs">
                  Based on Fear & Greed Index, VIX, and market breadth analysis
                </p>
              </div>
            </div>
          </div>
        </motion.section>
      )}

      {/* Analysis Results */}
      {portfolioData && (
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-card-gradient rounded-xl p-6 border border-primary-800/30 shadow-lg"
        >
          <h2 className="text-2xl font-semibold text-primary-50 mb-6">
            Analysis Results
          </h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {Object.values(portfolioData.portfolio_analysis).map((analysis) => (
              <motion.div
                key={analysis.symbol}
                whileHover={{ scale: 1.02 }}
                className="bg-primary-900/50 rounded-lg p-5 border border-primary-800/20"
              >
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-xl font-semibold text-primary-50">{analysis.symbol}</h3>
                    <p className="text-primary-200 text-sm">{analysis.name}</p>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-sm font-medium ${getRiskColor(analysis.risk_level)}`}>
                    {analysis.risk_level} RISK
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <p className="text-primary-400 text-sm">Start Price</p>
                    <p className="text-primary-50 font-semibold">${analysis.start_price}</p>
                  </div>
                  <div>
                    <p className="text-primary-400 text-sm">End Price</p>
                    <p className="text-primary-50 font-semibold">${analysis.end_price}</p>
                  </div>
                  <div>
                    <p className="text-primary-400 text-sm">Total Return</p>
                    <p className={`font-semibold ${analysis.total_return >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {analysis.total_return > 0 ? '+' : ''}{analysis.total_return.toFixed(2)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-primary-400 text-sm">Volatility</p>
                    <p className="text-primary-50 font-semibold">{analysis.volatility.toFixed(2)}%</p>
                  </div>
                  <div>
                    <p className="text-primary-400 text-sm">Sharpe Ratio</p>
                    <p className="text-primary-50 font-semibold">{analysis.sharpe_ratio.toFixed(3)}</p>
                  </div>
                  <div>
                    <p className="text-primary-400 text-sm">AI Recommendation</p>
                    <p className={`font-semibold ${getRecommendationColor(analysis.ai_recommendation)}`}>
                      {analysis.ai_recommendation}
                    </p>
                  </div>
                </div>

                <div className="pt-3 border-t border-primary-800/20">
                  <p className="text-primary-400 text-xs">
                    Last Updated: {new Date(analysis.last_updated).toLocaleString()}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.section>
      )}
    </div>
  );
};

export default Portfolio; 