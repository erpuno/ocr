"""Main entry point."""
from uuid import UUID

from fastapi import FastAPI, File, BackgroundTasks
from fastapi.concurrency import run_in_threadpool
from fastapi.openapi.utils import get_openapi

from ocr import get_pages
import db
import models

from pydantic import Json

app = FastAPI()


def openapi_schema():
    schema = get_openapi(
        title="Document search",
        version="0.1",
        description="Search documents from any forrmat",
        routes=app.routes,
    )
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = openapi_schema


@app.on_event("startup")
async def startup():
    await db.database.connect()


@app.on_event("shutdown")
async def shutdown():
    await db.database.disconnect()


async def process_document(document_id, stream: bytes):
    """Processs uploaded document."""
    pages = await run_in_threadpool(lambda: get_pages(stream))
    await db.update_document_text(document_id, pages)


@app.get("/documents/{document_id}", response_model=models.Document)
async def get_document(
        document_id: UUID):
    return await db.get_document(document_id)


@app.get(
    "/documents/{document_id}/highlights",
    response_model=list[models.Highlight])
async def highlights(document_id: UUID, query: str):
    return await db.highlight_document(document_id, query)


@app.get("/search", response_model=list[models.SearchResult])
async def search(query: str, limit: int = 50, offset: int = 0):
    return await db.search_documents(query, limit, offset)


@app.post("/documents/", response_model=models.Document)
async def create_document(
        background_tasks: BackgroundTasks,
        meta: Json, file: bytes = File()):
    document = await db.create_document(meta)
    background_tasks.add_task(process_document, document["id"], file)

    return document
