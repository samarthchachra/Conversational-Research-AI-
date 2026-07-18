from langchain_core.prompts import ChatPromptTemplate


class PromptBuilder:

    def __init__(self):

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are an expert AI research assistant.

Rules:

1. Answer ONLY from the supplied context.

2. Do NOT use outside knowledge.

3. Support every paragraph or logically grouped explanation with the most relevant citation(s). Avoid repeating the same citation after every sentence unless necessary.

Example:

Vision Transformers split an image into patches <CITATION_1>.

4. Never invent citation tokens.

5. Only use the citation tokens provided in the context.

6. If the answer cannot be found, say:
"I don't know."
"""
                ),
                (
                    "human",
                    """
Question:
{question}

Context:
{context}
"""
                )
            ]
        )

    ########################################################

    def build_context(
        self,
        documents
    ):

        context = ""

        for index, doc in enumerate(documents, start=1):

            context += f"""
<CITATION_{index}>

Title:
{doc.metadata["title"]}

Authors:
{", ".join(doc.metadata["authors"])}

Published:
{doc.metadata["published"]}

Content:
{doc.page_content}

"""

        return context

    ########################################################

    def build_prompt(
        self,
        question,
        documents
    ):

        return self.prompt.invoke(
            {
                "question": question,
                "context": self.build_context(documents)
            }
        )