from __future__ import annotations

import os
import time
from typing import Any, List, Optional
import requests
from dotenv import load_dotenv

from pydantic import Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
    AIMessage,
)
from langchain_core.outputs import ChatResult, ChatGeneration

load_dotenv()

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

DEFAULT_MODELS = [
    "nvidia/nemotron-3.5-lightning:free",
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "openrouter/free",
]


class ChatOpenRouter(BaseChatModel):
    model: str = Field(default=os.getenv("OPENROUTER_MODEL", DEFAULT_MODELS[0]))
    api_key: Optional[str] = Field(default=None)
    temperature: float = Field(default=0.0)
    timeout: int = Field(default=45)
    max_retries: int = Field(default=2)

    @property
    def _llm_type(self) -> str:
        return "openrouter-chat"

    def _convert_messages(self, messages: List[BaseMessage]) -> List[dict[str, str]]:
        formatted: List[dict[str, str]] = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                role = "system"
            elif isinstance(msg, AIMessage):
                role = "assistant"
            elif isinstance(msg, HumanMessage):
                role = "user"
            else:
                role = getattr(msg, "type", "user")
                if role not in ("system", "user", "assistant"):
                    role = "user"
            formatted.append({"role": role, "content": str(msg.content)})
        return formatted

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        key = self.api_key or os.getenv("OPENROUTER_API_KEY")
        if not key:
            raise ValueError(
                "OPENROUTER_API_KEY is not set. Please set it in your environment or .env file."
            )

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/samarthchachra/research-ai-system",
            "X-Title": "Conversational Research AI",
        }

        formatted_messages = self._convert_messages(messages)
        candidate_models = [self.model] + [m for m in DEFAULT_MODELS if m != self.model]

        last_error = None
        for current_model in candidate_models:
            payload: dict[str, Any] = {
                "model": current_model,
                "messages": formatted_messages,
                "temperature": self.temperature,
            }
            if stop:
                payload["stop"] = stop

            for attempt in range(self.max_retries):
                try:
                    response = requests.post(
                        OPENROUTER_API_URL,
                        headers=headers,
                        json=payload,
                        timeout=self.timeout,
                    )
                    if response.status_code == 200:
                        data = response.json()
                        content = data["choices"][0]["message"]["content"]
                        return ChatResult(
                            generations=[ChatGeneration(message=AIMessage(content=content))]
                        )

                    # If model is deprecated or unavailable, immediately break to next model
                    if response.status_code == 404:
                        last_error = f"Model {current_model} returned 404"
                        break

                    # Transient provider issue (429 rate limit or 5xx) -> back off and retry
                    last_error = f"Model {current_model} status {response.status_code}: {response.text[:100]}"
                    time.sleep(0.5 * (attempt + 1))
                except Exception as e:
                    last_error = e
                    time.sleep(0.5 * (attempt + 1))

        raise RuntimeError(
            f"All OpenRouter candidate models failed. Last error: {last_error}"
        )


llm = ChatOpenRouter()
