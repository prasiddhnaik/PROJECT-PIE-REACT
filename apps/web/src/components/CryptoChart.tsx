"use client";

import React, { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface CryptoHistoryData {
  timestamp: string;
  price: number;
  volume: number;
  date: string;
}

interface CryptoChartProps {
  symbol: string;
  days?: number;
  height?: number;
  showVolume?: boolean;
  chartType?: 'line' | 'area';
}

// Cache utilities
const getCachedData = (symbol: string, days: number): CryptoHistoryData[] | null => {
  try {
    const cacheKey = `chart_${symbol}_${days}d`;
    const cached = localStorage.getItem(cacheKey);
    if (cached) {
      const { data, timestamp } = JSON.parse(cached);
      // Check if cache is less than 3 minutes old
      if (Date.now() - timestamp < 3 * 60 * 1000) {
        return data;
      }
    }
  } catch (error) {
    console.warn('Cache read error:', error);
  }
  return null;
};

const setCachedData = (symbol: string, days: number, data: CryptoHistoryData[]) => {
  try {
    const cacheKey = `chart_${symbol}_${days}d`;
    const cacheData = {
      data,
      timestamp: Date.now()
    };
    localStorage.setItem(cacheKey, JSON.stringify(cacheData));
  } catch (error) {
    console.warn('Cache write error:', error);
  }
};

const CryptoChart: React.FC<CryptoChartProps> = ({ 
  symbol, 
  days = 7, 
  height = 300,
  showVolume = false,
  chartType = 'area'
}) => {
  const [data, setData] = useState<CryptoHistoryData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchChartData = async () => {
      let controller: AbortController | null = null;
      let timeoutId: NodeJS.Timeout | null = null;
      
      const maxRetries = 2;
      let currentRetry = 0;
      
      const attemptFetch = async (): Promise<void> => {
        try {
          setLoading(true);
          setError(null);

          // Check cache first
          const cachedData = getCachedData(symbol, days);
          if (cachedData && cachedData.length > 0) {
            setData(cachedData);
            setLoading(false);
            return;
          }

          // Create abort controller and timeout
          controller = new AbortController();
          timeoutId = setTimeout(() => {
            if (controller && !controller.signal.aborted) {
              controller.abort();
            }
          }, 20000); // 20 second timeout for heavy API load
          
          const response = await fetch(
            `http://localhost:8001/api/crypto/${symbol}/history?days=${days}`,
            { 
              signal: controller.signal,
              headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
              }
            }
          );
          
          // Clear timeout on successful response
          if (timeoutId) {
            clearTimeout(timeoutId);
            timeoutId = null;
          }

          if (!response.ok) {
            throw new Error(`API returned ${response.status}`);
          }

          const result = await response.json();
          
          // Support both legacy and new API response shapes
          const historyArray =
            (result && Array.isArray(result.history) && result.history) ||
            (result && result.data && Array.isArray(result.data.history) && result.data.history);

          if (historyArray && historyArray.length > 0) {
            const chartData = historyArray.map((item: any) => ({
              timestamp: item.timestamp,
              price: parseFloat(item.price) || 0,
              volume: parseFloat(item.volume) || 0,
              date: item.date
            }));
            
            setData(chartData);
            setCachedData(symbol, days, chartData);
          } else {
            throw new Error('Invalid data format received');
          }

        } catch (error: any) {
          // Clear timeout on error
          if (timeoutId) {
            clearTimeout(timeoutId);
          }
          
          // Don't log abort errors as they're expected
          if (error.name !== 'AbortError') {
            console.error(`Chart data fetch failed for ${symbol} (attempt ${currentRetry + 1}):`, error);
          }
          
          // Retry logic for timeouts and server errors
          if ((error.name === 'AbortError' || error.message.includes('500')) && currentRetry < maxRetries) {
            currentRetry++;
            setError(`Retrying... (${currentRetry}/${maxRetries})`);
            
            // Wait a bit before retrying
            await new Promise(resolve => setTimeout(resolve, 2000));
            return attemptFetch();
          }
          
          // Final error handling
          if (error.name === 'AbortError') {
            setError('API timeout - chart temporarily unavailable');
          } else if (error.message.includes('500')) {
            setError('Server error - chart temporarily unavailable');
          } else if (error.message.includes('404')) {
            setError(`Chart data not available for ${symbol.toUpperCase()}`);
          } else {
            setError('Unable to load chart data');
          }
        } finally {
          // Cleanup
          if (timeoutId) {
            clearTimeout(timeoutId);
          }
          setLoading(false);
        }
      };

      if (symbol) {
        // Add small random delay to stagger multiple chart requests
        const delay = Math.random() * 1000; // 0-1 second random delay
        setTimeout(() => {
          attemptFetch();
        }, delay);
      }
    };

    fetchChartData();
  }, [symbol, days]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center" style={{ height: `${height}px` }}>
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mb-3"></div>
        <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>
          {error && error.includes('Retrying') 
            ? error 
            : `Loading ${symbol.toUpperCase()} chart data...`}
        </span>
        <span className="text-xs mt-1" style={{ color: 'var(--text-secondary)', opacity: 0.7 }}>
          {error && error.includes('Retrying') 
            ? 'Heavy API load detected' 
            : 'This may take a moment during peak usage'}
        </span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center" style={{ height: `${height}px` }}>
        <div style={{ color: 'var(--text-secondary)' }} className="text-sm text-center">
          <div className="mb-2">
            {error.includes('timeout') || error.includes('slow') ? '⏱️' : '⚠️'} {error}
          </div>
          <div className="text-xs opacity-75">
            {error.includes('timeout') || error.includes('slow') 
              ? 'Crypto APIs are experiencing high traffic. Data will load when available.' 
              : 'Chart data will load automatically when available'}
          </div>
          <div className="text-xs opacity-50 mt-1">
            Auto-retry in progress...
          </div>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center" style={{ height: `${height}px` }}>
        <div style={{ color: 'var(--text-secondary)' }} className="text-sm">
          No chart data available
        </div>
      </div>
    );
  }

  return (
    <div style={{ height: `${height}px` }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis 
            dataKey="date" 
            axisLine={false}
            tickLine={false}
            fontSize={12}
            stroke="var(--text-secondary)"
          />
          <YAxis 
            axisLine={false}
            tickLine={false}
            fontSize={12}
            stroke="var(--text-secondary)"
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'var(--background-secondary)',
              border: '1px solid var(--border)',
              borderRadius: '6px',
              color: 'var(--text-primary)'
            }}
            formatter={(value: any, name: string) => [
              name === 'price' ? `$${Number(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 6 })}` : Number(value).toLocaleString(),
              name === 'price' ? 'Price' : 'Volume'
            ]}
            labelStyle={{ color: 'var(--text-secondary)' }}
          />
          <Area
            type="monotone"
            dataKey="price"
            stroke={chartType === 'area' ? '#3b82f6' : '#10b981'}
            fill={chartType === 'area' ? 'rgba(59, 130, 246, 0.1)' : 'none'}
            strokeWidth={2}
            dot={false}
          />
          {showVolume && (
            <Area
              type="monotone"
              dataKey="volume"
              stroke="#8b5cf6"
              fill="rgba(139, 92, 246, 0.1)"
              strokeWidth={1}
              dot={false}
            />
          )}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CryptoChart; 