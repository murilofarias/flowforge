from __future__ import annotations
from fastapi import APIRouter
from app.services.nodes import catalog

router = APIRouter(prefix="/api/nodes", tags=["nodes"])


@router.get("/catalog")
def node_catalog():
    return {"nodes": catalog()}
