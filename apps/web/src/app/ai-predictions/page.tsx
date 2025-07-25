"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import AdaptiveLoadingAnimation from '@/components/AdaptiveLoadingAnimation';

interface AnalysisResult {
  prediction: string;
  confidence: number;
  factors: string[];
  timeframe: string;
}

export default function AIPredictionsPage() {
  const router = useRouter();
  const [selectedCrypto, setSelectedCrypto] = useState('bitcoin');
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // State for Quick Actions functionality
  const [showComparisonModal, setShowComparisonModal] = useState(false);
  const [showAlertsModal, setShowAlertsModal] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [showExportSuccess, setShowExportSuccess] = useState(false);
  const [selectedCryptos, setSelectedCryptos] = useState<string[]>([]);

  const popularCryptos = [
    { id: 'bitcoin', name: 'Bitcoin', symbol: 'BTC' },
    { id: 'ethereum', name: 'Ethereum', symbol: 'ETH' },
    { id: 'binancecoin', name: 'Binance Coin', symbol: 'BNB' },
    { id: 'cardano', name: 'Cardano', symbol: 'ADA' },
    { id: 'solana', name: 'Solana', symbol: 'SOL' },
    { id: 'polkadot', name: 'Polkadot', symbol: 'DOT' }
  ];

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    setError(null);
    
    try {
      const response = await fetch('/api/ai/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbol: selectedCrypto,
          timeframe: '7d'
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get AI prediction');
      }

      const data = await response.json();
      setAnalysisResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('AI prediction error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'success';
    if (confidence >= 60) return 'warning';
    return 'error';
  };

  // Quick Actions handlers
  const handleViewMarketCharts = () => {
    router.push(`/market?symbol=${selectedCrypto}`);
  };

  const handleComparePredictions = () => {
    setShowComparisonModal(true);
  };

  const handleExportAnalysis = async () => {
    if (!analysisResult) {
      alert('No analysis data to export. Please generate a prediction first.');
      return;
    }

    setIsExporting(true);
    try {
      // Create export data
      const exportData = {
        cryptocurrency: selectedCrypto,
        analysis_date: new Date().toISOString(),
        prediction: analysisResult.prediction,
        confidence: analysisResult.confidence,
        factors: analysisResult.factors,
        timeframe: analysisResult.timeframe,
        generated_by: 'AI Crypto Analytics Platform'
      };

      // Generate PDF-style export (simplified version)
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `crypto-ai-analysis-${selectedCrypto}-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      setShowExportSuccess(true);
      setTimeout(() => setShowExportSuccess(false), 3000);
    } catch (error) {
      console.error('Export failed:', error);
      alert('Export failed. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  const handleSetPriceAlerts = () => {
    setShowAlertsModal(true);
  };

  const handleSavePriceAlert = (alertData: { symbol: string; threshold: number; type: 'above' | 'below'; }) => {
    // Save to localStorage for persistence
    const alerts = JSON.parse(localStorage.getItem('priceAlerts') || '[]');
    const newAlert = {
      id: Date.now(),
      ...alertData,
      created: new Date().toISOString(),
      enabled: true
    };
    alerts.push(newAlert);
    localStorage.setItem('priceAlerts', JSON.stringify(alerts));

    // Request notification permission
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }

    setShowAlertsModal(false);
    alert('Price alert configured successfully!');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-50 to-neutral-100 dark:from-neutral-900 dark:to-neutral-800">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-gradient mb-4">
            🤖 AI Cryptocurrency Predictions
          </h1>
          <p className="text-lg text-neutral-600 dark:text-neutral-400 max-w-3xl mx-auto">
            Leverage advanced machine learning algorithms to analyze market trends, 
            social sentiment, and technical indicators for intelligent cryptocurrency predictions.
          </p>
        </div>

        {/* Cryptocurrency Selection */}
        <Card variant="elevated" className="mb-8">
          <CardHeader>
            <h2 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
              Select Cryptocurrency
            </h2>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {popularCryptos.map((crypto) => (
                <button
                  key={crypto.id}
                  onClick={() => setSelectedCrypto(crypto.id)}
                  className={`
                    p-4 rounded-xl border-2 transition-all duration-200 font-medium
                    focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
                    ${selectedCrypto === crypto.id
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                      : 'border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 hover:border-neutral-300 dark:hover:border-neutral-600 hover:bg-neutral-50 dark:hover:bg-neutral-700'
                    }
                  `}
                  aria-label={`Select ${crypto.name} for analysis`}
                  aria-pressed={selectedCrypto === crypto.id}
                >
                  <div className="font-bold text-lg mb-1">{crypto.symbol}</div>
                  <div className="text-sm opacity-75">{crypto.name}</div>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Analysis Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Analysis Panel */}
          <div className="lg:col-span-2">
            <Card variant="elevated">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
                    AI Market Analysis
                  </h2>
                  <Button 
                    onClick={handleAnalyze}
                    loading={isAnalyzing}
                    disabled={isAnalyzing}
                    variant="primary"
                  >
                    {analysisResult ? 'Refresh Analysis' : 'Generate Prediction'}
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {isAnalyzing ? (
                  <div className="flex flex-col items-center justify-center py-12">
                    <AdaptiveLoadingAnimation isVisible={true} task="ai_analysis" customMessage="Analyzing cryptocurrency data..." />
                    <div className="mt-6 text-center">
                      <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-2">
                        Analyzing Market Data...
                      </h3>
                      <p className="text-neutral-600 dark:text-neutral-400">
                        Processing technical indicators, market sentiment, and historical patterns
                      </p>
                    </div>
                  </div>
                ) : error ? (
                  <div className="text-center py-12">
                    <div className="text-4xl mb-4">⚠️</div>
                    <h3 className="text-xl font-bold text-error-600 mb-2">Analysis Failed</h3>
                    <p className="text-neutral-600 dark:text-neutral-400 mb-4">{error}</p>
                    <Button onClick={handleAnalyze} variant="outline">
                      Try Again
                    </Button>
                  </div>
                ) : analysisResult ? (
                  <div className="space-y-6">
                    {/* Prediction Summary */}
                    <div className="bg-gradient-to-r from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 rounded-xl p-6">
                      <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-3">
                        Prediction Summary
                      </h3>
                      <p className="text-neutral-700 dark:text-neutral-300 text-lg leading-relaxed">
                        {analysisResult.prediction}
                      </p>
                    </div>

                    {/* Confidence Meter */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
                          Confidence Level
                        </span>
                        <Badge 
                          variant={getConfidenceColor(analysisResult.confidence) as any}
                          size="sm"
                        >
                          {analysisResult.confidence}%
                        </Badge>
                      </div>
                      <div className="w-full bg-neutral-200 dark:bg-neutral-700 rounded-full h-3">
                        <div 
                          className={`h-3 rounded-full transition-all duration-500 ${
                            analysisResult.confidence >= 80 ? 'bg-success-500' :
                            analysisResult.confidence >= 60 ? 'bg-warning-500' : 'bg-error-500'
                          }`}
                          style={{ width: `${analysisResult.confidence}%` }}
                        />
                      </div>
                    </div>

                    {/* Key Factors */}
                    <div>
                      <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-3">
                        Key Analysis Factors
                      </h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {analysisResult.factors.map((factor) => (
                          <div 
                            key={factor}
                            className="flex items-center space-x-2 p-3 bg-neutral-50 dark:bg-neutral-800 rounded-lg"
                          >
                            <div className="w-2 h-2 bg-primary-500 rounded-full" />
                            <span className="text-sm text-neutral-700 dark:text-neutral-300">
                              {factor}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Timeframe */}
                    <div className="flex items-center justify-between p-4 bg-neutral-50 dark:bg-neutral-800 rounded-lg">
                      <span className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
                        Analysis Timeframe
                      </span>
                      <Badge variant="info" size="sm">
                        {analysisResult.timeframe}
                      </Badge>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <div className="text-4xl mb-4">🔮</div>
                    <h3 className="text-xl font-bold text-neutral-900 dark:text-neutral-100 mb-2">
                      Ready for AI Analysis
                    </h3>
                    <p className="text-neutral-600 dark:text-neutral-400 mb-4">
                      Click "Generate Prediction" to analyze {popularCryptos.find(c => c.id === selectedCrypto)?.name} using advanced AI algorithms
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* AI Features */}
            <Card variant="elevated">
              <CardHeader>
                <h3 className="text-xl font-bold text-neutral-900 dark:text-neutral-100">
                  AI Features
                </h3>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start space-x-3">
                  <div className="text-2xl">📊</div>
                  <div>
                    <h4 className="font-semibold text-neutral-900 dark:text-neutral-100">
                      Technical Analysis
                    </h4>
                    <p className="text-sm text-neutral-600 dark:text-neutral-400">
                      Advanced pattern recognition and trend analysis
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <div className="text-2xl">💬</div>
                  <div>
                    <h4 className="font-semibold text-neutral-900 dark:text-neutral-100">
                      Sentiment Analysis
                    </h4>
                    <p className="text-sm text-neutral-600 dark:text-neutral-400">
                      Social media and news sentiment tracking
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <div className="text-2xl">🧠</div>
                  <div>
                    <h4 className="font-semibold text-neutral-900 dark:text-neutral-100">
                      Machine Learning
                    </h4>
                    <p className="text-sm text-neutral-600 dark:text-neutral-400">
                      Neural networks trained on historical data
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <div className="text-2xl">⚡</div>
                  <div>
                    <h4 className="font-semibold text-neutral-900 dark:text-neutral-100">
                      Real-time Data
                    </h4>
                    <p className="text-sm text-neutral-600 dark:text-neutral-400">
                      Live market data integration and analysis
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Disclaimer */}
            <Card variant="outlined">
              <CardContent className="p-4">
                <div className="flex items-start space-x-2">
                  <div className="text-warning-500 text-lg">⚠️</div>
                  <div>
                    <h4 className="font-semibold text-neutral-900 dark:text-neutral-100 text-sm mb-1">
                      Investment Disclaimer
                    </h4>
                    <p className="text-xs text-neutral-600 dark:text-neutral-400 leading-relaxed">
                      AI predictions are for informational purposes only and should not be considered as financial advice. 
                      Cryptocurrency markets are highly volatile and unpredictable. Always do your own research and 
                      consult with financial advisors before making investment decisions.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card variant="elevated">
              <CardHeader>
                <h3 className="text-xl font-bold text-neutral-900 dark:text-neutral-100">
                  Quick Actions
                </h3>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={handleViewMarketCharts}
                >
                  📈 View Market Charts
                </Button>
                
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={handleComparePredictions}
                >
                  📊 Compare Predictions
                </Button>
                
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={handleExportAnalysis}
                  loading={isExporting}
                  disabled={!analysisResult}
                >
                  {isExporting ? '📋 Exporting...' : '📋 Export Analysis'}
                </Button>
                
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={handleSetPriceAlerts}
                >
                  🔔 Set Price Alerts
                </Button>

                {/* Export Success Message */}
                {showExportSuccess && (
                  <div className="text-center p-2 bg-success-50 dark:bg-success-900/20 text-success-700 dark:text-success-300 rounded-lg text-sm">
                    ✅ Analysis exported successfully!
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Comparison Modal */}
            {showComparisonModal && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
                  <h2 className="text-xl font-bold mb-4">Compare Predictions</h2>
                  <p className="text-gray-600 mb-4">Select cryptocurrencies to compare predictions:</p>
                  
                  <div className="space-y-2 mb-6">
                    {['bitcoin', 'ethereum', 'cardano', 'solana', 'polkadot'].map((crypto) => (
                      <label key={crypto} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={selectedCryptos.includes(crypto)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedCryptos([...selectedCryptos, crypto]);
                            } else {
                              setSelectedCryptos(selectedCryptos.filter(c => c !== crypto));
                            }
                          }}
                          className="rounded"
                        />
                        <span className="capitalize">{crypto}</span>
                      </label>
                    ))}
                  </div>

                  <div className="flex space-x-4">
                    <Button
                      onClick={() => {
                        if (selectedCryptos.length > 0) {
                          router.push(`/ai-predictions/compare?symbols=${selectedCryptos.join(',')}`);
                        }
                      }}
                      disabled={selectedCryptos.length === 0}
                    >
                      Compare Selected
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => setShowComparisonModal(false)}
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              </div>
            )}

            {/* Price Alerts Modal */}
            {showAlertsModal && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                  <h2 className="text-xl font-bold mb-4">Set Price Alert</h2>
                  <form onSubmit={(e) => {
                    e.preventDefault();
                    const formData = new FormData(e.target as HTMLFormElement);
                    handleSavePriceAlert({
                      symbol: selectedCrypto,
                      threshold: Number(formData.get('threshold')),
                      type: formData.get('type') as 'above' | 'below'
                    });
                  }}>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium mb-1">Cryptocurrency</label>
                        <input
                          type="text"
                          value={selectedCrypto}
                          disabled
                          className="w-full p-2 border rounded bg-gray-100 capitalize"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium mb-1">Price Threshold</label>
                        <input
                          name="threshold"
                          type="number"
                          step="0.01"
                          required
                          className="w-full p-2 border rounded"
                          placeholder="Enter price threshold"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium mb-1">Alert Type</label>
                        <select name="type" required className="w-full p-2 border rounded">
                          <option value="above">Alert when price goes above</option>
                          <option value="below">Alert when price goes below</option>
                        </select>
                      </div>
                    </div>

                    <div className="flex space-x-4 mt-6">
                      <Button type="submit" className="flex-1">
                        Create Alert
                      </Button>
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => setShowAlertsModal(false)}
                        className="flex-1"
                      >
                        Cancel
                      </Button>
                    </div>
                  </form>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
} 