from qdrant_client import QdrantClient

_client = None

def get_client():
    global _client

    if _client is None:
        _client = QdrantClient(path="./qdrant_db")

    return _client