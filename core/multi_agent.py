import logging
import sys
import os
from pathlib import Path

# Add copaw_lib to path
lib_path = Path("c:/Users/Karl/Jarvis/Mark-XXX/modules/copaw_lib/src")
if lib_path.exists() and str(lib_path) not in sys.path:
    sys.path.append(str(lib_path))

from typing import List, Optional
from modules.copaw_lib.src.copaw.agents import CoPawAgent
from core.system_ops import ops as sys_ops
from agent.planner    import unified_llm
import asyncio

logger = logging.getLogger(__name__)

class SpecializedAgent:
    """Base class for Alfred's specialized tactical agents."""
    def __init__(self, role: str, goal: str, **kwargs):
        self.role = role
        self.goal = goal
        self.system_prompt = f"You are the {role}. Your objective: {goal}. Stay loyal to Master Bell."
        self.copaw_agent = None
        
        # Try to initialize CoPawAgent if possible
        try:
            from modules.copaw_lib.src.copaw.agents import CoPawAgent
            self.copaw_agent = CoPawAgent(env_context=self.system_prompt, **kwargs)
            logger.info(f"[{role}] CoPaw engine initialized.")
        except Exception as e:
            logger.warning(f"[{role}] CoPaw initialization failed, using UnifiedLLM fallback: {e}")

    async def reply(self, content: str):
        """Standard reply interface."""
        if self.copaw_agent:
            try:
                # CoPaw reply is usually sync or async depending on version
                if asyncio.iscoroutinefunction(self.copaw_agent.reply):
                    return await self.copaw_agent.reply(content)
                else:
                    return self.copaw_agent.reply(content)
            except Exception as e:
                logger.error(f"[{self.role}] CoPaw reply failed: {e}")
        
        # Fallback to UnifiedLLM
        logger.info(f"[{self.role}] Handling via UnifiedLLM")
        response = unified_llm.generate_content(
            model_name="gemini-2.5-flash",
            prompt=content,
            system_instruction=self.system_prompt
        )
        return response

class WindowsOpsAgent(SpecializedAgent):
    """Specialized in Windows System Operations."""
    def __init__(self, **kwargs):
        super().__init__(
            role="Windows Operations Tactical",
            goal="Manage system services, files, hardware controls (volume, brightness), and deep OS maneuvers.",
            **kwargs
        )
        # We can register custom tools here if needed, 
        # but CoPawAgent already has execute_shell_command which we use for SystemOps.

class WebTacticalAgent(SpecializedAgent):
    """Specialized in Web Intelligence & Automation."""
    def __init__(self, **kwargs):
        super().__init__(
            role="Web Tactical Analyst",
            goal="Execute complex web research, automation using SeleniumBase, and sensitive data scraping.",
            **kwargs
        )

class DevSecAgent(SpecializedAgent):
    """Specialized in Code Audits & Technical Security."""
    def __init__(self, **kwargs):
        super().__init__(
            role="DevSec Specialist",
            goal="Perform code reviews, security audits, and manage the technical skill arsenal.",
            **kwargs
        )

class MissionControl:
    """The Orchestrator. Master Bell's primary interface to the agency."""
    def __init__(self):
        self.orchestrator = SpecializedAgent(
            role="Alfred (Orchestrator)",
            goal="Coordinate specialized agents to fulfill Master Bell's objectives."
        )
        self.ops = WindowsOpsAgent()
        self.web = WebTacticalAgent()
        self.devsec = DevSecAgent()

    async def execute_mission(self, tactical_request: str):
        """
        Decomposes the mission and delegates to the appropriate agent.
        """
        print(f"[MissionControl] Decomposing mission: {tactical_request}")
        
        # Simple delegation logic
        target_agent = self.orchestrator
        if any(word in tactical_request.lower() for word in ["service", "volume", "brightness", "system"]):
            target_agent = self.ops
            print("[MissionControl] Routing to WindowsOpsAgent")
        elif any(word in tactical_request.lower() for word in ["search", "web", "browser", "news"]):
            target_agent = self.web
            print("[MissionControl] Routing to WebTacticalAgent")
        
        response = await target_agent.reply(tactical_request)
        print(f"[MissionControl] Response received from {target_agent.role}")
        return response

# Singleton access
mission_control = MissionControl()
