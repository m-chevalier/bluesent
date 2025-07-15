'use client'

import { Sentiment } from '@/types'
import { SentimentBadge } from './SentimentBadge'

interface SentimentListProps {
  sentiments: Sentiment[]
}

export function SentimentList({ sentiments }: SentimentListProps) {
  if (sentiments.length === 0) {
    return (
      <div className="text-gray-500 text-sm italic">
        No sentiment analysis available
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {sentiments.map((sentiment, index) => (
        <SentimentBadge
          key={`${sentiment.llm_name}-${sentiment.sentiment_name}-${index}`}
          sentiment={sentiment}
        />
      ))}
    </div>
  )
}
