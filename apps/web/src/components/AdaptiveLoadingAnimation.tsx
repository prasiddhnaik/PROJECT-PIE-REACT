'use client';

import React from 'react';
import { useEffect, useState } from 'react';

export type LoadingTask = 
  | 'quick' 
  | 'api_call' 
  | 'data_processing' 
  | 'ai_analysis' 
  | 'complex_calculation'
  | 'market_data'
  | 'portfolio_analysis';

interface AdaptiveLoadingAnimationProps {
  isVisible: boolean;
  task: LoadingTask;
  customMessage?: string;
  onComplete?: () => void;
}

const taskConfigs = {
  quick: {
    duration: 800,
    message: "Loading",
    color: "from-green-500 to-blue-500",
    icon: "⚡"
  },
  api_call: {
    duration: 1200,
    message: "Connecting",
    color: "from-blue-500 to-purple-500",
    icon: "🔗"
  },
  data_processing: {
    duration: 1500,
    message: "Processing",
    color: "from-purple-500 to-pink-500",
    icon: "📊"
  },
  ai_analysis: {
    duration: 1800,
    message: "AI Analysis",
    color: "from-pink-500 to-red-500",
    icon: "🤖"
  },
  complex_calculation: {
    duration: 2000,
    message: "Computing",
    color: "from-red-500 to-orange-500",
    icon: "🧮"
  },
  market_data: {
    duration: 1000,
    message: "Market Data",
    color: "from-blue-500 to-green-500",
    icon: "📈"
  },
  portfolio_analysis: {
    duration: 1500,
    message: "Portfolio",
    color: "from-green-500 to-teal-500",
    icon: "💼"
  }
};

export default function AdaptiveLoadingAnimation({ 
  isVisible, 
  task, 
  customMessage,
  onComplete 
}: AdaptiveLoadingAnimationProps) {
  const config = taskConfigs[task];
  const [progress, setProgress] = useState(0);
  const [dots, setDots] = useState('');

  useEffect(() => {
    if (!isVisible) return;

    setProgress(0);
    setDots('');

    const totalDuration = config.duration;
    const intervalTime = 50; // Smooth 60fps updates
    const totalSteps = totalDuration / intervalTime;

    let currentStep = 0;

    const timer = setInterval(() => {
      currentStep++;
      const elapsed = currentStep * intervalTime;
      const progressPercent = (elapsed / totalDuration) * 100;

      setProgress(Math.min(100, progressPercent));

      // Animated dots
      const dotCount = Math.floor((elapsed / 200) % 4);
      setDots('.'.repeat(dotCount));

      if (elapsed >= totalDuration) {
        clearInterval(timer);
        setProgress(100);
        // Small delay before completing to show 100%
        setTimeout(() => onComplete?.(), 150);
      }
    }, intervalTime);

    return () => clearInterval(timer);
  }, [isVisible, task, config, onComplete]);

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-80 backdrop-blur-sm">
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-2xl max-w-sm w-full mx-4">
        {/* Icon and message */}
        <div className="text-center mb-6">
          <div className="text-5xl mb-3 animate-bounce">{config.icon}</div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            {customMessage || config.message}
          </h3>
          <p className="text-gray-600 dark:text-gray-400 text-sm">
            Please wait{dots}
          </p>
        </div>

        {/* Progress bar */}
        <div className="relative">
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
            <div 
              className={`h-full bg-gradient-to-r ${config.color} transition-all duration-100 ease-out relative`}
              style={{ width: `${progress}%` }}
            >
              {/* Shimmer effect */}
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-30 animate-pulse"></div>
            </div>
          </div>
          
          {/* Progress percentage */}
          <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
            <span>Loading...</span>
            <span>{Math.round(progress)}%</span>
          </div>
        </div>

        {/* Quick completion indicator */}
        {progress > 95 && (
          <div className="mt-4 text-center">
            <div className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
              <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Almost ready!
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 