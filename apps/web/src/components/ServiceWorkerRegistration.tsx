"use client";

import { useEffect, useState } from 'react';

interface ServiceWorkerState {
  isSupported: boolean;
  isRegistered: boolean;
  isOnline: boolean;
  updateAvailable: boolean;
  registration: ServiceWorkerRegistration | null;
}

export const ServiceWorkerRegistration = () => {
  const [swState, setSwState] = useState<ServiceWorkerState>({
    isSupported: false,
    isRegistered: false,
    isOnline: true,
    updateAvailable: false,
    registration: null
  });

  const [showUpdatePrompt, setShowUpdatePrompt] = useState(false);

  useEffect(() => {
    // Check if service workers are supported
    if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
      setSwState(prev => ({ ...prev, isSupported: true }));
      registerServiceWorker();
    }

    // Listen for online/offline changes
    const handleOnline = () => setSwState(prev => ({ ...prev, isOnline: true }));
    const handleOffline = () => setSwState(prev => ({ ...prev, isOnline: false }));

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const registerServiceWorker = async () => {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js', {
        scope: '/'
      });

      console.log('✅ Service Worker registered successfully:', registration);
      
      setSwState(prev => ({ 
        ...prev, 
        isRegistered: true, 
        registration 
      }));

      // Check for updates
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        
        if (newWorker) {
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              // New content is available, show update prompt
              setSwState(prev => ({ ...prev, updateAvailable: true }));
              setShowUpdatePrompt(true);
            }
          });
        }
      });

      // Handle service worker messages
      navigator.serviceWorker.addEventListener('message', (event) => {
        if (event.data && event.data.type === 'CACHE_UPDATED') {
          console.log('💾 Cache updated:', event.data.cacheName);
        }
      });

      // Check if there's already a waiting service worker
      if (registration.waiting) {
        setSwState(prev => ({ ...prev, updateAvailable: true }));
        setShowUpdatePrompt(true);
      }

    } catch (error) {
      console.error('❌ Service Worker registration failed:', error);
    }
  };

  const handleUpdate = () => {
    if (swState.registration?.waiting) {
      // Tell the waiting service worker to skip waiting and take control
      swState.registration.waiting.postMessage({ type: 'SKIP_WAITING' });
      
      // Listen for the controlling service worker to change
      navigator.serviceWorker.addEventListener('controllerchange', () => {
        window.location.reload();
      });
    }
    setShowUpdatePrompt(false);
  };

  const handleDismissUpdate = () => {
    setShowUpdatePrompt(false);
  };

  const clearCache = async () => {
    if (swState.registration) {
      swState.registration.active?.postMessage({ type: 'CLEAR_CACHE' });
      console.log('🗑️ Cache clear requested');
    }
  };

  // Don't render anything if service workers aren't supported
  if (!swState.isSupported) {
    return null;
  }

  return (
    <>
      {/* Offline Indicator */}
      {!swState.isOnline && (
        <div className="fixed top-0 left-0 right-0 z-50 bg-yellow-500 text-black text-center py-2 px-4">
          <div className="flex items-center justify-center gap-2">
            <span>📡</span>
            <span className="font-medium">You're offline</span>
            <span className="text-sm">• Some features may be limited</span>
          </div>
        </div>
      )}

      {/* Update Prompt */}
      {showUpdatePrompt && (
        <div className="fixed bottom-4 left-4 right-4 md:left-auto md:w-96 z-50">
          <div 
            className="p-4 rounded-lg shadow-xl border backdrop-blur-sm"
            style={{ 
              background: 'rgba(59, 130, 246, 0.95)',
              borderColor: 'rgba(255, 255, 255, 0.2)',
              color: 'white'
            }}
          >
            <div className="flex items-start gap-3">
              <span className="text-2xl">🔄</span>
              <div className="flex-1">
                <h3 className="font-bold text-white mb-1">
                  Update Available
                </h3>
                <p className="text-sm text-blue-100 mb-3">
                  A new version of Crypto Analytics is ready. Refresh to get the latest features and improvements.
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={handleUpdate}
                    className="px-4 py-2 bg-white text-blue-600 rounded-md font-medium text-sm hover:bg-blue-50 transition-colors"
                  >
                    🚀 Update Now
                  </button>
                  <button
                    onClick={handleDismissUpdate}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md font-medium text-sm hover:bg-blue-700 transition-colors border border-blue-400"
                  >
                    Later
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Service Worker Status (Development Only) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="fixed bottom-4 right-4 z-40">
          <div 
            className="p-3 rounded-lg shadow-lg border text-xs"
            style={{ 
              background: 'rgba(0, 0, 0, 0.8)',
              borderColor: 'rgba(255, 255, 255, 0.1)',
              color: 'white'
            }}
          >
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span 
                  className={`w-2 h-2 rounded-full ${
                    swState.isRegistered ? 'bg-green-400' : 'bg-red-400'
                  }`}
                />
                <span>SW: {swState.isRegistered ? 'Active' : 'Inactive'}</span>
              </div>
              
              <div className="flex items-center gap-2">
                <span 
                  className={`w-2 h-2 rounded-full ${
                    swState.isOnline ? 'bg-green-400' : 'bg-yellow-400'
                  }`}
                />
                <span>Network: {swState.isOnline ? 'Online' : 'Offline'}</span>
              </div>

              {swState.updateAvailable && (
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-blue-400" />
                  <span>Update Ready</span>
                </div>
              )}

              <button
                onClick={clearCache}
                className="text-xs text-blue-400 hover:text-blue-300 underline mt-2"
              >
                Clear Cache
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

// Hook to check if app is running in standalone mode (installed as PWA)
export const useIsStandalone = (): boolean => {
  const [isStandalone, setIsStandalone] = useState(false);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const checkStandalone = () => {
        const isStandaloneMode = 
          window.matchMedia('(display-mode: standalone)').matches ||
          (window.navigator as any).standalone ||
          document.referrer.includes('android-app://');
        
        setIsStandalone(isStandaloneMode);
      };

      checkStandalone();
      
      // Listen for display mode changes
      const mediaQuery = window.matchMedia('(display-mode: standalone)');
      mediaQuery.addEventListener('change', checkStandalone);

      return () => {
        mediaQuery.removeEventListener('change', checkStandalone);
      };
    }
  }, []);

  return isStandalone;
};

// Hook to register for push notifications
export const usePushNotifications = () => {
  const [isSupported, setIsSupported] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [subscription, setSubscription] = useState<PushSubscription | null>(null);

  useEffect(() => {
    if (typeof window !== 'undefined' && 'serviceWorker' in navigator && 'PushManager' in window) {
      setIsSupported(true);
      checkSubscription();
    }
  }, []);

  const checkSubscription = async () => {
    try {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();
      
      setIsSubscribed(!!subscription);
      setSubscription(subscription);
    } catch (error) {
      console.error('Error checking push subscription:', error);
    }
  };

  const subscribe = async () => {
    try {
      const registration = await navigator.serviceWorker.ready;
      
      // Request notification permission
      const permission = await Notification.requestPermission();
      
      if (permission !== 'granted') {
        throw new Error('Notification permission denied');
      }

      // Subscribe to push notifications
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY
      });

      setIsSubscribed(true);
      setSubscription(subscription);

      // Send subscription to server (implement as needed)
      console.log('Push subscription:', subscription);
      
      return subscription;
    } catch (error) {
      console.error('Error subscribing to push notifications:', error);
      throw error;
    }
  };

  const unsubscribe = async () => {
    try {
      if (subscription) {
        await subscription.unsubscribe();
        setIsSubscribed(false);
        setSubscription(null);
      }
    } catch (error) {
      console.error('Error unsubscribing from push notifications:', error);
      throw error;
    }
  };

  return {
    isSupported,
    isSubscribed,
    subscription,
    subscribe,
    unsubscribe
  };
};

export default ServiceWorkerRegistration; 