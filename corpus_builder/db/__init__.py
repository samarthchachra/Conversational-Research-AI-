"""PostgreSQL paper tracking for the offline corpus builder.

Records which papers have been successfully ingested so that repeated
runs of the corpus builder skip already-indexed papers (deduplication).
Uses a standalone SQLAlchemy session — no dependency on the backend app.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    DateTime,
    create_engine,
    select,
)
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from corpus_builder.config import POSTGRES_URL


Base = declarative_base()


class IngestedPaper(Base):
    """ORM model mirroring the production ingested_papers table."""

    __tablename__ = "ingested_papers"

    paper_id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    pdf_url = Column(String)
    ingested_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )


# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------

_engine = None
_SessionLocal = None


def _get_session_factory() -> sessionmaker:
    global _engine, _SessionLocal
    if _SessionLocal is None:
        if not POSTGRES_URL:
            raise ValueError(
                "POSTGRES_URL is not set. "
                "Add it to your .env file before running the corpus builder."
            )
        _engine = create_engine(POSTGRES_URL)
        Base.metadata.create_all(bind=_engine)
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=_engine,
        )
    return _SessionLocal


def get_db_session() -> Session:
    """Return a new SQLAlchemy session. Caller is responsible for closing it."""
    factory = _get_session_factory()
    return factory()


# ---------------------------------------------------------------------------
# Repository
# ---------------------------------------------------------------------------

class PaperRepository:
    """Data access for ingested paper records."""

    def get_existing_ids(
        self,
        db: Session,
        paper_ids: list[str],
    ) -> set[str]:
        """Return the subset of paper_ids that are already in the DB."""
        rows = db.execute(
            select(IngestedPaper.paper_id).where(
                IngestedPaper.paper_id.in_(paper_ids)
            )
        ).scalars().all()
        return set(rows)

    def bulk_insert(
        self,
        db: Session,
        papers: list[dict],
    ) -> None:
        """Insert paper records. Silently skips duplicates via primary-key conflict."""
        objects = [
            IngestedPaper(
                paper_id=paper["id"],
                title=paper["title"],
                pdf_url=paper.get("pdf_url", ""),
            )
            for paper in papers
        ]
        db.bulk_save_objects(objects)
        db.commit()
