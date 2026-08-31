import os
import requests

from dotenv import load_dotenv

from utils.pdfProcessing import (
    ingest_pdf
)

load_dotenv()

API_KEY = os.getenv("OPENALEX_API_KEY")

BASE_URL = "https://api.openalex.org/works"


def reconstruct_abstract(inverted_index):

    if not inverted_index:
        return ""

    word_positions = []

    for word, positions in inverted_index.items():

        for pos in positions:

            word_positions.append(
                (pos, word)
            )

    sorted_words = sorted(word_positions)

    abstract = " ".join(
        word for _, word in sorted_words
    )

    return abstract


def search_openalex(
    query: str,
    limit: int
):

    try:

        params = {

            "search": query,

            "per-page": limit,

            "api_key": API_KEY
        }

        response = requests.get(

            BASE_URL,

            params=params,

            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        papers = []

        for paper in data["results"]:

            reconstructed_abstract = (
                reconstruct_abstract(
                    paper.get(
                        "abstract_inverted_index"
                    )
                )
            )

            authors = []

            for author in paper.get(
                "authorships", []
            ):

                author_name = (
                    author.get("author", {})
                    .get("display_name")
                )

                if author_name:

                    authors.append(author_name)

            pdf_url = (
                paper.get("open_access", {})
                .get("oa_url")
            )

            metadata = {

                "title": paper.get(
                    "display_name"
                ),

                "authors": authors,

                "published": paper.get(
                    "publication_year"
                ),

                "citations": paper.get(
                    "cited_by_count"
                ),

                "paper_url": (
                    paper.get(
                        "primary_location", {}
                    ).get(
                        "landing_page_url"
                    )
                ),

                "pdf_url": pdf_url,

                "source": "openalex"
            }

            # DEFAULT CONTENT = ABSTRACT

            content = reconstructed_abstract

            # TRY PDF INGESTION

            if pdf_url:

                try:

                    print(
                        f"\nTrying PDF ingestion:\n{pdf_url}\n"
                    )

                    ingestion_response = ingest_pdf(

                        pdf_url=pdf_url,

                        metadata=metadata
                    )

                    if ingestion_response["success"]:

                        print(
                            "\nPDF processed successfully\n"
                        )

                        content = (
                            ingestion_response[
                                "document"
                            ].page_content
                        )

                    else:

                        print(
                            "\nPDF ingestion failed\n"
                        )

                        print(
                            ingestion_response[
                                "error"
                            ]
                        )

                        print(
                            "\nUsing abstract fallback\n"
                        )

                except Exception as pdf_error:

                    print(
                        f"\nPDF processing error:"
                        f"\n{pdf_error}\n"
                    )

                    print(
                        "\nUsing abstract fallback\n"
                    )

            papers.append({

                "content": content,

                "metadata": metadata
            })

        return {

            "success": True,

            "query": query,

            "total_results": len(papers),

            "papers": papers
        }

    except Exception as e:

        return {

            "success": False,

            "query": query,

            "error": str(e)
        }