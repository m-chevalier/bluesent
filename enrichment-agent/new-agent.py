import os
import yaml
from huggingface_hub import InferenceClient

#HF_TOKEN = os.getenv("HF_TOKEN", None)
#if not HF_TOKEN:
#    raise ValueError("HF_TOKEN environment variable is not set. Please set it to your Hugging Face API token.")

client = InferenceClient(
    provider="auto",
    api_key=f"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"
)

topics = ["speed", "cost", "quality", "safety", "reliability", "performance"]

sysprompt = f"""You are an assistant used to detect sentiments of several topics in texts. In each message, you will receive a post from a social media which talks about LLMs, you need to analyze the text and return the sentiment for each topic based on the content of the text.
You will only detect sentiments related to a set of topics which are: {", ".join(topics)}.
You will return the sentiment for each topic among this sentiments: positive, negative or neutral. If a topic is not present in the text, you will return "not-present" for that topic.
You will answer in yaml format, with the following structure and without any additional text or formatting syntax:
topic1: sentiment1
topic2: sentiment2
..."""

completion = client.chat.completions.create(
    model="mistralai/Magistral-Small-2506",
    messages=[
        {
            "role": "system",
            "content": sysprompt
        },
        {
            "role": "user",
            "content": "ChatGPT is a useful tool for developers. It is really fast and cost effective. However, it has really shitty performances."
        }
    ],
)


content = yaml.safe_load(completion.choices[0].message.content)

print(content)

