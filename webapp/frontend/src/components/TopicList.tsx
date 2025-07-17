import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';

interface TopicListProps {
  topics: {
    sentiment_name: string;
  }[];
}

export function TopicList({ topics }: TopicListProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Sentiments by Topic</CardTitle>
      </CardHeader>
      <CardContent>
        <ul>
          {topics.map((topic, index) => (
            <li key={index} className="flex justify-between items-center mb-2">
              <span>{topic.sentiment_name}</span>
              <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
                {topic.sentiment_name}
              </span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
