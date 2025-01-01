import Link from 'next/link';
import React from 'react';

const Navbar: React.FC = () => {
  return (
    <nav>
      <ul className="flex space-x-6">
        <li>
          <Link href="/" className="hover:underline text-lg">
            Home
          </Link>
        </li>
        <li>
          <Link href="/" className="hover:underline text-lg">
            Reports
          </Link>
        </li>
        <li>
          <Link href="/" className="hover:underline text-lg">
            About
          </Link>
        </li>
        <li>
          <Link href="/" className="hover:underline text-lg">
            Settings
          </Link>
        </li>
      </ul>
    </nav>
  );
};

export default Navbar;
