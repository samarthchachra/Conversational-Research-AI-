from app.services.llm.openrouter_service import llm

from app.services.generation.prompt_builder import PromptBuilder
from app.services.generation.citation_resolver import CitationResolver


class GenerationService:

    def __init__(self):

        self.prompt_builder = PromptBuilder()

        self.citation_resolver = CitationResolver()

    ########################################################

    def generate(
        self,
        question: str,
        documents: list,
        has_knowledge_gap: bool = False
    ):

        prompt = self.prompt_builder.build_prompt(
            question=question,
            documents=documents,
            has_knowledge_gap=has_knowledge_gap
        )

        response = llm.invoke(
            prompt
        )

        if has_knowledge_gap:
            return {
                "answer": response.content,
                "citations": []
            }

        return self.citation_resolver.resolve(
            answer=response.content,
            documents=documents
        )
