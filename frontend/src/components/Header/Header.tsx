'use client';

import React, { useState, useEffect } from 'react';
import Image from 'next/image';

import Navbar from '@/components/Navbar/Navbar';

const Header: React.FC = () => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  // Initialize dark mode from localStorage on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('darkMode');
      const initialDarkMode = saved === 'true';
      setIsDarkMode(initialDarkMode);

      if (initialDarkMode) {
        document.documentElement.classList.add('dark');
      }
    }
  }, []);

  // Toggle dark mode
  const toggleDarkMode = () => {
    setIsDarkMode((prev) => {
      const newMode = !prev;

      if (newMode) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }

      localStorage.setItem('darkMode', String(newMode));
      return newMode;
    });
  };

  return (
    <header className="bg-blue-800 dark:bg-gray-900 text-white flex flex-wrap items-center justify-between py-4 px-6 shadow-md">
      <div className="flex items-center gap-4">
        <div className="mx-4">
          <Image
            className="dark:invert rounded-lg"
            src="/b-header-logo.png"
            alt="Vercel logomark"
            width={50}
            height={50}
          />
        </div>
        <h1 className="font-serif text-3xl font-bold">Breakout Filtering Utility</h1>
      </div>
      <div className="flex items-center gap-4">
        <button
          onClick={toggleDarkMode}
          className="px-3 py-2 rounded-md bg-blue-700 dark:bg-gray-800 hover:bg-blue-600 dark:hover:bg-gray-700 transition-colors"
          aria-label="Toggle dark mode"
        >
          {isDarkMode ? '☀️ Light' : '🌙 Dark'}
        </button>
        <Navbar />
      </div>
    </header>
  );
};

export default Header;
