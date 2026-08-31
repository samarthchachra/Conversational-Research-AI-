from dotenv import load_dotenv
load_dotenv()

import os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_embedding(text, task_type="RETRIEVAL_DOCUMENT", dimensions=768):
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=dimensions
        )
    )
    return result.embeddings[0].values

vector = get_embedding("Amazon Bedrock makes it easy to build with foundation models.")
print(len(vector), vector[:5])