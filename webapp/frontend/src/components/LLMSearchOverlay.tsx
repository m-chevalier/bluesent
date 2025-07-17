'use client'

import { useState } from 'react'
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

interface LLMSearchOverlayProps {
  isOpen: boolean
  onClose: () => void
}

export function LLMSearchOverlay({ isOpen, onClose }: LLMSearchOverlayProps) {
  const router = useRouter()
  const [llmName, setLLMName] = useState('')

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
            <Input
              id="llm-search"
              type="text"
              value={llmName}
              onChange={(e) => setLLMName(e.target.value)}
              placeholder="Enter LLM name..."
              autoFocus
            />
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
