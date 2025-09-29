"use client";

import { useQuery, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';

export interface StockApiResponse {
  symbol: string;
  currentPrice: number;
  change: number;
  changePercent: number;
  prices: number[];
  timestamps: string[];
  indicators?: any;
}

async function fetchStock(symbol: string): Promise<StockApiResponse> {
  const { data } = await axios.get(`/api/stock-data`, { params: { symbol } });
  return data;
}

export function useStockData(symbol: string) {
  return useQuery({
    queryKey: ['stock', symbol],
    queryFn: () => fetchStock(symbol),
    staleTime: 60 * 1000,
    gcTime: 5 * 60 * 1000,
  });
}

export function useIsCached(symbol: string) {
  const client = useQueryClient();
  const cached = client.getQueryData<StockApiResponse>(['stock', symbol]);
  return { cached };
}




