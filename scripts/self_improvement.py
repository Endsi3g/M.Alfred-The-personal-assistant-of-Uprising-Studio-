import os
import glob
import re
from pathlib import Path
from core.llm_manager import UnifiedLLM

class MissionReflector:
    """
    Analyzes mission logs for failures and generates improvement protocols.
    """
    def __init__(self, log_path: str = "logs/mission.log"):
        self.log_path = Path(log_path)
        self.llm = UnifiedLLM()

    def analyze_recent_failures(self, days: int = 1) -> str:
        """
        Scans logs for [ERROR] or FAILED steps and reflects on them.
        """
        if not self.log_path.exists():
            return "No mission logs found to analyze, Master Bell."

        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Simple heuristic for failure patterns
            failures = re.findall(r"\[ERROR\].*|.*Step.*FAILED.*", content)
            if not failures:
                return "Recent missions have been flawless. No improvements required at this time."

            failure_context = "\n".join(failures[-5:]) # Last 5 failures
            
            prompt = f"""You are Alfred, reflecting on recent mission data for Master Bell.
Recent Failure Patterns:
{failure_context}

Analyze these failures. Suggest ONE specific improvement for your 'INSTRUCTIONS_AI.md' or 'ALFRED_PROTOCOLS.md' to prevent these in the future.
Return your response structured as:
[LESSON LEARNED]: ...
[PROPOSED PROTOCOL UPDATE]: ...
"""
            reflection = self.llm.generate_content(
                model_name="gemini-1.5-flash",
                prompt=prompt,
                system_instruction="You are Alfred, a self-improving digital majordomo. Be precise and professional."
            )
            return reflection

        except Exception as e:
            return f"Error during reflection: {e}"

    def apply_improvement(self, suggestion: str):
        """
        Technically would patch the doc, but for now we'll just log it 
        for Master Bell's review.
        """
        print(f"[Self-Improvement] Proposed update:\n{suggestion}")

# Simple CLI hook
if __name__ == "__main__":
    reflector = MissionReflector()
    report = reflector.analyze_recent_failures()
    print("=== ALFRED SELF-REFLECTION REPORT ===")
    print(report)
