import React from 'react';
import Image from 'next/image';

import Navbar from '@/components/Navbar/Navbar';

const Header: React.FC = () => {
  return (
    <header className="bg-blue-800 text-white flex flex-wrap items-center justify-between py-4 px-6 shadow-md">
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
      <Navbar />
    </header>
  );
};

export default Header;
