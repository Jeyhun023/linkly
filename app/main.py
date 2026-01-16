from fastapi import FastAPI

from app.routes import links_router, stats_router, redirect_router

app = FastAPI(
    title="Linkly",
    description="URL Shortener Service",
    version="1.0.0",
)

app.include_router(links_router)
app.include_router(stats_router)
app.include_router(redirect_router)
