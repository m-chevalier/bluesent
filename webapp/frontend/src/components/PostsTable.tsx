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
      <div className="text-center py-8 text-muted-foreground">
        No posts available
      </div>
    )
  }

  return (
    <Table className="w-full table-fixed">
      <TableHeader>
        <TableRow>
          <TableHead className="w-[20%]">Date</TableHead>
          <TableHead className="w-[50%]">Content</TableHead>
          <TableHead className="w-[20%]">Sentiment Analysis</TableHead>
          <TableHead className="w-[10%]">LLM Count</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {posts.map((post) => (
          <TableRow key={post.uuid}>
            <TableCell className="font-medium text-sm">
              {formatDate(post.date)}
            </TableCell>
            <TableCell>
              <div className="space-y-1">
                <p className="text-sm whitespace-pre-wrap break-words">
                  {post.content}
                </p>
              </div>
            </TableCell>
            <TableCell>
              <SentimentList sentiments={post.sentiment} />
            </TableCell>
            <TableCell className="text-center">
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-accent text-accent-foreground">
                {post.sentiment.length} {post.sentiment.length === 1 ? 'analysis' : 'analyses'}
              </span>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
