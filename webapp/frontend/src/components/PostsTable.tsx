'use client'

import { PostWithSentiments } from '@/types'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from './ui/table'
import { SentimentList } from './SentimentList'

interface PostsTableProps {
  posts: PostWithSentiments[]
}

export function PostsTable({ posts }: PostsTableProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const truncateContent = (content: string, maxLength: number = 100) => {
    if (content.length <= maxLength) return content
    return content.substring(0, maxLength) + '...'
  }

  if (posts.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No posts available
      </div>
    )
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-[100px]">Date</TableHead>
          <TableHead className="w-[40%]">Content</TableHead>
          <TableHead className="w-[40%]">Sentiment Analysis</TableHead>
          <TableHead className="w-[20%]">LLM Count</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {posts.map((post) => (
          <TableRow key={post.uuid}>
            <TableCell className="font-medium text-sm">
              {formatDate(post.date)}
            </TableCell>
            <TableCell>
              <div className="max-w-md">
                <p className="text-sm leading-relaxed">
                  {truncateContent(post.content, 150)}
                </p>
              </div>
            </TableCell>
            <TableCell>
              <SentimentList sentiments={post.sentiment} />
            </TableCell>
            <TableCell className="text-center">
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {post.sentiment.length} {post.sentiment.length === 1 ? 'analysis' : 'analyses'}
              </span>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
