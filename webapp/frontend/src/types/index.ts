export interface Post {
  uuid: string
  content: string
  date: string
  sentiment: Sentiment[]
}

export interface Sentiment {
  post_uuid: string
  llm_name: string
  sentiment_name: string
  sentiment_analysis: string
}

export interface PostWithSentiments extends Post {
  sentiment: Sentiment[]
}
