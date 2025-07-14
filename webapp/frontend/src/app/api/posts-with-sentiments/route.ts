import { NextResponse } from 'next/server'
import { getPosts } from '@/lib/database'

export async function GET() {
  try {
    const posts = await getPosts()
    return NextResponse.json(posts)
  } catch (error) {
    console.error('Error fetching posts with sentiments:', error)
    return NextResponse.json({ error: 'Failed to fetch posts with sentiments' }, { status: 500 })
  }
}
