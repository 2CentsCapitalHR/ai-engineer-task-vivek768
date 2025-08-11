import google.generativeai as genai
import os
import faiss
import json
from sentence_transformers import SentenceTransformer
from docx import Document

# ====== CONFIG ======
INDEX_PATH = "data/aoa_index.faiss"
META_PATH = "data/aoa_metadata.json"

# Load Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Load FAISS index & metadata
print("🔄 Loading index & metadata...")
index = faiss.read_index(INDEX_PATH)
with open(META_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_clauses_from_docx(doc_path):
    doc = Document(doc_path)
    clauses = []
    current_title = None
    current_text = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        if text.isupper() and len(text.split()) <= 12:
            if current_title and current_text:
                clauses.append({"title": current_title, "text": " ".join(current_text)})
            current_title = text
            current_text = []
        else:
            current_text.append(text)

    if current_title and current_text:
        clauses.append({"title": current_title, "text": " ".join(current_text)})
    return clauses

def retrieve_similar_clauses(user_clause, k=3):
    vec = model.encode([user_clause], convert_to_numpy=True)
    D, I = index.search(vec, k)
    return [metadata[idx] for idx in I[0]]

def compare_with_gemini(user_clause, official_clause):
    prompt = f"""
You are an ADGM AoA compliance checker.
Compare the following clauses and identify:
1. Missing obligations
2. Extra terms
3. Differences in wording
4. Potential compliance risks

User Clause:
{user_clause}

Official Clause:
{official_clause}
"""
    model_gemini = genai.GenerativeModel("models/gemini-1.5-flash")

    response = model_gemini.generate_content(prompt)
    return response.text

def main():
    user_doc = r"C:\Users\vicky\Desktop\Documentschecker\user_uploads\adgm-ra-model-articles-private-company-limited-by-shares.docx"


    user_clauses = extract_clauses_from_docx(user_doc)

    for clause in user_clauses:
        print(f"\n🔍 Checking clause: {clause['title']}")
        similar = retrieve_similar_clauses(clause["text"], k=1)[0]
        print("📌 Most similar official clause:", similar["clause_title"])

        report = compare_with_gemini(clause["text"], similar["clause_text"])
        print("💡 Gemini Analysis:\n", report)

if __name__ == "__main__":
    main()
