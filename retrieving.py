import numpy as np


def cosine_similarity(a, b):
    prod = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    val = prod / (norm_a * norm_b)
    return val.item()


def retrieve(query, vecs, top_k):
    vals = []
    for i, vec in enumerate(vecs):
        val = cosine_similarity(query, vec)
        vals.append(val)
    top_idxs = np.argsort(vals)[-top_k:][::-1]
    top_vals = [vals[i] for i in top_idxs]
    return top_idxs, top_vals
