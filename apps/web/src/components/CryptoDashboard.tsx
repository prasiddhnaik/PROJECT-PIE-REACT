/**
 * @fileoverview Main cryptocurrency dashboard component for the analytics platform
 * 
 * This file contains the primary dashboard component that displays real-time
 * cryptocurrency market data, including prices, market caps, volume, and
 * percentage changes. It serves as the central hub for crypto market analysis
 * and provides an intuitive interface for exploring cryptocurrency data.
 * 
 * Key features:
 * - Real-time crypto price tracking
 * - Popular cryptocurrency selection
 * - Market data visualization
 * - Responsive design for all devices
 * - Loading states and error handling
 * - Accessibility-first approach
 * 
 * @version 1.0.0
 */

"use client";

import React from 'react';
import Link from 'next/link';
import { useTop100Crypto } from '@/hooks/useTop100';
import { useTrendingCrypto } from '@/hooks/useTrendingCrypto';
import { formatCurrency, formatPercentage } from '@/lib/utils';

export const CryptoDashboard: React.FC = () => {
  const { data: topData, isLoading: topLoading } = useTop100Crypto();
  const { data: trendingData, isLoading: trendingLoading } = useTrendingCrypto();

  const topCryptos = topData?.data?.slice(0, 8) || [];
  const trendingCryptos = trendingData?.trending_crypto?.slice(0, 4) || [];

  return (
    <div className="space-y-8">
      {/* Trending Section */}
      <div className="bg-white/5 backdrop-blur-sm rounded-3xl p-8 border border-white/10">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold text-white flex items-center gap-3">
            🔥 Trending Cryptocurrencies
          </h3>
          <Link 
            href="/crypto" 
            className="text-blue-400 hover:text-blue-300 font-medium transition-colors"
          >
            View All →
          </Link>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {trendingLoading ? (
            Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="animate-pulse">
                <div className="bg-white/10 rounded-2xl p-6 space-y-3">
                  <div className="h-4 bg-white/20 rounded w-3/4"></div>
                  <div className="h-6 bg-white/20 rounded w-1/2"></div>
                  <div className="h-3 bg-white/20 rounded w-1/3"></div>
                </div>
              </div>
            ))
          ) : (
            trendingCryptos.map((crypto, index) => (
              <Link
                key={crypto.id || crypto.symbol || index}
                href={`/crypto/${crypto.symbol?.toLowerCase() || crypto.id}`}
                className="group"
              >
                <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/20 hover:border-white/30 transition-all duration-300 hover:scale-105 group-hover:bg-white/15">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center text-white font-bold">
                      {crypto.symbol?.charAt(0) || '?'}
                    </div>
                    <div>
                      <h4 className="text-white font-semibold">{crypto.symbol?.toUpperCase()}</h4>
                      <p className="text-white/60 text-sm">{crypto.name}</p>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="text-xl font-bold text-white">
                      {formatCurrency(crypto.current_price || 0)}
                    </div>
                    <div className={`text-sm font-medium ${
                      (crypto.price_change_percent_24h || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {formatPercentage(crypto.price_change_percent_24h || 0)} 24h
                    </div>
                  </div>
                </div>
              </Link>
            ))
          )}
        </div>
      </div>

      {/* Top Cryptocurrencies */}
      <div className="bg-white/5 backdrop-blur-sm rounded-3xl p-8 border border-white/10">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold text-white flex items-center gap-3">
            👑 Top Cryptocurrencies
          </h3>
          <Link 
            href="/market" 
            className="text-blue-400 hover:text-blue-300 font-medium transition-colors"
          >
            View All Markets →
          </Link>
        </div>

        {topLoading ? (
          <div className="space-y-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="animate-pulse flex items-center gap-4 p-4">
                <div className="w-12 h-12 bg-white/20 rounded-full"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-white/20 rounded w-1/4"></div>
                  <div className="h-3 bg-white/20 rounded w-1/6"></div>
                </div>
                <div className="space-y-2">
                  <div className="h-4 bg-white/20 rounded w-20"></div>
                  <div className="h-3 bg-white/20 rounded w-16"></div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {topCryptos.map((crypto, index) => (
              <Link
                key={crypto.id || crypto.symbol || index}
                href={`/crypto/${crypto.symbol?.toLowerCase() || crypto.id}`}
                className="group"
              >
                <div className="flex items-center gap-4 p-4 rounded-2xl bg-gradient-to-r from-white/5 to-white/10 border border-white/10 hover:border-white/20 transition-all duration-300 hover:bg-white/15 group-hover:scale-[1.02]">
                  {/* Rank */}
                  <div className="w-8 text-center">
                    <span className="text-white/60 font-medium">#{crypto.market_cap_rank || index + 1}</span>
                  </div>

                  {/* Crypto Info */}
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center text-white font-bold text-lg">
                      {crypto.symbol?.charAt(0) || '?'}
                    </div>
                    <div className="min-w-0">
                      <h4 className="text-white font-semibold group-hover:text-blue-300 transition-colors">
                        {crypto.symbol?.toUpperCase()}
                      </h4>
                      <p className="text-white/60 text-sm truncate">{crypto.name}</p>
                    </div>
                  </div>

                  {/* Price */}
                  <div className="text-right min-w-0">
                    <div className="text-lg font-bold text-white">
                      {formatCurrency(crypto.current_price || 0)}
                    </div>
                    <div className={`text-sm font-medium ${
                      (crypto.price_change_percent_24h || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {formatPercentage(crypto.price_change_percent_24h || 0)} 24h
                    </div>
                  </div>

                  {/* Market Cap */}
                  <div className="text-right min-w-0 hidden lg:block">
                    <div className="text-white/80 font-medium">
                      {formatCurrency(crypto.market_cap || 0, 'USD', 0, 0)}
                    </div>
                    <div className="text-white/60 text-sm">Market Cap</div>
                  </div>

                  {/* Volume */}
                  <div className="text-right min-w-0 hidden xl:block">
                    <div className="text-white/80 font-medium">
                      {formatCurrency(crypto.volume_24h || 0, 'USD', 0, 0)}
                    </div>
                    <div className="text-white/60 text-sm">24h Volume</div>
                  </div>

                  {/* Arrow */}
                  <div className="text-white/40 group-hover:text-white/80 transition-colors">
                    →
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link href="/crypto-analytics" className="group">
          <div className="bg-gradient-to-br from-blue-500/20 to-purple-500/20 backdrop-blur-sm rounded-2xl p-6 border border-blue-400/20 hover:border-blue-400/40 transition-all duration-300 hover:scale-105">
            <div className="text-3xl mb-3">📈</div>
            <h3 className="text-lg font-bold text-white mb-2">Technical Analysis</h3>
            <p className="text-white/70 text-sm mb-4">
              Advanced charts, indicators, and trading signals for professional analysis.
            </p>
            <div className="text-blue-400 font-medium group-hover:text-blue-300 transition-colors">
              Analyze Markets →
            </div>
          </div>
        </Link>

        <Link href="/ai-predictions" className="group">
          <div className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 backdrop-blur-sm rounded-2xl p-6 border border-purple-400/20 hover:border-purple-400/40 transition-all duration-300 hover:scale-105">
            <div className="text-3xl mb-3">🤖</div>
            <h3 className="text-lg font-bold text-white mb-2">AI Predictions</h3>
            <p className="text-white/70 text-sm mb-4">
              Machine learning-powered price predictions and market insights.
            </p>
            <div className="text-purple-400 font-medium group-hover:text-purple-300 transition-colors">
              View Predictions →
            </div>
          </div>
        </Link>

        <Link href="/market" className="group">
          <div className="bg-gradient-to-br from-green-500/20 to-teal-500/20 backdrop-blur-sm rounded-2xl p-6 border border-green-400/20 hover:border-green-400/40 transition-all duration-300 hover:scale-105">
            <div className="text-3xl mb-3">🌍</div>
            <h3 className="text-lg font-bold text-white mb-2">Global Markets</h3>
            <p className="text-white/70 text-sm mb-4">
              Comprehensive view of all cryptocurrency markets and exchanges.
            </p>
            <div className="text-green-400 font-medium group-hover:text-green-300 transition-colors">
              Explore Markets →
            </div>
          </div>
        </Link>
      </div>
    </div>
  );
};

export default CryptoDashboard; 