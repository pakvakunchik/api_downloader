from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import File


async def file_name_saver(session: AsyncSession, file_names: List[str]):
    count = 0
    for file_name in file_names:
        stmt = select(File).where(File.name == file_name)
        result = await session.execute(stmt)
        file = result.scalar_one_or_none()
        file = File(
            name=file_name,
            content='',

        )


