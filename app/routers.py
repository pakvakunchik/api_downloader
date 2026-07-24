import asyncio
import os
from typing import List, Optional
from sqlalchemy import select, func, desc
from fastapi import Depends, APIRouter, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.constants import BASE_URL_FETCH_NAMES, BASE_URL_DOWNLOAD_ZIP, TEMPLATES_DIR
from app.database import engine, Base, get_db
from app.models import File
from app.schemas import FileResponse, PaginatedFilesResponse, CalculationResponse, FileStats, CalculateRequest
from app.utils import fetch_names, download_zip
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def download_page():
    with open(os.path.join(TEMPLATES_DIR, "download.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@router.get("/files_page", response_class=HTMLResponse)
async def files_page():
    with open(os.path.join(TEMPLATES_DIR, "files_page.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@router.post("/start-download")
async def start_download():
    while True:
        names = await fetch_names(BASE_URL_FETCH_NAMES)
        if not names or 'file_names' not in names or not names['file_names']:
            return 'конец пачек имен'
        zip_downloader = await download_zip(BASE_URL_DOWNLOAD_ZIP, names)
        await asyncio.sleep(1)
        return {
            'status' : 'completed',
        }

@router.get("/files", response_model=PaginatedFilesResponse)
async def get_files(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * per_page
    total_query = select(func.count()).select_from(File)
    total = await db.scalar(total_query)
    query = select(File).order_by(desc(File.downloaded_at)).offset(offset).limit(per_page)
    result = await db.execute(query)
    files = result.scalars().all()
    return {
        "items": [FileResponse.model_validate(f) for f in files],
        "total": total,
        "page": page,
        "per_page": per_page
    }

@router.post("/calculate", response_model=CalculationResponse)
async def calculate_stats(
    request: CalculateRequest,
    db: AsyncSession = Depends(get_db)
):
    file_ids = request.file_ids
    try:

        query = select(File)
        if file_ids:
            query = query.where(File.id.in_(file_ids))
        result = await db.execute(query)
        files = result.scalars().all()
        total_counts = [0] * 10
        per_file_stats = []
        for f in files:
            counts = [0] * 10
            content = f.content or ""
            for ch in content:
                if ch.isdigit():
                    counts[int(ch)] += 1
            total_counts = [total_counts[i] + counts[i] for i in range(10)]
            per_file_stats.append(
                FileStats(file_id=f.id, file_name=f.name, counts=counts)
            )
        return CalculationResponse(total_counts=total_counts, per_file=per_file_stats)
    except Exception as e:
        print(f'ошибка в calculate {e}')
        raise

@router.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
