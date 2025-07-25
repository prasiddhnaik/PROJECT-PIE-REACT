"use client";

import React from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

interface ReactQueryProviderProps {
  children: React.ReactNode
}

export default function ReactQueryProvider({ children }: ReactQueryProviderProps) {
  // Create QueryClient in component to ensure it's available on both server and client
  const [queryClient] = React.useState(() => new QueryClient({
      defaultOptions: {
        queries: {
          staleTime: 60 * 1000, // 1 minute
          gcTime: 5 * 60 * 1000, // 5 minutes (renamed from cacheTime in v5)
          refetchOnWindowFocus: false,
          retry: (failureCount: number, error: any) => {
            // Don't retry on 4xx errors
            if (error?.status >= 400 && error?.status < 500) {
              return false
            }
            // Retry up to 3 times for other errors
            return failureCount < 3
          },
          retryDelay: (attemptIndex: number) => Math.min(1000 * 2 ** attemptIndex, 30000),
        },
        mutations: {
          retry: 1,
          retryDelay: 1000,
        },
      },
  }));

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {/* Only show devtools in development */}
      {process.env.NODE_ENV === 'development' && (
        <ReactQueryDevtools initialIsOpen={false} />
      )}
    </QueryClientProvider>
  );
}