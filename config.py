"""
Central configuration for the video QA app.
Change paths, model names, or chunking behavior here — nowhere else.
"""

import os

# --- Directories ---
DATA_DIR = "data"
VIDEO_DIR = os.path.join(DATA_DIR, "videos")
AUDIO_DIR = os.path.join(DATA_DIR, "audio")
TRANSCRIPT_DIR = os.path.join(DATA_DIR, "transcripts")
CHUNKS_DIR = os.path.join(DATA_DIR, "chunks")

for _d in (VIDEO_DIR, AUDIO_DIR, TRANSCRIPT_DIR, CHUNKS_DIR):
    os.makedirs(_d, exist_ok=True)

# --- yt-dlp ---
# Set to None to disable cookie use (may hit "Sign in to confirm you're
# not a bot" errors on some videos). Set to "chrome", "firefox", "edge",
# etc. to read cookies from that browser's profile. The browser must be
# fully closed while the app runs, or its cookie DB will be locked.
YTDLP_COOKIES_BROWSER = None

# --- Whisper ---
WHISPER_MODEL_SIZE = "tiny"       # tiny/base/small/medium/large-v3
WHISPER_DEVICE = "cpu"            # "cuda" if you have a GPU
WHISPER_COMPUTE_TYPE = "int8"     # int8 for cpu, float16 for cuda
WHISPER_BEAM_SIZE = 5
WHISPER_VAD_FILTER = True         # skip silent/non-speech stretches

# --- Embeddings ---
EMBED_MODEL_NAME = "BAAI/bge-m3"
EMBED_DIM = 1024
EMBED_BATCH_SIZE = 32

# --- Reranker ---
RERANKER_MODEL_NAME = "BAAI/bge-reranker-v2-m3"
RERANK_TOP_K = 5          # how many chunks to keep after reranking
RETRIEVE_TOP_K = 20        # how many chunks to pull from Qdrant before reranking

# --- Chunking ---
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200

# --- Qdrant ---
QDRANT_PATH = "./qdrant_db"
COLLECTION_NAME = "video_lectures"

# --- LLM ---
GROQ_MODEL_NAME = "llama-3.3-70b-versatile"
GROQ_API_KEY_ENV_VAR = "GROQ_API_KEY"