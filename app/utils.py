import asyncio
import io
import zipfile
from typing import Callable, Any
import httpx
from sqlalchemy.dialects.postgresql import insert
from tenacity import retry, stop_after_attempt, wait_exponential, AsyncRetrying, retry_if_exception_type
from app.constants import CANDIDATE_ID, BASE_URL_DOWNLOADED
from app.database import AsyncSessionLocal
from app.models import File

async def fetch_names(url):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers={"X-Candidate-Id": CANDIDATE_ID})
            return response.json()
    except Exception as e:
        print(e)
        return None

async def download_zip(url, data, count: int = 3, max_retries: int = 3):
        file_list = data['file_names']
        async with httpx.AsyncClient() as client:
            while file_list:
                batch = file_list[:count]
                retries = 0
                while retries < max_retries:
                    try:
                        response = await client.post(
                            url,
                            headers={"X-Candidate-Id": CANDIDATE_ID},
                            json={'file_names': batch},
                            timeout=30
                        )
                        if response.status_code == 429:
                            rety_after = int(response.headers['Retry-After'])
                            await asyncio.sleep(rety_after)
                            retries += 1
                            continue
                        response.raise_for_status()
                        break
                    except(httpx.HTTPStatusError, httpx.RequestError) as e:
                        print(f'ошибка загрузки {e}')
                        retries += 1
                        await asyncio.sleep(2 ** retries)
                else:
                    print(f'не получилось скачать пачку {batch}')
                    return None
                zip_buffer = io.BytesIO(response.content)
                async  with AsyncSessionLocal() as db_session:
                    async with db_session.begin():
                        with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
                            for file_name in zip_ref.namelist():
                                with zip_ref.open(file_name) as zip_file:
                                    file_content = zip_file.read().decode('utf-8')
                                    file_content_insert = insert(File).values(
                                        name=file_name,
                                        content=file_content
                                    )
                                    await db_session.execute(file_content_insert)
                        await marked_downloaded(BASE_URL_DOWNLOADED, batch)
                del file_list[:count]
                await asyncio.sleep(1)
        return response

async def marked_downloaded(url, names):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            headers={"X-Candidate-Id": CANDIDATE_ID},
            json=names
        )
        return response


