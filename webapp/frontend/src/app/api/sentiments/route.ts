import { NextResponse } from 'next/server'
import { getSentiments } from '@/lib/database'

export async function GET() {
  try {
    const sentiments = await getSentiments()
    return NextResponse.json(sentiments)
  } catch (error) {
    console.error('Error fetching sentiments:', error)
    return NextResponse.json({ error: 'Failed to fetch sentiments' }, { status: 500 })
  }
}
