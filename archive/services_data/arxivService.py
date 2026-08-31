from langchain_community.document_loaders import ArxivLoader


def arxiv_search(
    query: str,
    limit: int 
):

    try:

        loader = ArxivLoader(
            query=query,
            load_max_docs=limit,
            load_all_available_meta=True,
            max_results=limit,
            
        )

        docs = loader.load()

        papers = []

        for doc in docs:

            papers.append({

                "content": doc.page_content,

                "metadata": {

                    "title": doc.metadata.get("Title"),

                    "authors": doc.metadata.get("Authors"),

                    "published": str(
                        doc.metadata.get("Published")
                    ),

                    "summary": doc.metadata.get("Summary"),

                    "entry_id": doc.metadata.get("Entry ID"),

                    "pdf_url": doc.metadata.get("pdf_url"),

                    "primary_category": doc.metadata.get(
                        "Primary Category"
                    ),

                    "categories": doc.metadata.get(
                        "Categories"
                    )
                }
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