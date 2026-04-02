from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.workflows import router as workflows_router
from app.api.runs import router as runs_router
from app.api.nodes import router as nodes_router
from app.api.webhooks import router as webhooks_router


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="FlowForge API",
        version="0.1.0",
        description="Visual workflow automation platform.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/healthz")
    def healthz():
        return {"ok": True, "fixture_mode": settings.fixture_mode}

    app.include_router(workflows_router)
    app.include_router(runs_router)
    app.include_router(nodes_router)
    app.include_router(webhooks_router)
    return app


app = create_app()
