import os
from pydantic import BaseModel
from typing import List, Literal, Optional
from mistralai import Mistral
import logging
import json
import time
import random
from enum import Enum

topics = ["speed", "cost", "quality", "safety", "reliability", "performance", "coding_ability", "creativity", "privacy", "hallucination"]
llms = ["chatGPT", "claude","gemini","bard","llama","mistral","grok","kimi"]

LlmEnum = Enum('LlmEnum', {v: v for v in llms})

MISTRAL_KEY = os.getenv("MISTRAL_KEY", None)
if not MISTRAL_KEY:
    raise ValueError("MISTRAL_KEY environment variable is not set. Please set it to use the Mistral API.")


SentimentValue = Literal["positive", "negative", "neutral", "not-present"]

# Define the Pydantic models for the response structure
class Sentiments(BaseModel):
    speed: Optional[SentimentValue]
    cost: Optional[SentimentValue]
    quality: Optional[SentimentValue]
    safety: Optional[SentimentValue]
    reliability: Optional[SentimentValue]
    performance: Optional[SentimentValue]
    coding_ability: Optional[SentimentValue]
    creativity: Optional[SentimentValue]
    privacy: Optional[SentimentValue]
    hallucination: Optional[SentimentValue]

class LLMEntry(BaseModel):
    name: LlmEnum
    sentiments: Sentiments

class LLMResponse(BaseModel):
    status: Literal["success", "error"]
    llms: List[LLMEntry]


client = Mistral(MISTRAL_KEY)


def analyse_post(text, retries=5):
    model="mistral-large-latest"
    nl = "\n"
    sysprompt=f"""
You are a specialized AI assistant for sentiment analysis. Your task is to analyze the user's text to find mentions of specific Large Language Models (LLMs) and determine the sentiment for a predefined set of topics.

Your entire response MUST be a single, valid JSON object that conforms to the provided schema. Do not add any text or explanation before or after the JSON.

### Rules:

1.  **Target LLMs & Standardization:**
    You must only detect the LLMs listed below. In your output, you MUST use the exact standardized names provided:
    {nl.join(llms)}

2.  **Sentiment Topics:**
    For each detected LLM, you MUST assess sentiment for the following four topics ONLY:
    {nl.join(topics)}
    
3.  **Sentiment Values:**
    For each topic, the sentiment value MUST be one of the following strings:
    - "positive"
    - "negative"
    - "neutral"
    - "not-present" (Use this if the topic is not mentioned for that LLM).

4.  **JSON Output Structure:**
    The output must be a JSON object with two keys: "status" and "llms".
    - The "status" key should always be "success".
    - The "llms" key must be a list of objects. Each object represents one detected LLM and contains its "name" and its "sentiments".

5.  **Handling No LLMs:**
    If the text contains no mentions of the target LLMs, you MUST return a JSON object where the "llms" list is empty.

### Example 1: LLM mentionned

**User Input:**
"I've been testing the new Claude model. It's incredibly fast and the quality is amazing. I'm still worried about its privacy implications though. The cost is also higher than I'd like."

**Your JSON Output:**
```json
{{
  "status": "success",
  "llms": [
    {{
      "name": "claude",
      "sentiments": {{
        "speed": "positive",
        "cost": "positive",
        "quality": "positive",
        "privacy": "negative",
        "reliability": "not-present",
        "performance": "not-present",
        "coding_ability": "not-present",
        "creativity": "not-present",
        "hallucination": "not-present"
      }}
    }}
  ]
}}

### Example 2: No LLM mentions
**User Input:**
"I am currently starting to use ai for my daily life, let's see what it can do."

**Your JSON Output:**
```json
{{
  "status": "success",
  "llms": []
}}

### Example 3: Multiple LLMs with mixed sentiments

**User Input:**
"I was using ChatGPT for my essay, but the creativity was lacking. I switched to Claude, and the results were much more imaginative. ChatGPT is free to use though, which is a big advantage."

**Your JSON Output:**
```json
{{
  "status": "success",
  "llms": [
    {{
      "name": "chatGPT",
      "sentiments": {{
        "speed": "not-present",
        "cost": "positive",
        "quality": "not-present",
        "safety": "not-present",
        "reliability": "not-present",
        "performance": "not-present",
        "coding_ability": "not-present",
        "creativity": "negative",
        "privacy": "not-present",
        "hallucination": "not-present"
      }}
    }},
    {{
      "name": "claude",
      "sentiments": {{
        "speed": "not-present",
        "cost": "not-present",
        "quality": "not-present",
        "safety": "not-present",
        "reliability": "not-present",
        "performance": "not-present",
        "coding_ability": "not-present",
        "creativity": "positive",
        "privacy": "not-present",
        "hallucination": "not-present"
      }}
    }}
  ]
}}
```
### Example 4: Implicit topics and neutral sentiment

**User Input:**
"I asked Llama to generate a Python script for data analysis, and it produced a working solution immediately. The documentation also says Grok is trained on 314 billion parameters."

**Your JSON Output:**
{{
  "status": "success",
  "llms": [
    {{
      "name": "llama",
      "sentiments": {{
        "speed": "positive",
        "cost": "not-present",
        "quality": "positive",
        "safety": "not-present",
        "reliability": "not-present",
        "performance": "positive",
        "coding_ability": "positive",
        "creativity": "not-present",
        "privacy": "not-present",
        "hallucination": "not-present"
      }}
    }},
    {{
      "name": "grok",
      "sentiments": {{
        "speed": "not-present",
        "cost": "not-present",
        "quality": "not-present",
        "safety": "not-present",
        "reliability": "not-present",
        "performance": "neutral",
        "coding_ability": "not-present",
        "creativity": "not-present",
        "privacy": "not-present",
        "hallucination": "not-present"
      }}
    }}
  ]
}}

### Example 5: Handling an inherently negative topic

**User Input:**
"My biggest problem with older models was their tendency to hallucinate. I've found that the new Gemini model is much more reliable and rarely makes things up."

**Your JSON Output:**
```json
{{
  "status": "success",
  "llms": [
    {{
      "name": "gemini",
      "sentiments": {{
        "speed": "not-present",
        "cost": "not-present",
        "quality": "not-present",
        "safety": "not-present",
        "reliability": "positive",
        "performance": "not-present",
        "coding_ability": "not-present",
        "creativity": "not-present",
        "privacy": "not-present",
        "hallucination": "positive"
      }}
      
    }}
  ]
}}

### Example 6: LLM mentioned but no relevant topics discussed

**User Input:**
"I saw on the news that Mistral just announced a new major partnership. It will be interesting to see what they do next."

**Your JSON Output:**
```json
{{
  "status": "success",
  "llms": [
    {{
      "name": "mistral",
      "sentiments": {{
        "speed": "not-present",
        "cost": "not-present",
        "quality": "not-present",
        "safety": "not-present",
        "reliability": "not-present",
        "performance": "not-present",
        "coding_ability": "not-present",
        "creativity": "not-present",
        "privacy": "not-present",
        "hallucination": "not-present"
      }}
    }}
  ]
}}
    ```
    """

    try:
        chat_response = client.chat.parse(
            model=model,
            messages=[
                {
                    "role": "system", 
                    "content": sysprompt
                },
                {
                    "role": "user", 
                    "content": text
                },
            ],
            response_format=LLMResponse,
            max_tokens=2048,
            temperature=0.7
        )


        response = chat_response.choices[0].message.content
        tokens_count = chat_response.usage.total_tokens
        return json.loads(response), tokens_count
    except Exception as e:
        if "429" in str(e):
            wait = (6 - retries) + random.uniform(0, 1)
            time.sleep(wait)
            logging.info(f"Mistral API rate limit exceeded, retrying in {wait:.2f} seconds...")
            if retries > 0:
                return analyse_post(text, retries - 1)
            else:
                raise Exception("Mistral API rate limit exceeded, passing this message")
        else:
            logging.error(f"Something went wrong with Mistral: {e}")

def get_analysis(text):
    data = {}

    sentiments, tokens_count = analyse_post(text)
    if sentiments["status"] == "success":
        if len(sentiments["llms"]) == 0:
            data = None
        for llm in sentiments["llms"]:
            llm_name = llm["name"]
            sentiments_data = llm["sentiments"]
            llm_analysis = []
            for topic, sentiment in sentiments_data.items():
                if sentiment == "not-present":
                    continue
                llm_analysis.append({
                    "sentiment_name": topic,
                    "sentiment_analysis": sentiment
                })
            data[llm_name] = llm_analysis

            all_empty = True
            for llm in data:
                if len(data[llm]) != 0:
                    all_empty = False
                    break
            if all_empty:
                data = None
    else:
        data = None
    return data, tokens_count
