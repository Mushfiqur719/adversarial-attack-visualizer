import React from 'react';
import { Cpu } from 'lucide-react';

export default function ModelSelector({
    models = [],
    selectedModel,
    onSelectModel,
}) {
    const selectedInfo = models.find((m) => m.name === selectedModel);

    return (
        <div className="card" style={{ marginBottom: 12 }}>
            <div className="card-header">
                <div className="card-title">
                    <Cpu size={14} className="card-title-icon" />
                    Model
                </div>
            </div>

            <div className="form-group">
                <label className="form-label">Target Model</label>
                <select
                    className="form-select"
                    value={selectedModel || ''}
                    onChange={(e) => onSelectModel(e.target.value)}
                >
                    <option value="">Choose model…</option>
                    {models.map((m) => (
                        <option key={m.name} value={m.name}>
                            {m.display_name}
                        </option>
                    ))}
                </select>
            </div>

            {selectedInfo && (
                <div style={{ marginTop: 10, fontSize: 12 }}>
                    <div style={{ color: 'var(--text-muted)', marginBottom: 4 }}>Architecture</div>
                    <div style={{ color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)', fontSize: 11 }}>
                        {selectedInfo.architecture}
                    </div>
                    {selectedInfo.num_parameters && (
                        <div style={{ color: 'var(--text-muted)', marginTop: 6 }}>
                            Parameters: <span style={{ color: 'var(--accent-cyan)' }}>
                                {(selectedInfo.num_parameters / 1e6).toFixed(1)}M
                            </span>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
