// Service Worker for Crypto Analytics App
// Provides offline support and intelligent caching

const CACHE_NAME = 'crypto-analytics-v1';
const API_CACHE_NAME = 'crypto-api-v1';
const STATIC_CACHE_NAME = 'crypto-static-v1';

// Files to cache immediately
const STATIC_ASSETS = [
  '/',
  '/crypto-analytics',
  '/market',
  '/manifest.json',
  // Add other critical routes
];

// API endpoints to cache
const API_ENDPOINTS = [
  '/api/top100/crypto',
  '/api/trending/crypto',
  '/api/crypto/history',
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('🔧 Service Worker installing...');
  
  event.waitUntil(
    Promise.all([
      // Cache static assets
      caches.open(STATIC_CACHE_NAME).then((cache) => {
        console.log('📦 Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      }),
      // Skip waiting to activate immediately
      self.skipWaiting()
    ])
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('✅ Service Worker activated');
  
  event.waitUntil(
    Promise.all([
      // Clean up old caches
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME && 
                cacheName !== API_CACHE_NAME && 
                cacheName !== STATIC_CACHE_NAME) {
              console.log('🗑️ Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      // Take control of all clients
      self.clients.claim()
    ])
  );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Handle API requests
  if (isAPIRequest(url)) {
    event.respondWith(handleAPIRequest(request));
    return;
  }

  // Handle static assets
  if (isStaticAsset(url)) {
    event.respondWith(handleStaticAsset(request));
    return;
  }

  // Handle navigation requests
  if (request.mode === 'navigate') {
    event.respondWith(handleNavigation(request));
    return;
  }

  // Default: network first with cache fallback
  event.respondWith(
    fetch(request)
      .catch(() => caches.match(request))
  );
});

// Check if request is to API
function isAPIRequest(url) {
  return url.pathname.startsWith('/api/') || 
         url.hostname === 'localhost' && url.port === '8001';
}

// Check if request is for static asset
function isStaticAsset(url) {
  const staticExtensions = ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2'];
  return staticExtensions.some(ext => url.pathname.endsWith(ext));
}

// Handle API requests with network-first strategy
async function handleAPIRequest(request) {
  const cache = await caches.open(API_CACHE_NAME);
  
  try {
    // Try network first
    const networkResponse = await fetch(request.clone());
    
    if (networkResponse.ok) {
      // Cache successful responses
      const responseClone = networkResponse.clone();
      
      // Only cache crypto data endpoints
      if (shouldCacheAPIResponse(request.url)) {
        await cache.put(request, responseClone);
        console.log('💾 Cached API response:', request.url);
      }
      
      return networkResponse;
    }
    
    throw new Error(`Network response not ok: ${networkResponse.status}`);
  } catch (error) {
    console.log('🌐 Network failed, trying cache:', request.url);
    
    // Fall back to cache
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      console.log('📦 Serving from cache:', request.url);
      
      // Add offline indicator header
      const headers = new Headers(cachedResponse.headers);
      headers.set('X-Served-From', 'cache');
      headers.set('X-Cache-Date', new Date().toISOString());
      
      return new Response(cachedResponse.body, {
        status: cachedResponse.status,
        statusText: cachedResponse.statusText,
        headers: headers
      });
    }
    
    // Return offline fallback for crypto data
    if (request.url.includes('/api/top100/crypto')) {
      return new Response(JSON.stringify({
        data: [],
        count: 0,
        total_market_cap: 0,
        timestamp: new Date().toISOString(),
        isOffline: true,
        message: 'Data unavailable offline'
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    throw error;
  }
}

// Handle static assets with cache-first strategy
async function handleStaticAsset(request) {
  const cache = await caches.open(STATIC_CACHE_NAME);
  
  // Try cache first
  const cachedResponse = await cache.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }
  
  // Fall back to network and cache
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      await cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.log('🚫 Static asset unavailable:', request.url);
    throw error;
  }
}

// Handle navigation requests
async function handleNavigation(request) {
  try {
    // Try network first for navigation
    const networkResponse = await fetch(request);
    return networkResponse;
  } catch (error) {
    // Fall back to cached page or offline page
    const cache = await caches.open(STATIC_CACHE_NAME);
    const cachedResponse = await cache.match('/') || 
                          await cache.match('/offline.html');
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return minimal offline page
    return new Response(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>Crypto Analytics - Offline</title>
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <style>
            body { 
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
              text-align: center; 
              padding: 50px; 
              background: #0f172a;
              color: white;
            }
            .container { max-width: 400px; margin: 0 auto; }
            .icon { font-size: 4rem; margin-bottom: 1rem; }
            h1 { color: #60a5fa; margin-bottom: 1rem; }
            p { color: #94a3b8; line-height: 1.6; }
            button { 
              background: linear-gradient(135deg, #3b82f6, #1d4ed8);
              color: white; 
              border: none; 
              padding: 12px 24px; 
              border-radius: 8px; 
              cursor: pointer;
              font-size: 16px;
              margin-top: 20px;
            }
            button:hover { opacity: 0.9; }
          </style>
        </head>
        <body>
          <div class="container">
            <div class="icon">📡</div>
            <h1>You're Offline</h1>
            <p>
              Crypto Analytics is currently unavailable. 
              Please check your internet connection and try again.
            </p>
            <p>
              Some cached data may still be available when you return online.
            </p>
            <button onclick="window.location.reload()">
              🔄 Try Again
            </button>
          </div>
        </body>
      </html>
    `, {
      status: 200,
      headers: { 'Content-Type': 'text/html' }
    });
  }
}

// Determine if API response should be cached
function shouldCacheAPIResponse(url) {
  return API_ENDPOINTS.some(endpoint => url.includes(endpoint));
}

// Background sync for failed requests
self.addEventListener('sync', (event) => {
  if (event.tag === 'crypto-data-sync') {
    console.log('🔄 Background sync triggered');
    event.waitUntil(syncCryptoData());
  }
});

// Sync crypto data in background
async function syncCryptoData() {
  try {
    // Retry failed API requests
    const cache = await caches.open(API_CACHE_NAME);
    
    for (const endpoint of API_ENDPOINTS) {
      try {
        const response = await fetch(endpoint);
        if (response.ok) {
          await cache.put(endpoint, response.clone());
          console.log('🔄 Background synced:', endpoint);
        }
      } catch (error) {
        console.log('❌ Background sync failed for:', endpoint);
      }
    }
  } catch (error) {
    console.log('❌ Background sync error:', error);
  }
}

// Push notifications for price alerts (future feature)
self.addEventListener('push', (event) => {
  if (event.data) {
    const data = event.data.json();
    
    const options = {
      body: data.body || 'Check out the latest crypto prices!',
      icon: '/icons/icon-192x192.png',
      badge: '/icons/badge-72x72.png',
      tag: 'crypto-alert',
      data: {
        url: data.url || '/crypto-analytics'
      },
      actions: [
        {
          action: 'view',
          title: 'View Details',
          icon: '/icons/view-icon.png'
        },
        {
          action: 'dismiss',
          title: 'Dismiss',
          icon: '/icons/dismiss-icon.png'
        }
      ]
    };
    
    event.waitUntil(
      self.registration.showNotification(data.title || 'Crypto Alert', options)
    );
  }
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  if (event.action === 'view') {
    event.waitUntil(
      self.clients.openWindow(event.notification.data.url)
    );
  }
});

// Periodic background updates (when supported)
self.addEventListener('periodicsync', (event) => {
  if (event.tag === 'crypto-price-update') {
    event.waitUntil(syncCryptoData());
  }
});

// Handle messages from main app
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'CLEAR_CACHE') {
    event.waitUntil(
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => caches.delete(cacheName))
        );
      })
    );
  }
});

console.log('🚀 Service Worker loaded successfully'); 