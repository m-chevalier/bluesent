import os
from pydantic import BaseModel
from typing import List, Literal, Optional
from mistralai import Mistral
import logging
import json


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


def analyse_post(text):
    model="mistral-small-latest"
    sysprompt=f"""You are an assistant used to detect sentiments of several topics in texts. You will receive messages supposed to talk about LLMs. In each message, you will need to analyze the text and return the sentiment for each topic based on the content of the text.\n    You will only detect LLM names and sentiments related to this LLM on these topics only: speed, cost, robustness, privacy. You will also only detect some LLMs, which are: mistral, gemini, claude, chatGPT, llama and bard. You can detect multiple versions and append them at the end of the name of the LLM in your answer, you can also reduce the name of the LLM to a more standard one, for example you can reduce "OpenAI's LLM" to "chatGPT".\n    You will return the sentiment for each topic among this sentiments: {", ".join(topics)}. If a topic is not present in the text, you will return the value "not-present" for that topic.\n    If you think that the post is not talking about LLM return a status "error" and an empty list of llms. Otherwise, return a status "success" and a list of llms with their sentiments.\n    You will answer in json format according to the schema provided, with the following structure and without any additional text or formatting syntax"""

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
        return json.loads(response)
    except Exception as e:
        logging.error(f"Something went wrong with Mistral: {e}")

def get_analysis(text):
    data = {}

    sentiments = analyse_post(text)
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
    else:
        data = None
    return data