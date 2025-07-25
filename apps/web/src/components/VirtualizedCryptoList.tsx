"use client";

import React, { memo, useMemo } from 'react';
import { formatCurrency, formatPercentage, getChangeIndicator, getChangeIndicatorString } from '../lib/utils';

interface CryptoItem {
  id: string;
  symbol: string;
  name: string;
  current_price: number;
  price_change_percent_24h: number;
  market_cap: number;
  market_cap_rank: number;
  volume_24h: number;
  image?: string;
}

interface VirtualizedCryptoListProps {
  cryptos: CryptoItem[];
  height: number;
  itemHeight?: number;
  onCryptoClick?: (crypto: CryptoItem) => void;
  className?: string;
}

interface CryptoRowProps {
  crypto: CryptoItem;
  onCryptoClick?: (crypto: CryptoItem) => void;
}

// Memoized crypto row component for performance
const CryptoRow = memo<CryptoRowProps>(({ crypto, onCryptoClick }) => {
  if (!crypto) return null;

  const changeData = getChangeIndicator(crypto.price_change_percent_24h);
  const changeIcon = getChangeIndicatorString(crypto.price_change_percent_24h);
  const isPositive = changeData.isPositive;

  return (
    <div className="px-4 py-2">
      <div 
        className={`crypto-card p-4 cursor-pointer transition-all card-hover ${
          onCryptoClick ? 'hover:shadow-lg hover:-translate-y-0.5' : ''
        }`}
        onClick={() => onCryptoClick?.(crypto)}
        role={onCryptoClick ? 'button' : 'listitem'}
        tabIndex={onCryptoClick ? 0 : -1}
        onKeyDown={(e) => {
          if (onCryptoClick && (e.key === 'Enter' || e.key === ' ')) {
            e.preventDefault();
            onCryptoClick(crypto);
          }
        }}
        aria-label={`${crypto.name} (${crypto.symbol.toUpperCase()}): ${formatCurrency(crypto.current_price)}, ${formatPercentage(crypto.price_change_percent_24h)} change`}
      >
        <div className="flex items-center justify-between">
          {/* Left: Rank, Icon, Name/Symbol */}
          <div className="flex items-center gap-3 flex-1 min-w-0">
            {/* Rank */}
            <div 
              className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0"
              style={{ 
                background: 'var(--gradient-primary)',
                color: 'var(--text-inverse)'
              }}
            >
              {crypto.market_cap_rank}
            </div>

            {/* Crypto Icon */}
            <div className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0">
              {crypto.image ? (
                <img 
                  src={crypto.image} 
                  alt={`${crypto.name} logo`}
                  className="w-full h-full rounded-full"
                  loading="lazy"
                  onError={(e) => {
                    // Fallback to symbol if image fails
                    const target = e.target as HTMLImageElement;
                    const parent = target.parentElement;
                    if (parent) {
                      parent.innerHTML = `
                        <div class="w-full h-full rounded-full flex items-center justify-center text-sm font-bold" 
                             style="background: var(--gradient-accent); color: var(--text-inverse)">
                          ${crypto.symbol.slice(0, 2).toUpperCase()}
                        </div>
                      `;
                    }
                  }}
                />
              ) : (
                <div 
                  className="w-full h-full rounded-full flex items-center justify-center text-sm font-bold"
                  style={{ 
                    background: 'var(--gradient-accent)',
                    color: 'var(--text-inverse)'
                  }}
                >
                  {crypto.symbol.slice(0, 2).toUpperCase()}
                </div>
              )}
            </div>

            {/* Name and Symbol */}
            <div className="min-w-0 flex-1">
              <div 
                className="font-semibold text-sm truncate"
                style={{ color: 'var(--text-primary)' }}
              >
                {crypto.name}
              </div>
              <div 
                className="text-xs uppercase font-medium"
                style={{ color: 'var(--text-secondary)' }}
              >
                {crypto.symbol}
              </div>
            </div>
          </div>

          {/* Center: Price */}
          <div className="text-right min-w-0 flex-1">
            <div 
              className="font-bold text-sm"
              style={{ color: 'var(--text-primary)' }}
            >
              {formatCurrency(crypto.current_price)}
            </div>
            <div 
              className="text-xs"
              style={{ color: 'var(--text-secondary)' }}
            >
              ${crypto.current_price.toLocaleString('en-US', { 
                minimumFractionDigits: 2,
                maximumFractionDigits: 6
              })}
            </div>
          </div>

          {/* Right: 24h Change */}
          <div className="text-right min-w-0 flex-1">
            <div 
              className={`font-semibold text-sm flex items-center justify-end gap-1 ${
                isPositive ? 'status-positive' : 'status-negative'
              }`}
              style={{ 
                padding: '4px 8px',
                borderRadius: '6px',
                fontSize: '12px'
              }}
            >
              <span>{changeIcon}</span>
              <span>{formatPercentage(Math.abs(crypto.price_change_percent_24h))}</span>
            </div>
            <div 
              className="text-xs mt-1"
              style={{ color: 'var(--text-secondary)' }}
            >
              24h change
            </div>
          </div>

          {/* Far Right: Market Cap (hidden on small screens) */}
          <div className="text-right min-w-0 flex-1 hidden md:block">
            <div 
              className="font-medium text-sm"
              style={{ color: 'var(--text-primary)' }}
            >
              {formatCurrency(crypto.market_cap)}
            </div>
            <div 
              className="text-xs"
              style={{ color: 'var(--text-secondary)' }}
            >
              Market Cap
            </div>
          </div>
        </div>
      </div>
    </div>
  );
});

CryptoRow.displayName = 'CryptoRow';

// Main crypto list component with optimized rendering
export const VirtualizedCryptoList: React.FC<VirtualizedCryptoListProps> = ({
  cryptos,
  height,
  itemHeight = 80,
  onCryptoClick,
  className = '',
}) => {
  if (!cryptos || cryptos.length === 0) {
    return (
      <div 
        className={`crypto-card p-8 text-center ${className}`}
        style={{ height }}
      >
        <div 
          className="text-lg font-medium mb-2"
          style={{ color: 'var(--text-secondary)' }}
        >
          No cryptocurrencies found
        </div>
        <div 
          className="text-sm"
          style={{ color: 'var(--text-tertiary)' }}
        >
          Try adjusting your search criteria or check back later
        </div>
      </div>
    );
  }

  return (
    <div className={`crypto-card ${className}`}>
      {/* Header */}
      <div className="px-4 py-3 border-b" style={{ borderColor: 'var(--border)' }}>
        <div className="grid grid-cols-4 md:grid-cols-5 gap-4 text-xs font-semibold uppercase tracking-wide" style={{ color: 'var(--text-secondary)' }}>
          <div>Cryptocurrency</div>
          <div className="text-right">Price</div>
          <div className="text-right">24h Change</div>
          <div className="text-right hidden md:block">Market Cap</div>
          <div className="text-right hidden md:block">Volume</div>
        </div>
      </div>

      {/* Crypto List with overflow scrolling */}
      <div 
        className="overflow-y-auto scrollbar-hide"
        style={{ height: height - 60 }} // Subtract header height
      >
        {cryptos.map((crypto) => (
          <CryptoRow
            key={crypto.id}
            crypto={crypto}
            onCryptoClick={onCryptoClick}
          />
        ))}
      </div>

      {/* Footer with stats */}
      <div 
        className="px-4 py-2 border-t text-xs text-center"
        style={{ 
          borderColor: 'var(--border)',
          color: 'var(--text-secondary)'
        }}
      >
        Showing {cryptos.length.toLocaleString()} cryptocurrencies
      </div>
    </div>
  );
};

// Loading skeleton for the crypto list
export const VirtualizedCryptoListSkeleton: React.FC<{ 
  height: number; 
  itemHeight?: number; 
  className?: string;
}> = ({ 
  height, 
  itemHeight = 80, 
  className = '' 
}) => {
  const skeletonCount = Math.ceil((height - 60) / itemHeight);

  return (
    <div className={`crypto-card ${className}`}>
      {/* Header skeleton */}
      <div className="px-4 py-3 border-b" style={{ borderColor: 'var(--border)' }}>
        <div className="grid grid-cols-4 md:grid-cols-5 gap-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <div 
              key={i}
              className="loading-skeleton h-4 rounded"
            />
          ))}
        </div>
      </div>

      {/* List skeleton */}
      <div style={{ height: height - 60 }} className="overflow-hidden">
        {Array.from({ length: skeletonCount }).map((_, index) => (
          <div key={index} className="px-4 py-2">
            <div className="flex items-center gap-4 h-16">
              <div className="loading-skeleton w-8 h-8 rounded-full" />
              <div className="loading-skeleton w-10 h-10 rounded-full" />
              <div className="flex-1">
                <div className="loading-skeleton h-4 w-24 mb-2 rounded" />
                <div className="loading-skeleton h-3 w-16 rounded" />
              </div>
              <div className="loading-skeleton h-4 w-20 rounded" />
              <div className="loading-skeleton h-4 w-16 rounded" />
              <div className="loading-skeleton h-4 w-24 rounded hidden md:block" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default VirtualizedCryptoList; 