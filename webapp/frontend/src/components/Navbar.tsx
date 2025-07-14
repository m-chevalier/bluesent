'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

export function Navbar() {
  const pathname = usePathname()

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
  ]

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white shadow-sm">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-14 items-center justify-between">
          <div className="flex items-center">
            <Link href="/" className="mr-8 flex items-center space-x-2">
              <span className="font-bold text-lg text-gray-900">
                BlueSent
              </span>
            </Link>
            <nav className="hidden md:flex space-x-8">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`text-sm font-medium transition-colors hover:text-gray-900 ${
                    pathname === item.href
                      ? 'text-blue-600 border-b-2 border-blue-600'
                      : 'text-gray-700'
                  }`}
                >
                  {item.name}
                </Link>
              ))}
            </nav>
          </div>
          
          {/* Mobile menu */}
          <nav className="md:hidden flex space-x-4">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className={`text-sm font-medium transition-colors hover:text-gray-900 ${
                  pathname === item.href
                    ? 'text-blue-600'
                    : 'text-gray-700'
                }`}
              >
                {item.name}
              </Link>
            ))}
          </nav>
        </div>
      </div>
    </header>
  )
}
