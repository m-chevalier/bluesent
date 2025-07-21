"use client";

import { useEffect, useState } from 'react';
import { RankingTable } from '@/components/RankingTable';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { LoadingTable } from '@/components/LoadingTable';

interface RankedLlm {
  llmName: string;
  score: number;
  positive: number;
  negative: number;
  neutral: number;
}

interface TopicRanking {
  topicName: string;
  llms: RankedLlm[];
}

export default function RankingPage() {
  const [rankings, setRankings] = useState<TopicRanking[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRankings = async () => {
      try {
        const response = await fetch('/api/ranking');
        const data = await response.json();
        setRankings(data);
      } catch (error) {
        console.error('Error fetching rankings:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchRankings();
  }, []);

  return (
    <div className="container mx-auto p-4">
      <div className="mb-4">
        <h1 className="text-2xl font-bold">LLM Rankings by Topic</h1>
        <p className="text-muted-foreground">
          The LLMs are ranked by topic using a scoring formula that takes into
          account the number of positive and negative reviews.
        </p>
      </div>
      {loading ? (
        <LoadingTable />
      ) : (
        <div className="space-y-4">
          {rankings.map((topic) => (
            <Card key={topic.topicName}>
              <CardHeader>
                <CardTitle>{topic.topicName}</CardTitle>
                <CardDescription>
                  LLM rankings for the topic "{topic.topicName}".
                </CardDescription>
              </CardHeader>
              <CardContent>
                <RankingTable llms={topic.llms} />
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
