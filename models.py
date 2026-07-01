


import logging

from faster_whisper import WhisperModel
from sentence_transformers import SentenceTransformer
from FlagEmbedding import FlagReranker

import config

logger = logging.getLogger(__name__)

logger.info("Loading Whisper model (%s)...", config.WHISPER_MODEL_SIZE)
whisper_model = WhisperModel(
    config.WHISPER_MODEL_SIZE,
    device=config.WHISPER_DEVICE,
    compute_type=config.WHISPER_COMPUTE_TYPE,
)

logger.info("Loading embedding model (%s)...", config.EMBED_MODEL_NAME)
embed_model = SentenceTransformer(config.EMBED_MODEL_NAME)

logger.info("Loading reranker (%s)...", config.RERANKER_MODEL_NAME)
reranker = FlagReranker(config.RERANKER_MODEL_NAME, use_fp16=False)

logger.info("All models loaded.")