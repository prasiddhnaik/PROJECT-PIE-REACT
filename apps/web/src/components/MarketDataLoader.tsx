"use client";

import React from 'react';
import { useMarketOverview } from '@/hooks/useMarketOverview';
import { useFearGreed } from '@/hooks/useFearGreed';
import { formatCurrency } from '@/lib/utils';

export const MarketDataLoader: React.FC = () => {
  const { data: overview, isLoading: overviewLoading } = useMarketOverview();
  const { data: fearGreed, isLoading: fgLoading } = useFearGreed();

  const marketStats = [
    {
      label: 'Total Market Cap',
      value: overviewLoading ? '—' : formatCurrency(overview?.total_market_cap?.usd || 0, 'USD', 0, 0),
      change: overview?.market_cap_change_percentage_24h_usd || 0,
      icon: '💰',
      color: 'from-blue-400 to-blue-600'
    },
    {
      label: '24h Volume',
      value: overviewLoading ? '—' : formatCurrency(overview?.total_volume?.usd || 0, 'USD', 0, 0),
      change: null,
      icon: '📊',
      color: 'from-green-400 to-green-600'
    },
    {
      label: 'Fear & Greed',
      value: fgLoading ? '—' : `${fearGreed?.value || 0}`,
      subtext: fearGreed?.interpretation || '',
      icon: '⚡',
      color: 'from-purple-400 to-purple-600'
    }
  ];

  return (
    <>
      {marketStats.map((stat, index) => (
        <div 
          key={stat.label}
          className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20 hover:bg-white/15 transition-all duration-300 hover:scale-105"
          style={{ animationDelay: `${index * 0.1}s` }}
        >
          {/* Icon and Label */}
          <div className="flex items-center justify-between mb-4">
            <div className="text-3xl">{stat.icon}</div>
            <div className={`w-3 h-3 rounded-full bg-gradient-to-r ${stat.color}`}></div>
          </div>
          
          {/* Value */}
          <div className="mb-2">
            <h3 className="text-white/70 text-sm font-medium mb-1">{stat.label}</h3>
            <p className="text-2xl font-bold text-white">{stat.value}</p>
          </div>
          
          {/* Change or Subtext */}
          {stat.change !== null && stat.change !== undefined ? (
            <div className={`text-sm font-medium ${
              stat.change >= 0 ? 'text-green-400' : 'text-red-400'
            }`}>
              {stat.change >= 0 ? '+' : ''}{stat.change.toFixed(2)}% 24h
            </div>
          ) : stat.subtext ? (
            <div className="text-sm text-white/60">{stat.subtext}</div>
          ) : (
            <div className="text-sm text-white/60">Real-time data</div>
          )}
        </div>
      ))}
    </>
  );
};

export default MarketDataLoader; 