import { NextResponse } from 'next/server';
import { Prisma } from '@prisma/client';
import { prisma } from '@/lib/database';

export async function GET() {
  try {
    const sentiments = await prisma.sentiment.groupBy({
      by: ['sentiment_name', 'llm_name', 'sentiment_analysis'],
      _count: {
        sentiment_analysis: true,
      },
    });

    const topics = sentiments.reduce((acc, curr) => {
      const topicName = curr.sentiment_name;
      const llmName = curr.llm_name;
      const sentiment = curr.sentiment_analysis;
      const count = curr._count.sentiment_analysis;

      if (!acc[topicName]) {
        acc[topicName] = {};
      }

      if (!acc[topicName][llmName]) {
        acc[topicName][llmName] = {
          positive: 0,
          negative: 0,
          neutral: 0,
        };
      }

      if (sentiment === 'positive') {
        acc[topicName][llmName].positive = count;
      } else if (sentiment === 'negative') {
        acc[topicName][llmName].negative = count;
      } else {
        acc[topicName][llmName].neutral = count;
      }

      return acc;
    }, {} as Record<string, Record<string, { positive: number; negative: number; neutral: number }>>);

    const rankedTopics = Object.entries(topics).map(([topicName, llms]) => {
      const rankedLlms = Object.entries(llms)
        .map(([llmName, counts]) => {
          const { positive, negative } = counts;
          const n = positive + negative;

          if (n === 0) {
            return {
              llmName,
              score: 0,
              ...counts,
            };
          }

          const z = 1.96; // 95% confidence level
          const p_hat = positive / n;
          const score =
            (p_hat +
              (z * z) / (2 * n) -
              z * Math.sqrt((p_hat * (1 - p_hat)) / n + (z * z) / (4 * n * n))) /
            (1 + (z * z) / n);

          return {
            llmName,
            score,
            ...counts,
          };
        })
        .sort((a, b) => b.score - a.score);

      return {
        topicName,
        llms: rankedLlms,
      };
    });

    return NextResponse.json(rankedTopics);
  } catch (error) {
    console.error('Error fetching ranking data:', error);
    return NextResponse.json({ error: 'Failed to fetch ranking data' }, { status: 500 });
  }
}
