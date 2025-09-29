"use client";

import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

async function fetchTickers(): Promise<string[]> {
  const { data } = await axios.get('/api/tickers');
  return data.symbols as string[];
}

export function useTickers() {
  return useQuery({
    queryKey: ['tickers'],
    queryFn: fetchTickers,
    staleTime: 10 * 60 * 1000,
  });
}




