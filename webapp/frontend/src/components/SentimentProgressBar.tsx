import { Progress } from "@/components/ui/progress";

interface SentimentProgressBarProps {
  positive: number;
  negative: number;
  className?: string;
  compact?: boolean;
}

export function SentimentProgressBar({ positive, negative, className = "", compact = false }: SentimentProgressBarProps) {
  const total = positive + negative;

  // Handle edge case where total is 0
  if (total === 0) {
    return (
      <div className={`${compact ? 'w-24' : 'w-full'} ${className}`}>
        <div className={`${compact ? 'w-24 h-2' : 'w-full h-4'} bg-gray-200 rounded-full flex items-center justify-center`}>
          <span className="text-xs text-gray-500">No data</span>
        </div>
      </div>
    );
  }

  const positivePercentage = (positive / total) * 100;
  const negativePercentage = (negative / total) * 100;

  return (
    <div className={`${compact ? 'w-24' : 'w-full'} ${className}`}>
      {/* Progress bar container with custom dual-color implementation */}
      <div className={`relative ${compact ? 'w-24 h-2' : 'w-full h-4'}`}>
        {/* Background progress bar for negative (pink/rose) */}
        <Progress
          value={100}
          className={`absolute inset-0 ${compact ? 'h-2' : 'h-4'} bg-gray-200`}
        />
        <div className={`absolute inset-0 ${compact ? 'h-2' : 'h-4'} rounded-full`}
             style={{
               width: `${negativePercentage}%`,
               marginLeft: `${positivePercentage}%`,
               backgroundColor: '#d57d97' // Using your negative sentiment color
             }}
             title={`${negative} negative (${negativePercentage.toFixed(1)}%)`}
        />

        {/* Foreground progress bar for positive (blue) */}
        <Progress
          value={positivePercentage}
          className={`absolute inset-0 ${compact ? 'h-2' : 'h-4'} bg-transparent [&>div]:bg-blue-900`}
          title={`${positive} positive (${positivePercentage.toFixed(1)}%)`}
        />
      </div>

      {/* Labels below the progress bar - only show in non-compact mode */}
      {!compact && (
        <div className="flex justify-between text-xs mt-1 text-gray-600">
          <span className="text-blue-900">
            {positive} ({positivePercentage.toFixed(1)}%)
          </span>
          <span style={{ color: '#d57d97' }}>
            {negative} ({negativePercentage.toFixed(1)}%)
          </span>
        </div>
      )}
    </div>
  );
}
