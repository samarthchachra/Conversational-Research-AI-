from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    AIMessage
)

from app.services.llm.mistral_service import llm


class QueryRewriter:

    def __init__(self):

        self.system_prompt = SystemMessage(
            content="""
You are an expert query rewriting assistant.

Your task is to rewrite the user's latest question into a complete standalone query.

Rules:

1. Use the conversation history for context.
2. Resolve pronouns like:
   - it
   - they
   - this
   - these
   - those
3. Preserve the original intent.
4. Do NOT answer the question.
5. Return ONLY the rewritten query.
6. If the latest question is already standalone, return it unchanged.
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

    def rewrite(
        self,
        history,
        query: str
    ):

        messages = self.build_messages(
            history=history,
            query=query
        )

        response = llm.invoke(
            messages
        )

        return response.content.strip()