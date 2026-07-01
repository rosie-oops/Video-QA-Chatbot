
from __future__ import annotations

import logging

from qdrant_client.models import Filter, FieldCondition, MatchValue

import config
from db import get_client
from models import embed_model, reranker
from answer import generate_answer

logger = logging.getLogger(__name__)


def _rerank(query: str, chunks: list[dict]) -> list[dict]:
    if not chunks:
        return []

    pairs = [[query, c["text"]] for c in chunks]
    scores = reranker.compute_score(pairs)

    for c, s in zip(chunks, scores):
        c["rerank_score"] = s

    chunks.sort(key=lambda x: x["rerank_score"], reverse=True)
    return chunks[: config.RERANK_TOP_K]


def ask_question(query: str, video_id: str | None = None) -> str:
    logger.info("Question: %r (video_id=%r)", query, video_id)

    client = get_client()
    query_embedding = embed_model.encode(query).tolist()


    query_filter = None
    if video_id is not None:
        query_filter = Filter(
            must=[FieldCondition(key="video_id", match=MatchValue(value=video_id))]
        )

    results = client.query_points(
        collection_name=config.COLLECTION_NAME,
        query=query_embedding,
        query_filter=query_filter,
        limit=config.RETRIEVE_TOP_K,
    )

    retrieved_chunks = [
        {
            "text": point.payload["text"],
            "start": point.payload["start"],
            "end": point.payload["end"],
        }
        for point in results.points
    ]

    if not retrieved_chunks:
        return "I could not find this in the video."

    top_chunks = _rerank(query, retrieved_chunks)
    return generate_answer(query, top_chunks)
