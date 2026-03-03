# Next Steps — Project B.E.L.L. (A.L.F.R.E.D.)

Strategic roadmap for upcoming milestones and tactical improvements.

---

## Milestone 3: Vision (VLM) & Multi-tier Memory

- [x] Integrate a Vision-Language Model for real-time screen understanding
- [x] Implement persistent long-term memory (SQLite or Redis-backed)
- [x] Add episodic memory for conversation context across sessions
- [x] Build semantic search over past interactions

## Milestone 4: Windows HUD & Pro Distribution

- [ ] Develop an always-on overlay HUD (transparent widget on desktop)
- [ ] Package Alfred as a standalone `.exe` installer (PyInstaller / Nuitka)
- [ ] Add auto-update mechanism via GitHub releases
- [ ] Create a first-time setup wizard with guided API key configuration

## Technical Debt & Improvements

- [x] Add `.gitignore` for `__pycache__/`, `node_modules/`, `.env`
- [ ] Migrate remaining `google-generativeai` references to `google-genai`
- [ ] Implement proper async event loop management across all agents
- [ ] Add structured logging (replace print statements with `logging`)
- [ ] Write unit tests for core modules (`planner`, `executor`, `multi_agent`)

## Agent Intelligence

- [ ] Enhance delegation logic in `MissionControl` with LLM-based intent classification
- [ ] Add agent-to-agent communication protocol (not just orchestrator-to-agent)
- [ ] Implement task memory so agents learn from previous mission outcomes
- [ ] Build a feedback loop: failed missions auto-generate improvement suggestions

## UX & Interface

- [ ] Add voice wake-word detection ("Hey Alfred")
- [ ] Implement streaming responses in the Web Command Center
- [ ] Mobile-responsive design for the Web UI
- [ ] Add dark/light theme toggle in the Command Center

---

*"The mission is never truly complete, Master Bell. There is always room for refinement."*
— Alfred
