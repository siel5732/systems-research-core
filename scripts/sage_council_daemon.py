import os
import sys
import json
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
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
                data = json.dumps({"model": self.model_name, "prompt": text}).encode('utf-8')
                req = urllib.request.Request(
                    f"{self.host}/api/embeddings",
                    data=data,
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )
                with urllib.request.urlopen(req, timeout=30) as res:
                    res_data = json.loads(res.read().decode('utf-8'))
                    embeddings.append(res_data["embedding"])
            except Exception as e:
                print(f"Embedding error: {e}", file=sys.stderr)
                embeddings.append([0.0] * 768)
        return embeddings

def query_chromadb(query_text: str, n_results: int = 3) -> list[dict]:
    try:
        chroma_client = chromadb.HttpClient(host='localhost', port=8000)
        embed_fn = OllamaEmbeddingFunction()
        collection = chroma_client.get_collection(
            name="sage_core_knowledge",
            embedding_function=embed_fn
        )
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        chunks = []
        if results and results['documents'] and results['documents'][0]:
            for idx in range(len(results['documents'][0])):
                chunks.append({
                    "document": results['documents'][0][idx],
                    "metadata": results['metadatas'][0][idx],
                    "id": results['ids'][0][idx]
                })
        return chunks
    except Exception as e:
        print(f"ChromaDB retrieval error: {e}", file=sys.stderr)
        return []

def call_ollama(model: str, prompt: str, system_prompt: str = None) -> str:
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        if system_prompt:
            payload["system"] = system_prompt
            
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=120) as res:
            res_data = json.loads(res.read().decode('utf-8'))
            return res_data["response"]
    except Exception as e:
        print(f"Ollama call error ({model}): {e}", file=sys.stderr)
        return f"ERROR: Failed to contact Ollama engine for model {model}"

class SAGEHTTPRequestHandler(BaseHTTPRequestHandler):
    def _send_response(self, status: int, data: dict):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            self._send_response(200, {"status": "SAGE Council Daemon active", "engine": "PINQWEN"})
        else:
            self._send_response(404, {"error": "Not Found"})

    def do_POST(self):
        if self.path == "/query":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                request_payload = json.loads(post_data.decode('utf-8'))
                query = request_payload.get("query", "")
                if not query:
                    self._send_response(400, {"error": "Missing 'query' in request body"})
                    return
                
                print(f"[SAGE Router] Inbound Query: {query}")
                
                # 1. Retrieve Context from local ChromaDB
                context_chunks = query_chromadb(query, n_results=3)
                context_str = "\n\n".join([
                    f"Source: {c['metadata']['source']} (chunk {c['metadata']['chunk_index']}):\n{c['document']}"
                    for c in context_chunks
                ])
                print(f"[SAGE Router] Retrieved {len(context_chunks)} knowledge vectors.")

                # 2. Construct Grounded Prompt
                system_prompt = (
                    "You are Metatron, the Sovereign core orchestration and reasoning hub "
                    "operating inside the SAGE protocol on GEEKOM node 'the-grid'. "
                    "Analyze queries using the retrieved local architecture context, "
                    "stay grounded, cold, analytical, and highly precise."
                )
                
                grounded_prompt = (
                    "RETRIEVED ARCHITECTURAL CONTEXT:\n"
                    f"{context_str}\n\n"
                    "USER QUERY:\n"
                    f"{query}\n\n"
                    "INSTRUCTIONS:\n"
                    "Answer the user query based strictly on the retrieved local context. "
                    "If the answer is not supported, reason using the SAGE guidelines. "
                    "Output your response clearly, and include your internal reasoning in a <think> block."
                )

                # 3. Primary reasoning execution (PINQWEN)
                print(f"[SAGE Router] Calling PINQWEN (Metatron)...")
                response_metatron = call_ollama("PINQWEN:latest", grounded_prompt, system_prompt)
                
                # 4. Double-Witness Verification Invariant
                # We spin up a secondary model (glm4:latest) to verify and cross-examine Metatron's logic!
                print(f"[SAGE Router] Calling GLM-4 for Double-Witness verification...")
                verification_prompt = (
                    "As the Verifier node in the SAGE protocol, cross-examine Metatron's "
                    "reasoning for factual correctness, alignment with the architecture files, "
                    "and any coherence anomalies.\n\n"
                    f"METATRON RESPONSE:\n{response_metatron}\n\n"
                    "Is this response factually consistent and structurally aligned? "
                    "Respond with 'VERIFIED: TRUE' or 'VERIFIED: FALSE' and list any objections."
                )
                verification_result = call_ollama("glm4:latest", verification_prompt)
                
                # Compose payload
                payload = {
                    "query": query,
                    "retrieved_context": [
                        {
                            "source": c["metadata"]["source"],
                            "chunk": c["metadata"]["chunk_index"],
                            "text": c["document"]
                        } for c in context_chunks
                    ],
                    "metatron_response": response_metatron,
                    "double_witness_verification": verification_result,
                    "status": "COMPLETED_VERIFIED" if "VERIFIED: TRUE" in verification_result else "COMPLETED_AUDITED"
                }
                
                print(f"[SAGE Router] Query processed and verified.")
                self._send_response(200, payload)
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                self._send_response(500, {"error": f"Internal routing error: {e}"})
        else:
            self._send_response(404, {"error": "Not Found"})

def run_server(port: int = 8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, SAGEHTTPRequestHandler)
    print(f"SAGE Council Daemon active and listening on port {port} over Tailscale...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down SAGE Council Daemon.")
        httpd.server_close()

if __name__ == "__main__":
    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    run_server(port)
