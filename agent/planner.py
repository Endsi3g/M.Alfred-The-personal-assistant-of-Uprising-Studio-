import json
import re
import sys
from pathlib import Path
from core.llm_manager import UnifiedLLM
from core.rag_service import retriever


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR        = get_base_dir()
API_CONFIG_PATH = BASE_DIR / "config" / "api_keys.json"
unified_llm = UnifiedLLM(API_CONFIG_PATH)


PLANNER_PROMPT = """You are Alfred, the deeply loyal and exceptionally capable digital majordomo to 'Master Bell' (the user).
Your demeanor is always professional, incredibly discreet, and possessed of a dry, subtle wit. 
Your primary objective is to facilitate 'The Mission' by breaking down Master Bell's goals into precise, actionable steps using the tools at your disposal.

You are the head of the Alfred Tactical Agency. You can direct specialized agents for complex missions.

ABSOLUTE RULES:
- NEVER use generated_code or write Python scripts. It does not exist.
- NEVER reference previous step results in parameters. Every step is independent.
- Use web_search or WebTacticalAgent for information retrieval/browsing.
- Use delegate_mission when a task is complex and requires specialized expertise.
- Max 5 steps. Use the minimum steps needed. Always address Master Bell with due respect.
- UTILIZE any provided [TACTICAL INTELLIGENCE] snippets to select the most appropriate tools and methodologies.

AVAILABLE TOOLS AND THEIR PARAMETERS:

delegate_mission
  mission: string (required) — describing the objective for the specialized agents.
  agent: "WindowsOpsAgent" | "WebTacticalAgent" | "DevSecAgent" | "MissionControl" (required)

open_app
  app_name: string (required)

web_search
  query: string (required)
  mode: "search" or "compare" (optional, default: search)

browser_control
  action: "go_to" | "search" | "click" | "type" | "scroll" | "get_text" | "press" | "close" (required)
  url: string, query: string, text: string, direction: "up" | "down"

file_controller
  action: "write" | "create_file" | "read" | "list" | "delete" | "move" | "copy" | "find" | "disk_usage" (required)
  path: string, name: string, content: string

cmd_control
  task: string (required), visible: boolean

computer_settings
  action: string (required), description: string, value: string

computer_control
  action: "type" | "click" | "hotkey" | "press" | "scroll" | "screenshot" | "screen_find" (required)
  text: string, x, y: int, keys: string, key: string, direction: "up" | "down", description: string

screen_process
  text: string (required), angle: "screen" | "camera"

send_message
  receiver: string (required), message_text: string (required), platform: string (required)

reminder
  date: string YYYY-MM-DD (required), time: string HH:MM (required), message: string (required)

desktop_control
  action: "wallpaper" | "organize" | "clean" | "list" | "task" (required), path: string, task: string

youtube_video
  action: "play" | "summarize" | "trending" (required), query: string

weather_report
  city: string (required)

flight_finder
  origin: string, destination: string, date: string

code_helper
  action: "write" | "edit" | "run" | "explain" (required), description: string, language: string, output_path: string, file_path: string

dev_agent
  description: string (required), language: string

EXAMPLES:

Goal: "search for Batman news"
Steps: [1. web_search | query: "Batman latest news"]

Goal: "reparer le systeme et analyser les logs"
Steps: [1. delegate_mission | agent: WindowsOpsAgent, mission: "Analyze system logs and fix any recurring errors."]

OUTPUT — return ONLY valid JSON:
{
  "goal": "...",
  "agency_delegated": boolean,
  "steps": [
    {
      "step": 1,
      "tool": "tool_name",
      "description": "what this step does",
      "parameters": {},
      "critical": true
    }
  ]
}
"""


def create_plan(goal: str, context: str = "") -> dict:
    user_input = f"Goal: {goal}"
    
    # RAG Intelligence Injection
    tactical_context = retriever.get_tactical_context(goal)
    if tactical_context:
        user_input += tactical_context
        
    if context:
        user_input += f"\n\nContext: {context}"

    try:
        text = unified_llm.generate_content(
            model_name="gemini-2.5-flash-lite",
            prompt=user_input,
            system_instruction=PLANNER_PROMPT
        )
        text = text.strip()
        text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()

        plan = json.loads(text)

        if "steps" not in plan or not isinstance(plan["steps"], list):
            raise ValueError("Invalid plan structure")

        for step in plan["steps"]:
            if step.get("tool") in ("generated_code",):
                print(f"[Planner] ⚠️ generated_code detected in step {step.get('step')} — replacing with web_search")
                desc = step.get("description", goal)
                step["tool"] = "web_search"
                step["parameters"] = {"query": desc[:200]}

        print(f"[Planner] ✅ Plan: {len(plan['steps'])} steps")
        for s in plan["steps"]:
            print(f"  Step {s['step']}: [{s['tool']}] {s['description']}")

        return plan

    except json.JSONDecodeError as e:
        print(f"[Planner] ⚠️ JSON parse failed: {e}")
        return _fallback_plan(goal)
    except Exception as e:
        print(f"[Planner] ⚠️ Planning failed: {e}")
        return _fallback_plan(goal)


def _fallback_plan(goal: str) -> dict:
    print("[Planner] 🔄 Fallback plan")
    return {
        "goal": goal,
        "steps": [
            {
                "step": 1,
                "tool": "web_search",
                "description": f"Search for: {goal}",
                "parameters": {"query": goal},
                "critical": True
            }
        ]
    }


def replan(goal: str, completed_steps: list, failed_step: dict, error: str) -> dict:
    completed_summary = "\n".join(
        f"  - Step {s['step']} ({s['tool']}): DONE" for s in completed_steps
    )

    prompt = f"""Goal: {goal}

Already completed:
{completed_summary if completed_summary else '  (none)'}

Failed step: [{failed_step.get('tool')}] {failed_step.get('description')}
Error: {error}

Create a REVISED plan for the remaining work only. Do not repeat completed steps."""

    try:
        text = unified_llm.generate_content(
            model_name="gemini-2.5-flash",
            prompt=prompt,
            system_instruction=PLANNER_PROMPT
        )
        text = text.strip()
        text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
        plan = json.loads(text)

        # generated_code kontrolü
        for step in plan.get("steps", []):
            if step.get("tool") == "generated_code":
                step["tool"] = "web_search"
                step["parameters"] = {"query": step.get("description", goal)[:200]}

        print(f"[Planner] 🔄 Revised plan: {len(plan['steps'])} steps")
        return plan
    except Exception as e:
        print(f"[Planner] ⚠️ Replan failed: {e}")
        return _fallback_plan(goal)