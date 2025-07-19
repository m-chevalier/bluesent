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
        <div
          key={`${sentiment.llm_name}-${sentiment.sentiment_name}-${index}`}
          className="flex flex-col space-y-1"
        >
          <div className="flex items-center space-x-2">
            <span className="text-xs font-medium text-muted-foreground">
              {sentiment.llm_name}
            </span>
            <span className="text-xs text-muted-foreground/70">
              ({sentiment.sentiment_name})
            </span>
          </div>
          <SentimentBadge sentiment={sentiment.sentiment_analysis} />
        </div>
      ))}
    </div>
  )
}
