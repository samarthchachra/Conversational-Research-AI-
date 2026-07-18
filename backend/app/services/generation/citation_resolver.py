import re


class CitationResolver:

    def resolve(
        self,
        answer: str,
        documents: list
    ):

        citations = []

        pattern = r"<CITATION_(\d+)>"

        matches = re.findall(
            pattern,
            answer
        )

        seen = set()

        for match in matches:

            idx = int(match) - 1

            if idx >= len(documents):
                continue

            doc = documents[idx]

            title = doc.metadata["title"]

            answer = answer.replace(
                f"<CITATION_{match}>",
                f"[{title}]"
            )

            if title not in seen:

                citations.append({

                    "title":
                        title,

                    "authors":
                        doc.metadata["authors"],

                    "published":
                        doc.metadata["published"],

                    "pdf_url":
                        doc.metadata["pdf_url"]

                })

                seen.add(title)

        return {

            "answer": answer,

            "citations": citations

        }