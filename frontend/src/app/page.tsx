'use client';

import Header from '@/components/Header/Header';
import HomePage from '@/components/HomePage/HomePage';

export default function Home() {
  return (
    <div className="font-sans">
      <Header />
      <main className="flex flex-1 gap-2 row-start-2 items-center sm:items-start">
        <HomePage />
      </main>
    </div>
  );
}
