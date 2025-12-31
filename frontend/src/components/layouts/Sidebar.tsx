"use client"

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

const navItems = [
  {
    title: 'Scanner',
    href: '/',
    icon: '📊',
  },
  {
    title: 'Reports',
    href: '/reports',
    icon: '📈',
  },
  {
    title: 'Settings',
    href: '/settings',
    icon: '⚙️',
  },
  {
    title: 'About',
    href: '/about',
    icon: 'ℹ️',
  },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r bg-card p-4">
      <div className="mb-8">
        <h2 className="text-xl font-bold">Breakout Screener</h2>
        <p className="text-sm text-muted-foreground">NSE Stock Analysis</p>
      </div>

      <nav className="space-y-2">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'hover:bg-accent hover:text-accent-foreground'
              )}
            >
              <span className="text-xl">{item.icon}</span>
              <span className="font-medium">{item.title}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
