import { z } from "zod";

export const FearGreedSchema = z.object({
  value: z.number(),
  interpretation: z.string(),
  last_updated: z.string().optional(),
});
export type FearGreedResponse = z.infer<typeof FearGreedSchema>;

export const MarketSentimentSchema = z.object({
  sentiment_score: z.number(),
  bullish_percent: z.number(),
  bearish_percent: z.number(),
  neutral_percent: z.number(),
  indicators: z.record(z.string(), z.any()).optional(),
  last_updated: z.string().optional(),
});
export type MarketSentimentResponse = z.infer<typeof MarketSentimentSchema>; 