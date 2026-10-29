import tomllib
from pathlib import Path

with open(Path(__file__).parent / "config.toml", "rb") as f:
    _cfg = tomllib.load(f)

KNOWLEDGE_BASE_PATH = _cfg["knowledge_base"]["path"]
CHAT_MODEL = _cfg["models"]["chat"]
EMBEDDING_MODEL = _cfg["models"]["embedding"]
CHUNK_SIZE = _cfg["chunking"]["chunk_size"]
CHUNK_OVERLAP = _cfg["chunking"]["chunk_overlap"]
TOP_K = _cfg["retrieving"]["top_k"]
