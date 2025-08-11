import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pathlib

CLAUSES_JSON = "src/aoa_clauses.json"
INDEX_PATH = "data/aoa_index.faiss"
META_PATH = "data/aoa_metadata.json"

def main():
    # Load clauses from Step 1
    with open(CLAUSES_JSON, "r", encoding="utf-8") as f:
        clauses = json.load(f)

    # Load embedding model
    print("🔄 Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Encode each clause text
    print("🔄 Encoding clauses...")
    texts = [c["clause_text"] for c in clauses]
    embeddings = model.encode(texts, convert_to_numpy=True)

    # Create FAISS index
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    # Save index & metadata
    pathlib.Path("data").mkdir(exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(clauses, f, indent=2, ensure_ascii=False)

    print(f"✅ Indexed {len(clauses)} clauses")
    print(f"📦 Saved index to {INDEX_PATH}")
    print(f"📦 Saved metadata to {META_PATH}")

if __name__ == "__main__":
    main()
