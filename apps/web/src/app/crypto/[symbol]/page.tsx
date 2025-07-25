"use client";

import React from 'react';
import { useRouter } from 'next/navigation';
import { useCryptoData } from '../../../hooks/useCryptoData';

interface CryptoDetailPageProps {
  params: Promise<{
    symbol: string;
  }>;
}

export default function CryptoDetailPage({ params }: CryptoDetailPageProps) {
  const router = useRouter();
  const { symbol } = React.use(params);
  const { data: cryptoData, isLoading, error } = useCryptoData(symbol);

  if (isLoading) {
    return (
      <div className="min-h-screen p-6" style={{ background: 'var(--bg-primary)' }}>
        <div className="container mx-auto">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 mx-auto" style={{ borderColor: 'var(--accent-primary)' }}></div>
            <p className="mt-4" style={{ color: 'var(--text-secondary)' }}>Loading {symbol.toUpperCase()} data...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen p-6" style={{ background: 'var(--bg-primary)' }}>
        <div className="container mx-auto">
          <div className="text-center">
            <h1 className="text-2xl font-bold mb-4" style={{ color: 'var(--status-error)' }}>Error Loading Data</h1>
            <p style={{ color: 'var(--text-secondary)' }}>
              Failed to load data for {symbol.toUpperCase()}. Please try again later.
            </p>
            <button 
              onClick={() => router.back()}
              className="mt-4 btn-primary"
            >
              Go Back
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!cryptoData) {
  return (
      <div className="min-h-screen p-6" style={{ background: 'var(--bg-primary)' }}>
        <div className="container mx-auto">
          <div className="text-center">
            <h1 className="text-2xl font-bold mb-4" style={{ color: 'var(--text-secondary)' }}>No Data Available</h1>
            <p style={{ color: 'var(--text-secondary)' }}>
              No data found for {symbol.toUpperCase()}.
            </p>
            <button 
              onClick={() => router.back()}
              className="mt-4 btn-primary"
            >
              Go Back
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6" style={{ background: 'var(--bg-primary)' }}>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button 
            onClick={() => router.back()}
            className="mb-4 text-lg font-medium hover:opacity-80 transition-opacity"
            style={{ color: 'var(--accent-primary)' }}
          >
            ← Back to Dashboard
          </button>
          
          <div className="flex items-center space-x-4">
            <div 
              className="w-16 h-16 rounded-full flex items-center justify-center text-white text-2xl font-bold"
              style={{ background: 'var(--gradient-primary)' }}
            >
              {cryptoData.symbol?.slice(0, 1)?.toUpperCase() || symbol.slice(0, 1).toUpperCase()}
            </div>
            <div>
              <h1 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
                {cryptoData.name || symbol.toUpperCase()}
              </h1>
              <p className="text-xl" style={{ color: 'var(--text-secondary)' }}>
                {cryptoData.symbol?.toUpperCase() || symbol.toUpperCase()}
              </p>
            </div>
          </div>
        </div>

        {/* Price Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="crypto-card">
            <h3 className="text-sm font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>Current Price</h3>
            <p className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
              {cryptoData.current_price ? `$${Number(cryptoData.current_price).toLocaleString()}` : 'N/A'}
            </p>
                </div>

          <div className="crypto-card">
            <h3 className="text-sm font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>24h Change</h3>
            <p className={`text-2xl font-bold ${
              cryptoData.price_change_percentage_24h && cryptoData.price_change_percentage_24h >= 0 
                ? 'status-positive' 
                : 'status-negative'
            }`}>
              {cryptoData.price_change_percentage_24h != null 
                ? `${cryptoData.price_change_percentage_24h >= 0 ? '+' : ''}${cryptoData.price_change_percentage_24h.toFixed(2)}%`
                : 'N/A'
              }
                    </p>
                  </div>

          <div className="crypto-card">
            <h3 className="text-sm font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>Market Cap</h3>
            <p className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
              {cryptoData.market_cap && cryptoData.market_cap > 0 ? `$${Number(cryptoData.market_cap).toLocaleString()}` : 'N/A'}
            </p>
          </div>

          <div className="crypto-card">
            <h3 className="text-sm font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>24h Volume</h3>
            <p className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
              {cryptoData.total_volume && cryptoData.total_volume > 0 ? `$${Number(cryptoData.total_volume).toLocaleString()}` : 'N/A'}
            </p>
          </div>
                </div>
                
        {/* Additional Information */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="crypto-card">
            <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Price Statistics</h3>
            <div className="space-y-3">
                <div className="flex justify-between">
                <span style={{ color: 'var(--text-secondary)' }}>All-Time High:</span>
                <span className="font-medium" style={{ color: 'var(--text-primary)' }}>
                  {cryptoData.ath ? `$${Number(cryptoData.ath).toLocaleString()}` : 'N/A'}
                  </span>
                </div>
                  <div className="flex justify-between">
                <span style={{ color: 'var(--text-secondary)' }}>All-Time Low:</span>
                <span className="font-medium" style={{ color: 'var(--text-primary)' }}>
                  {cryptoData.atl ? `$${Number(cryptoData.atl).toLocaleString()}` : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                <span style={{ color: 'var(--text-secondary)' }}>Last Updated:</span>
                <span className="font-medium" style={{ color: 'var(--text-primary)' }}>
                  {cryptoData.last_updated ? new Date(cryptoData.last_updated).toLocaleString() : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                <span style={{ color: 'var(--text-secondary)' }}>Price Change (1h):</span>
                <span className={`font-medium ${
                  cryptoData.price_change_percentage_1h_in_currency && cryptoData.price_change_percentage_1h_in_currency >= 0 
                    ? 'status-positive' 
                    : 'status-negative'
                }`}>
                  {cryptoData.price_change_percentage_1h_in_currency != null 
                    ? `${cryptoData.price_change_percentage_1h_in_currency >= 0 ? '+' : ''}${cryptoData.price_change_percentage_1h_in_currency.toFixed(2)}%`
                    : 'N/A'
                  }
                </span>
                    </div>
                  </div>
          </div>

          <div className="crypto-card">
            <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Market Information</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span style={{ color: 'var(--text-secondary)' }}>Market Cap Rank:</span>
                <span className="font-medium" style={{ color: 'var(--text-primary)' }}>
                  {cryptoData.market_cap_rank ? `#${cryptoData.market_cap_rank}` : 'N/A'}
                </span>
        </div>
              <div className="flex justify-between">
                <span style={{ color: 'var(--text-secondary)' }}>24h High:</span>
                <span className="font-medium" style={{ color: 'var(--text-primary)' }}>
                  {cryptoData.high_24h && cryptoData.high_24h > 0 ? `$${Number(cryptoData.high_24h).toLocaleString()}` : 'N/A'}
                </span>
      </div>
              <div className="flex justify-between">
                <span style={{ color: 'var(--text-secondary)' }}>24h Low:</span>
                <span className="font-medium" style={{ color: 'var(--text-primary)' }}>
                  {cryptoData.low_24h && cryptoData.low_24h > 0 ? `$${Number(cryptoData.low_24h).toLocaleString()}` : 'N/A'}
                </span>
                </div>
              <div className="flex justify-between">
                <span style={{ color: 'var(--text-secondary)' }}>Circulating Supply:</span>
                <span className="font-medium" style={{ color: 'var(--text-primary)' }}>
                  {cryptoData.circulating_supply && cryptoData.circulating_supply > 0
                    ? `${Number(cryptoData.circulating_supply).toLocaleString()} ${cryptoData.symbol?.toUpperCase()}`
                    : 'N/A'
                  }
                </span>
              </div>
              <div className="flex justify-between">
                <span style={{ color: 'var(--text-secondary)' }}>Total Supply:</span>
                <span className="font-medium" style={{ color: 'var(--text-primary)' }}>
                  {cryptoData.total_supply && cryptoData.total_supply > 0
                    ? `${Number(cryptoData.total_supply).toLocaleString()} ${cryptoData.symbol?.toUpperCase()}`
                    : 'N/A'
                  }
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Real-time Data Notice */}
        <div className="mt-8 text-center">
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            💡 Data refreshed in real-time from multiple cryptocurrency exchanges
          </p>
        </div>
      </div>
    </div>
  );
} 