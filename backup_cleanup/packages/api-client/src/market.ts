import { get } from "./http";
import { MarketOverviewSchema, MarketOverviewResponse } from "@fa/types";

export async function getMarketOverview(): Promise<MarketOverviewResponse> {
  const data = await get("/api/market/overview");
  return MarketOverviewSchema.parse(data);
} 