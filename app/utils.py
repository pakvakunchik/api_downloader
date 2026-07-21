import asyncio
import io
import zipfile
from datetime import datetime, timezone
from typing import Callable, Any, List

import httpx
from sqlalchemy import select
from tenacity import retry, stop_after_attempt, wait_exponential, AsyncRetrying, retry_if_exception_type

from app.constants import CANDIDATE_ID, BASE_URL
from app.database import AsyncSessionLocal
from app.models import DownloadedZip, File


async def retrier_util(
        func: Callable,
        *args: Any,
        retries: int = 3,
        min_wait: int = 1,
        max_wait: int = 10,
        exception: tuple = (Exception,),
        **kwargs: Any
)-> Any:
    retrier = AsyncRetrying(
        stop=stop_after_attempt(retries),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        retry=retry_if_exception_type(exception),
        reraise=True,
    )

async def safe_fetch(client: httpx.AsyncClient, url: str, method: str = "GET", json_data: dict = None):
    while True:
        try:
            if method == "GET":
                resp = await client.get(url, headers={"X-Candidate-Id": CANDIDATE_ID})
            else:  # POST
                resp = await client.post(url, json=json_data, headers={"X-Candidate-Id": CANDIDATE_ID})
            if resp.status_code == 200:
                return resp
        except Exception:
            pass
        await asyncio.sleep(5)

async def get_names(client: httpx.AsyncClient) -> list[str]:
    resp = await safe_fetch(client, f"{BASE_URL}/api/files/names")
    return resp.json()

async def download_zip(client: httpx.AsyncClient, batch: list[str]) -> bytes:
    resp = await safe_fetch(client, f"{BASE_URL}/api/files/download", method="POST", json_data={"files": batch})
    return resp.content

async def mark_downloaded(client: httpx.AsyncClient, names: list[str]):
    await safe_fetch(client, f"{BASE_URL}/api/files/downloaded", method="POST", json_data={"files": names})

def chunk_list(lst: list, n: int = 3) -> list[list]:
    return [lst[i:i + n] for i in range(0, len(lst), n)]

async def extract_zip_from_db(zip_id: int, expected_names: list[str]) -> list[dict]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(DownloadedZip).where(DownloadedZip.id == zip_id))
        zip_rec = result.scalar_one()
        zip_buffer = io.BytesIO(zip_rec.zip_data)
        extracted = []
        with zipfile.ZipFile(zip_buffer) as zf:
            for name in expected_names:
                if name in zf.namelist():
                    content = zf.read(name).decode("utf-8")
                    extracted.append({"filename": name, "content": content})
        return extracted

async def save_files_to_db(files_info: list[dict], zip_id: int):
    async with AsyncSessionLocal() as session:
        for finfo in files_info:
            session.add(File(
                filename=finfo["filename"],
                content=finfo["content"],
                download_time=datetime.now(timezone.utc),
                zip_id=zip_id
            ))
        await session.commit()

async def one_loop(client: httpx.AsyncClient, batch: list[str]):
    zip_data = await download_zip(client, batch)
    async with AsyncSessionLocal() as session:
        zip_rec = DownloadedZip(zip_data=zip_data)
        session.add(zip_rec)
        await session.commit()
        await session.refresh(zip_rec)
        zip_id = zip_rec.id
    extracted = await extract_zip_from_db(zip_id, batch)
    await save_files_to_db(extracted, zip_id)

async def download_all_files():
    async with httpx.AsyncClient() as client:
        while True:
            names = await get_names(client)
            if not names:
                break
            chunks = chunk_list(names, 3)
            for chunk in chunks:
                await one_loop(client, chunk)
            await mark_downloaded(client, names)