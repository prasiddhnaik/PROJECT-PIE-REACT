"use client";

import { useState, useEffect } from "react";
import { useRouter } from 'next/navigation';
import { useTop100Crypto } from '@/hooks/useTop100';
import { useTrendingCrypto } from '@/hooks/useTrendingCrypto';
import CryptoChart from '@/components/CryptoChart';
import CryptoSearch from '../../components/CryptoSearch';
import DebugApiTest from '../../components/DebugApiTest';
import { ThemeToggle } from '@/components/ThemeProvider';
import PerformanceMonitor from '../../components/PerformanceMonitor';

export default function CryptoAnalyticsPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'trending' | 'top100' | 'watchlist'>('top100');
  
  const { data: top100Data, isLoading: top100Loading, error: top100Error } = useTop100Crypto();
  const { data: trendingData, isLoading: trendingLoading, error: trendingError } = useTrendingCrypto();

  const formatPrice = (price: number | null | undefined): string => {
    if (price === null || price === undefined || isNaN(price)) return '—';
    
    if (price < 0.01) {
      return `$${price.toFixed(8)}`;
    } else if (price < 1) {
      return `$${price.toFixed(4)}`;
    } else {
      return `$${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }
  };

  const formatMarketCap = (marketCap: number | null | undefined): string => {
    if (marketCap === null || marketCap === undefined || isNaN(marketCap)) return '—';
    
    if (marketCap >= 1e12) {
      return `$${(marketCap / 1e12).toFixed(2)}T`;
    } else if (marketCap >= 1e9) {
      return `$${(marketCap / 1e9).toFixed(2)}B`;
    } else if (marketCap >= 1e6) {
      return `$${(marketCap / 1e6).toFixed(2)}M`;
    } else {
      return `$${marketCap.toLocaleString()}`;
    }
  };

  const getChangeColor = (change: number) => {
    if (change > 0) return "status-positive";
    if (change < 0) return "status-negative";
    return "status-neutral";
  };

  const getChangeIcon = (change: number) => {
    if (change > 0) return "📈";
    if (change < 0) return "📉";
    return "➡️";
  };

  const handleCryptoSelect = (crypto: any) => {
    router.push(`/crypto/${crypto.id}`);
  };

  const renderCryptoCard = (crypto: any) => (
    <div key={crypto.id || crypto.symbol} className="crypto-card card-hover p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div 
            className="w-12 h-12 rounded-full flex items-center justify-center text-lg font-bold"
            style={{ background: 'var(--gradient-primary)' }}
          >
            <span className="text-white font-bold text-lg">
              {crypto.symbol ? crypto.symbol.slice(0, 2).toUpperCase() : '₿'}
            </span>
          </div>
          <div>
            <h3 className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>{crypto.symbol?.toUpperCase()}</h3>
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>{crypto.name}</p>
          </div>
        </div>
        <div className="text-right">
          {crypto.market_cap_rank && (
            <div className="px-2 py-1 rounded-full text-xs font-medium mb-1 status-positive">
              #{crypto.market_cap_rank}
            </div>
          )}
        </div>
      </div>

      {/* Mini Chart */}
      <div className="mb-4" style={{ height: '120px' }}>
        <CryptoChart 
          symbol={crypto.symbol?.toLowerCase() || crypto.id}
          days={7}
          height={120}
          chartType="area"
          showVolume={false}
        />
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Current Price</p>
          <p className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
            {formatPrice(crypto.current_price)}
          </p>
        </div>
        <div>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Market Cap</p>
          <p className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
            {formatMarketCap(crypto.market_cap)}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <div>
          <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>1h Change</p>
          <p className={`text-sm font-medium ${getChangeColor(crypto.price_change_percent_1h || 0)}`}>
            {getChangeIcon(crypto.price_change_percent_1h || 0)} {(crypto.price_change_percent_1h || 0).toFixed(2)}%
          </p>
        </div>
        <div>
          <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>24h Change</p>
          <p className={`text-sm font-medium ${getChangeColor(crypto.price_change_percent_24h || 0)}`}>
            {getChangeIcon(crypto.price_change_percent_24h || 0)} {(crypto.price_change_percent_24h || 0).toFixed(2)}%
          </p>
        </div>
        <div>
          <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>7d Change</p>
          <p className={`text-sm font-medium ${getChangeColor(crypto.price_change_percent_7d || 0)}`}>
            {getChangeIcon(crypto.price_change_percent_7d || 0)} {(crypto.price_change_percent_7d || 0).toFixed(2)}%
          </p>
        </div>
      </div>

              {crypto.volume_24h && (
          <div className="border-t pt-3 mb-4" style={{ borderColor: 'var(--border)' }}>
            <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>24h Volume</p>
            <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
              {formatMarketCap(crypto.volume_24h)}
            </p>
          </div>
        )}

      {/* Trading Actions */}
      <div className="flex space-x-2 mt-4">
        <button
          onClick={() => router.push(`/crypto/${crypto.symbol?.toLowerCase()}`)}
          className="flex-1 btn-secondary py-2 px-4 text-sm font-medium"
        >
          📊 Analyze
        </button>
        <button
          onClick={() => {
            // Mock trading functionality - you can replace with real trading logic
            alert(`🚀 Mock Buy Order for ${crypto.symbol}\nPrice: ${formatPrice(crypto.current_price)}\n\nIn a real trading app, this would open a buy order dialog.`);
          }}
          className="flex-1 text-white py-2 px-4 rounded-lg text-sm font-medium transition-colors hover:opacity-90"
          style={{ background: 'var(--accent-green)' }}
        >
          💰 Buy
        </button>
        <button
          onClick={() => {
            // Mock trading functionality - you can replace with real trading logic
            alert(`📉 Mock Sell Order for ${crypto.symbol}\nPrice: ${formatPrice(crypto.current_price)}\n\nIn a real trading app, this would open a sell order dialog.`);
          }}
          className="flex-1 text-white py-2 px-4 rounded-lg text-sm font-medium transition-colors hover:opacity-90"
          style={{ background: 'var(--accent-red)' }}
        >
          📈 Sell
        </button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen p-6 animate-fade-in" style={{ background: 'var(--background)' }}>
      {/* Header */}
      <header className="crypto-card shadow-sm border-b mb-8" style={{ borderColor: 'var(--border)' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <button
                onClick={() => router.back()}
                className="w-10 h-10 rounded-lg flex items-center justify-center transition-colors btn-primary"
              >
                <span className="text-white font-bold">←</span>
              </button>
              <div>
                <h1 className="text-2xl font-bold gradient-text">
                  🚀 Crypto Trading Hub
                </h1>
                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                  Real-time cryptocurrency analytics and trading platform
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <ThemeToggle />
              <button
                onClick={() => {
                  alert('🎯 Market Scanner\n\nThis would open a crypto market scanner to find trading opportunities based on:\n• Technical indicators\n• Volume spikes\n• Price breakouts\n• News sentiment');
                }}
                className="px-4 py-2 text-white rounded-lg text-sm font-medium transition-colors btn-primary"
              >
                🎯 Scanner
              </button>
              <button
                onClick={() => {
                  alert('📝 Portfolio\n\nThis would open your crypto portfolio showing:\n• Current holdings\n• P&L summary\n• Asset allocation\n• Trade history');
                }}
                className="px-4 py-2 text-white rounded-lg text-sm font-medium transition-colors btn-secondary"
              >
                📝 Portfolio
              </button>
              <div className="px-3 py-1 rounded-full text-sm font-medium status-positive">
                🟢 Live Data
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Section */}
        <div className="mb-8">
          <div className="crypto-card p-6">
            <h2 className="text-lg font-semibold mb-4 gradient-text">
              🔍 Search Cryptocurrencies
            </h2>
            <CryptoSearch 
              onSelect={handleCryptoSelect}
              placeholder="Search Bitcoin, Ethereum, Solana..."
              className="w-full max-w-2xl"
            />
            <p className="text-sm mt-2" style={{ color: 'var(--text-secondary)' }}>
              Type any cryptocurrency name or symbol to find detailed analysis and charts
            </p>
          </div>
        </div>

        {/* Debug Section - Temporary */}
        <div className="mb-8">
          <DebugApiTest />
        </div>

        {/* Featured Charts Section */}
        <div className="mb-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div className="crypto-card p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div 
                    className="w-10 h-10 rounded-full flex items-center justify-center text-lg font-bold"
                    style={{ background: 'var(--gradient-primary)' }}
                  >
                    <span className="text-white font-bold">₿</span>
                  </div>
                  <div>
                    <h3 className="text-xl font-bold gradient-text">Bitcoin (BTC)</h3>
                    <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>The original cryptocurrency</p>
                  </div>
                </div>
                <div className="px-3 py-1 rounded-full text-xs font-medium status-positive">
                  #1
                </div>
              </div>
              <CryptoChart 
                symbol="btc"
                days={30}
                height={200}
                chartType="area"
                showVolume={false}
              />
            </div>
            
            <div className="crypto-card p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div 
                    className="w-10 h-10 rounded-full flex items-center justify-center text-lg font-bold"
                    style={{ background: 'linear-gradient(135deg, #627eea, #8a92b2)' }}
                  >
                    <span className="text-white font-bold">Ξ</span>
                  </div>
                  <div>
                    <h3 className="text-xl font-bold gradient-text">Ethereum (ETH)</h3>
                    <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Smart contract platform</p>
                  </div>
                </div>
                <div className="px-3 py-1 rounded-full text-xs font-medium status-positive">
                  #2
                </div>
              </div>
              <CryptoChart 
                symbol="eth"
                days={30}
                height={200}
                chartType="area"
                showVolume={false}
              />
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="mb-8">
          <div className="flex space-x-4 mb-6">
            <button
              onClick={() => setActiveTab('top100')}
              className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                activeTab === 'top100'
                  ? 'btn-primary'
                  : 'btn-secondary'
              }`}
            >
              📊 Top 50 Cryptocurrencies
            </button>
            <button
              onClick={() => setActiveTab('trending')}
              className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                activeTab === 'trending'
                  ? 'btn-primary'
                  : 'btn-secondary'
              }`}
            >
              🔥 Trending Crypto
            </button>
            <button
              onClick={() => setActiveTab('watchlist')}
              className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                activeTab === 'watchlist'
                  ? 'btn-primary'
                  : 'btn-secondary'
              }`}
            >
              ⭐ My Watchlist
            </button>
          </div>

          {/* Summary Stats */}
          {activeTab === 'top100' && top100Data && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="crypto-card card-hover p-4">
                <div className="flex items-center">
                  <span className="text-2xl mr-3">🪙</span>
                  <div>
                    <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Total Cryptocurrencies</p>
                    <p className="text-xl font-bold gradient-text">{top100Data.count}</p>
                  </div>
                </div>
              </div>
              <div className="crypto-card card-hover p-4">
                <div className="flex items-center">
                  <span className="text-2xl mr-3">💰</span>
                  <div>
                    <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Total Market Cap</p>
                    <p className="text-xl font-bold gradient-text">
                      {formatMarketCap(top100Data.total_market_cap)}
                    </p>
                  </div>
                </div>
              </div>
              <div className="crypto-card card-hover p-4">
                <div className="flex items-center">
                  <span className="text-2xl mr-3">📈</span>
                  <div>
                    <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Average 24h Change</p>
                                         <p className={`text-xl font-bold ${getChangeColor(
                       top100Data.data.reduce((sum: number, crypto: any) => sum + (crypto.price_change_percent_24h || 0), 0) / top100Data.data.length
                     )}`}>
                       {((top100Data.data.reduce((sum: number, crypto: any) => sum + (crypto.price_change_percent_24h || 0), 0) / top100Data.data.length) || 0).toFixed(2)}%
                    </p>
                  </div>
                </div>
              </div>
              <div className="crypto-card card-hover p-4">
                <div className="flex items-center">
                  <span className="text-2xl mr-3">⏰</span>
                  <div>
                    <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Last Updated</p>
                    <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                      {new Date(top100Data.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Content */}
        {activeTab === 'top100' && (
          <div>
            {top100Loading && (
              <div className="crypto-card p-8 text-center">
                <div className="loading-spinner mx-auto mb-4"></div>
                <p style={{ color: 'var(--text-secondary)' }}>Loading top 50 cryptocurrencies...</p>
              </div>
            )}

            {top100Error && (
              <div className="crypto-card p-6 border-2" style={{ borderColor: 'var(--accent-red)' }}>
                <div className="flex items-center">
                  <span className="text-xl mr-3" style={{ color: 'var(--accent-red)' }}>⚠️</span>
                  <div>
                    <h3 className="font-medium status-negative">Error Loading Data</h3>
                    <p className="text-sm status-negative">{top100Error.message}</p>
                  </div>
                </div>
              </div>
            )}

            {top100Data && !top100Loading && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {top100Data.data.map(renderCryptoCard)}
              </div>
            )}
          </div>
        )}

        {activeTab === 'trending' && (
          <div>
            {trendingLoading && (
              <div className="crypto-card p-8 text-center">
                <div className="loading-spinner mx-auto mb-4"></div>
                <p style={{ color: 'var(--text-secondary)' }}>Loading trending cryptocurrencies...</p>
              </div>
            )}

            {trendingError && (
              <div className="crypto-card p-6 border-2" style={{ borderColor: 'var(--accent-red)' }}>
                <div className="flex items-center">
                  <span className="text-xl mr-3" style={{ color: 'var(--accent-red)' }}>⚠️</span>
                  <div>
                    <h3 className="font-medium status-negative">Error Loading Trending Data</h3>
                    <p className="text-sm status-negative">{trendingError.message}</p>
                  </div>
                </div>
              </div>
            )}

            {trendingData && !trendingLoading && (
              <div>
                <div className="mb-6 crypto-card p-6">
                  <h2 className="text-xl font-semibold gradient-text mb-2">
                    🔥 Trending Cryptocurrencies
                  </h2>
                  <p style={{ color: 'var(--text-secondary)' }}>
                    {trendingData.count} trending cryptocurrencies based on search volume and price action
                  </p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {trendingData.trending_crypto.map(renderCryptoCard)}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'watchlist' && (
          <div>
            <div className="crypto-card card-hover p-8 text-center">
              <span className="text-6xl mb-6 block" style={{ color: 'var(--accent-blue)' }}>⭐</span>
              <h2 className="text-2xl font-bold gradient-text mb-4">Your Trading Watchlist</h2>
              <p className="mb-6 max-w-md mx-auto" style={{ color: 'var(--text-secondary)' }}>
                Create your personalized watchlist to track cryptocurrencies you're interested in trading.
              </p>
              <div className="space-y-4">
                <button
                  onClick={() => {
                    alert('🎯 Add to Watchlist\n\nFeatures coming soon:\n• Search and add cryptocurrencies\n• Set price alerts\n• Track performance\n• Custom notes and analysis');
                  }}
                  className="btn-primary px-6 py-3 font-medium mr-4"
                >
                  ➕ Add Cryptocurrency
                </button>
                <button
                  onClick={() => {
                    alert('🚨 Price Alerts\n\nSet alerts for:\n• Price thresholds\n• Volume spikes\n• Technical indicators\n• News sentiment changes');
                  }}
                  className="btn-secondary px-6 py-3 font-medium"
                >
                  🚨 Set Alert
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Empty states */}
        {activeTab === 'top100' && top100Data?.data.length === 0 && (
          <div className="crypto-card p-8 text-center border-2" style={{ borderColor: 'var(--accent-yellow)' }}>
            <span className="text-4xl mb-4 block" style={{ color: 'var(--accent-yellow)' }}>🪙</span>
            <h3 className="font-medium mb-2" style={{ color: 'var(--text-primary)' }}>No Cryptocurrency Data</h3>
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
              Cryptocurrency data is currently unavailable. Please try again later.
            </p>
          </div>
        )}

        {activeTab === 'trending' && trendingData?.trending_crypto.length === 0 && (
          <div className="crypto-card p-8 text-center border-2" style={{ borderColor: 'var(--accent-yellow)' }}>
            <span className="text-4xl mb-4 block" style={{ color: 'var(--accent-yellow)' }}>🔥</span>
            <h3 className="font-medium mb-2" style={{ color: 'var(--text-primary)' }}>No Trending Data</h3>
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
              No trending cryptocurrency data is currently available. Please try again later.
            </p>
          </div>
        )}
      </main>

      {/* Performance Monitor */}
      <PerformanceMonitor enabled position="bottom-left" />
    </div>
  );
} 