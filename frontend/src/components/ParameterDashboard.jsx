import React, { useState } from 'react';
import { SlidersHorizontal, Plus, Trash2 } from 'lucide-react';

/**
 * Parameter Dashboard — renders sliders for built-in attacks
 * AND supports user-defined custom parameters.
 */
export default function ParameterDashboard({
    attackType,
    attackParams = [],
    params = {},
    onParamChange,
    customParams = [],
    onCustomParamsChange,
}) {
    const [newParamName, setNewParamName] = useState('');

    const handleSliderChange = (name, value, type) => {
        const parsed = type === 'int' ? parseInt(value) : parseFloat(value);
        onParamChange({ ...params, [name]: parsed });
    };

    const handleBoolChange = (name, value) => {
        onParamChange({ ...params, [name]: value });
    };

    const addCustomParam = () => {
        if (!newParamName.trim()) return;
        const newParam = {
            name: newParamName.trim().toLowerCase().replace(/\s+/g, '_'),
            label: newParamName.trim(),
            type: 'float',
            min: 0,
            max: 1,
            step: 0.01,
            default: 0.5,
        };
        onCustomParamsChange([...customParams, newParam]);
        onParamChange({ ...params, [newParam.name]: newParam.default });
        setNewParamName('');
    };

    const removeCustomParam = (idx) => {
        const removed = customParams[idx];
        const newCustom = customParams.filter((_, i) => i !== idx);
        const newParams = { ...params };
        delete newParams[removed.name];
        onCustomParamsChange(newCustom);
        onParamChange(newParams);
    };

    const allParams = [...attackParams, ...customParams];

    return (
        <div className="card">
            <div className="card-header">
                <div className="card-title">
                    <SlidersHorizontal size={14} className="card-title-icon" />
                    Parameters
                </div>
                {attackType && (
                    <span className="badge badge-info">{attackType.toUpperCase()}</span>
                )}
            </div>

            {allParams.length === 0 && !attackType && (
                <div className="empty-state" style={{ padding: '20px 10px' }}>
                    <span className="empty-state-text">Select an attack to configure parameters</span>
                </div>
            )}

            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                {allParams.map((p, idx) => {
                    if (p.type === 'bool') {
                        return (
                            <div key={p.name} className="slider-group">
                                <div className="slider-header">
                                    <span className="slider-label">{p.label || p.name}</span>
                                    <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                                        <input
                                            type="checkbox"
                                            checked={params[p.name] ?? p.default ?? false}
                                            onChange={(e) => handleBoolChange(p.name, e.target.checked)}
                                            style={{ accentColor: 'var(--accent-cyan)' }}
                                        />
                                        <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                                            {params[p.name] ? 'On' : 'Off'}
                                        </span>
                                    </label>
                                </div>
                            </div>
                        );
                    }

                    const value = params[p.name] ?? p.default ?? 0;
                    const isCustom = idx >= attackParams.length;

                    return (
                        <div key={p.name} className="slider-group">
                            <div className="slider-header">
                                <span className="slider-label">
                                    {p.label || p.name}
                                    {isCustom && (
                                        <button
                                            className="btn btn-icon"
                                            style={{ marginLeft: 6, padding: 2 }}
                                            onClick={() => removeCustomParam(idx - attackParams.length)}
                                        >
                                            <Trash2 size={10} color="var(--accent-red)" />
                                        </button>
                                    )}
                                </span>
                                <span className="slider-value">
                                    {p.type === 'int' ? Math.round(value) : value.toFixed(p.step < 0.01 ? 4 : p.step < 0.1 ? 3 : 2)}
                                </span>
                            </div>
                            <input
                                type="range"
                                min={p.min ?? 0}
                                max={p.max ?? 1}
                                step={p.step ?? 0.01}
                                value={value}
                                onChange={(e) => handleSliderChange(p.name, e.target.value, p.type)}
                            />
                        </div>
                    );
                })}
            </div>

            {/* Custom Parameter Addition */}
            <div style={{ marginTop: 16, paddingTop: 12, borderTop: '1px solid var(--border-subtle)' }}>
                <label className="form-label" style={{ marginBottom: 6 }}>
                    <Plus size={10} style={{ marginRight: 4 }} />
                    Add Custom Parameter
                </label>
                <div style={{ display: 'flex', gap: 6 }}>
                    <input
                        className="form-input"
                        placeholder="Parameter name"
                        value={newParamName}
                        onChange={(e) => setNewParamName(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && addCustomParam()}
                        style={{ flex: 1, fontSize: 12 }}
                    />
                    <button className="btn btn-secondary btn-sm" onClick={addCustomParam}>
                        <Plus size={12} /> Add
                    </button>
                </div>
            </div>
        </div>
    );
}
