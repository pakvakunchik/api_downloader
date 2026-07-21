from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class FilesNamesResponse(BaseModel):
    files_names: str

class ProgressResponse(BaseModel):
    status: str
    start_time: Optional[datetime] = None
    total_files: int
    downloaded_count: int
    error_message: Optional[str] = None

