/**
 * Simple HTTP client for crypto analytics API
 */

// Direct backend URL - this should work with proper CORS setup
const BACKEND_URL = 'http://localhost:8001';

// Log configuration for debugging
console.log('HTTP Client Configuration:', {
  BACKEND_URL,
  environment: typeof window !== 'undefined' ? 'browser' : 'server',
  timestamp: new Date().toISOString()
});

// Simple fetch-based HTTP client with enhanced error handling
export const get = async <T = any>(endpoint: string): Promise<T> => {
  const url = `${BACKEND_URL}${endpoint}`;
  console.log(`Making GET request to: ${url}`);
  
  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      mode: 'cors', // Explicitly set CORS mode
      credentials: 'omit', // Don't send credentials to avoid CORS issues
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log(`GET ${endpoint} success:`, data);
    return data;
  } catch (error) {
    console.error(`GET ${endpoint} failed:`, error);
    throw error;
  }
};

export const post = async <T = any>(endpoint: string, data?: any): Promise<T> => {
  const url = `${BACKEND_URL}${endpoint}`;
  console.log(`Making POST request to: ${url}`);
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      mode: 'cors', // Explicitly set CORS mode
      credentials: 'omit', // Don't send credentials to avoid CORS issues
      body: data ? JSON.stringify(data) : undefined,
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    console.log(`POST ${endpoint} success:`, result);
    return result;
  } catch (error) {
    console.error(`POST ${endpoint} failed:`, error);
    throw error;
  }
};

export const put = async <T = any>(endpoint: string, body?: any): Promise<T> => {
  const url = `${BACKEND_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: body ? JSON.stringify(body) : undefined,
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error: any) {
    console.error(`PUT ${endpoint} failed:`, error.message);
    throw error;
  }
};

export const del = async <T = any>(endpoint: string): Promise<T> => {
  const url = `${BACKEND_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error: any) {
    console.error(`DELETE ${endpoint} failed:`, error.message);
    throw error;
  }
};

// Create a simple mock httpClient object for compatibility
export const httpClient = {
  get,
  post,
  put,
  delete: del,
};

export default httpClient; 
