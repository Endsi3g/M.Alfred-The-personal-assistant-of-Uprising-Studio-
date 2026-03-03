import React, { useState, useEffect, useRef } from 'react';
import { CommandBar } from './components/CommandBar';
import { ResponseCard } from './components/ResponseCard';
import { Dashboard } from './components/Dashboard';

declare global {
  interface Window {
    electronAPI: {
      hideWindow: () => void;
      closeApp: () => void;
      setStealth: (s: boolean) => void;
      onAssistTriggered: (cb: () => void) => void;
    };
  }
}

function App() {
  const [tokens, setTokens] = useState<string[]>([]);
  const [isThinking, setIsThinking] = useState(false);
  const [isDashboardOpen, setIsDashboardOpen] = useState(false); // Added isDashboardOpen state
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Connect to Alfred Python Backend
    const connect = () => {
      const ws = new WebSocket('ws://localhost:8000/ws/cluely');

      ws.onopen = () => {
        console.log('Connected to A.L.F.R.E.D loop');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'token') {
            setIsThinking(false);
            setTokens(prev => [...prev, data.text]);
          } else if (data.type === 'status') {
            setIsThinking(true);
            setTokens([]);
          }
        } catch (e) {
          console.error(e);
        }
      };

      ws.onclose = () => {
        console.log('Disconnected, retrying in 2s');
        setTimeout(connect, 2000);
      };

      wsRef.current = ws;
    };

    connect();

    // Listen for global shortcut trigger from Electron
    if (window.electronAPI) {
      window.electronAPI.onAssistTriggered(() => {
        handleAssist(false); // Global shortcut defaults to non-pilot for now
      });
    }

    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  const handleAssist = (isPilotMode: boolean) => { // Modified handleAssist signature
    // Trigger Assist mode: Clear tokens, set thinking UI, and send to backend
    setTokens([]);
    setIsThinking(true);
    if (isDashboardOpen) setIsDashboardOpen(false); // Close dashboard if open

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        action: 'assist',
        context: 'User requested assistance from overlay.',
        pilot_mode: isPilotMode // Added pilot_mode
      }));
    }
  };

  return (
    <div style={{ width: '100vw', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <CommandBar
        onAssist={handleAssist}
        onToggleDashboard={() => setIsDashboardOpen(!isDashboardOpen)} // Added onToggleDashboard
      />
      {isDashboardOpen ? ( // Conditional rendering for Dashboard
        <Dashboard onClose={() => setIsDashboardOpen(false)} />
      ) : (
        <ResponseCard tokens={tokens} isThinking={isThinking} />
      )}
    </div>
  );
}

export default App;
