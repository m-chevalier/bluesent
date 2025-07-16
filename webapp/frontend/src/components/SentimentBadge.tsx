'use client'

interface SentimentBadgeProps {
  sentiment: string
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
    } else if (lowerAnalysis.includes('joy')) {
        return 'bg-yellow-100 text-yellow-900 border-yellow-300'
    } else if (lowerAnalysis.includes('sadness')) {
        return 'bg-gray-100 text-gray-900 border-gray-300'
    } else if (lowerAnalysis.includes('fear')) {
        return 'bg-purple-100 text-purple-900 border-purple-300'
    } else if (lowerAnalysis.includes('disgust')) {
        return 'bg-green-100 text-green-900 border-green-300'
    } else if (lowerAnalysis.includes('anger')) {
        return 'bg-red-100 text-red-900 border-red-300'
    }

    return 'bg-accent text-accent-foreground border-border'
  }

  return (
    <span
      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getSentimentColor(
        sentiment
      )}`}
    >
      {sentiment}
    </span>
  )
}
