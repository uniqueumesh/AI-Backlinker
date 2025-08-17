from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Ensure environment variables from .env are loaded before importing routers
load_dotenv()

from app.routers import research, emails, send


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

    # Routers
    app.include_router(research.router)
    app.include_router(emails.router)
    app.include_router(send.router)

    return app


app = create_app()


