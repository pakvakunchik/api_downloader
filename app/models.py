from datetime import datetime
from typing import List
from sqlalchemy import String, Text, func, ForeignKey, Enum, LargeBinary, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models_enum import Status

# class Candidates(Base):
#     __tablename__ = 'candidates'
#     id: Mapped[int] = mapped_column(primary_key=True)
#     candidate_id: Mapped[int] = mapped_column(unique=True, index=True)
#     files: Mapped[List["File"]] = relationship(back_populates="candidate")
#     progress: Mapped["DownloadProgress"] = relationship(back_populates="candidate", uselist=False)

class DownloadedZip(Base):
    __tablename__ = "downloaded_zips"
    id: Mapped[int] = mapped_column(primary_key=True)
    zip_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

class File(Base):
    __tablename__ = 'files'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    content: Mapped[str] = mapped_column(Text)
    downloaded_at: Mapped[datetime] = mapped_column(default=func.now())
    candidate_id: Mapped[int] = mapped_column(ForeignKey('candidates.candidate_id'), index=True)
    zip_data: Mapped[bytes] = mapped_column(Integer, ForeignKey('downloaded_zips.id'), index=True)

class DownloadProgress(Base):
    __tablename__ = 'download_progress'
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey('candidates.candidate_id'), unique=True, index=True)
    start_time: Mapped[datetime] = mapped_column(default=func.now())
    total_files: Mapped[int] = mapped_column(default=0)
    downloaded_count: Mapped[int] = mapped_column(default=0)
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.SUCCESS)