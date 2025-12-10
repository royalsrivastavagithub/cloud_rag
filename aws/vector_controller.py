# aws/vector_controller.py

import os
from dotenv import load_dotenv

# Load .env BEFORE anything else
load_dotenv()

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

DB_DIR = "./vector_db"
os.makedirs(DB_DIR, exist_ok=True)

# Initialize embedding model
embeddings = OpenAIEmbeddings(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Initialize Chroma vector store (new API persists automatically)
vector_store = Chroma(
    collection_name="logs",
    embedding_function=embeddings,
    persist_directory=DB_DIR,
)

def embed_and_store(log_line: str, metadata: dict):
    """
    Embed a log line and store it in ChromaDB.
    Persistence happens automatically when using persist_directory.
    """
    vector_store.add_texts(
        texts=[log_line],
        metadatas=[metadata]
    )
    # ❌ DO NOT CALL vector_store.persist() — not supported in langchain-chroma
