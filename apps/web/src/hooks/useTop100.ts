"use client";

import { useQuery } from "@tanstack/react-query";

export interface Top100Crypto {
  id: string;
  symbol: string;
  name: string;
  image?: string;
  current_price: number;
  market_cap: number;
  market_cap_rank: number;
  volume_24h: number;
  price_change_24h: number;
  price_change_percent_24h: number;
  price_change_percent_1h: number;
  price_change_percent_7d: number;
  circulating_supply: number;
  total_supply: number;
  max_supply: number | null;
  ath: number;
  ath_change_percentage: number;
  ath_date: string;
  atl: number;
  atl_change_percentage: number;
  atl_date: string;
  last_updated: string;
  asset_type: string;
}

export interface Top100CryptoResponse {
  data: Top100Crypto[];
  count: number;
  total_market_cap: number;
  timestamp: string;
  isDemo?: boolean;
}

// Local storage cache key
const CACHE_KEY = 'top100_crypto_cache';
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

// Mock data removed - using only real API data

// Cache management functions
function getCachedData(): Top100CryptoResponse | null {
  if (typeof window === 'undefined') return null;
  
  try {
    const cached = localStorage.getItem(CACHE_KEY);
    if (!cached) return null;
    
    const { data, timestamp } = JSON.parse(cached);
    const now = Date.now();
    
    // Check if cache is still valid
    if (now - timestamp < CACHE_DURATION) {
      return data;
    }
    
    // Cache expired, remove it
    localStorage.removeItem(CACHE_KEY);
    return null;
  } catch (error) {
    console.warn('Error reading cache:', error);
    return null;
  }
}

function setCachedData(data: Top100CryptoResponse): void {
  if (typeof window === 'undefined') return;
  
  try {
    const cacheEntry = {
      data,
      timestamp: Date.now()
    };
    localStorage.setItem(CACHE_KEY, JSON.stringify(cacheEntry));
  } catch (error) {
    console.warn('Error writing cache:', error);
  }
}

async function fetchTop100Crypto(): Promise<Top100CryptoResponse> {
  // First, try to get cached data
  const cachedData = getCachedData();
  if (cachedData) {
    console.log('📦 Serving top 100 data from local cache');
    return cachedData;
  }

  try {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8001';
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
    
    const response = await fetch(`${backendUrl}/api/top100/crypto`, {
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (response.ok) {
      const data: Top100CryptoResponse = await response.json();
      
      // Cache the successful response
      setCachedData(data);
      console.log('💾 Fresh top 100 data cached for 5 minutes');
      
      return data;
    } else {
      throw new Error(`API returned ${response.status}`);
    }
  } catch (error) {
    console.error('⚠️  API failed:', error);
    
    // Don't use mock data - throw error to be handled by React Query
    throw new Error(`Failed to fetch top 100 crypto: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

export function useTop100Crypto() {
  return useQuery({
    queryKey: ["top100Crypto"],
    queryFn: fetchTop100Crypto,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes garbage collection
    retry: false, // Don't retry since we have mock data fallback
    refetchOnWindowFocus: false,
    refetchOnReconnect: true,
  });
} 