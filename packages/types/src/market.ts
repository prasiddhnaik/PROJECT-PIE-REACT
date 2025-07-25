import { z } from "zod";

// Flexible schema matching the flattened /api/market/overview response
export const MarketOverviewSchema = z.object({
  total_market_cap: z.record(z.number()).optional(),
  total_volume: z.record(z.number()).optional(),
  market_cap_percentage: z.record(z.number()).optional(),
  market_cap_change_percentage_24h_usd: z.number().optional(),
  active_cryptocurrencies: z.number().optional(),
  markets: z.number().optional(),
  source: z.string().optional(),
  timestamp: z.string().optional(),
});

export type MarketOverviewResponse = z.infer<typeof MarketOverviewSchema>; 