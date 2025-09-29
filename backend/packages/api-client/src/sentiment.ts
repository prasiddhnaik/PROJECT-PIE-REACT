import { get } from "./http";
import { FearGreedSchema, FearGreedResponse, MarketSentimentSchema, MarketSentimentResponse } from "@fa/types";

export async function getFearGreed(): Promise<FearGreedResponse> {
  const data = await get("/api/market/fear-greed");
  return FearGreedSchema.parse(data);
}

export async function getMarketSentiment(): Promise<MarketSentimentResponse> {
  const data = await get("/api/market/sentiment");
  return MarketSentimentSchema.parse(data);
} 