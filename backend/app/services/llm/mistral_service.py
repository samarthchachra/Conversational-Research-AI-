from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv
import os
load_dotenv()


llm = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0,
    api_key = os.getenv("MISTRAL_API_KEY")
)