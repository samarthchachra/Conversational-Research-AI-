import json
import re
from typing import Literal, TypedDict

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    AIMessage
)
from langsmith import traceable

from app.services.llm.openrouter_service import llm

IntentType = Literal["research", "general question"]


class RewriteResult(TypedDict):
    intent: IntentType
    rewritten_query: str | None  # Standalone search query if research, None if general question
    reply: str | None            # Direct conversational response if general question, None if research


class QueryRewriter:

    def __init__(self):

        self.system_prompt = SystemMessage(
            content="""
You are an expert intent classifier and query rewriting assistant for an academic research paper Q&A system.

Analyze the user's latest message and conversation history, then output a JSON object with this exact structure:
{
  "intent": "research" or "general question",
  "rewritten_query": "string or null",
  "reply": "string or null"
}

Classification Rules:
1. "general question":
   - Greetings, goodbyes, compliments, or conversational pleasantries (e.g., "hi", "hello", "thank you", "who are you?").
   - Off-topic, general knowledge, or common questions not requiring academic research paper citations (e.g., "what is 2+2?", "tell me a joke").
   - Action: Set "rewritten_query" to null. In "reply", provide a polite, natural response. If asked who you are or what you do, explain that you are an AI research assistant capable of answering questions grounded in academic literature.

2. "research":
   - Technical, scientific, conceptual, or academic questions regarding machine learning, AI, architectures, or papers (e.g., "explain self-attention", "how does LoRA compare to full fine-tuning?").
   - Action: Set "reply" to null. In "rewritten_query", resolve all pronouns (it, they, this, these) using conversation history into a standalone search query. Do NOT answer the question.

Output format: Return ONLY the JSON object. Do not include markdown code block syntax or extra text.
"""
        )

    ##########################################################

    def build_messages(
        self,
        history,
        query: str
    ):

        messages = [
            self.system_prompt
        ]

        for message in history:

            if message.role.value == "user":

                messages.append(
                    HumanMessage(
                        content=message.content
                    )
                )

            elif message.role.value == "assistant":

                messages.append(
                    AIMessage(
                        content=message.content
                    )
                )

        messages.append(
            HumanMessage(
                content=query
            )
        )

        return messages

    ##########################################################

    def _parse_response(self, text: str, fallback_query: str) -> RewriteResult:
        """Robustly extract and validate JSON from LLM response."""
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)

        try:
            data = json.loads(cleaned)
            raw_intent = str(data.get("intent", "research")).strip().lower()

            if raw_intent == "general question":
                return {
                    "intent": "general question",
                    "rewritten_query": None,
                    "reply": data.get("reply") or "Hello! How can I assist you with research papers today?"
                }
            else:
                return {
                    "intent": "research",
                    "rewritten_query": data.get("rewritten_query") or fallback_query,
                    "reply": None
                }
        except (json.JSONDecodeError, AttributeError):
            return {
                "intent": "research",
                "rewritten_query": fallback_query,
                "reply": None
            }

    ##########################################################

    @traceable(name="query_rewriter", run_type="chain")
    def rewrite(
        self,
        history,
        query: str
    ) -> RewriteResult:

        messages = self.build_messages(
            history=history,
            query=query
        )

        response = llm.invoke(
            messages
        )

        return self._parse_response(
            text=response.content,
            fallback_query=query
        )
