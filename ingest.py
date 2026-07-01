

from __future__ import annotations

import logging
import os
import uuid

import ffmpeg
from yt_dlp import YoutubeDL
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client.models import Distance, VectorParams, PointStruct

import config
from db import get_client
from models import whisper_model, embed_model

logger = logging.getLogger(__name__)


def _make_point_id(video_id: str, chunk_index: int) -> str:
    
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{video_id}_{chunk_index}"))


def _download_audio(video_url: str) -> tuple[str, str, str, float]:
    
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(config.VIDEO_DIR, "%(id)s.%(ext)s"),
        "quiet": True,
    }
    if config.YTDLP_COOKIES_BROWSER:
        ydl_opts["cookiesfrombrowser"] = (config.YTDLP_COOKIES_BROWSER,)

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        downloaded_path = ydl.prepare_filename(info)

    video_id = info.get("id")
    video_title = info.get("title", "")
    video_duration = info.get("duration")

    audio_path = os.path.join(config.AUDIO_DIR, f"{video_id}.wav")
    (
        ffmpeg
        .input(downloaded_path)
        .output(audio_path, ac=1, ar=16000)
        .run(overwrite_output=True, quiet=True)
    )

    return audio_path, video_id, video_title, video_duration


def _transcribe(audio_path: str) -> list[dict]:
    segments, _ = whisper_model.transcribe(
        audio_path,
        beam_size=config.WHISPER_BEAM_SIZE,
        vad_filter=config.WHISPER_VAD_FILTER,
    )
    return [
        {
            "start": round(seg.start, 2),
            "end": round(seg.end, 2),
            "text": seg.text.strip(),
        }
        for seg in segments
    ]


def _chunk_transcript(
    transcript: list[dict], video_id: str, video_title: str, video_duration: float
) -> list[dict]:
    full_text = ""
    mapping = []
    current_pos = 0

    for seg in transcript:
        start_pos = current_pos
        full_text += seg["text"] + " "
        current_pos = len(full_text)
        mapping.append(
            {
                "start_char": start_pos,
                "end_char": current_pos,
                "start_time": seg["start"],
                "end_time": seg["end"],
            }
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", "? ", "! ", " "],
    )
    texts = splitter.split_text(full_text)

    chunks = []
    search_start = 0

    for chunk_id, chunk_text in enumerate(texts):
        start_char = full_text.find(chunk_text, search_start)
        end_char = start_char + len(chunk_text)
        search_start = end_char - 1

        start_time = None
        end_time = None
        for seg in mapping:
            if start_time is None and seg["end_char"] >= start_char:
                start_time = seg["start_time"]
            if seg["start_char"] < end_char:
                end_time = seg["end_time"]
            elif seg["start_char"] >= end_char:
                break

        chunks.append(
            {
                "chunk_id": chunk_id,
                "video_id": video_id,
                "video_title": video_title,
                "text": chunk_text,
                "start": start_time,
                "end": end_time,
                "duration": video_duration,
            }
        )

    return chunks


def _store_chunks(chunks: list[dict], video_id: str) -> None:
    client = get_client()

    existing = [c.name for c in client.get_collections().collections]
    if config.COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=config.COLLECTION_NAME,
            vectors_config=VectorParams(size=config.EMBED_DIM, distance=Distance.COSINE),
        )

    texts = [c["text"] for c in chunks]
    embeddings = embed_model.encode(
        texts, batch_size=config.EMBED_BATCH_SIZE, show_progress_bar=False
    )

    points = [
        PointStruct(
            id=_make_point_id(video_id, i),
            vector=embedding.tolist(),
            payload=chunk,
        )
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ]

    client.upsert(collection_name=config.COLLECTION_NAME, points=points)


def process_video(video_url: str) -> dict:
   
    video_url = (video_url or "").strip()
    if not video_url:
        raise ValueError("A YouTube URL must be provided.")

    logger.info("Downloading audio for %s", video_url)
    audio_path, video_id, video_title, video_duration = _download_audio(video_url)

    logger.info("Transcribing %s", video_id)
    transcript = _transcribe(audio_path)
    if not transcript:
        raise ValueError("No speech detected in this video.")

    logger.info("Chunking transcript for %s", video_id)
    chunks = _chunk_transcript(transcript, video_id, video_title, video_duration)

    logger.info("Embedding + storing %d chunks for %s", len(chunks), video_id)
    _store_chunks(chunks, video_id)

    return {
        "video_id": video_id,
        "video_title": video_title,
        "num_chunks": len(chunks),
    }