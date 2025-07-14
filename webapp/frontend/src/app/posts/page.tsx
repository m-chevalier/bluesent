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
      <div className="min-h-[calc(100vh-3.5rem)] bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <div className="mt-2 text-sm text-red-700">
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
    <div className="min-h-[calc(100vh-3.5rem)] bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Posts with Sentiment Analysis</h1>
          <p className="mt-2 text-gray-600">
            View all posts with their associated sentiment analysis from different LLMs
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Posts Overview</h2>
            {!loading && (
              <p className="text-sm text-gray-600 mt-1">
                Showing {posts.length} {posts.length === 1 ? 'post' : 'posts'}
              </p>
            )}
          </div>

          <div className="overflow-x-auto">
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
