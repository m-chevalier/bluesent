'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { LlmStats } from '@/types';
import { Navbar } from '@/components/Navbar';
import { PostsTable } from '@/components/PostsTable';
import { SentimentBadge } from '@/components/SentimentBadge';
import { LoadingTable } from '@/components/LoadingTable';

export default function LlmStatsPage() {
  const [stats, setStats] = useState<LlmStats | null>(null);
  const [filteredPosts, setFilteredPosts] = useState<any[]>([]);
  const [selectedTopic, setSelectedTopic] = useState<string>('all');
  const params = useParams();
  const llmName = params.llmName as string;

  useEffect(() => {
    if (llmName) {
      fetch(`/api/llm/${llmName}/stats`)
        .then((res) => res.json())
        .then((data) => {
          setStats(data);
          setFilteredPosts(data.recentPosts);
        });
    }
  }, [llmName]);

  useEffect(() => {
    if (stats) {
      if (selectedTopic === 'all') {
        setFilteredPosts(stats.recentPosts);
      } else {
        setFilteredPosts(
          stats.recentPosts.filter((post) =>
            post.sentiment.some(
              (s: any) => s.sentiment_name === selectedTopic
            )
          )
        );
      }
    }
  }, [selectedTopic, stats]);

  if (!stats) {
    return <LoadingTable/>;
  }

  const topics = [
    'all',
    ...Array.from(new Set(stats.sentimentStats.map((s) => s.sentiment_name))),
  ];

  return (
    <div>
      <Navbar />
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Statistics for {llmName}</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          <div className="p-4 border rounded">
            <h2 className="text-xl font-semibold mb-2">Sentiment Summary</h2>
            <div className="flex justify-around">
                {stats.totalSentiments.map((sentiment, index) => (
                    <div key={index} className="text-center">
                        <p className="text-lg capitalize">{sentiment.sentiment_analysis}</p>
                        <p className="text-3xl font-bold">{sentiment._count.sentiment_analysis}</p>
                    </div>
                ))}
            </div>
          </div>
          <div className="p-4 border rounded">
            <h2 className="text-xl font-semibold mb-2">Sentiments by Topic</h2>
            <ul>
              {stats.sentimentStats.map((stat, index) => (
                <li key={index} className="flex justify-between">
                  <span>{stat.sentiment_name}</span>
                  <SentimentBadge sentiment={stat.sentiment_name} />
                </li>
              ))}
            </ul>
          </div>
        </div>


        <div>
          <h2 className="text-xl font-semibold mb-2">Recent Posts</h2>
          <div className="mb-4">
            <label htmlFor="topic-filter" className="mr-2">Filter by topic:</label>
            <select
              id="topic-filter"
              value={selectedTopic}
              onChange={(e) => setSelectedTopic(e.target.value)}
              className="p-2 border rounded"
            >
              {topics.map((topic) => (
                <option key={topic} value={topic}>
                  {topic}
                </option>
              ))}
            </select>
          </div>
          <PostsTable posts={filteredPosts} />
        </div>
      </div>
    </div>
  );
}
