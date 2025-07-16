import { PrismaClient } from '../generated/prisma'

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined
}

export const prisma = globalForPrisma.prisma ?? new PrismaClient()

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma

export async function getPosts() {
  return await prisma.post.findMany({
    include: {
      sentiment: true
    },
    orderBy: {
      date: 'desc'
    }
  })
}

export async function getSentiments() {
  return prisma.sentiment.findMany({
    include: {
      post: true
    }
  })
}

export async function getPostStats() {
  const totalPosts = await prisma.post.count()
  const totalSentiments = await prisma.sentiment.count()
  const uniqueLLMs = await prisma.sentiment.findMany({
    distinct: ['llm_name'],
    select: {
      llm_name: true
    }
  })
  const uniqueSentimentTypes = await prisma.sentiment.findMany({
    distinct: ['sentiment_name'],
    select: {
      sentiment_name: true
    }
  })

  return {
    totalPosts,
    totalSentiments,
    uniqueLLMs: uniqueLLMs.length,
    uniqueSentimentTypes: uniqueSentimentTypes.length,
    llmNames: uniqueLLMs.map(llm => llm.llm_name),
    sentimentTypes: uniqueSentimentTypes.map(sentiment => sentiment.sentiment_name)
  }
}

export async function getSentimentAnalysisByLLM() {
  const result = await prisma.sentiment.groupBy({
    by: ['llm_name', 'sentiment_analysis'],
    _count: {
      sentiment_analysis: true
    }
  })

  return result
}
