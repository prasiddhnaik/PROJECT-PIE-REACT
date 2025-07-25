"use client";

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';

// Theme types
type Theme = 'light' | 'dark' | 'crypto';

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  systemTheme: 'light' | 'dark';
}

// Create theme context
const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// Custom hook to use theme
export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

interface ThemeProviderProps {
  children: ReactNode;
  defaultTheme?: Theme;
  storageKey?: string;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({
  children,
  defaultTheme = 'dark',
  storageKey = 'crypto-analytics-theme',
}) => {
  const [theme, setThemeState] = useState<Theme>(defaultTheme);
  const [systemTheme, setSystemTheme] = useState<'light' | 'dark'>('dark');
  const [mounted, setMounted] = useState(false);

  // Detect system theme preference
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    setSystemTheme(mediaQuery.matches ? 'dark' : 'light');

    const handleChange = (e: MediaQueryListEvent) => {
      setSystemTheme(e.matches ? 'dark' : 'light');
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  // Load theme from localStorage on mount
  useEffect(() => {
    try {
      const savedTheme = localStorage.getItem(storageKey) as Theme;
      if (savedTheme && ['light', 'dark', 'crypto'].includes(savedTheme)) {
        setThemeState(savedTheme);
      }
    } catch (error) {
      console.warn('Failed to load theme from localStorage:', error);
    }
    setMounted(true);
  }, [storageKey]);

  // Apply theme to document
  useEffect(() => {
    if (!mounted) return;

    const root = document.documentElement;
    
    // Remove all theme classes first
    root.removeAttribute('data-theme');
    
    // Apply new theme
    if (theme !== 'light') {
      root.setAttribute('data-theme', theme);
    }

    // Save to localStorage
    try {
      localStorage.setItem(storageKey, theme);
    } catch (error) {
      console.warn('Failed to save theme to localStorage:', error);
    }

    // Update meta theme-color for mobile browsers
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
      const themeColors = {
        light: '#ffffff',
        dark: '#0f172a',
        crypto: '#000814',
      };
      metaThemeColor.setAttribute('content', themeColors[theme]);
    }
  }, [theme, mounted, storageKey]);

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
  };

  const toggleTheme = () => {
    const themes: Theme[] = ['light', 'dark', 'crypto'];
    const currentIndex = themes.indexOf(theme);
    const nextIndex = (currentIndex + 1) % themes.length;
    setTheme(themes[nextIndex]);
  };

  const value: ThemeContextType = {
    theme,
    setTheme,
    toggleTheme,
    systemTheme,
  };

  // Provide context even before mounted to avoid server-side errors.
  if (!mounted) {
    return (
      <ThemeContext.Provider value={value}>
        <div className="opacity-0">{children}</div>
      </ThemeContext.Provider>
    );
  }

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

// Theme toggle button component
export const ThemeToggle: React.FC<{ className?: string }> = ({ className = '' }) => {
  const { theme, toggleTheme } = useTheme();

  const getThemeIcon = (currentTheme: Theme) => {
    switch (currentTheme) {
      case 'light':
        return '☀️';
      case 'dark':
        return '🌙';
      case 'crypto':
        return '₿';
      default:
        return '🌙';
    }
  };

  const getThemeLabel = (currentTheme: Theme) => {
    switch (currentTheme) {
      case 'light':
        return 'Light Mode';
      case 'dark':
        return 'Dark Mode';
      case 'crypto':
        return 'Crypto Mode';
      default:
        return 'Dark Mode';
    }
  };

  return (
    <button
      onClick={toggleTheme}
      className={`btn-secondary flex items-center gap-2 ${className}`}
      aria-label={`Switch to next theme (current: ${getThemeLabel(theme)})`}
      title={`Switch to next theme (current: ${getThemeLabel(theme)})`}
    >
      <span className="text-lg">{getThemeIcon(theme)}</span>
      <span className="hidden sm:inline">{getThemeLabel(theme)}</span>
    </button>
  );
};

// Theme selector dropdown component
export const ThemeSelector: React.FC<{ className?: string }> = ({ className = '' }) => {
  const { theme, setTheme } = useTheme();
  const [isOpen, setIsOpen] = useState(false);

  const themes: { value: Theme; label: string; icon: string; description: string }[] = [
    { value: 'light', label: 'Light', icon: '☀️', description: 'Clean and bright interface' },
    { value: 'dark', label: 'Dark', icon: '🌙', description: 'Easy on the eyes' },
    { value: 'crypto', label: 'Crypto', icon: '₿', description: 'Bitcoin-inspired gold theme' },
  ];

  return (
    <div className={`relative ${className}`}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="btn-secondary flex items-center gap-2 min-w-[140px]"
        aria-label="Select theme"
      >
        <span className="text-lg">{themes.find(t => t.value === theme)?.icon}</span>
        <span>{themes.find(t => t.value === theme)?.label}</span>
        <span className={`transition-transform ${isOpen ? 'rotate-180' : ''}`}>▼</span>
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          
          {/* Dropdown */}
          <div className="absolute top-full left-0 mt-2 w-64 crypto-card p-2 z-50 animate-scale-in">
            {themes.map((themeOption) => (
              <button
                key={themeOption.value}
                onClick={() => {
                  setTheme(themeOption.value);
                  setIsOpen(false);
                }}
                className={`w-full flex items-center gap-3 p-3 rounded-lg text-left transition-colors ${
                  theme === themeOption.value 
                    ? 'bg-var(--surface-elevated) border border-var(--primary-500)' 
                    : 'hover:bg-var(--surface-hover)'
                }`}
              >
                <span className="text-xl">{themeOption.icon}</span>
                <div className="flex-1">
                  <div className="font-medium" style={{ color: 'var(--text-primary)' }}>
                    {themeOption.label}
                  </div>
                  <div className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                    {themeOption.description}
                  </div>
                </div>
                {theme === themeOption.value && (
                  <span className="text-sm font-medium" style={{ color: 'var(--primary-500)' }}>
                    ✓
                  </span>
                )}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}; 