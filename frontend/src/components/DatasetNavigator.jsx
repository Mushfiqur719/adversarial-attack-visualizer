import React from 'react';
import { Database, ImageIcon } from 'lucide-react';

export default function DatasetNavigator({
    datasets = [],
    selectedDataset,
    onSelectDataset,
    samples = [],
    selectedSampleIndex,
    onSelectSample,
    loading = false,
}) {
    return (
        <div className="card" style={{ marginBottom: 12 }}>
            <div className="card-header">
                <div className="card-title">
                    <Database size={14} className="card-title-icon" />
                    Dataset
                </div>
            </div>

            <div className="form-group" style={{ marginBottom: 12 }}>
                <label className="form-label">Select Dataset</label>
                <select
                    className="form-select"
                    value={selectedDataset || ''}
                    onChange={(e) => onSelectDataset(e.target.value)}
                >
                    <option value="">Choose dataset…</option>
                    {datasets.map((ds) => (
                        <option key={ds.name} value={ds.name}>
                            {ds.display_name}
                        </option>
                    ))}
                </select>
            </div>

            {samples.length > 0 && (
                <>
                    <label className="form-label" style={{ marginBottom: 6 }}>
                        <ImageIcon size={11} style={{ marginRight: 4 }} />
                        Select Sample (#{selectedSampleIndex})
                    </label>
                    <div className="image-grid">
                        {samples.map((b64, idx) => (
                            <div
                                key={idx}
                                className={`image-grid-item ${idx === selectedSampleIndex ? 'selected' : ''}`}
                                onClick={() => onSelectSample(idx)}
                            >
                                <img
                                    src={`data:image/png;base64,${b64}`}
                                    alt={`Sample ${idx}`}
                                />
                            </div>
                        ))}
                    </div>
                </>
            )}

            {loading && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 10 }}>
                    <div className="loading-spinner" />
                    <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Loading dataset…</span>
                </div>
            )}
        </div>
    );
}
