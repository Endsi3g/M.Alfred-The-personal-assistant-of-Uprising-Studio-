import React, { useState, useEffect, useRef } from 'react';
import { CommandBar } from './components/CommandBar';
import { ResponseCard } from './components/ResponseCard';

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
        handleAssist();
      });
    }

    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  const handleAssist = () => {
    // Trigger Assist mode: Clear tokens, set thinking UI, and send to backend
    setTokens([]);
    setIsThinking(true);

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      // Send a dummy context request for now to trigger Alfred
      wsRef.current.send(JSON.stringify({
        action: 'assist',
        context: 'User requested assistance from overlay.'
      }));
    }
  };

  return (
    <div style={{ width: '100vw', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <CommandBar onAssist={handleAssist} />
      <ResponseCard tokens={tokens} isThinking={isThinking} />
    </div>
  );
}

export default App;
