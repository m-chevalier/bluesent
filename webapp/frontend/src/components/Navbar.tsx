'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState } from 'react'
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  navigationMenuTriggerStyle,
} from '@/components/ui/navigation-menu'
import { Button } from '@/components/ui/button'
import { LLMSearchOverlay } from './LLMSearchOverlay'
import { cn } from '@/lib/utils'

export function Navbar() {
  const pathname = usePathname()
  const [showLLMSearch, setShowLLMSearch] = useState(false)

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
    <>
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 items-center">
          <div className="mr-4 hidden md:flex">
            <Link href="/" className="mr-6 flex items-center space-x-2">
              <span className="hidden font-bold sm:inline-block">
                BlueSent
              </span>
            </Link>
            <NavigationMenu>
              <NavigationMenuList>
                {navigation.map((item) => (
                  <NavigationMenuItem key={item.name}>
                    <Link href={item.href} passHref>
                      <NavigationMenuLink
                        className={cn(
                          navigationMenuTriggerStyle(),
                          pathname === item.href && "bg-accent"
                        )}
                      >
                        {item.name}
                      </NavigationMenuLink>
                    </Link>
                  </NavigationMenuItem>
                ))}
              </NavigationMenuList>
            </NavigationMenu>
          </div>

          {/* Mobile navigation */}
          <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
            <div className="w-full flex-1 md:w-auto md:flex-none">
              <div className="flex md:hidden">
                <Link href="/" className="mr-6 flex items-center space-x-2">
                  <span className="font-bold">BlueSent</span>
                </Link>
              </div>
            </div>
            <nav className="flex items-center space-x-1">
              {/* Mobile menu items */}
              <div className="flex md:hidden space-x-2">
                {navigation.map((item) => (
                  <Link key={item.name} href={item.href}>
                    <Button
                      variant={pathname === item.href ? "default" : "ghost"}
                      size="sm"
                    >
                      {item.name}
                    </Button>
                  </Link>
                ))}
              </div>

              {/* LLM Stats button */}
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowLLMSearch(true)}
              >
                LLM Stats
              </Button>
            </nav>
          </div>
        </div>
      </header>

      <LLMSearchOverlay
        isOpen={showLLMSearch}
        onClose={() => setShowLLMSearch(false)}
      />
    </>
  )
}
