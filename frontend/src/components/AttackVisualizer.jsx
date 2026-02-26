import React, { useState, useEffect, useMemo } from 'react';
import { Eye, Play, Pause, SkipBack, SkipForward, Maximize2 } from 'lucide-react';

/**
 * Step-by-step attack frame viewer with scrubber/timeline.
 */
export default function AttackVisualizer({
    frames = [],
    originalImage,
    status = 'idle',
}) {
    const [currentFrame, setCurrentFrame] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);
    const [viewMode, setViewMode] = useState('perturbed'); // perturbed | noise | side-by-side

    // Auto-advance to latest frame when running
    useEffect(() => {
        if (status === 'running' && frames.length > 0) {
            setCurrentFrame(frames.length - 1);
        }
    }, [frames.length, status]);

    // Playback timer
    useEffect(() => {
        if (!isPlaying || frames.length === 0) return;
        const timer = setInterval(() => {
            setCurrentFrame((prev) => {
                if (prev >= frames.length - 1) {
                    setIsPlaying(false);
                    return prev;
                }
                return prev + 1;
            });
        }, 200);
        return () => clearInterval(timer);
    }, [isPlaying, frames.length]);

    const frame = frames[currentFrame];
    const hasFrames = frames.length > 0;

    const currentPrediction = frame?.prediction || {};
    const currentMetrics = frame?.metrics || {};

    return (
        <div className="viz-container" style={{ flex: 1 }}>
            <div className="card-header" style={{ padding: '12px 16px', margin: 0 }}>
                <div className="card-title">
                    <Eye size={14} className="card-title-icon" />
                    Visualization
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <div className="tabs">
                        {['perturbed', 'noise', 'side-by-side'].map((mode) => (
                            <button
                                key={mode}
                                className={`tab ${viewMode === mode ? 'active' : ''}`}
                                onClick={() => setViewMode(mode)}
                            >
                                {mode === 'side-by-side' ? 'Compare' : mode.charAt(0).toUpperCase() + mode.slice(1)}
                            </button>
                        ))}
                    </div>
                    {status === 'running' && <div className="status-dot running" />}
                    {status === 'complete' && <div className="status-dot success" />}
                </div>
            </div>

            {/* Image Display */}
            <div className="viz-image-wrapper">
                {!hasFrames ? (
                    <div className="empty-state">
                        <div className="empty-state-icon">🎯</div>
                        <div className="empty-state-text">
                            {status === 'running'
                                ? 'Generating adversarial example…'
                                : 'Configure and run an attack to see results'}
                        </div>
                        {status === 'running' && <div className="loading-spinner" />}
                    </div>
                ) : viewMode === 'side-by-side' ? (
                    <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: 10, color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.1em' }}>Original</div>
                            {originalImage && (
                                <img
                                    src={`data:image/png;base64,${originalImage}`}
                                    alt="Original"
                                    className="viz-image"
                                    style={{ width: 200, height: 200 }}
                                />
                            )}
                        </div>
                        <div style={{ fontSize: 24, color: 'var(--text-muted)' }}>→</div>
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: 10, color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.1em' }}>
                                Iteration {frame?.iteration ?? 0}
                            </div>
                            {frame?.image_base64 && (
                                <img
                                    src={`data:image/png;base64,${frame.image_base64}`}
                                    alt="Adversarial"
                                    className="viz-image"
                                    style={{ width: 200, height: 200 }}
                                />
                            )}
                        </div>
                    </div>
                ) : viewMode === 'noise' ? (
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: 10, color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.1em' }}>
                            Perturbation (×10 amplified)
                        </div>
                        {frame?.noise_base64 ? (
                            <img
                                src={`data:image/png;base64,${frame.noise_base64}`}
                                alt="Noise"
                                className="viz-image"
                                style={{ width: 280, height: 280, filter: 'contrast(2)' }}
                            />
                        ) : frame?.image_base64 ? (
                            <img
                                src={`data:image/png;base64,${frame.image_base64}`}
                                alt="Current frame"
                                className="viz-image"
                                style={{ width: 280, height: 280 }}
                            />
                        ) : null}
                    </div>
                ) : (
                    <div style={{ textAlign: 'center' }}>
                        {frame?.image_base64 && (
                            <img
                                src={`data:image/png;base64,${frame.image_base64}`}
                                alt={`Frame ${currentFrame}`}
                                className="viz-image"
                                style={{ width: 280, height: 280 }}
                            />
                        )}
                        {currentPrediction.label !== undefined && (
                            <div style={{ marginTop: 10, fontSize: 12 }}>
                                <span style={{ color: 'var(--text-muted)' }}>Predicted: </span>
                                <span style={{ color: 'var(--accent-cyan)', fontWeight: 600, fontFamily: 'var(--font-mono)' }}>
                                    {currentPrediction.label}
                                </span>
                                <span style={{ color: 'var(--text-muted)', marginLeft: 8 }}>
                                    ({(currentPrediction.confidence * 100).toFixed(1)}%)
                                </span>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Scrubber Toolbar */}
            {hasFrames && (
                <div className="viz-toolbar">
                    <button
                        className="btn btn-icon btn-secondary btn-sm"
                        onClick={() => setCurrentFrame(0)}
                        disabled={currentFrame === 0}
                    >
                        <SkipBack size={14} />
                    </button>
                    <button
                        className="btn btn-icon btn-secondary btn-sm"
                        onClick={() => setIsPlaying(!isPlaying)}
                    >
                        {isPlaying ? <Pause size={14} /> : <Play size={14} />}
                    </button>
                    <button
                        className="btn btn-icon btn-secondary btn-sm"
                        onClick={() => setCurrentFrame(frames.length - 1)}
                        disabled={currentFrame === frames.length - 1}
                    >
                        <SkipForward size={14} />
                    </button>
                    <div className="viz-scrubber scrubber-container">
                        <span className="scrubber-label">{currentFrame}</span>
                        <input
                            type="range"
                            min={0}
                            max={Math.max(frames.length - 1, 0)}
                            value={currentFrame}
                            onChange={(e) => {
                                setCurrentFrame(parseInt(e.target.value));
                                setIsPlaying(false);
                            }}
                            style={{ flex: 1 }}
                        />
                        <span className="scrubber-label">{frames.length - 1}</span>
                    </div>
                </div>
            )}
        </div>
    );
}
