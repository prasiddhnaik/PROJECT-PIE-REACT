"use client";

import { useQuery } from "@tanstack/react-query";
import { getMarketOverview } from "@fa/api-client";
import { MarketOverviewResponse } from "@fa/types";

export function useMarketOverview() {
  return useQuery({
    queryKey: ["marketOverview"],
    queryFn: fetchMarketOverview,
    staleTime: 60 * 1000, // 1 minute
  });
}

async function fetchMarketOverview(): Promise<MarketOverviewResponse> {
  return getMarketOverview();
} 