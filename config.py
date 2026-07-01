import os

#  Directories 
DATA_DIR = "data"
VIDEO_DIR = os.path.join(DATA_DIR, "videos")
AUDIO_DIR = os.path.join(DATA_DIR, "audio")
TRANSCRIPT_DIR = os.path.join(DATA_DIR, "transcripts")
CHUNKS_DIR = os.path.join(DATA_DIR, "chunks")

for _d in (VIDEO_DIR, AUDIO_DIR, TRANSCRIPT_DIR, CHUNKS_DIR):
    os.makedirs(_d, exist_ok=True)


YTDLP_COOKIES_BROWSER = None

# Whisper 
WHISPER_MODEL_SIZE = "tiny"      
WHISPER_DEVICE = "cpu"            
WHISPER_COMPUTE_TYPE = "int8"     
WHISPER_BEAM_SIZE = 5
WHISPER_VAD_FILTER = True         
#  Embeddings
EMBED_MODEL_NAME = "BAAI/bge-m3"
EMBED_DIM = 1024
EMBED_BATCH_SIZE = 32

#  Reranker 
RERANKER_MODEL_NAME = "BAAI/bge-reranker-v2-m3"
RERANK_TOP_K = 5         
RETRIEVE_TOP_K = 20        
# Chunking 
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200

# --- Qdrant ---
QDRANT_PATH = "./qdrant_db"
COLLECTION_NAME = "video_lectures"

# --- LLM ---
GROQ_MODEL_NAME = "llama-3.3-70b-versatile"
GROQ_API_KEY_ENV_VAR = "GROQ_API_KEY"
