#!/usr/bin/env python3
"""
🛰️ HYPATIA MASTER GENERATIVE AUDIO MATH CRAWLER
Author: Acutis / SAGE Core Plane / Logos OS
Scrapes arXiv API for the deep mathematical foundations of modern generative audio:
1. EnCodec (Neural audio compression)
2. Residual Vector Quantization (RVQ / codebook theory)
3. MusicGen / AudioCraft (Autoregressive delayed codebook prediction)
4. Audio transformers and cross-attention/conditioning
5. Sliding-window continuation mathematics
"""

import os
import sys
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re
from datetime import datetime

NAMESPACES = {
    'atom': 'http://www.w3.org/2005/Atom',
    'arxiv': 'http://arxiv.org/schemas/atom'
}

def clean_xml_text(text):
    if text is None:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def search_arxiv_topic(query_str, max_results=5):
    """Query arXiv API for structured academic metadata."""
    encoded_query = urllib.parse.quote(query_str)
    url = f"http://export.arxiv.org/api/query?search_query={encoded_query}&max_results={max_results}&sortBy=relevance"
    
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'HypatiaAudioMathCrawler/1.0 (acutis-mind-sync)'}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read()
    except Exception as e:
        print(f"  [-] Connection error for query '{query_str[:30]}...': {e}")
        return None

def parse_and_format(xml_data, topic_name):
    if not xml_data:
        return ""
        
    try:
        root = ET.fromstring(xml_data)
    except Exception as e:
        print(f"  [-] XML parsing failed: {e}")
        return ""
        
    entries = root.findall('atom:entry', NAMESPACES)
    if not entries:
        return ""
        
    markdown_output = f"## 📚 Sourced arXiv Papers: {topic_name}\n\n"
    
    for entry in entries:
        title = clean_xml_text(entry.find('atom:title', NAMESPACES).text)
        summary = clean_xml_text(entry.find('atom:summary', NAMESPACES).text)
        arxiv_id = entry.find('atom:id', NAMESPACES).text.strip()
        published = entry.find('atom:published', NAMESPACES).text.strip()[:10]
        
        authors = []
        for auth in entry.findall('atom:author', NAMESPACES):
            name_elem = auth.find('atom:name', NAMESPACES)
            if name_elem is not None:
                authors.append(name_elem.text.strip())
                
        markdown_output += f"### 📄 {title}\n"
        markdown_output += f"*   **Authors:** {', '.join(authors)}\n"
        markdown_output += f"*   **Published:** {published} | **arXiv Link:** [{arxiv_id}]({arxiv_id})\n"
        markdown_output += f"*   **Abstract:** {summary}\n\n"
        
    return markdown_output

def main():
    print("=" * 80)
    print("      🛰️ SAGE-HYPATIA: AUDIO MATH & ENCODEC RESEARCH HARVESTER")
    print("=" * 80)
    
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(scripts_dir)
    harvest_dir = os.path.join(workspace_dir, "harvested_research")
    os.makedirs(harvest_dir, exist_ok=True)
    
    # Define our 4 targeted audio math vectors
    research_vectors = {
        "EnCodec & Neural Audio Compression": {
            "query": 'all:"EnCodec" OR all:"neural audio compression" OR all:"soundstream"',
            "filename": "hypatia_encodec_neural_compression_math.md"
        },
        "Residual Vector Quantization": {
            "query": 'all:"Residual Vector Quantization" OR all:"RVQ" OR all:"codebook prediction"',
            "filename": "hypatia_rvq_codebook_mathematics.md"
        },
        "MusicGen & Autoregressive Delayed Codebooks": {
            "query": 'all:"MusicGen" OR all:"AudioCraft" OR all:"delayed codebook" OR all:"music generation"',
            "filename": "hypatia_musicgen_transformer_architecture.md"
        },
        "Cross-Attention & Audio Conditioning": {
            "query": 'all:"cross-attention audio" OR all:"audio conditioning" OR all:"text-to-music"',
            "filename": "hypatia_audio_conditioning_mechanisms.md"
        }
    }
    
    for topic, meta in research_vectors.items():
        print(f"\n[*] Harvesting Topic: '{topic}'...")
        xml_data = search_arxiv_topic(meta["query"])
        
        if xml_data:
            formatted_md = parse_and_format(xml_data, topic)
            if formatted_md:
                file_path = os.path.join(harvest_dir, meta["filename"])
                
                # Append a metadata header
                header = f"# ⚛️ SAGE-HYPATIA HARVESTED INTELLIGENCE: {topic.upper()}\n"
                header += f"*   **Harvest Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S EST')}\n"
                header += f"*   **Source Interface:** arXiv Academic API Feed\n"
                header += f"--------------------------------------------------------------------------------\n\n"
                
                with open(file_path, "w") as f:
                    f.write(header + formatted_md)
                print(f"  ✅ [SUCCESS] Harvested {meta['filename']} successfully!")
            else:
                print(f"  [-] No relevant entries returned for '{topic}'.")
        else:
            print(f"  [-] Skipping harvest for '{topic}' due to connection errors.")
            
    print("\n" + "=" * 80)
    print("🚀 [FINISHED] Hypatia has successfully harvested the generative audio math!")
    print("=" * 80)

if __name__ == "__main__":
    main()
