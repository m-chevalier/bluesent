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
    },
    {
      name: 'Ranking',
      href: '/ranking',
      description: 'LLM rankings by topic'
    }
  ]

  return (
    <>
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto flex h-14 items-center justify-between">
          {/* Desktop navigation */}
          <div className="hidden md:flex items-center space-x-6">
            <Link href="/" className="flex items-center space-x-2">
              <span className="font-bold text-lg">
                BlueSent
              </span>
            </Link>
            <NavigationMenu>
              <NavigationMenuList>
                {navigation.map((item) => (
                  <NavigationMenuItem key={item.name}>
                    <Link href={item.href} legacyBehavior passHref>
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
          <div className="flex md:hidden items-center space-x-2">
            <Link href="/" className="flex items-center space-x-2">
              <span className="font-bold text-lg">BlueSent</span>
            </Link>
            {navigation.map((item) => (
              <Button
                  key={item.name}
                  variant={pathname === item.href ? "default" : "ghost"}
                  size="sm"
                  asChild
                >
                  <Link href={item.href}>{item.name}</Link>
                </Button>
            ))}
          </div>

          {/* LLM Stats button - always on the right */}
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowLLMSearch(true)}
          >
            LLM Stats
          </Button>
        </div>
      </header>

      <LLMSearchOverlay
        isOpen={showLLMSearch}
        onClose={() => setShowLLMSearch(false)}
      />
    </>
  )
}
