import httpx
from fastapi import Depends, FastAPI, HTTPException, APIRouter, Header, BackgroundTasks
from starlette import status
from app.constants import BASE_URL
from app.database import engine, Base
from app.utils import download_all_files

router = FastAPI()

@router.post("/start-download")
async def start_download(background_tasks: BackgroundTasks, ):
    background_tasks.add_task(download_all_files())
    return {'status': 'started'}


@router.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
