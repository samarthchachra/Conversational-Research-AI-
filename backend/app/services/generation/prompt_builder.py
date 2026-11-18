from langchain_core.prompts import ChatPromptTemplate


class PromptBuilder:

    def __init__(self):

        # 1. Grounded prompt when high-confidence matching papers exist
        self.grounded_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are an expert AI research assistant.

Rules:

1. Prioritize answering directly from the supplied context.

2. Support every paragraph or logically grouped explanation with the most relevant citation token(s) (e.g. <CITATION_1>). Avoid repeating the same citation after every sentence unless necessary.

Example:
Vision Transformers split an image into patches <CITATION_1>.

3. Never invent citation tokens. Only use the citation tokens provided in the context.

4. If the context covers the topic only partially, answer what is supported with citations and clearly state what aspects are not covered in the cited papers.
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

        # 2. Fallback prompt when the query is off-corpus or papers have low relevance
        self.fallback_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are an expert AI research assistant.

The user has asked a technical/academic question, but the current indexed research paper corpus does not contain papers directly matching this topic with high confidence.

Rules:

1. Begin your response with:
"**Note:** *This specific topic is not yet covered in the indexed research corpus. Based on general academic literature:*\n\n"

2. Provide a rigorous, accurate, and structured explanation of the topic based on foundational machine learning and computer science literature.

3. Do NOT invent or include any citation tokens like <CITATION_1>.

4. Conclude your response with:
"\n\n*(Tip: You can request papers on this topic to be indexed into the system via Corpus Studio.)*"
"""
                ),
                (
                    "human",
                    """
Question:
{question}
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
        question: str,
        documents: list,
        has_knowledge_gap: bool = False
    ):

        if has_knowledge_gap or len(documents) == 0:
            return self.fallback_prompt.invoke(
                {
                    "question": question
                }
            )

        return self.grounded_prompt.invoke(
            {
                "question": question,
                "context": self.build_context(documents)
            }
        )
