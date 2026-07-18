from sqlalchemy import Column,String,DateTime
from datetime import datetime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class IngestedPaper(Base):

    __tablename__ = "ingested_papers"

    paper_id = Column(
        String,
        primary_key=True,
        index=True
    )

    title = Column(
        String,
        nullable=False
    )

    pdf_url = Column(String)

    ingested_at = Column(
        DateTime,
        default=datetime.utcnow
    )