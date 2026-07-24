from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class FilesNamesResponse(BaseModel):
    files_names: str

class ProgressResponse(BaseModel):
    status: str
    start_time: Optional[datetime] = None
    total_files: int
    downloaded_count: int
    error_message: Optional[str] = None

class FileResponse(BaseModel):
    id: int
    name: str
    downloaded_at: datetime

    class Config:
        from_attributes = True

class PaginatedFilesResponse(BaseModel):
    items: List[FileResponse]
    total: int
    page: int
    per_page: int

class FileStats(BaseModel):
    file_id: int
    file_name: str
    counts: List[int]

class CalculationResponse(BaseModel):
    total_counts: List[int]
    per_file: List[FileStats]

class CalculateRequest(BaseModel):
    file_ids: Optional[List[int]] = None