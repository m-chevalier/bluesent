'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState } from 'react';
import { LLMSearchOverlay } from './LLMSearchOverlay';

export function Navbar() {
  const pathname = usePathname();
  const [showLLMSearch, setShowLLMSearch] = useState(false);

  const navigation = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      description: 'View analytics and statistics'
    },
    {
      name: 'Posts',
      href: '/posts',
      description: 'Browse posts with sentiment analysis'
    }
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/80 backdrop-blur-sm shadow-sm">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-14 items-center justify-between">
          <div className="flex items-center">
            <Link href="/" className="mr-8 flex items-center space-x-2">
              <span className="font-bold text-lg text-primary">
                BlueSent
              </span>
            </Link>
            <nav className="hidden md:flex space-x-8">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`text-sm font-medium transition-colors hover:text-primary ${
                    pathname === item.href
                      ? 'text-primary border-b-2 border-primary'
                      : 'text-muted-foreground'
                  }`}
                >
                  {item.name}
                </Link>
              ))}
              <button
                className="text-sm font-medium transition-colors hover:text-primary text-muted-foreground border border-primary rounded px-3 py-1 ml-4"
                onClick={() => setShowLLMSearch(true)}
              >
                LLM Stats
              </button>
            </nav>
          </div>
          {/* Mobile menu */}
          <nav className="md:hidden flex space-x-4">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className={`text-sm font-medium transition-colors hover:text-primary ${
                  pathname === item.href
                    ? 'text-primary'
                    : 'text-muted-foreground'
                }`}
              >
                {item.name}
              </Link>
            ))}
            <button
              className="text-sm font-medium transition-colors hover:text-primary text-muted-foreground border border-primary rounded px-2 py-1"
              onClick={() => setShowLLMSearch(true)}
            >
              LLM Stats
            </button>
          </nav>
        </div>
      </div>

      <LLMSearchOverlay
        isOpen={showLLMSearch}
        onClose={() => setShowLLMSearch(false)}
      />
    </header>
  );
}
