"use client";

import { ReactNode, useEffect, useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { PersistQueryClientProvider } from '@tanstack/react-query-persist-client';
import { createSyncStoragePersister } from '@tanstack/query-sync-storage-persister';

interface Props { children: ReactNode }

export default function ReactQueryProvider({ children }: Props) {
  const [client] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        retry: 1,
        refetchOnWindowFocus: false,
        staleTime: 60 * 1000,
        cacheTime: 5 * 60 * 1000,
      },
    },
  }));

  const [persister, setPersister] = useState<any>(null);

  useEffect(() => {
    const p = createSyncStoragePersister({ storage: window.localStorage });
    setPersister(p);
  }, []);

  if (!persister) {
    return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
  }

  return (
    <PersistQueryClientProvider client={client} persistOptions={{ persister }}>
      {children}
    </PersistQueryClientProvider>
  );
}




