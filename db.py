"""DB related."""
import re

from sqlalchemy import text, bindparam, String, Float
from sqlalchemy.dialects.postgresql import JSONB

import databases

SEARCH_CONFIG = 'ukrainian'

DATABASE_URL = 'postgresql://postgres:11@localhost/documents'

database = databases.Database(DATABASE_URL)


async def get_document(id):
    """Get document by id."""
    query = text(
        "SELECT id, status, meta FROM documents WHERE id = :id"
    ).bindparams(id=id).columns(id=String, status=String, meta=JSONB)

    return await database.fetch_one(query=query)


async def create_document(meta):
    """Create new document."""
    query = text(
        """INSERT INTO documents (meta) VALUES (:meta)
        RETURNING id, status, meta""").bindparams(
        bindparam('meta', value=meta, type_=JSONB)).columns(
        id=String, status=String, meta=JSONB)

    return await database.fetch_one(query=query)


async def update_document_text(document_id, pages: list):
    """Update document text and status."""
    async with database.transaction():
        await database.execute_many(
            query="""INSERT INTO pages (document_id, number, text)
                VALUES (:document_id, :number, :text)""",
            values=[{
                "document_id": document_id,
                "number": number,
                "text": text
            } for number, text in enumerate(pages, start=1)]
        )
    await database.execute(
            query="""UPDATE documents
                SET text = :text, status = :status
                WHERE id = :id""",
            values={
                "id": document_id,
                "text": "\n".join(pages),
                "status": "OK"
            }
        )


def plainto_tsquery(query):
    """Convert plain query to tsquery input.
    Supports ! (not) and * (prefix) modifiers."""
    words = re.findall(r'!?\w+\*?', query)
    return " & ".join(words).replace('*', ':*')


async def search_documents(plain_query, limit, offset):
    """Search documents."""
    query = text("""
        SELECT id, status, meta,
               ts_headline(:search_config, text, query) AS headline,
               ts_rank_cd(ts, query) AS rank
        FROM   documents, to_tsquery(:search_config, :ts_query) query
        WHERE  query @@ ts
        ORDER BY rank DESC
        LIMIT :limit OFFSET :offset;""").bindparams(
            search_config=SEARCH_CONFIG,
            ts_query=plainto_tsquery(plain_query),
            limit=limit,
            offset=offset
        ).columns(
            id=String, status=String, meta=JSONB, headline=String, rank=Float)

    return await database.fetch_all(query=query)


async def highlight_document(document_id, plain_query):
    """Highlights pages in document."""
    return await database.fetch_all(
        query="""
            SELECT number as page_number,
                   ts_headline(:search_config, text, query) AS headline
            FROM   pages, to_tsquery(:search_config, :ts_query) query
            WHERE  to_tsvector(:search_config, text) @@ query AND
                   document_id = :document_id
            ORDER BY number""",
        values={
            "search_config": SEARCH_CONFIG,
            "document_id": document_id,
            "ts_query": plainto_tsquery(plain_query)
        }
    )
