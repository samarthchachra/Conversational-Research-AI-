from sqlalchemy import select

from app.models.research_paper import IngestedPaper


class IngestedPaperRepository:

    ###################################################

    def get_existing_ids(
        self,
        db,
        paper_ids: list[str]
    ):

        rows = db.execute(

            select(
                IngestedPaper.paper_id
            ).where(

                IngestedPaper.paper_id.in_(paper_ids)
            )

        ).scalars().all()

        return set(rows)

    ###################################################

    def bulk_insert(
        self,
        db,
        papers: list[dict]
    ):

        objects = [

            IngestedPaper(

                paper_id=paper["id"],

                title=paper["title"],

                pdf_url=paper["pdf_url"]

            )

            for paper in papers

        ]

        db.bulk_save_objects(objects)

        db.commit()