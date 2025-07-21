import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { SentimentProgressBar } from './SentimentProgressBar';

interface SentimentBreakdownItem {
    sentiment_name: string;
    sentiment_analysis: string;
    _count: {
        sentiment_analysis: number;
    };
}

interface TopicListItem {
    sentiment_name: string;
    positive: number;
    negative: number;
    total: number;
}

interface TopicListProps {
    sentimentTopicBreakdown: SentimentBreakdownItem[];
}

export function TopicList({ sentimentTopicBreakdown }: TopicListProps) {
  // Process the breakdown data to group by topic and separate positive/negative counts
  const processedTopics: TopicListItem[] = [];

  // Group by sentiment_name and calculate positive/negative counts
  const topicMap = new Map<string, { positive: number; negative: number }>();

  sentimentTopicBreakdown.forEach(item => {
    if (!topicMap.has(item.sentiment_name)) {
      topicMap.set(item.sentiment_name, { positive: 0, negative: 0 });
    }

    const topic = topicMap.get(item.sentiment_name)!;
    if (item.sentiment_analysis === 'positive') {
      topic.positive = item._count.sentiment_analysis;
    } else if (item.sentiment_analysis === 'negative') {
      topic.negative = item._count.sentiment_analysis;
    }
  });

  // Convert map to array
  topicMap.forEach((counts, topicName) => {
    processedTopics.push({
      sentiment_name: topicName,
      positive: counts.positive,
      negative: counts.negative,
      total: counts.positive + counts.negative
    });
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Sentiments by Topic</CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="space-y-3">
          {processedTopics.map((topic, index) => (
            <li key={index} className="border-b pb-2 last:border-b-0">
              <div className="flex justify-between items-center">
                <div className="flex flex-col">
                  <span className="font-medium">{topic.sentiment_name}</span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {topic.positive} pos, {topic.negative} neg ({topic.total} total)
                  </span>
                </div>
                <SentimentProgressBar
                  positive={topic.positive}
                  negative={topic.negative}
                  compact={true}
                />
              </div>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
