#!/usr/bin/env python3
"""
🛰️ HYPATIA MASTER ASTRA & QUANTUM CRAWLER
Author: Acutis / SAGE Core Plane / Logos OS
Scrapes arXiv API for the bleeding-edge August 2026 breakthroughs identified by Claude:
1. Non-sofic groups (Gromov's soficity conjecture resolution)
2. Connes's rigidity conjecture disproof (von Neumann algebras & property T)
3. Erdos's 1946 unit distance counterexamples (May 2026)
4. Tantalum superconducting qubits (200°C krypton sputtering)
5. Trapped-ion tunable reservoirs (Rice University)
6. Dual-rail cavity qubits (D-Wave superconducting gates)
7. Lean 4 formal verification soundness (the compiler acceptance bug)
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

def search_arxiv_topic(query_str, max_results=3):
    """Query arXiv API for structured academic metadata."""
    encoded_query = urllib.parse.quote(query_str)
    url = f"http://export.arxiv.org/api/query?search_query={encoded_query}&max_results={max_results}&sortBy=relevance"
    
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'HypatiaAstraCrawler/1.0 (acutis-mind-sync)'}
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
    print("      🛰️ SAGE-HYPATIA: BLEEDING-EDGE RESEARCH HARVESTER (AUGUST 2026)")
    print("=" * 80)
    
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(scripts_dir)
    harvest_dir = os.path.join(workspace_dir, "harvested_research")
    os.makedirs(harvest_dir, exist_ok=True)
    
    # Define our 7 targeted research vectors based on Claude's landscape
    research_vectors = {
        "Non-Sofic Groups": {
            "query": 'all:"non-sofic" OR all:"soficity" OR all:"Gromov non-sofic"',
            "filename": "hypatia_non_sofic_groups_research.md"
        },
        "Connes Rigidity Conjecture Disproof": {
            "query": 'all:"Connes rigidity" OR all:"property T" OR all:"von Neumann algebra"',
            "filename": "hypatia_connes_rigidity_research.md"
        },
        "Erdos Unit Distance Counterexample": {
            "query": 'all:"Erdos unit distance" OR all:"unit distance problem" OR all:"Erdos 1946"',
            "filename": "hypatia_erdos_unit_distance_research.md"
        },
        "Tantalum Superconducting Qubits": {
            "query": 'all:"tantalum qubit" OR all:"superconducting qubits tantalum" OR all:"krypton sputtering"',
            "filename": "hypatia_tantalum_qubits_research.md"
        },
        "Trapped-Ion Tunable Reservoirs": {
            "query": 'all:"trapped-ion simulator" OR all:"tunable reservoirs" OR all:"exciton trapped-ion"',
            "filename": "hypatia_trapped_ion_reservoirs_research.md"
        },
        "Dual-Rail Superconducting Gates": {
            "query": 'all:"dual-rail cavity" OR all:"superconducting cavity qubits" OR all:"dual-rail qubit"',
            "filename": "hypatia_dual_rail_qubits_research.md"
        },
        "Lean 4 Compiler Soundness Verification": {
            "query": 'all:"Lean formal verification" OR all:"formal verification bug" OR all:"Lean 4 proof check"',
            "filename": "hypatia_lean_soundness_verification.md"
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
    print("🚀 [FINISHED] Hypatia has successfully seeded GEEKOM's digital garden!")
    print("=" * 80)

if __name__ == "__main__":
    main()
