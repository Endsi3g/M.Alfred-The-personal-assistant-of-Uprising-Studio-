import React from 'react';
import { Copy, Check } from 'lucide-react';

interface ResponseCardProps {
    tokens: string[];
    isThinking: boolean;
}

export const ResponseCard: React.FC<ResponseCardProps> = ({ tokens, isThinking }) => {
    const [copied, setCopied] = React.useState(false);

    if (tokens.length === 0 && !isThinking) return null;

    const content = tokens.join('');

    const handleCopy = () => {
        navigator.clipboard.writeText(content);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div
            className="glass no-drag"
            style={{
                width: '100%',
                maxWidth: '500px',
                padding: '16px',
                marginTop: '8px',
                maxHeight: '400px',
                overflowY: 'auto',
                position: 'relative',
                animation: 'slideDown 0.2s cubic-bezier(0.16, 1, 0.3, 1)'
            }}
        >
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', alignItems: 'center' }}>
                <div style={{ fontSize: '12px', color: 'var(--accent)', fontWeight: 600 }}>
                    {isThinking ? 'AI is analyzing context...' : 'Response Ready'}
                </div>

                {!isThinking && content && (
                    <button
                        onClick={handleCopy}
                        style={{
                            background: 'rgba(255,255,255,0.1)',
                            border: 'none',
                            color: '#fff',
                            cursor: 'pointer',
                            padding: '4px 8px',
                            borderRadius: '6px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px',
                            fontSize: '12px'
                        }}
                    >
                        {copied ? <Check size={12} /> : <Copy size={12} />}
                        {copied ? 'Copied' : 'Copy'}
                    </button>
                )}
            </div>

            <div style={{
                lineHeight: '1.5',
                fontSize: '14px',
                color: isThinking ? 'var(--text-secondary)' : 'var(--text-primary)',
                whiteSpace: 'pre-wrap',
                fontFamily: isThinking ? 'var(--font-mono)' : 'var(--font-sans)',
            }}>
                {content}
                {isThinking && (
                    <span style={{ animation: 'pulse 1s infinite', marginLeft: '4px' }}>▍</span>
                )}
            </div>

            <style>
                {`
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0; }
          }
          @keyframes slideDown {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
          }
        `}
            </style>
        </div>
    );
};
