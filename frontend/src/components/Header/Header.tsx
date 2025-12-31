'use client';

import React from 'react';
import Image from 'next/image';
import ThemeToggle from '@/components/layouts/ThemeToggle';

const Header: React.FC = () => {
  return (
    <header className="border-b bg-card px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Image
            className="dark:invert rounded-lg"
            src="/b-header-logo.png"
            alt="Breakout Screener Logo"
            width={50}
            height={50}
          />
          <h1 className="font-serif text-2xl font-bold text-foreground">
            Breakout Filtering Utility
          </h1>
        </div>
        <div className="flex items-center gap-4">
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
};

export default Header;
