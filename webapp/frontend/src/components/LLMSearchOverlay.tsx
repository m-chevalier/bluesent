'use client'

import React, {useEffect, useState} from 'react'
import { useRouter } from 'next/navigation'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import {cn} from "@/lib/utils";

interface LLMSearchOverlayProps {
  isOpen: boolean
  onClose: () => void
}

export function LLMSearchOverlay({ isOpen, onClose }: LLMSearchOverlayProps) {
  const router = useRouter()
  const [llmName, setLLMName] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [llmList, setLlmList] = useState<string[]>([]);
  const [activeIndex, setActiveIndex] = useState(-1);

  const handleSuggestionClick = (suggestion: string) => {
    setLLMName(suggestion);
    setSuggestions([]);
    setActiveIndex(-1);
  };


  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    // Handle arrow keys and escape when suggestions are visible
    if (suggestions.length > 0) {
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setActiveIndex(prevIndex => (prevIndex + 1) % suggestions.length);
          break;

        case 'ArrowUp':
          e.preventDefault();
          setActiveIndex(prevIndex => (prevIndex - 1 + suggestions.length) % suggestions.length);
          break;

        case 'Enter':
          e.preventDefault();
          if (activeIndex !== -1) {
            handleSuggestionClick(suggestions[activeIndex]);
          } else if (suggestions.length > 0) {
            handleSuggestionClick(suggestions[0]);
          }
          break;

        case 'Escape':
          // Clear suggestions to hide the list
          setSuggestions([]);
          setActiveIndex(-1);
          break;
      }
    }
  };


  useEffect(() => {
    const fetchLlmList = async () => {
      try {
        const response = await fetch('/api/llm/listllms')
        if (!response.ok) {
          throw new Error('Failed to fetch LLM list')
        }
        const data = await response.json()
        setLlmList(data.llmNames)
      } catch (error) {
        console.error('Error fetching LLM list:', error)
      }
    };

    fetchLlmList();
  }, [])

  useEffect(() => {
    if (llmName.trim().length > 0 && llmList.length > 0) {
      const filteredSuggestions = llmList.filter(name =>
          name.toLowerCase().includes(llmName.toLowerCase())
      );
      setSuggestions(filteredSuggestions);
    } else {
      setSuggestions([]);
    }
    setActiveIndex(-1);
  }, [llmName, llmList]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (llmName.trim()) {
      router.push(`/llm/${llmName.trim()}`)
      onClose()
      setLLMName('')
    }
  }

  const handleClose = () => {
    onClose()
    setLLMName('')
  }

  const handleOpenChange = (open: boolean) => {
    if (!open) {
      handleClose()
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Search LLM Stats</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="llm-search">LLM Name</Label>
            <div className="relative">
              <Input
                id="llm-search"
                type="text"
                value={llmName}
                onChange={(e) => setLLMName(e.target.value)}
                placeholder="Enter LLM name..."
                onKeyDown={handleKeyDown}
                autoFocus
              />
              {suggestions.length > 0 && (
                  <ul className="absolute z-10 w-full mt-1 bg-background border rounded-md shadow-lg max-h-60 overflow-y-auto">
                    {suggestions.map((suggestion, index) => (
                        <li
                            key={suggestion}
                            className={cn(
                                'px-3 py-2 text-sm cursor-pointer hover:bg-accent',
                                index === activeIndex && 'bg-accent'
                            )}
                            onClick={() => handleSuggestionClick(suggestion)}
                        >
                          {suggestion}
                        </li>
                    ))}
                  </ul>
              )}
            </div>
          </div>
          <div className="flex justify-end space-x-2">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
            >
              Cancel
            </Button>
            <Button type="submit">
              Go
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
