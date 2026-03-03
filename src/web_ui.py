from fastapi import FastAPI, WebSocket, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
import asyncio
import threading
import psutil
import platform
import subprocess
import os
import mss
import mss.tools
from pathlib import Path

app = FastAPI()

# Global state
logs = []
status = "ONLINE"
jarvis_instance = None
ROOT_DIR = Path(__file__).resolve().parent.parent

# Start Live Insights Worker for Cluely passive audio memory
from core.transcription_worker import start_live_insights_worker, get_live_transcript
start_live_insights_worker()

def get_system_stats():
    return {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "os": platform.system(),
        "status": status
    }

# Premium Glassmorphism UI with Skills Explorer
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A.L.F.R.E.D. COMMAND CENTER</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #ffcc00; /* Batman Gold */
            --secondary: #00d4ff; /* Tactical Blue */
            --bg: #02060a; /* Shadow Black */
            --glass: rgba(5, 10, 15, 0.8);
            --border: rgba(255, 204, 0, 0.2);
            --card-bg: rgba(255, 255, 255, 0.03);
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: var(--bg);
            background-image: radial-gradient(circle at 50% 50%, #001520 0%, #00080d 100%);
            color: #8ffcff;
            font-family: 'Outfit', sans-serif;
            height: 100vh;
            display: flex;
            overflow: hidden;
        }

        /* Sidebar */
        aside {
            width: 300px;
            background: var(--glass);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            z-index: 100;
        }

        .sidebar-header {
            padding: 2rem 1rem;
            text-align: center;
            border-bottom: 1px solid var(--border);
        }

        .sidebar-header h1 { font-size: 1.2rem; letter-spacing: 0.2rem; color: var(--primary); }

        .nav-items { flex: 1; padding: 1rem 0; }
        .nav-item {
            padding: 1rem 1.5rem;
            cursor: pointer;
            transition: 0.3s;
            display: flex;
            align-items: center;
            gap: 1rem;
            color: rgba(143, 252, 255, 0.6);
        }
        .nav-item:hover, .nav-item.active {
            background: rgba(255, 204, 0, 0.1);
            color: var(--primary);
            border-left: 3px solid var(--primary);
        }

        /* Main Content */
        main { flex: 1; display: flex; flex-direction: column; overflow: hidden; position: relative; }

        .dashboard-header {
            padding: 1rem 2rem;
            background: rgba(0, 0, 0, 0.4);
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .stats-grid { display: flex; gap: 2rem; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; }
        .stat-box { display: flex; flex-direction: column; }
        .stat-value { color: var(--primary); font-weight: bold; }
        .stat-label { color: var(--secondary); font-size: 0.6rem; text-transform: uppercase; }

        .view-content { flex: 1; padding: 2rem; overflow-y: auto; display: none; }
        .view-content.active { display: block; }

        /* Terminals/Console */
        #console-view { background: #000; padding: 1rem; border-radius: 8px; border: 1px solid var(--border); height: 80%; overflow-y: auto; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; }
        .log-line { margin-bottom: 0.5rem; padding-bottom: 0.5rem; border-bottom: 1px solid rgba(0, 212, 255, 0.05); }
        .log-ai { color: var(--secondary); }
        .log-you { color: var(--primary); }

        /* Skills Explorer */
        .skills-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-top: 1rem;
        }
        .skill-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            padding: 1.5rem;
            border-radius: 12px;
            transition: 0.3s;
        }
        .skill-card:hover { transform: translateY(-5px); border-color: var(--primary); box-shadow: 0 5px 15px rgba(255, 204, 0, 0.1); }
        .skill-name { color: var(--primary); font-weight: 600; margin-bottom: 0.5rem; display: block; }
        .skill-desc { font-size: 0.85rem; color: rgba(143, 252, 255, 0.7); line-height: 1.4; }
        .skill-tag { font-size: 0.6rem; background: rgba(0, 212, 255, 0.15); color: var(--secondary); padding: 2px 6px; border-radius: 4px; margin-top: 1rem; display: inline-block; }

        .search-bar { width: 100%; max-width: 500px; padding: 0.8rem 1.5rem; border-radius: 50px; background: rgba(0,0,0,0.5); border: 1px solid var(--border); color: #fff; margin-bottom: 2rem; outline: none; }

        /* Input Zone */
        .input-zone {
            padding: 1.5rem 2rem;
            background: var(--glass);
            border-top: 1px solid var(--border);
            display: flex; gap: 1rem;
        }
        #user-input { flex: 1; background: #000; border: 1px solid var(--border); border-radius: 50px; padding: 0.8rem 1.5rem; color: var(--primary); font-family: inherit; }
        .btn-send { background: var(--primary); border: none; width: 45px; height: 45px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; }

        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: var(--border); }
    </style>
</head>
<body>
    <aside>
        <div class="sidebar-header">
            <h1>A.L.F.R.E.D.</h1>
            <p style="font-size: 0.6rem; opacity: 0.5; margin-top: 0.5rem;">TACTICAL OS V3.0</p>
        </div>
        <nav class="nav-items">
            <div class="nav-item active" onclick="switchView('terminal')">COMMAND LOGS</div>
            <div class="nav-item" onclick="switchView('skills')">SKILLS CATALOG</div>
            <div class="nav-item" onclick="switchView('tactical')">TACTICAL SCRIPTS</div>
        </nav>
        <div style="padding: 2rem; font-size: 0.7rem; opacity: 0.4;">
            MISSION: PROTECT THE BELL ESTATE.
        </div>
    </aside>

    <main>
        <div class="dashboard-header">
            <div class="stats-grid">
                <div class="stat-box">
                    <span class="stat-label">BATCHIP</span>
                    <span class="stat-value" id="cpu-val">0%</span>
                </div>
                <div class="stat-box">
                    <span class="stat-label">BATCAVE MEM</span>
                    <span class="stat-value" id="ram-val">0%</span>
                </div>
            </div>
            <div style="display:flex; align-items:center; gap: 1rem;">
                <span id="status-badge" style="background: rgba(255, 204, 0, 0.2); color: var(--primary); padding: 4px 10px; border-radius: 4px; font-size: 0.6rem; font-weight: bold;">DIRECTIVE: READY</span>
            </div>
        </div>

        <!-- Terminal View -->
        <div id="view-terminal" class="view-content active">
            <div id="console-view"></div>
        </div>

        <!-- Skills View -->
        <div id="view-skills" class="view-content">
            <input type="text" class="search-bar" id="skill-search" placeholder="Search Master Bell's Arsenal (900+ skills)..." oninput="filterSkills()">
            <div class="skills-grid" id="skills-container">
                <!-- Loaded via JS -->
            </div>
        </div>

        <!-- Tactical View -->
        <div id="view-tactical" class="view-content">
            <h2 style="color: var(--primary); margin-bottom: 2rem;">Utility Protocols</h2>
            <div class="skills-grid">
                <div class="skill-card" onclick="runScript('test_system')">
                    <span class="skill-name">SYSTEM DIAGNOSTICS</span>
                    <span class="skill-desc">Run comprehensive E2E tests for Frontend, Backend, and Modules.</span>
                    <span class="skill-tag">scripts/test_system.py</span>
                </div>
                <div class="skill-card" onclick="runScript('update_skills')">
                    <span class="skill-name">RE-INDEX ARSENAL</span>
                    <span class="skill-desc">Update and re-index the Awesome-Skills catalog from local sources.</span>
                    <span class="skill-tag">scripts/update_skills.py</span>
                </div>
            </div>
        </div>

        <div class="input-zone">
            <input type="text" id="user-input" placeholder="Initiate verbal protocol..." autocomplete="off">
            <button class="btn-send" onclick="sendCommand()">
                 <svg viewBox="0 0 24 24" width="20" height="20"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" fill="currentColor"></path></svg>
            </button>
        </div>
    </main>

    <script>
        let allSkills = [];

        function switchView(view) {
            document.querySelectorAll('.view-content').forEach(v => v.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            document.getElementById('view-' + view).classList.add('active');
            event.currentTarget.classList.add('active');
            if(view === 'skills' && allSkills.length === 0) loadSkills();
        }

        async function loadSkills() {
            try {
                const resp = await fetch('/api/skills');
                allSkills = await resp.json();
                renderSkills(allSkills);
            } catch (e) { console.error("Arsenal offline", e); }
        }

        function renderSkills(skills) {
            const container = document.getElementById('skills-container');
            container.innerHTML = skills.slice(0, 50).map(s => `
                <div class="skill-card">
                    <span class="skill-name">${s.name}</span>
                    <span class="skill-desc">${s.description || 'No data recorded.'}</span>
                    <span class="skill-tag">${s.category || 'general'}</span>
                </div>
            `).join('');
        }

        function filterSkills() {
            const q = document.getElementById('skill-search').value.toLowerCase();
            const filtered = allSkills.filter(s => s.name.toLowerCase().includes(q) || (s.description && s.description.toLowerCase().includes(q)));
            renderSkills(filtered);
        }

        function appendLog(text) {
            const div = document.createElement('div');
            const isYou = text.toLowerCase().startsWith('you:');
            div.className = 'log-line ' + (isYou ? 'log-you' : 'log-ai');
            div.innerHTML = `<strong>${isYou ? 'BELL' : 'ALFRED'}:</strong> ${text.replace(/^[A-Za-z]+:\\s*/, '')}`;
            const consoleView = document.getElementById('console-view');
            consoleView.appendChild(div);
            consoleView.scrollTop = consoleView.scrollHeight;
        }

        async function sendCommand() {
            const input = document.getElementById('user-input');
            const cmd = input.value.trim();
            if(!cmd) return;
            appendLog('YOU: ' + cmd);
            input.value = '';
            await fetch('/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({goal: cmd})
            });
        }

        async function runScript(name) {
            appendLog('ALFRED: Initiating Protocol ' + name + '...');
            const resp = await fetch('/run-script/' + name);
            const data = await resp.json();
            appendLog('ALFRED: ' + data.output);
        }

        document.getElementById('user-input').addEventListener('keypress', e => { if(e.key === 'Enter') sendCommand(); });

        const ws = new WebSocket(`ws://${location.host}/ws`);
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'log') appendLog(data.text);
            else if (data.type === 'stats') {
                document.getElementById('cpu-val').innerText = data.cpu + '%';
                document.getElementById('ram-val').innerText = data.ram + '%';
            }
        };
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_index():
    return HTML_TEMPLATE

@app.get("/api/skills")
async def get_skills():
    path = Path("modules/awesome_skills/skills_index.json")
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return JSONResponse(content=json.load(f))
    return JSONResponse(content=[])

@app.get("/run-script/{name}")
async def run_script(name: str):
    script_map = {
        "test_system": "scripts/test_system.py",
        "update_skills": "scripts/update_skills.py"
    }
    target = script_map.get(name)
    if target and os.path.exists(target):
        try:
            result = subprocess.run([sys.executable, target], capture_output=True, text=True)
            return {"status": "ok", "output": result.stdout if result.returncode == 0 else result.stderr}
        except Exception as e:
            return {"status": "error", "output": str(e)}
    return {"status": "not_found", "output": "Protocol not found."}

@app.post("/command")
async def handle_command(request: Request):
    data = await request.json()
    goal = data.get("goal")
    if goal and jarvis_instance:
        from agent.task_queue import get_queue
        get_queue().submit(goal=goal, priority="normal", speak=jarvis_instance.speak)
        return {"status": "ok"}
    return {"status": "failed"}

active_websockets = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_websockets.append(websocket)
    try:
        while True: await websocket.receive_text()
    except:
        if websocket in active_websockets: active_websockets.remove(websocket)

@app.websocket("/ws/cluely")
async def cluely_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                action = payload.get("action")
                
                if action == "assist" and jarvis_instance:
                    text_context = payload.get("context", "")
                    await websocket.send_text(json.dumps({"type": "status", "status": "Taking screenshot..."}))
                    
                    # 1. Grab screenshot async
                    def grab_screen() -> bytes:
                        with mss.mss() as sct:
                            monitor = sct.monitors[1]
                            shot = sct.grab(monitor)
                            return mss.tools.to_png(shot.rgb, shot.size)
                    
                    loop = asyncio.get_event_loop()
                    png_bytes = await loop.run_in_executor(None, grab_screen)
                    
                    await websocket.send_text(json.dumps({"type": "status", "status": "Analyzing context..."}))
                    
                    # 2. Call Gemini Vision with Streaming
                    def analyze_and_stream():
                        try:
                            from core.llm_manager import UnifiedLLM
                            engine = UnifiedLLM(Path("config/api_keys.json"))
                            if not engine.client:
                                return "Error: Gemini API key missing."
                            
                            sys_prompt = (
                                "You are Cluely, an invisible tactical overlay. "
                                "Analyze the provided screenshot and user context. "
                                "Be concise, direct, and use Markdown for formatting."
                            )
                            
                            live_audio_context = get_live_transcript()
                            
                            full_prompt = sys_prompt + f"\n\nUser Notes: {text_context}"
                            if live_audio_context:
                                full_prompt += f"\n\nLive Audio Transcript (Last 60s):\n{live_audio_context}"
                            
                            response_iter = engine.client.models.generate_content_stream(
                                model="gemini-1.5-flash",
                                contents=[
                                    full_prompt,
                                    {"mime_type": "image/png", "data": png_bytes}
                                ]
                            )
                            
                            for chunk in response_iter:
                                if chunk.text:
                                    if loop.is_running():
                                        asyncio.run_coroutine_threadsafe(
                                            websocket.send_text(json.dumps({"type": "token", "text": chunk.text})),
                                            loop
                                        )
                            
                            # Final token to mark completion
                            if loop.is_running():
                                asyncio.run_coroutine_threadsafe(
                                    websocket.send_text(json.dumps({"type": "token", "text": ""})),
                                    loop
                                )
                        except Exception as e:
                            print(f"[Cluely] Vision Analysis Error: {e}")
                            if loop.is_running():
                                asyncio.run_coroutine_threadsafe(
                                    websocket.send_text(json.dumps({"type": "token", "text": f"\n\n*Error: {e}*"})),
                                    loop
                                )

                    # Run the generation in background thread to avoid blocking main event loop
                    threading.Thread(target=analyze_and_stream, daemon=True).start()
                    
            except json.JSONDecodeError:
                pass
    except Exception:
        pass

async def broadcast(data: dict):
    msg = json.dumps(data)
    for ws in active_websockets:
        try: await ws.send_text(msg)
        except: pass

async def stats_pusher():
    while True:
        await broadcast({"type": "stats", **get_system_stats()})
        await asyncio.sleep(2)

def start_web_ui(jarvis_obj=None, port=8000):
    global jarvis_instance
    jarvis_instance = jarvis_obj
    def run_stats():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(stats_pusher())
    threading.Thread(target=run_stats, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=port)

def patch_ui_for_web(ui_instance, jarvis_instance_obj):
    global jarvis_instance
    jarvis_instance = jarvis_instance_obj
    original_write_log = ui_instance.write_log
    def web_write_log(text: str):
        original_write_log(text)
        # Simplified thread-safe broadcast for web logs
        if active_websockets:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.run_coroutine_threadsafe(broadcast({"type": "log", "text": text}), loop)
            except: pass
    ui_instance.write_log = web_write_log
