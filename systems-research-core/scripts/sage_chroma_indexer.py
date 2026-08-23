import os
import sys
import glob
from pathlib import Path
import requests
import chromadb
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings

class OllamaEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name: str = "nomic-embed-text", host: str = "http://localhost:11434"):
        self.model_name = model_name
        self.host = host

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for text in input:
            try:
                res = requests.post(
                    f"{self.host}/api/embeddings",
                    json={"model": self.model_name, "prompt": text},
                    timeout=30
                )
                res.raise_for_status()
                embeddings.append(res.json()["embedding"])
            except Exception as e:
                print(f"Error generating embedding for text: {text[:30]}... - {e}", file=sys.stderr)
                # Fallback to zero vector if embedding fails
                embeddings.append([0.0] * 768) # nomic-embed-text has 768 dimensions
        return embeddings

def chunk_text(text: str, max_chunk_len: int = 1000, overlap: int = 200) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chunk_len
        chunks.append(text[start:end])
        start += max_chunk_len - overlap
    return chunks

def index_files():
    # Setup Chroma client
    chroma_client = chromadb.HttpClient(host='localhost', port=8000)
    
    # Register custom Ollama embedding function
    embed_fn = OllamaEmbeddingFunction()
    
    # Get or create collection
    collection = chroma_client.get_or_create_collection(
        name="sage_core_knowledge",
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"}
    )
    
    # Paths to index
    base_dir = Path("/home/fq9f/systems-research-core")
    files_to_index = [
        base_dir / "AGENTS.md",
        base_dir / "AGENCY_AI_BUSINESS_PLAN.md",
        base_dir / "HEARTBEAT.md",
        base_dir / "preconscious_buffer.md",
        base_dir / "harvested_research/hypatia_decentralized_training_research.md"
    ]
    
    indexed_count = 0
    for file_path in files_to_index:
        if not file_path.exists():
            print(f"File not found: {file_path}")
            continue
            
        print(f"Indexing: {file_path.name}")
        content = file_path.read_text(encoding="utf-8")
        chunks = chunk_text(content)
        
        documents = []
        metadatas = []
        ids = []
        
        for idx, chunk in enumerate(chunks):
            documents.append(chunk)
            metadatas.append({
                "source": file_path.name,
                "chunk_index": idx,
                "full_path": str(file_path)
            })
            # Create a deterministic ID
            ids.append(f"{file_path.name}_chunk_{idx}")
            
        if documents:
            collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            indexed_count += len(documents)
            print(f"Successfully upserted {len(documents)} chunks from {file_path.name}")
            
    print(f"Done! Ingested {indexed_count} total knowledge chunks into ChromaDB collection 'sage_core_knowledge'.")

if __name__ == "__main__":
    index_files()
