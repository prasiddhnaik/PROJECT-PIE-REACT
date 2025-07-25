import { useQuery } from "@tanstack/react-query";
import { getFearGreed } from "@fa/api-client";

export function useFearGreed() {
  return useQuery({
    queryKey: ["fearGreed"],
    queryFn: getFearGreed,
    staleTime: 50 * 60 * 1000,
  });
} 