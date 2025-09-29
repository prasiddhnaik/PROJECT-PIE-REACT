"use client";

import { useMemo, useState } from 'react';
import Link from 'next/link';
import { useTickers } from '@/hooks/useTickers';
import { useStockData } from '@/hooks/useStockData';
import Sparkline from '@/components/Sparkline';

function StockRow({ symbol }: { symbol: string }) {
  const { data, isLoading, isError } = useStockData(symbol);
  return (
    <div className="bg-gray-900/30 border border-gray-800 rounded-md p-4 hover:border-gray-600 transition-colors">
      <div className="flex items-center justify-between">
        <div>
          <div className="font-semibold">{symbol}</div>
          {isLoading && <div className="text-xs text-gray-500">Loading...</div>}
          {isError && <div className="text-xs text-red-400">Error</div>}
          {data && (
            <div className="text-sm text-gray-300">
              ₹{(data.currentPrice || data.prices?.[data.prices.length-1] || 0).toFixed(2)}
              <span className={data.change >= 0 ? 'text-green-400 ml-2' : 'text-red-400 ml-2'}>
                {data.change >= 0 ? '+' : ''}{(data.change || 0).toFixed(2)} ({(data.changePercent || 0).toFixed(2)}%)
              </span>
            </div>
          )}
        </div>
        <div className="w-40">
          {data && <Sparkline data={data.prices || []} stroke={data.change >= 0 ? '#10B981' : '#F87171'} />}
        </div>
      </div>
    </div>
  );
}

export default function ScreenerPage() {
  const { data: symbols, isLoading } = useTickers();
  const [query, setQuery] = useState('');

  const filtered = useMemo(() => {
    const list = symbols || [];
    const q = query.trim().toLowerCase();
    return q ? list.filter(s => s.toLowerCase().includes(q)) : list;
  }, [symbols, query]);

  return (
    <div className="min-h-screen bg-black text-white">
      <nav className="border-b border-gray-800 bg-black/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="text-2xl font-bold">FinanceOS</Link>
          <div className="flex gap-6 text-sm">
            <Link href="/dashboard" className="hover:text-gray-300">Dashboard</Link>
            <Link href="/news" className="hover:text-gray-300">News</Link>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex items-end justify-between mb-6">
          <div>
            <h1 className="text-4xl font-light">Stock Screener</h1>
            <p className="text-gray-400">400+ symbols. Real data. Cached with React Query.</p>
          </div>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search symbol…"
            className="bg-black border border-gray-700 rounded-md px-3 py-2 text-sm outline-none focus:border-gray-500"
          />
        </div>

        {isLoading ? (
          <div className="text-gray-500">Loading symbols…</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.slice(0, 420).map((s) => (
              <StockRow key={s} symbol={s} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}




