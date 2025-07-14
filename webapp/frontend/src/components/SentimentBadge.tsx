'use client'

import { Sentiment } from '@/types'

interface SentimentBadgeProps {
  sentiment: Sentiment
}

export function SentimentBadge({ sentiment }: SentimentBadgeProps) {
  const getSentimentColor = (analysis: string) => {
    const lowerAnalysis = analysis.toLowerCase()
    if (lowerAnalysis.includes('positive')) {
      return 'bg-green-100 text-green-800 border-green-200'
    } else if (lowerAnalysis.includes('negative')) {
      return 'bg-red-100 text-red-800 border-red-200'
    } else if (lowerAnalysis.includes('neutral')) {
      return 'bg-gray-100 text-gray-800 border-gray-200'
    }
    return 'bg-blue-100 text-blue-800 border-blue-200'
  }

  return (
    <div className="flex flex-col space-y-1">
      <div className="flex items-center space-x-2">
        <span className="text-xs font-medium text-gray-600">
          {sentiment.llm_name}
        </span>
        <span className="text-xs text-gray-500">
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
