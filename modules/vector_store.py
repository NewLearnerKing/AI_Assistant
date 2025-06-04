# modules/vector_store.py
import faiss
import os
import json
from sentence_transformers import SentenceTransformer
import numpy as np

MODEL = SentenceTransformer("all-MiniLM-L6-v2")
INDEX_PATH = "memory/long_term/index.faiss"
METADATA_PATH = "memory/long_term/store.json"

def safe_load_faiss_index(index_path, dimension=384):
    if os.path.exists(index_path):
        try:
            index = faiss.read_index(index_path)
            return index
        except Exception as e:
            print(f"[FAISS] Corrupt index file. Recreating. Reason: {e}")
    else:
        print("[FAISS] No existing index found. Creating new one.")
    
    index = faiss.IndexFlatL2(dimension)
    faiss.write_index(index, index_path)
    return index

# Usage:
index = safe_load_faiss_index(INDEX_PATH, 384)

# Load metadata safely
if os.path.exists(METADATA_PATH):
    try:
        with open(METADATA_PATH, "r") as f:
            content = f.read().strip()
            metadata = json.loads(content) if content else []
    except Exception as e:
        print(f"[METADATA] Corrupt JSON. Recreating. Reason: {e}")
        metadata = []
        with open(METADATA_PATH, "w") as f:
            json.dump(metadata, f)
else:
    metadata = []
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f)


def save_vector_store():
    faiss.write_index(index, INDEX_PATH)
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)

def add_to_vector_store(text: str, meta: dict):
    if is_duplicate(text):
        return  # Skip duplicate
    
    vector = MODEL.encode([text])
    index.add(np.array(vector, dtype="float32"))
    metadata.append({**meta, "text": text})
    save_vector_store()

def search_vector_store(query: str, top_k=3):
    if index.ntotal == 0:
        return []

    query_vec = MODEL.encode([query])
    D, I = index.search(np.array(query_vec, dtype="float32"), top_k)

    results = []
    for idx, dist in zip(I[0], D[0]):
        if idx < len(metadata):
            result = metadata[idx].copy()
            result["score"] = float(1.0 - dist)  # or just use `-dist` to make it similarity-like
            results.append(result)
    return results


def is_duplicate(text: str, threshold=0.9) -> bool:
    results = search_vector_store(text, top_k=1)
    return results and results[0]['score'] > threshold

