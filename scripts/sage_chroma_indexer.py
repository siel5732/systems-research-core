import os
import sys
import glob
from pathlib import Path
import requests
import chromadb
from chromadb.utils import embedding_functions

def chunk_text(text: str, max_chunk_len: int = 1000, overlap: int = 200) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chunk_len
        chunks.append(text[start:end])
        start += max_chunk_len - overlap
    return chunks

def index_files():
    # Setup Chroma client (Persistent, Serverless)
    chroma_client = chromadb.PersistentClient(path="./chroma_directory")
    
    # Register default ONNX local embedding function (Serverless)
    embed_fn = embedding_functions.DefaultEmbeddingFunction()
    
    # Get or create collection
    collection = chroma_client.get_or_create_collection(
        name="sage_core_knowledge",
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"}
    )
    
    # Paths to index
    base_dir = Path("/home/fq9f/systems-research-core")
    if not base_dir.exists():
        base_dir = Path(".")
        
    files_to_index = [
        base_dir / "AGENTS.md",
        base_dir / "AGENCY_AI_BUSINESS_PLAN.md",
        base_dir / "HEARTBEAT.md",
        base_dir / "preconscious_buffer.md",
        base_dir / "MEMORY.md"
    ]
    
    # Dynamically find all harvested research markdown files
    harvested_dir = base_dir / "harvested_research"
    if harvested_dir.exists():
        for md_file in harvested_dir.glob("*.md"):
            if md_file not in files_to_index:
                files_to_index.append(md_file)
    
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
