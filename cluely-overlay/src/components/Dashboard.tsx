import React, { useEffect, useState } from 'react';
import { Activity, Clock, Settings, Shield, Server, ArrowLeft } from 'lucide-react';

interface HistoryItem {
    id: string;
    timestamp: string;
    context: string;
    response: string;
}

interface DashboardProps {
    onClose: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onClose }) => {
    const [history, setHistory] = useState<HistoryItem[]>([]);
    const [activeTab, setActiveTab] = useState<'history' | 'settings'>('history');

    // Mock history for now. Let's assume we fetch from FastAPI later.
    useEffect(() => {
        fetch('http://localhost:8000/api/history')
            .then(res => res.json())
            .then(data => setHistory(data))
            .catch(() => {
                // Fallback fake data if endpoint is not up yet
                setHistory([
                    { id: '1', timestamp: new Date().toLocaleTimeString(), context: "How to fix this error?", response: "Check line 42." }
                ]);
            });
    }, []);

    return (
        <div
            className="glass no-drag"
            style={{
                width: '100%',
                maxWidth: '800px',
                height: '500px',
                marginTop: '16px',
                display: 'flex',
                flexDirection: 'column',
                animation: 'slideDown 0.2s cubic-bezier(0.16, 1, 0.3, 1)',
                overflow: 'hidden'
            }}
        >
            <div style={{ display: 'flex', borderBottom: '1px solid rgba(255,255,255,0.1)', padding: '16px', alignItems: 'center' }}>
                <button onClick={onClose} className="icon-btn" style={{ marginRight: '16px' }} title="Back to Overlay">
                    <ArrowLeft size={18} />
                </button>
                <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 500, flex: 1 }}>Cluely Control Center</h2>

                <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                        className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
                        onClick={() => setActiveTab('history')}
                    >
                        <Clock size={16} /> History
                    </button>
                    <button
                        className={`tab-btn ${activeTab === 'settings' ? 'active' : ''}`}
                        onClick={() => setActiveTab('settings')}
                    >
                        <Settings size={16} /> Settings
                    </button>
                </div>
            </div>

            <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
                {activeTab === 'history' && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        {history.length === 0 ? (
                            <div style={{ textAlign: 'center', color: 'var(--text-secondary)', marginTop: '40px' }}>
                                <Activity size={32} style={{ opacity: 0.5, marginBottom: '8px' }} />
                                <p>No assist history found in this session.</p>
                            </div>
                        ) : (
                            history.map(item => (
                                <div key={item.id} style={{ background: 'rgba(0,0,0,0.2)', padding: '12px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                                    <div style={{ fontSize: '12px', color: 'var(--accent)', marginBottom: '8px' }}>{item.timestamp}</div>
                                    <div style={{ fontSize: '14px', marginBottom: '8px', color: 'var(--text-secondary)' }}><b>Context:</b> {item.context || "Screenshare / Audio Context"}</div>
                                    <div style={{ fontSize: '14px', whiteSpace: 'pre-wrap' }}>{item.response}</div>
                                </div>
                            ))
                        )}
                    </div>
                )}

                {activeTab === 'settings' && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                        <div className="settings-card">
                            <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: 0 }}><Server size={18} /> Engine Configuration</h3>
                            <select className="select-input" defaultValue="gemini-1.5-flash">
                                <option value="gemini-1.5-flash">Gemini 1.5 Flash (Fast)</option>
                                <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
                                <option value="llama3">Ollama Llama3 (Local)</option>
                            </select>
                        </div>

                        <div className="settings-card">
                            <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: 0 }}><Shield size={18} /> Privacy & Stealth</h3>
                            <label style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ color: 'var(--text-secondary)' }}>Hardware Stealth (DWMWA_EXCLUDED_FROM_CAPTURE)</span>
                                <input type="checkbox" defaultChecked disabled />
                            </label>
                        </div>
                    </div>
                )}
            </div>

            <style>
                {`
          .tab-btn {
            background: rgba(255,255,255,0.05);
            border: 1px solid transparent;
            color: var(--text-secondary);
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 13px;
            font-family: var(--font-sans);
            transition: all 0.2s;
          }
          .tab-btn:hover { background: rgba(255,255,255,0.1); color: #fff; }
          .tab-btn.active {
            background: rgba(0, 212, 255, 0.1);
            color: #00d4ff;
            border-color: rgba(0, 212, 255, 0.3);
          }
          .settings-card {
            background: rgba(0,0,0,0.2);
            padding: 16px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.05);
          }
          .select-input {
            width: 100%;
            background: rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.1);
            color: #fff;
            padding: 8px;
            border-radius: 6px;
            outline: none;
            font-family: inherit;
          }
        `}
            </style>
        </div>
    );
};
