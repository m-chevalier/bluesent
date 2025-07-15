'use client'

import { useState, useEffect } from 'react'
import { PostWithSentiments } from '@/types'
import { PostsTable } from '@/components/PostsTable'
import { LoadingTable } from '@/components/LoadingTable'

export default function PostsPage() {
  const [posts, setPosts] = useState<PostWithSentiments[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchPosts() {
      try {
        setLoading(true)
        const response = await fetch('/api/posts-with-sentiments')
        if (!response.ok) {
          throw new Error('Failed to fetch posts')
        }
        const data = await response.json()
        setPosts(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred')
      } finally {
        setLoading(false)
      }
    }

    fetchPosts()
  }, [])

  if (error) {
    return (
      <div className="min-h-[calc(100vh-3.5rem)] bg-background p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-destructive" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-destructive">Error</h3>
                <div className="mt-2 text-sm text-destructive/80">
                  <p>{error}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-[calc(100vh-3.5rem)] bg-background p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground">Posts with Sentiment Analysis</h1>
          <p className="mt-2 text-muted-foreground">
            View all posts with their associated sentiment analysis from different LLMs
          </p>
        </div>

        <div className="bg-card rounded-lg shadow-sm border border-border">
          <div className="px-6 py-4 border-b border-border">
            <h2 className="text-lg font-semibold text-card-foreground">Posts Overview</h2>
            {!loading && (
              <p className="text-sm text-muted-foreground mt-1">
                Showing {posts.length} {posts.length === 1 ? 'post' : 'posts'}
              </p>
            )}
          </div>

          <div className={'w-full'}>
            {loading ? (
              <LoadingTable />
            ) : (
              <PostsTable posts={posts} />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
