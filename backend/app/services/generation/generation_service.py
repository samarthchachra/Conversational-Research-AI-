from app.services.llm.mistral_service import llm

from app.services.generation.prompt_builder import PromptBuilder
from app.services.generation.citation_resolver import CitationResolver


class GenerationService:

    def __init__(self):

        self.prompt_builder = PromptBuilder()

        self.citation_resolver = CitationResolver()

    ########################################################

    def generate(
        self,
        question,
        documents
    ):

        prompt = self.prompt_builder.build_prompt(
            question,
            documents
        )

        response = llm.invoke(
            prompt
        )

        return self.citation_resolver.resolve(
            answer=response.content,
            documents=documents
        )