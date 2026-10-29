def read_text(path):
    with open(file=path, mode="r", encoding="utf-8") as f:
        text = f.read()
    return text


def chunk(text, chunk_size, chunk_overlap, mark):
    # keep sentences complete while chunking

    chunks = []
    idx = 0
    while idx < len(text):
        start = idx
        end = min(idx + chunk_size, len(text) - 1)

        # search the natural boundary of a sentence
        while end < len(text) - 1 and text[end] not in mark:
            end += 1
        while start > 0 and text[start - 1] not in mark:
            start -= 1
        session = text[start : end + 1]

        chunks.append(session)
        idx += chunk_size - chunk_overlap
        if end == len(text) - 1:
            break
    return chunks
