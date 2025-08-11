import gradio as gr
import google.generativeai as genai
import os
import faiss
import json
from sentence_transformers import SentenceTransformer
from docx import Document

# ========== CONFIG ==========
INDEX_PATH = "data/aoa_index.faiss"
META_PATH = "data/aoa_metadata.json"
GEMINI_MODEL = "models/gemini-1.5-flash"  # or "models/gemini-1.5-pro"

# Set up Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Load FAISS index & metadata
index = faiss.read_index(INDEX_PATH)
with open(META_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)

# Load embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")


def extract_clauses_from_docx(file_path):
    """Extracts clauses with titles from a DOCX file."""
    doc = Document(file_path)
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


def retrieve_similar_clause(user_clause, k=1):
    """Retrieve the most similar clause from the official AoA index."""
    vec = embedder.encode([user_clause], convert_to_numpy=True)
    D, I = index.search(vec, k)
    return metadata[I[0][0]]


def compare_with_gemini(user_clause, official_clause):
    """Ask Gemini to compare two clauses and highlight differences."""
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
    model_gemini = genai.GenerativeModel(GEMINI_MODEL)
    response = model_gemini.generate_content(prompt)
    return response.text


def process_file(file):
    clauses = extract_clauses_from_docx(file.name)
    results = []

    for clause in clauses:
        similar = retrieve_similar_clause(clause["text"], k=1)
        analysis = compare_with_gemini(clause["text"], similar["clause_text"])
        results.append({
            "user_clause": clause["title"],
            "official_match": similar["clause_title"],
            "gemini_analysis": analysis
        })

    return "Gemini RAG AoA Compliance Report", results


iface = gr.Interface(
    fn=process_file,
    inputs=gr.File(file_types=[".docx"], label="Upload AoA File"),
    outputs=["text", "json"],
    title="ADGM AoA Compliance Checker (Gemini RAG)",
    description="Upload an Articles of Association file to check compliance using RAG + Gemini"
)

if __name__ == "__main__":
    iface.launch()

