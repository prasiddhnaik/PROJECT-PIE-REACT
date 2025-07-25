import { useState, useEffect } from 'react'

interface QueryOptions<T> {
  queryKey: string[]
  queryFn: () => Promise<T>
  enabled?: boolean
  refetchInterval?: number
  staleTime?: number
}

interface QueryResult<T> {
  data: T | undefined
  error: Error | null
  isLoading: boolean
  isError: boolean
  refetch: () => void
}

export function useTypedQuery<T>({
  queryKey,
  queryFn,
  enabled = true,
  refetchInterval,
}: QueryOptions<T>): QueryResult<T> {
  const [data, setData] = useState<T | undefined>(undefined)
  const [error, setError] = useState<Error | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const fetchData = async () => {
    if (!enabled) return
    
    setIsLoading(true)
    setError(null)
    
    try {
      const result = await queryFn()
      setData(result)
    } catch (err) {
      setError(err as Error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    
    if (refetchInterval) {
      const interval = setInterval(fetchData, refetchInterval)
      return () => clearInterval(interval)
    }
  }, [queryKey.join(','), enabled])

  return {
    data,
    error,
    isLoading,
    isError: !!error,
    refetch: fetchData,
  }
}
