from fastapi import FastAPI
from app.routers import router

app = FastAPI(title='API Downloader')
app.include_router(router)

