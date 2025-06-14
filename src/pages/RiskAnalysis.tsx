import {
    CalculatorIcon,
    ChartBarIcon,
    ClockIcon,
    ExclamationTriangleIcon,
    InformationCircleIcon,
    ShieldCheckIcon
} from '@heroicons/react/24/outline';
import axios from 'axios';
import { motion } from 'framer-motion';
import { useState } from 'react';
import toast from 'react-hot-toast';
import { useQuery } from 'react-query';

const API_BASE_URL = 'http://localhost:8001';

interface RiskMetrics {
  value_at_risk: {
    daily_var_95: number;
    daily_var_99: number;
    monthly_var_95: number;
    monthly_var_99: number;
  };
  portfolio_metrics: {
    total_value: number;
    volatility: number;
    sharpe_ratio: number;
    max_drawdown: number;
    beta: number;
  };
  risk_assessment: {
    risk_level: string;
    recommendations: string[];
    stress_test_results: {
      market_crash_scenario: number;
      interest_rate_shock: number;
      currency_crisis: number;
    };
  };
  last_updated: string;
}

interface PortfolioInput {
  symbol: string;
  quantity: number;
  purchase_price: number;
}

const RiskAnalysis = () => {
  const [portfolioInputs, setPortfolioInputs] = useState<PortfolioInput[]>([
    { symbol: '', quantity: 0, purchase_price: 0 }
  ]);
  const [confidenceLevel, setConfidenceLevel] = useState<95 | 99>(95);
  const [timeHorizon, setTimeHorizon] = useState<'daily' | 'monthly'>('daily');

  // Fetch risk analysis
  const { data: riskData, isLoading: riskLoading, refetch: refetchRisk } = useQuery<RiskMetrics>(
    ['risk-analysis', portfolioInputs, confidenceLevel],
    async () => {
      const validInputs = portfolioInputs.filter(p => p.symbol && p.quantity > 0 && p.purchase_price > 0);
      if (validInputs.length === 0) return null;
      
      const response = await axios.post(`${API_BASE_URL}/api/portfolio/risk-analysis`, {
        portfolio: validInputs,
        confidence_level: confidenceLevel / 100,
        time_horizon: timeHorizon
      });
      return response.data;
    },
    {
      enabled: portfolioInputs.some(p => p.symbol && p.quantity > 0 && p.purchase_price > 0),
      onError: () => toast.error('Failed to calculate risk metrics')
    }
  );

  const addPortfolioItem = () => {
    setPortfolioInputs([...portfolioInputs, { symbol: '', quantity: 0, purchase_price: 0 }]);
  };

  const removePortfolioItem = (index: number) => {
    if (portfolioInputs.length > 1) {
      setPortfolioInputs(portfolioInputs.filter((_, i) => i !== index));
    }
  };

  const updatePortfolioItem = (index: number, field: keyof PortfolioInput, value: string | number) => {
    const updated = [...portfolioInputs];
    updated[index] = { ...updated[index], [field]: value };
    setPortfolioInputs(updated);
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel.toUpperCase()) {
      case 'LOW': return 'text-green-400';
      case 'MODERATE': return 'text-yellow-400';
      case 'HIGH': return 'text-red-400';
      default: return 'text-primary-200';
    }
  };

  const getRiskLevelBg = (riskLevel: string) => {
    switch (riskLevel.toUpperCase()) {
      case 'LOW': return 'bg-green-500/20 border-green-500/30';
      case 'MODERATE': return 'bg-yellow-500/20 border-yellow-500/30';
      case 'HIGH': return 'bg-red-500/20 border-red-500/30';
      default: return 'bg-primary-800/20 border-primary-700/30';
    }
  };

  const handleCalculateRisk = () => {
    refetchRisk();
    toast.success('Calculating risk metrics...');
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
          Risk Analysis Center
        </h1>
        <p className="text-lg text-primary-100/80">
          Advanced portfolio risk metrics, VaR calculations, and stress testing
        </p>
      </motion.div>

      {/* Portfolio Input Section */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-card-gradient rounded-xl p-6 border border-primary-800/30 shadow-lg"
      >
        <h2 className="text-2xl font-semibold text-primary-50 mb-4 flex items-center">
          <CalculatorIcon className="h-6 w-6 mr-2 text-accent-emerald" />
          Portfolio Configuration
        </h2>
        
        <div className="space-y-4">
          {portfolioInputs.map((input, index) => (
            <div key={index} className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 bg-primary-900/30 rounded-lg border border-primary-800/20">
              <div>
                <label className="block text-primary-400 text-sm mb-1">Stock Symbol</label>
                <input
                  type="text"
                  placeholder="e.g., AAPL"
                  value={input.symbol}
                  onChange={(e) => updatePortfolioItem(index, 'symbol', e.target.value.toUpperCase())}
                  className="w-full px-3 py-2 bg-primary-900/50 border border-primary-800/30 rounded-lg text-primary-50 placeholder-primary-400 focus:border-accent-emerald focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-primary-400 text-sm mb-1">Quantity</label>
                <input
                  type="number"
                  placeholder="0"
                  value={input.quantity || ''}
                  onChange={(e) => updatePortfolioItem(index, 'quantity', parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 bg-primary-900/50 border border-primary-800/30 rounded-lg text-primary-50 placeholder-primary-400 focus:border-accent-emerald focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-primary-400 text-sm mb-1">Purchase Price ($)</label>
                <input
                  type="number"
                  step="0.01"
                  placeholder="0.00"
                  value={input.purchase_price || ''}
                  onChange={(e) => updatePortfolioItem(index, 'purchase_price', parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 bg-primary-900/50 border border-primary-800/30 rounded-lg text-primary-50 placeholder-primary-400 focus:border-accent-emerald focus:outline-none"
                />
              </div>
              <div className="flex items-end">
                <button
                  onClick={() => removePortfolioItem(index)}
                  disabled={portfolioInputs.length === 1}
                  className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
          
          <div className="flex gap-4">
            <button
              onClick={addPortfolioItem}
              className="px-4 py-2 bg-primary-700 hover:bg-primary-600 text-primary-50 rounded-lg transition-colors"
            >
              Add Stock
            </button>
            <button
              onClick={handleCalculateRisk}
              disabled={riskLoading || !portfolioInputs.some(p => p.symbol && p.quantity > 0 && p.purchase_price > 0)}
              className="px-6 py-2 bg-accent-emerald hover:bg-primary-500 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              <CalculatorIcon className="h-5 w-5 mr-2" />
              {riskLoading ? 'Calculating...' : 'Calculate Risk'}
            </button>
          </div>
        </div>

        {/* Risk Settings */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-primary-400 text-sm mb-2">Confidence Level</label>
            <select
              value={confidenceLevel}
              onChange={(e) => setConfidenceLevel(parseInt(e.target.value) as 95 | 99)}
              className="w-full px-3 py-2 bg-primary-900/50 border border-primary-800/30 rounded-lg text-primary-50 focus:border-accent-emerald focus:outline-none"
            >
              <option value={95}>95%</option>
              <option value={99}>99%</option>
            </select>
          </div>
          <div>
            <label className="block text-primary-400 text-sm mb-2">Time Horizon</label>
            <select
              value={timeHorizon}
              onChange={(e) => setTimeHorizon(e.target.value as 'daily' | 'monthly')}
              className="w-full px-3 py-2 bg-primary-900/50 border border-primary-800/30 rounded-lg text-primary-50 focus:border-accent-emerald focus:outline-none"
            >
              <option value="daily">Daily</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>
        </div>
      </motion.section>

      {/* Risk Analysis Results */}
      {riskData && (
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-card-gradient rounded-xl p-6 border border-primary-800/30 shadow-lg"
        >
          <h2 className="text-2xl font-semibold text-primary-50 mb-6 flex items-center">
            <ExclamationTriangleIcon className="h-6 w-6 mr-2 text-accent-emerald" />
            Risk Assessment Results
          </h2>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Value at Risk */}
            <div className="bg-primary-900/50 rounded-lg p-5 border border-primary-800/20">
              <h3 className="text-lg font-semibold text-primary-50 mb-3 flex items-center">
                <ChartBarIcon className="h-5 w-5 mr-2 text-accent-emerald" />
                Value at Risk (VaR)
              </h3>
              <div className="space-y-3">
                <div>
                  <p className="text-primary-400 text-sm">Daily VaR (95%)</p>
                  <p className="text-xl font-bold text-red-400">
                    -${Math.abs(riskData.value_at_risk.daily_var_95).toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-primary-400 text-sm">Daily VaR (99%)</p>
                  <p className="text-lg font-semibold text-red-300">
                    -${Math.abs(riskData.value_at_risk.daily_var_99).toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-primary-400 text-sm">Monthly VaR (95%)</p>
                  <p className="text-lg font-semibold text-red-300">
                    -${Math.abs(riskData.value_at_risk.monthly_var_95).toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-primary-400 text-sm">Monthly VaR (99%)</p>
                  <p className="text-lg font-semibold text-red-300">
                    -${Math.abs(riskData.value_at_risk.monthly_var_99).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>

            {/* Portfolio Metrics */}
            <div className="bg-primary-900/50 rounded-lg p-5 border border-primary-800/20">
              <h3 className="text-lg font-semibold text-primary-50 mb-3">Portfolio Metrics</h3>
              <div className="space-y-3">
                <div>
                  <p className="text-primary-400 text-sm">Total Value</p>
                  <p className="text-xl font-bold text-white">
                    ${riskData.portfolio_metrics.total_value.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-primary-400 text-sm">Volatility</p>
                  <p className="text-primary-50 font-semibold">
                    {(riskData.portfolio_metrics.volatility * 100).toFixed(2)}%
                  </p>
                </div>
                <div>
                  <p className="text-primary-400 text-sm">Sharpe Ratio</p>
                  <p className={`font-semibold ${
                    riskData.portfolio_metrics.sharpe_ratio > 1 ? 'text-green-400' :
                    riskData.portfolio_metrics.sharpe_ratio > 0.5 ? 'text-yellow-400' : 'text-red-400'
                  }`}>
                    {riskData.portfolio_metrics.sharpe_ratio.toFixed(2)}
                  </p>
                </div>
                <div>
                  <p className="text-primary-400 text-sm">Max Drawdown</p>
                  <p className="text-red-400 font-semibold">
                    {(riskData.portfolio_metrics.max_drawdown * 100).toFixed(2)}%
                  </p>
                </div>
                <div>
                  <p className="text-primary-400 text-sm">Beta</p>
                  <p className="text-primary-50 font-semibold">
                    {riskData.portfolio_metrics.beta.toFixed(2)}
                  </p>
                </div>
              </div>
            </div>

            {/* Risk Assessment */}
            <div className="bg-primary-900/50 rounded-lg p-5 border border-primary-800/20">
              <h3 className="text-lg font-semibold text-primary-50 mb-3 flex items-center">
                <ShieldCheckIcon className="h-5 w-5 mr-2 text-accent-emerald" />
                Risk Assessment
              </h3>
              <div className="space-y-4">
                <div>
                  <p className="text-primary-400 text-sm mb-2">Risk Level</p>
                  <div className={`px-3 py-2 rounded-lg border ${getRiskLevelBg(riskData.risk_assessment.risk_level)}`}>
                    <p className={`font-semibold text-center ${getRiskLevelColor(riskData.risk_assessment.risk_level)}`}>
                      {riskData.risk_assessment.risk_level.toUpperCase()}
                    </p>
                  </div>
                </div>
                
                <div>
                  <p className="text-primary-400 text-sm mb-2">Recommendations</p>
                  <div className="space-y-2">
                    {riskData.risk_assessment.recommendations.map((rec, index) => (
                      <div key={index} className="flex items-start">
                        <InformationCircleIcon className="h-4 w-4 text-accent-emerald mt-0.5 mr-2 flex-shrink-0" />
                        <p className="text-primary-200 text-sm">{rec}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Stress Test Results */}
          <div className="mt-6 bg-primary-900/50 rounded-lg p-5 border border-primary-800/20">
            <h3 className="text-lg font-semibold text-primary-50 mb-3">Stress Test Scenarios</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
                <h4 className="text-red-400 font-semibold mb-2">Market Crash</h4>
                <p className="text-red-300 text-2xl font-bold">
                  {riskData.risk_assessment.stress_test_results.market_crash_scenario.toFixed(1)}%
                </p>
                <p className="text-primary-400 text-sm">Portfolio loss in severe market downturn</p>
              </div>
              <div className="p-4 bg-orange-500/10 border border-orange-500/20 rounded-lg">
                <h4 className="text-orange-400 font-semibold mb-2">Interest Rate Shock</h4>
                <p className="text-orange-300 text-2xl font-bold">
                  {riskData.risk_assessment.stress_test_results.interest_rate_shock.toFixed(1)}%
                </p>
                <p className="text-primary-400 text-sm">Impact of sudden rate changes</p>
              </div>
              <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                <h4 className="text-yellow-400 font-semibold mb-2">Currency Crisis</h4>
                <p className="text-yellow-300 text-2xl font-bold">
                  {riskData.risk_assessment.stress_test_results.currency_crisis.toFixed(1)}%
                </p>
                <p className="text-primary-400 text-sm">Loss from currency volatility</p>
              </div>
            </div>
          </div>

          <div className="mt-4 flex items-center text-primary-400 text-sm">
            <ClockIcon className="h-4 w-4 mr-1" />
            Last Updated: {new Date(riskData.last_updated).toLocaleString()}
          </div>
        </motion.section>
      )}

      {/* Risk Education */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-card-gradient rounded-xl p-6 border border-primary-800/30 shadow-lg"
      >
        <h2 className="text-2xl font-semibold text-primary-50 mb-4">Understanding Risk Metrics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="p-4 bg-accent-emerald/10 border border-accent-emerald/20 rounded-lg">
              <h3 className="text-accent-emerald font-semibold mb-2">Value at Risk (VaR)</h3>
              <p className="text-primary-200 text-sm">
                The maximum expected loss over a given time period at a certain confidence level. 
                For example, a daily 95% VaR of $1,000 means there's a 5% chance of losing more than $1,000 in a day.
              </p>
            </div>
            <div className="p-4 bg-primary-800/30 border border-primary-700/20 rounded-lg">
              <h3 className="text-primary-50 font-semibold mb-2">Sharpe Ratio</h3>
              <p className="text-primary-200 text-sm">
                Measures risk-adjusted returns. Higher is better. Above 1.0 is good, above 2.0 is excellent.
              </p>
            </div>
          </div>
          <div className="space-y-4">
            <div className="p-4 bg-primary-800/30 border border-primary-700/20 rounded-lg">
              <h3 className="text-primary-50 font-semibold mb-2">Beta</h3>
              <p className="text-primary-200 text-sm">
                Measures portfolio sensitivity to market movements. Beta &gt; 1 means more volatile than market, 
                Beta &lt; 1 means less volatile.
              </p>
            </div>
            <div className="p-4 bg-primary-800/30 border border-primary-700/20 rounded-lg">
              <h3 className="text-primary-50 font-semibold mb-2">Max Drawdown</h3>
              <p className="text-primary-200 text-sm">
                The largest peak-to-trough decline in portfolio value. Lower percentages indicate better downside protection.
              </p>
            </div>
          </div>
        </div>
      </motion.section>
    </div>
  );
};

export default RiskAnalysis; 