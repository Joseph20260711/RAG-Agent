import ollama

from config import EMBEDDING_MODEL


def embed_chunks(chunks):
    vecs = []
    for i, chunk in enumerate(chunks):
        vec = ollama.embeddings(model=EMBEDDING_MODEL, prompt=chunk)
        vecs.append(vec.embedding)
    return vecs
