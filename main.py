import os
import sys
from datetime import datetime

import ollama

import chunking
import embedding
import logging_utils
import preprocess
import prompting
import retrieving
from config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBEDDING_MODEL,
    KNOWLEDGE_BASE_PATH,
    TOP_K,
)

# hyperparameters
LOG_DIR = "logs"
MARK = [".", "?", "!", "。", "？", "！", "\n"]

# check the hyperparameters
if CHUNK_OVERLAP >= CHUNK_SIZE:
    sys.exit("Error: CHUNK_OVERLAP > CHUNK_SIZE.")

# prepare the log file: logs/YYYYMMDD_HHMMSS.jsonl
os.makedirs(LOG_DIR, exist_ok=True)
start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_PATH = os.path.join(LOG_DIR, f"{start_time}.jsonl")

# load the knowledge base
print("Loading...", end="", flush=True)
text = preprocess.load_knowledge_base(KNOWLEDGE_BASE_PATH)
chunks = chunking.chunk(text, CHUNK_SIZE, CHUNK_OVERLAP, MARK)
vecs = embedding.embed_chunks(chunks)
print(f"\r{' ' * len('Loading...')}\r", end="", flush=True)

logging_utils.log(
    LOG_PATH,
    {
        "type": "chunking",
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "num_chunks": len(chunks),
        "chunk_lengths": [len(c) for c in chunks],
    },
)

# Q&A loop
while True:
    # load the question
    question = input("Q: ")
    if question.strip().lower() == "exit":
        break
    query = ollama.embeddings(model=EMBEDDING_MODEL, prompt=question).embedding

    # retrieve in the knowledge base
    idxs, vals = retrieving.retrieve(query, vecs, TOP_K)
    relevant_chunks = [chunks[i] for i in idxs]

    logging_utils.log(
        LOG_PATH,
        {
            "type": "retrieving",
            "question": question,
            "results": [
                {"chunk_index": int(i), "similarity": v, "text": chunks[i]}
                for i, v in zip(idxs, vals)
            ],
        },
    )

    # prompt & respond
    prompt = prompting.build_prompt(question, relevant_chunks)
    stream = prompting.generate_answer(prompt)
    print("A: ", end="", flush=True)
    for chunk in stream:
        print(chunk.response, end="", flush=True)
    print("\n\n---\n")
