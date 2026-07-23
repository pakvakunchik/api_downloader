from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Text, func, ForeignKey, Enum, LargeBinary, Integer, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models_enum import Status

class DownloadedFiles(Base):
    __tablename__ = "downloaded_files"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    zip_data: Mapped[bytes] = mapped_column(LargeBinary)

class File(Base):
    __tablename__ = 'files'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    downloaded_at: Mapped[datetime] = mapped_column(server_default=text("NOW() AT TIME ZONE 'Asia/Novosibirsk'"))
    zip_data: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('downloaded_files.id'), index=True, nullable=True)

class DownloadProgress(Base):
    __tablename__ = 'download_progress'
    id: Mapped[int] = mapped_column(primary_key=True)
    start_time: Mapped[datetime] = mapped_column(default=func.now())
    total_files: Mapped[int] = mapped_column(default=0)
    downloaded_count: Mapped[int] = mapped_column(default=0)
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.SUCCESS)