from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.career import router as career_router
from app.api.health import router as health_router
from app.api.presentation import router as presentation_router
from app.core.config import get_settings


settings = get_settings()
app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(presentation_router)
app.include_router(career_router)
