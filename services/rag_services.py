import chromadb
import PyPDF2
import requests
import os
import uuid
from sentence_transformers import SentenceTransformer
from services import gmail_bot
import re

def clean_text(text: str) -> str:
    """Remove HTML tags, links and extra whitespace"""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ----------------------
# Setup
# ----------------------

# Embedding model — runs locally, no API needed
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# ChromaDB — persistent storage in data/rag folder
chroma_client = chromadb.PersistentClient(path="data/rag")
collection = chroma_client.get_or_create_collection(name="pulsenova_docs")

LLM_URL = "http://localhost:1234/v1/chat/completions"

# ----------------------
# Helper — Split text into chunks
# ----------------------
def split_into_chunks(text: str, chunk_size: int = 200) -> list:
    """Split long text into smaller overlapping chunks"""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

# ----------------------
# 1. Ingest PDF
# ----------------------
def ingest_emails() -> dict:
    emails = gmail_bot.read_unread_emails()
    if not emails:
        return {"status": "error", "message": "No emails found"}

    chunks = []
    ids = []
    metadatas = []

    for email in emails:
        # ✅ Clean the body before storing
        clean_body = clean_text(email['body'])
        email_text = f"From: {email['from']}\nSubject: {email['subject']}\nBody: {clean_body}"
        chunks.append(email_text)
        ids.append(f"email_{uuid.uuid4().hex[:8]}")
        metadatas.append({
            "source": email['subject'],
            "type": "email",
            "from": email['from']
        })

    embeddings = embedding_model.encode(chunks).tolist()
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )

    return {
        "status": "ingested",
        "emails_stored": len(chunks)
    }

# ----------------------
# 2. Ingest Emails
# ----------------------
def ingest_emails() -> dict:
    """Fetch unread emails and store in ChromaDB"""

    emails = gmail_bot.read_unread_emails()

    if not emails:
        return {"status": "error", "message": "No emails found"}

    chunks = []
    ids = []
    metadatas = []

    for email in emails:
        # Combine email fields into one text chunk
        email_text = f"From: {email['from']}\nSubject: {email['subject']}\nBody: {email['body']}"
        chunks.append(email_text)
        ids.append(f"email_{uuid.uuid4().hex[:8]}")
        metadatas.append({
            "source": email['subject'],
            "type": "email",
            "from": email['from']
        })

    # Generate embeddings
    embeddings = embedding_model.encode(chunks).tolist()

    # Store in ChromaDB
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )

    return {
        "status": "ingested",
        "emails_stored": len(chunks)
    }

# ----------------------
# 3. Query RAG
# ----------------------
def query_rag(question: str) -> str:
    """Search ChromaDB for relevant chunks, then ask LLM"""
    try:
        # Step 1 — Convert question to embedding
        question_embedding = embedding_model.encode([question]).tolist()

        # Step 2 — Search ChromaDB for top 3 relevant chunks
        results = collection.query(
            query_embeddings=question_embedding,
            n_results=3
        )
        print(f"🔍 RAG Results: {results}")

        # Step 3 — Extract relevant chunks
        relevant_chunks = results['documents'][0]
        distances = results['distances'][0]
        relevant_chunks = [
        doc for doc, dist in zip(results['documents'][0], distances)
        if dist < 1.5  # only use chunks that are actually relevant
    ]

        if not relevant_chunks:
            return "❌ No relevant information found in your documents."

        # Step 4 — Build context from chunks
        context = "\n\n".join(relevant_chunks)

        # Step 5 — Send context + question to LLM
        response = requests.post(LLM_URL, json={
            "model": "local-model",
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": """You are PulseNova, a helpful assistant.
    Answer the user's question based ONLY on the provided context.
    If the answer is not in the context, say "I couldn't find that in your documents."
    Be concise and helpful."""},
                {"role": "user", "content": f"""Context:
    {context}

    Question: {question}"""}
            ]
        }, timeout=30)

    # ✅ Check if response is valid before parsing
        if not response.text.strip():
            return "❌ LLM returned empty response. Try again!"

        data = response.json()

        if "choices" not in data:
            print(f"⚠️ Unexpected response: {data}")
            return "❌ Something went wrong with the LLM response."

        return data["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        return "❌ LLM took too long to respond. Try again!"

    except requests.exceptions.JSONDecodeError:
        return "❌ LLM returned empty response. Try again!"

    except Exception as e:
        print(f"⚠️ RAG query error: {e}")
        return f"❌ Error: {str(e)}"

# ----------------------
# 4. List all documents
# ----------------------
def list_documents() -> list:
    """List all unique documents stored in ChromaDB"""
    results = collection.get()
    if not results['metadatas']:
        return []
    sources = list(set([m['source'] for m in results['metadatas']]))
    return sources