import os
import re
from pathlib import Path
from typing import List, Dict, Any

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


class DocumentChunk:
    def __init__(self, doc_name: str, section: str, content: str):
        self.doc_name = doc_name
        self.section = section
        self.content = content.strip()

    def to_dict(self) -> Dict[str, str]:
        return {
            "source": self.doc_name,
            "section": self.section,
            "content": self.content
        }


class RAGEngine:
    _instance = None

    def __init__(self):
        self.chunks: List[DocumentChunk] = []
        self._load_documents()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = RAGEngine()
        return cls._instance

    def _load_documents(self):
        self.chunks.clear()
        doc_files = [
            "01_Bangalore_City_Profile_Brief.md",
            "04_KF_Bangalore_ONLY.md",
            "04_THREE_PLATFORM_Bangalore_ONLY.md",
            "05_JLL_Bangalore_ONLY.md",
            "06_CBRE_Bangalore_ONLY.md"
        ]

        for filename in doc_files:
            file_path = DATA_DIR / filename
            if not file_path.exists():
                continue
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()

                # Split by markdown headers
                sections = re.split(r"\n(?=#{1,4}\s+)", text)
                current_section = "Overview"
                for sec in sections:
                    lines = sec.strip().split("\n")
                    if not lines or not lines[0].strip():
                        continue
                    if lines[0].startswith("#"):
                        current_section = lines[0].lstrip("#").strip()
                        body = "\n".join(lines[1:]).strip()
                    else:
                        body = sec.strip()

                    if len(body) > 40:
                        # Split very long sections into paragraphs
                        paras = [p.strip() for p in body.split("\n\n") if len(p.strip()) > 40]
                        for p in paras:
                            self.chunks.append(DocumentChunk(filename, current_section, p))
            except Exception as e:
                print(f"[RAG Load Warning] Could not load {filename}: {e}")

    def search(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        if not self.chunks:
            self._load_documents()

        query_tokens = set(re.findall(r"\w+", query.lower()))
        if not query_tokens:
            return [c.to_dict() for c in self.chunks[:top_k]]

        scored = []
        for chunk in self.chunks:
            content_lower = chunk.content.lower()
            section_lower = chunk.section.lower()
            
            score = 0
            for token in query_tokens:
                if len(token) < 3:
                    continue
                # Exact matches in section header get higher weight
                if token in section_lower:
                    score += 3
                # Matches in content
                cnt = content_lower.count(token)
                score += cnt

            if score > 0:
                scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = [item[1].to_dict() for item in scored[:top_k]]
        return results


def get_rag_engine() -> RAGEngine:
    return RAGEngine.get_instance()
