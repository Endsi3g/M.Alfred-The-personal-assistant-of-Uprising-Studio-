import React, { useState, useEffect } from 'react';
import {
    Grip,
    Mic,
    MicOff,
    Eye,
    EyeOff,
    Home,
    X,
    Sparkles
} from 'lucide-react';

interface CommandBarProps {
    onAssist: () => void;
}

export const CommandBar: React.FC<CommandBarProps> = ({ onAssist }) => {
    const [isMuted, setIsMuted] = useState(false);
    const [isStealth, setIsStealth] = useState(true);
    const [time, setTime] = useState(0);

    useEffect(() => {
        // Simple mock session timer
        const interval = setInterval(() => setTime(t => t + 1), 1000);
        return () => clearInterval(interval);
    }, []);

    const formatTime = (seconds: number) => {
        const m = Math.floor(seconds / 60).toString().padStart(2, '0');
        const s = (seconds % 60).toString().padStart(2, '0');
        return `${m}:${s}`;
    };

    const toggleStealth = () => {
        const newStealth = !isStealth;
        setIsStealth(newStealth);
        if (window.electronAPI) {
            window.electronAPI.setStealth(newStealth);
        }
    };

    const closeOverlay = () => {
        if (window.electronAPI) {
            window.electronAPI.closeApp();
        }
    };

    return (
        <div
            className="glass"
            style={{
                display: 'flex',
                alignItems: 'center',
                padding: '0 12px',
                height: '48px',
                width: '100%',
                maxWidth: '500px',
                justifyContent: 'space-between',
                userSelect: 'none'
            }}
        >
            {/* Draggable Handle */}
            <div
                className="drag-region"
                style={{
                    display: 'flex',
                    alignItems: 'center',
                    cursor: 'grab',
                    opacity: 0.5,
                }}
            >
                <Grip size={18} />
            </div>

            <div className="no-drag" style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                <button
                    onClick={() => setIsMuted(!isMuted)}
                    style={btnStyle}
                    title="Toggle Microphone"
                >
                    {isMuted ? <MicOff size={16} color="#ff4444" /> : <Mic size={16} color="#00d4ff" />}
                </button>

                <div style={{
                    fontSize: '14px',
                    fontFamily: 'var(--font-mono)',
                    color: 'var(--accent)',
                    background: 'rgba(255, 204, 0, 0.1)',
                    padding: '2px 8px',
                    borderRadius: '4px'
                }}>
                    {formatTime(time)} <span style={{ fontSize: '10px' }}>LIVE</span>
                </div>
            </div>

            <div className="no-drag" style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <button
                    onClick={onAssist}
                    style={{ ...btnStyle, background: 'rgba(0, 212, 255, 0.1)', color: '#00d4ff', padding: '4px 12px', borderRadius: '16px', display: 'flex', gap: '6px' }}
                    title="Manual Assist (CMD+Enter)"
                >
                    <Sparkles size={14} /> Smart
                </button>

                <button onClick={toggleStealth} style={btnStyle} title="Toggle Invisibility">
                    {isStealth ? <EyeOff size={16} color="var(--text-secondary)" /> : <Eye size={16} color="#00ff88" />}
                </button>

                <button style={btnStyle} title="Dashboard">
                    <Home size={16} color="var(--text-secondary)" />
                </button>

                <button onClick={closeOverlay} style={{ ...btnStyle, marginLeft: '8px' }} title="Close Session">
                    <X size={18} color="rgba(255,255,255,0.8)" />
                </button>
            </div>
        </div>
    );
};

// Vanilla React inline styles for simple buttons
const btnStyle: React.CSSProperties = {
    background: 'transparent',
    border: 'none',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'var(--text-secondary)',
    transition: '0.2s',
    padding: '6px',
    borderRadius: '8px',
};
