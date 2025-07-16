import { NextResponse } from 'next/server';
import {prisma} from "@/lib/database";

export async function GET(request: Request, { params }: { params: { llmName: string } }) {

  const { llmName } = await params;

  try {
    const sentimentStats = await prisma.sentiment.groupBy({
      by: ['sentiment_name'],
      where: {
        llm_name: llmName,
      },
      _count: {
        sentiment_name: true,
      },
    });

    const recentPosts = await prisma.post.findMany({
      where: {
        sentiment: {
          some: {
            llm_name: llmName,
          },
        },
      },
      include: {
        sentiment: {
          where: {
            llm_name: llmName,
          },
        },
      },
      orderBy: {
        date: 'desc',
      },
      take: 20,
    });

    const totalSentiments = await prisma.sentiment.groupBy({
        by: ['sentiment_analysis'],
        where: {
            llm_name: llmName,
            sentiment_analysis: {
                in: ['positive', 'negative']
            }
        },
        _count: {
            sentiment_analysis: true
        }
    });

    return NextResponse.json({
      sentimentStats,
      recentPosts,
      totalSentiments
    });
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'Failed to fetch LLM stats' }, { status: 500 });
  }
}
