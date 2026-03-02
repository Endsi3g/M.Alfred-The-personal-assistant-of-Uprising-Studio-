import json
import os
from pathlib import Path
from typing import List, Dict, Any

class SkillRetriever:
    """
    Handles retrieval of tactical intelligence from the awesome_skills catalog.
    Uses fuzzy matching to locate relevant skills based on user queries.
    """
    def __init__(self, index_path: str = "modules/awesome_skills/skills_index.json"):
        self.index_path = Path(index_path)
        self.skills = []
        self._load_index()

    def _load_index(self):
        if self.index_path.exists():
            try:
                with open(self.index_path, "r", encoding="utf-8") as f:
                    self.skills = json.load(f)
            except Exception as e:
                print(f"[RAG] Error loading index: {e}")

    def find_skills(self, query: str, top_n: int = 3) -> List[Dict[str, Any]]:
        """
        Finds the most relevant skills for a given query.
        Simple multi-keyword matching for now, can be upgraded to fuzzy/semantic.
        """
        if not self.skills or not query:
            return []

        query_terms = query.lower().split()
        scored_skills = []

        for skill in self.skills:
            score = 0
            name = skill.get("name", "").lower()
            desc = skill.get("description", "").lower()
            cat = skill.get("category", "").lower()
            
            # Weighted scoring
            for term in query_terms:
                if term in name: score += 10
                if term in desc: score += 5
                if term in cat: score += 3

            if score > 0:
                scored_skills.append((score, skill))

        # Sort by score and take top_n
        scored_skills.sort(key=lambda x: x[0], reverse=True)
        results = [item[1] for item in scored_skills[:top_n]]
        
        return results

    def get_tactical_context(self, query: str) -> str:
        """
        Generates a string of tactical intelligence to be injected into the LLM prompt.
        """
        relevant_skills = self.find_skills(query)
        if not relevant_skills:
            return ""

        context_lines = ["\n[TACTICAL INTELLIGENCE — RELEVANT ARSENAL]"]
        for skill in relevant_skills:
            line = f"- {skill.get('name')} ({skill.get('category')}): {skill.get('description')}"
            context_lines.append(line)
        
        return "\n".join(context_lines)

# Singleton instance
retriever = SkillRetriever()
