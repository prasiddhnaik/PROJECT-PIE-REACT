"use client";

import { useQuery } from "@tanstack/react-query";

export interface TrendingCrypto {
  id: string;
  symbol: string;
  name: string;
  current_price: number;
  market_cap: number;
  market_cap_rank: number;
  volume_24h: number;
  price_change_percent_24h: number;
  price_change_percent_1h: number;
  price_change_percent_7d: number;
  asset_type: string;
}

export interface TrendingCryptoResponse {
  trending_crypto: TrendingCrypto[];
  count: number;
  timestamp: string;
  isDemo?: boolean;
}

// Local storage cache key
const TRENDING_CACHE_KEY = 'trending_crypto_cache';
const TRENDING_CACHE_DURATION = 3 * 60 * 1000; // 3 minutes

// Mock data removed - using only real API data

// Cache management functions for trending data
function getTrendingCachedData(): TrendingCryptoResponse | null {
  if (typeof window === 'undefined') return null;
  
  try {
    const cached = localStorage.getItem(TRENDING_CACHE_KEY);
    if (!cached) return null;
    
    const { data, timestamp } = JSON.parse(cached);
    const now = Date.now();
    
    // Check if cache is still valid
    if (now - timestamp < TRENDING_CACHE_DURATION) {
      return data;
    }
    
    // Cache expired, remove it
    localStorage.removeItem(TRENDING_CACHE_KEY);
    return null;
  } catch (error) {
    console.warn('Error reading trending cache:', error);
    return null;
  }
}

function setTrendingCachedData(data: TrendingCryptoResponse): void {
  if (typeof window === 'undefined') return;
  
  try {
    const cacheEntry = {
      data,
      timestamp: Date.now()
    };
    localStorage.setItem(TRENDING_CACHE_KEY, JSON.stringify(cacheEntry));
  } catch (error) {
    console.warn('Error writing trending cache:', error);
  }
}

async function fetchTrendingCrypto(): Promise<TrendingCryptoResponse> {
  // First, try to get cached data
  const cachedData = getTrendingCachedData();
  if (cachedData) {
    console.log('📦 Serving trending crypto data from local cache');
    return cachedData;
  }

  try {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8001';
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000); // 15-second timeout to avoid premature aborts
    
    const response = await fetch(`${backendUrl}/api/crypto/trending`, {
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (response.ok) {
      const result = await response.json();
      
      // Transform the response to match our expected format
      const data: TrendingCryptoResponse = {
        trending_crypto: result.data || result.trending || [],
        count: result.count || (result.data || result.trending || []).length,
        timestamp: result.timestamp || new Date().toISOString()
      };
      
      // Cache the successful response
      setTrendingCachedData(data);
      console.log('💾 Fresh trending data cached for 3 minutes');
      
      return data;
    } else {
      throw new Error(`API returned ${response.status}`);
    }
  } catch (error) {
    console.error('⚠️  Trending API failed:', error);
    
    // Don't use mock data - throw error to be handled by React Query
    throw new Error(`Failed to fetch trending crypto: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

export function useTrendingCrypto() {
  return useQuery({
    queryKey: ["trendingCrypto"],
    queryFn: fetchTrendingCrypto,
    staleTime: 3 * 60 * 1000, // 3 minutes
    gcTime: 6 * 60 * 1000, // 6 minutes garbage collection
    retry: false, // Don't retry since we have mock data fallback
    refetchOnWindowFocus: false,
    refetchOnReconnect: true,
  });
} 