'use client';

import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';

interface ProviderHealth {
  id: string;
  name: string;
  category: string;
  priority_score: number;
  health_status: 'healthy' | 'degraded' | 'down' | 'unknown';
  last_check: string | null;
  response_time: number | null;
  error_message: string | null;
}

interface ProviderStatusData {
  providers: ProviderHealth[];
  healthy_count: number;
  total_count: number;
  timestamp: string;
}

const useProviderStatus = () => {
  return useQuery({
    queryKey: ['provider-status'],
    queryFn: async (): Promise<ProviderStatusData> => {
      const baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const response = await fetch(`${baseUrl}/api/crypto/providers/status`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch provider status');
      }
      
      const result = await response.json();
      return result.data;
    },
    refetchInterval: 30000, // Refresh every 30 seconds
    staleTime: 15000, // Data is fresh for 15 seconds
  });
};

const ProviderStatus: React.FC = () => {
  const { data, isLoading, error, refetch } = useProviderStatus();
  const [filter, setFilter] = useState<'all' | 'healthy' | 'degraded' | 'down'>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [showDetails, setShowDetails] = useState<string | null>(null);

  // Get unique categories
  const categories = data ? Array.from(new Set(data.providers.map(p => p.category))) : [];

  // Filter providers based on current filters
  const filteredProviders = data?.providers.filter(provider => {
    const matchesStatus = filter === 'all' || provider.health_status === filter;
    const matchesCategory = categoryFilter === 'all' || provider.category === categoryFilter;
    const matchesSearch = provider.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         provider.id.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesStatus && matchesCategory && matchesSearch;
  }) || [];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-100 text-green-800';
      case 'degraded': return 'bg-yellow-100 text-yellow-800';
      case 'down': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return '✅';
      case 'degraded': return '⚠️';
      case 'down': return '❌';
      default: return '❓';
    }
  };

  const formatResponseTime = (time: number | null) => {
    if (!time) return 'N/A';
    return time < 1000 ? `${time}ms` : `${(time / 1000).toFixed(1)}s`;
  };

  const formatLastCheck = (timestamp: string | null) => {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString();
  };

  if (isLoading) {
    return (
      <Card>
        <div className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-6 bg-gray-200 rounded w-1/4"></div>
            <div className="space-y-3">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="h-16 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <div className="p-6">
          <h2 className="text-xl font-bold text-red-600 mb-4">Provider Status Error</h2>
          <p className="text-gray-600 mb-4">Failed to load provider status data.</p>
          <Button onClick={() => refetch()}>Retry</Button>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Summary */}
      <Card>
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">Provider Status Dashboard</h2>
            <Button onClick={() => refetch()} variant="outline">
              🔄 Refresh
            </Button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-blue-600">Total Providers</h3>
              <p className="text-2xl font-bold text-blue-900">{data?.total_count || 0}</p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-green-600">Healthy</h3>
              <p className="text-2xl font-bold text-green-900">{data?.healthy_count || 0}</p>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-yellow-600">Degraded</h3>
              <p className="text-2xl font-bold text-yellow-900">
                {data?.providers.filter(p => p.health_status === 'degraded').length || 0}
              </p>
            </div>
            <div className="bg-red-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-red-600">Down</h3>
              <p className="text-2xl font-bold text-red-900">
                {data?.providers.filter(p => p.health_status === 'down').length || 0}
              </p>
            </div>
          </div>
        </div>
      </Card>

      {/* Filters */}
      <Card>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Filter by Status</label>
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value as any)}
                className="w-full p-2 border rounded"
              >
                <option value="all">All Statuses</option>
                <option value="healthy">Healthy</option>
                <option value="degraded">Degraded</option>
                <option value="down">Down</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Filter by Category</label>
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="w-full p-2 border rounded"
              >
                <option value="all">All Categories</option>
                {categories.map(category => (
                  <option key={category} value={category}>
                    {category.charAt(0).toUpperCase() + category.slice(1)}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Search Providers</label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by name or ID..."
                className="w-full p-2 border rounded"
              />
            </div>
          </div>
        </div>
      </Card>

      {/* Provider List */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">
            Providers ({filteredProviders.length})
          </h3>
          
          <div className="space-y-3">
            {filteredProviders.map((provider) => (
              <div key={provider.id} className="border rounded-lg p-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <span className="text-xl">{getStatusIcon(provider.health_status)}</span>
                    <div>
                      <h4 className="font-medium">{provider.name}</h4>
                      <p className="text-sm text-gray-600">
                        {provider.category} • Priority: {provider.priority_score}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <Badge className={getStatusColor(provider.health_status)}>
                      {provider.health_status}
                    </Badge>
                    <span className="text-sm text-gray-500">
                      {formatResponseTime(provider.response_time)}
                    </span>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setShowDetails(
                        showDetails === provider.id ? null : provider.id
                      )}
                    >
                      {showDetails === provider.id ? 'Hide' : 'Details'}
                    </Button>
                  </div>
                </div>
                
                {showDetails === provider.id && (
                  <div className="mt-4 pt-4 border-t bg-gray-50 rounded p-3">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <strong>Provider ID:</strong> {provider.id}
                      </div>
                      <div>
                        <strong>Last Check:</strong> {formatLastCheck(provider.last_check)}
                      </div>
                      <div>
                        <strong>Response Time:</strong> {formatResponseTime(provider.response_time)}
                      </div>
                      {provider.error_message && (
                        <div className="md:col-span-3">
                          <strong>Error:</strong> 
                          <span className="text-red-600 ml-2">{provider.error_message}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
          
          {filteredProviders.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              No providers match the current filters.
            </div>
          )}
        </div>
      </Card>

      {/* Last Updated */}
      <div className="text-center text-sm text-gray-500">
        Last updated: {data?.timestamp ? new Date(data.timestamp).toLocaleString() : 'Never'}
      </div>
    </div>
  );
};

export default ProviderStatus; 