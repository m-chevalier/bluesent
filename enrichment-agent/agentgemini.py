




import base64
import os
from google import genai
from google.genai import types
import json


GEMINI_KEY = os.getenv("GEMINI_KEY", None)
if not GEMINI_KEY:
    raise ValueError("GEMINI_KEY environment variable is not set. Please set it to use the Gemini API.")

def analyse_post(text):
    client = genai.Client(
        api_key=f"{GEMINI_KEY}",
    )

    topics = ["speed", "cost", "quality", "safety", "reliability", "performance"]


    topics_schema = {}
    for topic in topics:
        topics_schema[topic] = genai.types.Schema(
            type=genai.types.Type.STRING,
            enum=["positive", "negative", "neutral", "not-present"],
        )

    model = "gemini-2.0-flash-lite"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=text),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=genai.types.Schema(
            type = genai.types.Type.OBJECT,
            required = ["status", "llms"],
            properties = {
                "status": genai.types.Schema(
                    type = genai.types.Type.STRING,
                    enum=["success", "error"],
                ),
                "llms": genai.types.Schema(
                    type = genai.types.Type.ARRAY,
                    items = genai.types.Schema(
                        type = genai.types.Type.OBJECT,
                        properties = {
                            "name": genai.types.Schema(type = genai.types.Type.STRING),
                            "sentiments": genai.types.Schema(
                                type = genai.types.Type.OBJECT,
                                properties = topics_schema,
                            ),
                        },
                    ),
                ),
            },
        ),
        system_instruction=[
            types.Part.from_text(text=f"""You are an assistant used to detect sentiments of several topics in texts. You will receive messages supposed to talk about LLMs. In each message, you will need to analyze the text and return the sentiment for each topic based on the content of the text.
    You will only detect LLM names and sentiments related to this LLM on these topics only: {", ".join(topics)}. You will also only detect some LLMs, which are: gemini, claude, chatGPT, llama and bard. You can detect multiple versions and append them at the end of the name of the LLM in your answer, you can also reduce the name of the LLM to a more standard one, for example you can reduce "OpenAI's LLM" to "chatGPT".
    You will return the sentiment for each topic among this sentiments: positive, negative or neutral. If a topic is not present in the text, you will return the value "not-present" for that topic.
    If you think that the post is not talking about LLM return a status "error" and an empty list of llms. Otherwise, return a status "success" and a list of llms with their sentiments.
    You will answer in json format according to the schema provided in the response_schema field, with the following structure and without any additional text or formatting syntax"""),
        ],
    )

    text = ""

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        text += chunk.text

    data = json.loads(text)
    return data

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