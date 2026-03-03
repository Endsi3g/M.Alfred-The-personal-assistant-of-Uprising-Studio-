# Next Steps — Project B.E.L.L. (v1.2.0 Roadmap)

This document outlines the immediate technical objectives for the next phase of development, focusing on **Live Insights** and **Autonomous Pilot Mode**.

## Phase 9: Advanced Context Pipelines (Screen & Passive Audio)

- [ ] **Implement `core/transcription_worker.py`**
  - Integrate `Whisper` (local) or `SpeechRecognition` for background passive listening.
  - Setup multi-threaded audio buffering from `sounddevice`.
- [ ] **Add sliding-window audio context**
  - Maintain a rolling 60-second transcript buffer to provide conversational context to the LLM.
- [ ] **Implement `CMD+Enter` (Assist) screen capture bridge**
  - Connect the HUD hotkey to the `mss` screen capture utility.
  - Send base64 image data + audio transcript to Gemini 1.5/2.0 for multi-modal reasoning.
- [ ] **Update `overlay/alfred_overlay.py`**
  - Enhance the UI to show "Analyzing Screen..." states during Assist triggers.

## Phase 10: Dashboard & Pilot Mode

- [ ] **Implement `cluely-overlay/src/components/Dashboard.tsx`**
  - Create a React-based historical view of mission logs and interactions.
  - Add a "Settings" interface for system-wide preferences.
- [ ] **Backend API Expansion (`web_ui.py`)**
  - `GET /api/history`: Retrieve past interactions.
  - `POST /api/settings`: Persist user preferences.
- [ ] **Implement "Pilot Mode"**
  - Bridge the HUD output directly to the `agent/task_queue.py`.
  - Allow Alfred to autonomously click, type, and navigate based on the vision+audio context.
- [ ] **Final Verification & Release (v1.2.0)**
  - Comprehensive multi-modal testing.
  - Performance optimization for background transcription.

---
*Status: MISSION PENDING*
