from __future__ import annotations

import os
from pathlib import Path

from google import genai
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from src.ai_assistant.retrieval import CorpusDocument, RetrievedContext, _compact_text

COLLECTION_NAME = "finbank_corpus"


def get_qdrant_client(db_path: Path = Path("data/qdrant_db")) -> QdrantClient:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return QdrantClient(path=str(db_path))


def index_corpus(
    client: QdrantClient,
    documents: list[CorpusDocument],
    api_key: str,
    *,
    force_reindex: bool = False,
) -> None:
    """Embed corpus documents using Gemini and store them in a local Qdrant database."""
    # Check if collection exists
    exists = client.collection_exists(COLLECTION_NAME)

    if exists and not force_reindex:
        # Check if already indexed
        count = client.count(COLLECTION_NAME).count
        if count > 0:
            return  # Already indexed

    # Recreate collection (using 768 dimensions for text-embedding-004)
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )

    ai_client = genai.Client(api_key=api_key)
    model_name = os.getenv("GOOGLE_EMBEDDING_MODEL", "text-embedding-004")

    points = []
    for idx, doc in enumerate(documents):
        # Generate embedding
        response = ai_client.models.embed_content(
            model=model_name,
            contents=doc.text,
        )
        embedding = response.embeddings[0].values

        points.append(
            PointStruct(
                id=idx,
                vector=embedding,
                payload={
                    "source": doc.source,
                    "text": doc.text,
                },
            )
        )

    if points:
        client.upsert(collection_name=COLLECTION_NAME, points=points)


def retrieve_vector_context(
    query: str,
    client: QdrantClient,
    api_key: str,
    *,
    top_k: int = 3,
) -> list[RetrievedContext]:
    """Retrieve relevant contexts from Qdrant by embedding the query and searching cosine similarity."""
    if not client.collection_exists(COLLECTION_NAME):
        return []

    ai_client = genai.Client(api_key=api_key)
    model_name = os.getenv("GOOGLE_EMBEDDING_MODEL", "text-embedding-004")

    response = ai_client.models.embed_content(
        model=model_name,
        contents=query,
    )
    query_vector = response.embeddings[0].values

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k,
    )

    retrieved = []
    for res in results:
        payload = res.payload or {}
        retrieved.append(
            RetrievedContext(
                source=payload.get("source", "unknown"),
                text=_compact_text(payload.get("text", "")),
                score=int(res.score * 100),
            )
        )
    return retrieved
