import os
from pydantic import BaseModel
from typing import List, Literal, Optional
from mistralai import Mistral
import logging
import json
import time
import random


MISTRAL_KEY = os.getenv("MISTRAL_KEY", None)
if not MISTRAL_KEY:
    raise ValueError("MISTRAL_KEY environment variable is not set. Please set it to use the Mistral API.")


SentimentValue = Literal["positive", "negative", "neutral", "not-present"]

# Define the Pydantic models for the response structure
class Sentiments(BaseModel):
    speed: Optional[SentimentValue]
    cost: Optional[SentimentValue]
    robustness: Optional[SentimentValue]
    privacy: Optional[SentimentValue]


class LLMEntry(BaseModel):
    name: str
    sentiments: Sentiments


class LLMResponse(BaseModel):
    status: Literal["success", "error"]
    llms: List[LLMEntry]
    

topics = ["speed", "cost", "quality", "safety", "reliability", "performance"]



client = Mistral(MISTRAL_KEY)


def analyse_post(text, retries=5):
    model="mistral-large-latest"
    nl = "\n"
    sysprompt=f"""
You are an assistant used to detect sentiments of several topics in texts. You will receive messages that may discuss large language models (LLMs). Your task is to analyze each message and return the sentiment for each relevant topic, per LLM mentioned.
You must follow these rules:

Only detect the following LLMs (normalize variant names to a standard form):
chatGPT
Claude
Gemini
Bard
LLaMA
Mistral

Include version numbers if mentioned, e.g., "chatGPT 4.5". Standardize the name and append the version if found.

For each detected LLM, assess sentiment for the following topics:
{nl.join(topics)}

Sentiment values must be one of:
- positive
- neutral
- negative
- not-present (if the topic is not discussed for that LLM)

If you are certain that the message is not about LLMs, return an error status with an empty list of LLMs.
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