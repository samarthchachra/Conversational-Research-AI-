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
   Two sub-cases — handle them differently:

   a) Pleasantries or questions about the assistant (e.g., "hi", "hello", "thank you", "who are you?", "what can you do?"):
      → Respond naturally and helpfully. Explain that you are an AI research assistant that answers questions grounded in academic literature.

   b) Off-topic factual or general knowledge questions unrelated to academic research (e.g., "Who is the CEO of Apple?", "What is 2+2?", "Tell me a joke", "Write me a poem"):
      → Do NOT answer the question.
      → Politely decline and redirect. Example reply:
        "I'm a specialized research assistant focused on academic literature in machine learning and AI. I'm not able to help with that, but I'd be happy to answer any questions you have about research papers or technical concepts!"

   In both sub-cases: set "rewritten_query" to null.

2. "research":
   - Technical, scientific, conceptual, or academic questions about machine learning, AI, architectures, or papers (e.g., "explain self-attention", "how does LoRA compare to full fine-tuning?").
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
