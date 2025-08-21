from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Ensure environment variables from .env are loaded before importing routers
# Look for .env in root directory (parent of backend folder)
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(env_path)

from app.routers.research.start_research import router as research_start_router
from app.routers.research.status import router as research_status_router
from app.routers.emails.start_generation import router as emails_start_router
from app.routers.emails.status import router as emails_status_router
from app.routers.send.start_send import router as send_start_router
from app.routers.send.status import router as send_status_router


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Backlinker API",
        version="0.1.0",
        description=(
            "Backend API for AI Backlinker. Core research, email generation, and sending "
            "functions remain unchanged; this service exposes them over HTTP."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Minimal CORS (can tighten later)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", response_model=HealthResponse, summary="Service health check")
    def health() -> HealthResponse:
        return HealthResponse(status="ok", service="ai-backlinker", version=app.version or "0.0.0")

    # Include individual router functions
    app.include_router(research_start_router)
    app.include_router(research_status_router)
    app.include_router(emails_start_router)
    app.include_router(emails_status_router)
    app.include_router(send_start_router)
    app.include_router(send_status_router)

    return app


app = create_app()


