import React from 'react';
import { Zap, Play, Square } from 'lucide-react';

/**
 * Attack type selector and run controls.
 */
export default function AttackControls({
    attacks = [],
    selectedAttack,
    onSelectAttack,
    onRun,
    onCancel,
    status = 'idle',
    mode = 'builtin', // 'builtin' | 'custom'
    onModeChange,
}) {
    return (
        <div className="card" style={{ marginBottom: 12 }}>
            <div className="card-header">
                <div className="card-title">
                    <Zap size={14} className="card-title-icon" />
                    Attack
                </div>
            </div>

            {/* Mode Toggle */}
            <div className="tabs" style={{ marginBottom: 12 }}>
                <button
                    className={`tab ${mode === 'builtin' ? 'active' : ''}`}
                    onClick={() => onModeChange('builtin')}
                >
                    Built-in (ART)
                </button>
                <button
                    className={`tab ${mode === 'custom' ? 'active' : ''}`}
                    onClick={() => onModeChange('custom')}
                >
                    Custom Code
                </button>
            </div>

            {mode === 'builtin' && (
                <div className="form-group" style={{ marginBottom: 12 }}>
                    <label className="form-label">Attack Method</label>
                    <select
                        className="form-select"
                        value={selectedAttack || ''}
                        onChange={(e) => onSelectAttack(e.target.value)}
                    >
                        <option value="">Choose attack…</option>
                        {attacks.map((a) => (
                            <option key={a.name} value={a.name}>
                                {a.display_name}
                            </option>
                        ))}
                    </select>
                    {selectedAttack && attacks.find(a => a.name === selectedAttack)?.description && (
                        <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 6, lineHeight: 1.5 }}>
                            {attacks.find(a => a.name === selectedAttack).description}
                        </p>
                    )}
                </div>
            )}

            {/* Run/Cancel Buttons */}
            <div style={{ display: 'flex', gap: 8 }}>
                <button
                    className="btn btn-primary btn-lg"
                    style={{ flex: 1 }}
                    onClick={onRun}
                    disabled={status === 'running'}
                >
                    {status === 'running' ? (
                        <>
                            <div className="loading-spinner" style={{ width: 14, height: 14 }} />
                            Running…
                        </>
                    ) : (
                        <>
                            <Play size={14} />
                            Run Attack
                        </>
                    )}
                </button>
                {status === 'running' && (
                    <button className="btn btn-danger" onClick={onCancel}>
                        <Square size={14} />
                    </button>
                )}
            </div>
        </div>
    );
}
