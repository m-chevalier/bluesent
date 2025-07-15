'use client'

import { Sentiment } from '@/types'

interface SentimentBadgeProps {
  sentiment: Sentiment
}

export function SentimentBadge({ sentiment }: SentimentBadgeProps) {
  const getSentimentColor = (analysis: string) => {
    const lowerAnalysis = analysis.toLowerCase()
    if (lowerAnalysis.includes('positive')) {
      return 'bg-blue-100 text-blue-900 border-blue-300'
    } else if (lowerAnalysis.includes('negative')) {
      return 'bg-[#fde8f0] text-[#d57d97] border-[#d57d97]'
    } else if (lowerAnalysis.includes('neutral')) {
      return 'bg-muted text-muted-foreground border-border'
    }
    return 'bg-accent text-accent-foreground border-border'
  }

  return (
    <div className="flex flex-col space-y-1">
      <div className="flex items-center space-x-2">
        <span className="text-xs font-medium text-muted-foreground">
          {sentiment.llm_name}
        </span>
        <span className="text-xs text-muted-foreground/70">
          ({sentiment.sentiment_name})
        </span>
      </div>
      <span
        className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getSentimentColor(
          sentiment.sentiment_analysis
        )}`}
      >
        {sentiment.sentiment_analysis}
      </span>
    </div>
  )
}
