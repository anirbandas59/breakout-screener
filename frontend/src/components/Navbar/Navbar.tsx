import Link from 'next/link';
import React from 'react';

const Navbar: React.FC = () => {
  return (
    <nav className="bg-blue-800 text-white py-3">
      <ul className="flex gap-4 justify-center space-x-8">
        <li>
          <Link href="/" className="hover:underline text-base">
            Home
          </Link>
        </li>
        <li>
          <Link href="/" className="hover:underline text-base">
            Reports
          </Link>
        </li>
        <li>
          <Link href="/" className="hover:underline text-base">
            About
          </Link>
        </li>
        <li>
          <Link href="/" className="hover:underline text-base">
            Settings
          </Link>
        </li>
      </ul>
    </nav>
  );
};

export default Navbar;
