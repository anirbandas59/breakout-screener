import React from 'react';
import Image from 'next/image';

import Navbar from '@/components/Navbar/Navbar';

const Header: React.FC = () => {
  return (
    <header className="bg-blue-700 text-white flex items-center justify-between py-4 px-6 shadow-md">
      <div className="flex items-center">
        <div className="mx-4">
          <Image
            className="dark:invert"
            src="/vercel.svg"
            alt="Vercel logomark"
            width={20}
            height={20}
          />
        </div>
        <h1 className="text-xl font-bold">Breakout Filtering Utility</h1>
      </div>
      <Navbar />
    </header>
  );
};

export default Header;
