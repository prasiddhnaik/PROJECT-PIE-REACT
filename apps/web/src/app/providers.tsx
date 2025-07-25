'use client'

import React, { useState } from 'react'
import * as NavigationMenu from "@radix-ui/react-navigation-menu";
import Link from "next/link";
import { motion } from "framer-motion";

// Simple AI Chatbot Component with modern styling
function AIChatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Array<{role: 'user' | 'assistant', content: string}>>([
    { role: 'assistant', content: 'Hi! I\'m your AI assistant for crypto analysis. Ask me about cryptocurrencies, blockchain trends, or crypto trading strategies!' }
  ]);
  const [input, setInput] = useState('');
  const [isThinking, setIsThinking] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    const userMessage = input.trim();
    setInput('');
    
    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsThinking(true);
    
    try {
      // Call real AI API
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8001';
      const response = await fetch(`${backendUrl}/api/ai/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: data.response 
        }]);
      } else {
        throw new Error('API request failed');
      }
      setIsThinking(false);
    } catch (error) {
      console.error('AI Chat error:', error);
      // Fallback to crypto-focused responses
      const fallbackResponses = [
        "I'm experiencing connectivity issues. Based on general crypto analysis, focus on diversified crypto portfolios with established coins like Bitcoin and Ethereum.",
        "Unable to connect to live analysis. Consider technical indicators like RSI and moving averages for crypto evaluation, especially during high volatility periods.",
        "Connection interrupted. Remember to maintain proper risk management with stop-losses and position sizing in crypto trading.",
        "Service temporarily unavailable. Crypto market volatility requires careful analysis and patient DCA (Dollar-Cost Averaging) approaches."
      ];
      const fallbackResponse = fallbackResponses[Math.floor(Math.random() * fallbackResponses.length)];
      
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `${fallbackResponse} [Offline mode - reconnecting...]` 
      }]);
      setIsThinking(false);
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-16 h-16 neon-glow animate-float"
        style={{
          background: 'var(--gradient-primary)',
          borderRadius: '50%',
          border: 'none',
          color: 'white',
          fontSize: '1.5rem',
          zIndex: 1000,
          cursor: 'pointer',
          transition: 'all 0.3s ease'
        }}
        title="Open AI Assistant"
      >
        🤖
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 w-80 h-96 glass-effect rounded-lg shadow-xl z-50 flex flex-col animate-slide-in">
      {/* Header */}
      <div 
        className="flex items-center justify-between p-4 rounded-t-lg text-white"
        style={{ background: 'var(--gradient-primary)' }}
      >
        <div className="flex items-center space-x-2">
          <span className="animate-float">🤖</span>
          <span className="font-semibold">AI Assistant</span>
          <span className="text-xs status-positive">LIVE</span>
        </div>
        <button
          onClick={() => setIsOpen(false)}
          className="text-white hover:text-gray-200 transition-colors"
        >
          ✕
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 p-4 overflow-y-auto space-y-3">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}
          >
            <div
              className={`max-w-[80%] p-3 rounded-lg text-sm ${
                message.role === 'user'
                  ? 'text-white rounded-br-none'
                  : 'text-gray-200 rounded-bl-none'
              }`}
              style={{
                background: message.role === 'user' 
                  ? 'var(--gradient-primary)' 
                  : 'var(--surface-elevated)'
              }}
            >
              {message.content}
            </div>
          </div>
        ))}
        {isThinking && (
          <div className="flex justify-start">
            <div 
              className="px-4 py-2 rounded-lg rounded-bl-none text-gray-200"
              style={{ background: 'var(--surface-elevated)' }}
            >
              <div className="flex items-center space-x-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 rounded-full animate-bounce" style={{background: 'var(--accent-blue)', animationDelay: '0ms'}}></div>
                  <div className="w-2 h-2 rounded-full animate-bounce" style={{background: 'var(--accent-blue)', animationDelay: '150ms'}}></div>
                  <div className="w-2 h-2 rounded-full animate-bounce" style={{background: 'var(--accent-blue)', animationDelay: '300ms'}}></div>
                </div>
                <span className="text-xs text-gray-400">AI analyzing...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="p-4" style={{ borderTop: '1px solid var(--border)' }}>
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Ask about crypto, analysis..."
            className="flex-1 p-2 border rounded-lg text-sm focus:outline-none focus:ring-2 text-white"
            style={{
              background: 'var(--surface-elevated)',
              borderColor: 'var(--border)'
            }}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim()}
            className="btn-primary text-sm"
          >
            Send
          </button>
        </div>
        <p className="text-xs mt-2 text-center" style={{ color: 'var(--text-muted)' }}>
          Live AI • 100+ trained crypto responses • Real market data
        </p>
      </div>
    </div>
  );
}

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <>
      {/* Modern Navigation Bar */}
      <NavigationMenu.Root 
        className="px-6 py-4 shadow-lg glass-effect"
        style={{ 
          background: 'var(--surface)',
          borderBottom: '1px solid var(--border)'
        }}
      >
        <NavigationMenu.List className="flex gap-2">
          <NavigationMenu.Item>
            <NavigationMenu.Link asChild>
              <Link href="/" className="nav-item gradient-text font-bold text-lg">
                💰 CryptoPie
              </Link>
            </NavigationMenu.Link>
          </NavigationMenu.Item>
          <NavigationMenu.Item>
            <NavigationMenu.Link asChild>
              <Link href="/" className="nav-item">
                🏠 Dashboard
              </Link>
            </NavigationMenu.Link>
          </NavigationMenu.Item>
          <NavigationMenu.Item>
            <NavigationMenu.Link asChild>
              <Link href="/crypto" className="nav-item">
                ₿ Crypto
              </Link>
            </NavigationMenu.Link>
          </NavigationMenu.Item>
          <NavigationMenu.Item>
            <NavigationMenu.Link asChild>
              <Link href="/market" className="nav-item">
                📈 Market
              </Link>
            </NavigationMenu.Link>
          </NavigationMenu.Item>
          <NavigationMenu.Item>
            <NavigationMenu.Link asChild>
              <Link href="/crypto-analytics" className="nav-item">
                📊 Analytics
              </Link>
            </NavigationMenu.Link>
          </NavigationMenu.Item>
          <NavigationMenu.Item>
            <NavigationMenu.Link asChild>
              <Link href="/ai-predictions" className="nav-item neon-glow">
                🤖 AI Insights
              </Link>
            </NavigationMenu.Link>
          </NavigationMenu.Item>
          <NavigationMenu.Item>
            <NavigationMenu.Link asChild>
              <Link 
                href="http://localhost:8001/docs" 
                target="_blank"
                className="nav-item"
              >
                📚 API Docs
              </Link>
            </NavigationMenu.Link>
          </NavigationMenu.Item>
        </NavigationMenu.List>
      </NavigationMenu.Root>

      {/* Animated content wrapper */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="min-h-screen"
        style={{ background: 'var(--background)' }}
      >
        {children}
      </motion.div>

      {/* AI Chatbot */}
      <AIChatbot />
    </>
  )
}
