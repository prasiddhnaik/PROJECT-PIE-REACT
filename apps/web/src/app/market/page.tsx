'use client';

import React, { useState } from 'react';
import { useTop100Crypto } from '@/hooks/useTop100';
import { useTrendingCrypto } from '@/hooks/useTrendingCrypto';
import { useMarketOverview } from '@/hooks/useMarketOverview';
import { MarketDataLoader } from '@/components/MarketDataLoader';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { formatCurrency, formatPercentage, abbreviateNumber, getChangeIndicator } from '@/lib/utils';
import Link from 'next/link';

interface CryptoData {
  id: string;
  symbol: string;
  name: string;
  current_price: number;
  market_cap: number;
  market_cap_rank: number;
  price_change_percentage_24h: number;
  total_volume: number;
  image?: string;
}

export default function MarketPage() {
  const [sortBy, setSortBy] = useState<'market_cap' | 'current_price' | 'price_change_percentage_24h'>('market_cap');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [searchTerm, setSearchTerm] = useState('');

  const { data: top100Data, isLoading: top100Loading, error: top100Error } = useTop100Crypto();
  const { data: trendingData, isLoading: trendingLoading } = useTrendingCrypto();
  const { data: marketOverview, isLoading: marketLoading } = useMarketOverview();

  const handleSort = (column: typeof sortBy) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('desc');
    }
  };

  const filteredAndSortedData = React.useMemo(() => {
    if (!top100Data) return [];
    
    let filtered = top100Data.filter((crypto: CryptoData) =>
      crypto.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      crypto.symbol.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return filtered.sort((a: CryptoData, b: CryptoData) => {
      const aVal = a[sortBy];
      const bVal = b[sortBy];
      
      if (sortOrder === 'asc') {
        return aVal > bVal ? 1 : -1;
      }
      return aVal < bVal ? 1 : -1;
    });
  }, [top100Data, searchTerm, sortBy, sortOrder]);

  if (top100Loading || marketLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-neutral-50 to-neutral-100 dark:from-neutral-900 dark:to-neutral-800">
        <div className="container mx-auto px-4 py-8">
                     <MarketDataLoader isLoading={true} />
        </div>
      </div>
    );
  }

  if (top100Error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-neutral-50 to-neutral-100 dark:from-neutral-900 dark:to-neutral-800">
        <div className="container mx-auto px-4 py-8">
          <Card className="text-center">
            <CardContent className="p-8">
              <h2 className="text-2xl font-bold text-error-600 mb-4">Error Loading Market Data</h2>
              <p className="text-neutral-600 dark:text-neutral-400 mb-6">
                Unable to fetch market data. Please try again later.
              </p>
              <Button onClick={() => window.location.reload()}>
                Retry
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-50 to-neutral-100 dark:from-neutral-900 dark:to-neutral-800">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gradient mb-4">Cryptocurrency Market</h1>
          <p className="text-lg text-neutral-600 dark:text-neutral-400">
            Real-time cryptocurrency prices and market data
          </p>
        </div>

        {/* Market Overview */}
        {marketOverview && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <Card variant="elevated">
              <CardContent className="p-6">
                <h3 className="text-sm font-medium text-neutral-500 dark:text-neutral-400 mb-2">
                  Total Market Cap
                </h3>
                <p className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
                  {formatCurrency(marketOverview.total_market_cap?.usd || 0, 'USD', 0, 0)}
                </p>
                {marketOverview.market_cap_change_percentage_24h_usd && (
                  <Badge
                    variant={marketOverview.market_cap_change_percentage_24h_usd >= 0 ? 'success' : 'error'}
                    size="sm"
                    className="mt-2"
                  >
                    {formatPercentage(marketOverview.market_cap_change_percentage_24h_usd)}
                  </Badge>
                )}
              </CardContent>
            </Card>

            <Card variant="elevated">
              <CardContent className="p-6">
                <h3 className="text-sm font-medium text-neutral-500 dark:text-neutral-400 mb-2">
                  24h Trading Volume
                </h3>
                <p className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
                  {formatCurrency(marketOverview.total_volume?.usd || 0, 'USD', 0, 0)}
                </p>
              </CardContent>
            </Card>

            <Card variant="elevated">
              <CardContent className="p-6">
                <h3 className="text-sm font-medium text-neutral-500 dark:text-neutral-400 mb-2">
                  Bitcoin Dominance
                </h3>
                <p className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
                  {marketOverview.market_cap_percentage?.btc?.toFixed(1) || 0}%
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Trending Cryptocurrencies */}
        {trendingData && !trendingLoading && (
          <Card variant="elevated" className="mb-8">
            <CardHeader>
              <h2 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
                🔥 Trending Cryptocurrencies
              </h2>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {trendingData.coins?.slice(0, 6).map((coin: any, index: number) => (
                  <Card key={coin.item.id} variant="outlined" interactive>
                    <CardContent className="p-4">
                      <div className="flex items-center space-x-3">
                        <span className="text-sm font-medium text-neutral-500 dark:text-neutral-400">
                          #{index + 1}
                        </span>
                        {coin.item.large && (
                          <img
                            src={coin.item.large}
                            alt={coin.item.name}
                            className="w-8 h-8 rounded-full"
                          />
                        )}
                        <div>
                          <h3 className="font-semibold text-neutral-900 dark:text-neutral-100">
                            {coin.item.name}
                          </h3>
                          <p className="text-sm text-neutral-500 dark:text-neutral-400 uppercase">
                            {coin.item.symbol}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Search and Controls */}
        <Card variant="elevated" className="mb-6">
          <CardContent className="p-6">
            <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
              <div className="flex-1 max-w-md">
                <input
                  type="text"
                  placeholder="Search cryptocurrencies..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-4 py-2 border border-neutral-300 dark:border-neutral-600 rounded-lg bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleSort('market_cap')}
                >
                  Market Cap {sortBy === 'market_cap' && (sortOrder === 'desc' ? '↓' : '↑')}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleSort('current_price')}
                >
                  Price {sortBy === 'current_price' && (sortOrder === 'desc' ? '↓' : '↑')}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleSort('price_change_percentage_24h')}
                >
                  24h % {sortBy === 'price_change_percentage_24h' && (sortOrder === 'desc' ? '↓' : '↑')}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Cryptocurrency Table */}
        <Card variant="elevated">
          <CardHeader>
            <h2 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
              Top 100 Cryptocurrencies
            </h2>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-neutral-200 dark:border-neutral-700">
                    <th className="text-left py-3 px-4 font-semibold text-neutral-700 dark:text-neutral-300">
                      #
                    </th>
                    <th className="text-left py-3 px-4 font-semibold text-neutral-700 dark:text-neutral-300">
                      Name
                    </th>
                    <th className="text-right py-3 px-4 font-semibold text-neutral-700 dark:text-neutral-300">
                      Price
                    </th>
                    <th className="text-right py-3 px-4 font-semibold text-neutral-700 dark:text-neutral-300">
                      24h %
                    </th>
                    <th className="text-right py-3 px-4 font-semibold text-neutral-700 dark:text-neutral-300">
                      Market Cap
                    </th>
                    <th className="text-right py-3 px-4 font-semibold text-neutral-700 dark:text-neutral-300">
                      Volume (24h)
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {filteredAndSortedData.map((crypto: CryptoData) => {
                    const changeIndicator = getChangeIndicator(crypto.price_change_percentage_24h);
                    return (
                      <tr
                        key={crypto.id}
                        className="border-b border-neutral-100 dark:border-neutral-800 hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors cursor-pointer"
                        onClick={() => window.open(`/crypto/${crypto.id}`, '_blank')}
                      >
                        <td className="py-3 px-4 text-neutral-500 dark:text-neutral-400">
                          {crypto.market_cap_rank}
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex items-center space-x-3">
                            {crypto.image && (
                              <img
                                src={crypto.image}
                                alt={crypto.name}
                                className="w-8 h-8 rounded-full"
                              />
                            )}
                            <div>
                              <h3 className="font-semibold text-neutral-900 dark:text-neutral-100">
                                {crypto.name}
                              </h3>
                              <p className="text-sm text-neutral-500 dark:text-neutral-400 uppercase">
                                {crypto.symbol}
                              </p>
                            </div>
                          </div>
                        </td>
                        <td className="py-3 px-4 text-right font-semibold text-neutral-900 dark:text-neutral-100">
                          {formatCurrency(crypto.current_price)}
                        </td>
                        <td className="py-3 px-4 text-right">
                          <Badge
                            variant={changeIndicator.isPositive ? 'success' : 'error'}
                            size="sm"
                          >
                            {changeIndicator.icon} {formatPercentage(crypto.price_change_percentage_24h)}
                          </Badge>
                        </td>
                        <td className="py-3 px-4 text-right font-medium text-neutral-900 dark:text-neutral-100">
                          {formatCurrency(crypto.market_cap, 'USD', 0, 0)}
                        </td>
                        <td className="py-3 px-4 text-right font-medium text-neutral-900 dark:text-neutral-100">
                          {formatCurrency(crypto.total_volume, 'USD', 0, 0)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 