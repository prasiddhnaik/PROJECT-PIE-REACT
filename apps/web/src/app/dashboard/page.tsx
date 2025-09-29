'use client'

import { useState, useEffect } from 'react'
import { Metadata } from 'next'

export default function DashboardPage() {
  const [selectedStock, setSelectedStock] = useState('AAPL')
  const [marketData, setMarketData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchMarketData()
    const interval = setInterval(fetchMarketData, 30000) // Update every 30 seconds
    return () => clearInterval(interval)
  }, [selectedStock])

  const fetchMarketData = async () => {
    try {
      const response = await fetch(`/api/stock-data?symbol=${selectedStock}`)
      const data = await response.json()
      setMarketData(data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching market data:', error)
      setLoading(false)
    }
  }

  const stocks = [
    { symbol: 'AAPL', name: 'Apple Inc.' },
    { symbol: 'GOOGL', name: 'Alphabet Inc.' },
    { symbol: 'MSFT', name: 'Microsoft Corp.' },
    { symbol: 'TSLA', name: 'Tesla Inc.' },
    { symbol: 'AMZN', name: 'Amazon.com Inc.' },
    { symbol: 'NVDA', name: 'NVIDIA Corp.' },
  ]

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Navigation */}
      <nav className="border-b border-gray-800 bg-black/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="text-2xl font-bold">FinanceOS</div>
            <div className="flex items-center space-x-6">
              <div className="text-sm text-gray-400">
                Live Market Data • {new Date().toLocaleTimeString()}
              </div>
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Stock Selection */}
        <div className="mb-8">
          <h1 className="text-3xl font-light mb-6">Market Dashboard</h1>
          <div className="flex flex-wrap gap-2">
            {stocks.map((stock) => (
              <button
                key={stock.symbol}
                onClick={() => setSelectedStock(stock.symbol)}
                className={`px-4 py-2 rounded-md border transition-all ${
                  selectedStock === stock.symbol
                    ? 'bg-white text-black border-white'
                    : 'bg-black text-gray-300 border-gray-700 hover:border-gray-500'
                }`}
              >
                {stock.symbol}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Chart Area */}
            <div className="lg:col-span-2">
              <div className="bg-gray-900/30 border border-gray-800 rounded-lg p-6">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-2xl font-semibold">{selectedStock}</h2>
                    <p className="text-gray-400">{stocks.find(s => s.symbol === selectedStock)?.name}</p>
                  </div>
                  {marketData && (
                    <div className="text-right">
                      <div className="text-3xl font-bold">
                        ${marketData.currentPrice?.toFixed(2) || '---'}
                      </div>
                      <div className={`text-sm ${
                        marketData.change >= 0 ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {marketData.change >= 0 ? '+' : ''}
                        {marketData.change?.toFixed(2)} ({marketData.changePercent?.toFixed(2)}%)
                      </div>
                    </div>
                  )}
                </div>

                {/* Chart Placeholder */}
                <div className="h-64 bg-black border border-gray-800 rounded-lg flex items-center justify-center mb-6">
                  <div className="text-center">
                    <div className="text-4xl mb-2">📈</div>
                    <div className="text-gray-400">Interactive Chart</div>
                    <div className="text-xs text-gray-500 mt-1">Real-time price movements</div>
                  </div>
                </div>

                {/* Time Period Buttons */}
                <div className="flex space-x-2">
                  {['1D', '5D', '1M', '3M', '6M', '1Y'].map((period) => (
                    <button
                      key={period}
                      className="px-3 py-1 text-sm border border-gray-700 rounded hover:border-gray-500 transition-colors"
                    >
                      {period}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Technical Indicators */}
            <div className="space-y-6">
              <div className="bg-gray-900/30 border border-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Technical Indicators</h3>
                {marketData?.indicators ? (
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span className="text-gray-400">RSI (14)</span>
                      <span className={`font-mono ${
                        marketData.indicators.rsi?.[0] > 70 ? 'text-red-400' : 
                        marketData.indicators.rsi?.[0] < 30 ? 'text-green-400' : 'text-gray-300'
                      }`}>
                        {marketData.indicators.rsi?.[marketData.indicators.rsi.length - 1]?.toFixed(1) || '--'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">MACD</span>
                      <span className="font-mono text-gray-300">
                        {marketData.indicators.macd?.MACD?.[marketData.indicators.macd.MACD.length - 1]?.toFixed(3) || '--'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Signal</span>
                      <span className="font-mono text-gray-300">
                        {marketData.indicators.macd?.signal?.[marketData.indicators.macd.signal.length - 1]?.toFixed(3) || '--'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">SMA (20)</span>
                      <span className="font-mono text-gray-300">
                        {marketData.indicators.sma20?.[marketData.indicators.sma20.length - 1]?.toFixed(2) || '--'}
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="text-gray-500">Loading indicators...</div>
                )}
              </div>

              <div className="bg-gray-900/30 border border-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Bollinger Bands</h3>
                {marketData?.indicators?.bollingerBands ? (
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Upper</span>
                      <span className="font-mono text-green-400">
                        {marketData.indicators.bollingerBands.upper?.[marketData.indicators.bollingerBands.upper.length - 1]?.toFixed(2) || '--'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Middle</span>
                      <span className="font-mono text-gray-300">
                        {marketData.indicators.bollingerBands.middle?.[marketData.indicators.bollingerBands.middle.length - 1]?.toFixed(2) || '--'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Lower</span>
                      <span className="font-mono text-red-400">
                        {marketData.indicators.bollingerBands.lower?.[marketData.indicators.bollingerBands.lower.length - 1]?.toFixed(2) || '--'}
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="text-gray-500">Loading bands...</div>
                )}
              </div>

              <div className="bg-gray-900/30 border border-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
                <div className="space-y-3">
                  <button className="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded-md transition-colors">
                    Buy {selectedStock}
                  </button>
                  <button className="w-full bg-red-600 hover:bg-red-700 text-white py-2 rounded-md transition-colors">
                    Sell {selectedStock}
                  </button>
                  <button className="w-full border border-gray-600 hover:border-gray-500 text-white py-2 rounded-md transition-colors">
                    Add to Watchlist
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Market Overview */}
        <div className="mt-12">
          <h2 className="text-2xl font-light mb-6">Market Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-gray-900/30 border border-gray-800 rounded-lg p-6 text-center">
              <div className="text-2xl font-bold text-green-400 mb-1">24,467.80</div>
              <div className="text-gray-400 mb-1">NIFTY 50</div>
              <div className="text-green-400 text-sm">+1.2% today</div>
            </div>
            <div className="bg-gray-900/30 border border-gray-800 rounded-lg p-6 text-center">
              <div className="text-2xl font-bold text-green-400 mb-1">80,845.00</div>
              <div className="text-gray-400 mb-1">SENSEX</div>
              <div className="text-green-400 text-sm">+0.8% today</div>
            </div>
            <div className="bg-gray-900/30 border border-gray-800 rounded-lg p-6 text-center">
              <div className="text-2xl font-bold text-red-400 mb-1">51,234.50</div>
              <div className="text-gray-400 mb-1">BANK NIFTY</div>
              <div className="text-red-400 text-sm">-0.3% today</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}


