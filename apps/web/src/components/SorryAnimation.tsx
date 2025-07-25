'use client';

import React from 'react';
import { useEffect, useState } from 'react';

interface SorryAnimationProps {
  message?: string;
  onRetry?: () => void;
  isVisible: boolean;
}

export default function SorryAnimation({ 
  message = "Sorry, something went wrong", 
  onRetry,
  isVisible 
}: SorryAnimationProps) {
  const [currentEmoji, setCurrentEmoji] = useState('😢');
  
  useEffect(() => {
    if (!isVisible) return;
    
    const emojis = ['😢', '😔', '🥺', '😞', '😿'];
    let index = 0;
    
    const interval = setInterval(() => {
      index = (index + 1) % emojis.length;
      setCurrentEmoji(emojis[index]);
    }, 800);
    
    return () => clearInterval(interval);
  }, [isVisible]);

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900 bg-opacity-95">
      <div className="relative">
        {/* Background circles */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="relative w-40 h-40">
            <div className="absolute inset-4 border-2 border-red-300 rounded-full opacity-60 animate-ping"></div>
            <div className="absolute inset-8 border border-red-200 rounded-full opacity-40 animate-pulse"></div>
            <div className="absolute inset-12 border border-red-100 rounded-full opacity-20"></div>
          </div>
        </div>

        {/* Main content */}
        <div className="flex flex-col items-center justify-center w-40 h-40 text-center">
          {/* Animated emoji */}
          <div className="text-8xl mb-4 animate-bounce">
            {currentEmoji}
          </div>
        </div>

        {/* Message and retry */}
        <div className="mt-8 text-center max-w-md">
          <h2 className="text-white text-2xl font-bold mb-2">Oops!</h2>
          <p className="text-gray-300 text-lg mb-6">{message}</p>
          
          {/* Loading dots */}
          <div className="flex justify-center space-x-2 mb-6">
            <div className="w-3 h-3 bg-red-400 rounded-full animate-bounce"></div>
            <div className="w-3 h-3 bg-red-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
            <div className="w-3 h-3 bg-red-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          </div>

          {/* Retry button */}
          {onRetry && (
            <button 
              onClick={onRetry}
              className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-all duration-200 hover:scale-105 active:scale-95"
            >
              🔄 Try Again
            </button>
          )}
          
          {/* Auto retry message */}
          <p className="text-gray-400 text-sm mt-4">
            Don't worry, we're working on fixing this...
          </p>
        </div>
      </div>
    </div>
  );
} 