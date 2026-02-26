import React, { useMemo } from 'react';
import { BarChart3 } from 'lucide-react';
import Plot from 'react-plotly.js';

/**
 * Metrics Panel — live Plotly.js charts + summary metric cards.
 */
export default function MetricsPanel({ frames = [], result = null }) {
    // Build time-series data from frames
    const chartData = useMemo(() => {
        const iterations = [];
        const losses = [];
        const gradNorms = [];
        const confidences = [];

        frames.forEach((f) => {
            iterations.push(f.iteration ?? iterations.length);
            if (f.loss !== undefined && f.loss !== null) losses.push(f.loss);
            if (f.gradient_norm !== undefined && f.gradient_norm !== null) gradNorms.push(f.gradient_norm);
            if (f.prediction?.confidence !== undefined)
                confidences.push(f.prediction.confidence);
        });

        return { iterations, losses, gradNorms, confidences };
    }, [frames]);

    const metrics = result?.metrics || {};

    const plotLayout = {
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { family: 'Inter, sans-serif', color: '#94a3b8', size: 10 },
        margin: { t: 30, r: 10, b: 30, l: 40 },
        height: 160,
        xaxis: {
            gridcolor: 'rgba(255,255,255,0.04)',
            zerolinecolor: 'rgba(255,255,255,0.06)',
        },
        yaxis: {
            gridcolor: 'rgba(255,255,255,0.04)',
            zerolinecolor: 'rgba(255,255,255,0.06)',
        },
        showlegend: false,
    };

    const plotConfig = { displayModeBar: false, responsive: true };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {/* Summary Metrics */}
            <div className="card">
                <div className="card-header">
                    <div className="card-title">
                        <BarChart3 size={14} className="card-title-icon" />
                        Metrics
                    </div>
                    {result && (
                        <span className={`badge ${result.success ? 'badge-success' : 'badge-danger'}`}>
                            {result.success ? '✓ Attack Succeeded' : '✗ Attack Failed'}
                        </span>
                    )}
                </div>

                <div className="metrics-grid">
                    <div className="metric-card">
                        <span className="metric-label">L∞ Norm</span>
                        <span className="metric-value">{(metrics.linf_norm ?? 0).toFixed(4)}</span>
                    </div>
                    <div className="metric-card">
                        <span className="metric-label">L2 Norm</span>
                        <span className="metric-value">{(metrics.l2_norm ?? 0).toFixed(3)}</span>
                    </div>
                    <div className="metric-card">
                        <span className="metric-label">PSNR</span>
                        <span className="metric-value">{(metrics.psnr ?? 0).toFixed(1)}</span>
                        <span className="metric-unit">dB</span>
                    </div>
                    <div className="metric-card">
                        <span className="metric-label">SSIM</span>
                        <span className="metric-value">{(metrics.ssim ?? 0).toFixed(4)}</span>
                    </div>
                </div>

                {result && (
                    <div style={{ marginTop: 12, display: 'flex', gap: 12 }}>
                        <div className="metric-card" style={{ flex: 1 }}>
                            <span className="metric-label">Original</span>
                            <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--accent-green)' }}>
                                Class {result.original_label} ({(result.original_confidence * 100).toFixed(1)}%)
                            </span>
                        </div>
                        <div className="metric-card" style={{ flex: 1 }}>
                            <span className="metric-label">Adversarial</span>
                            <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--accent-red)' }}>
                                Class {result.adversarial_label} ({(result.adversarial_confidence * 100).toFixed(1)}%)
                            </span>
                        </div>
                    </div>
                )}
            </div>

            {/* Loss Curve */}
            {chartData.losses.length > 1 && (
                <div className="card" style={{ padding: 12 }}>
                    <div className="card-title" style={{ marginBottom: 8, fontSize: 12 }}>
                        Loss Curve
                    </div>
                    <Plot
                        data={[
                            {
                                x: chartData.iterations.slice(0, chartData.losses.length),
                                y: chartData.losses,
                                type: 'scatter',
                                mode: 'lines',
                                line: { color: '#06d6a0', width: 2 },
                                fill: 'tozeroy',
                                fillcolor: 'rgba(6, 214, 160, 0.05)',
                            },
                        ]}
                        layout={{ ...plotLayout, title: '' }}
                        config={plotConfig}
                        style={{ width: '100%' }}
                    />
                </div>
            )}

            {/* Confidence over iterations */}
            {chartData.confidences.length > 1 && (
                <div className="card" style={{ padding: 12 }}>
                    <div className="card-title" style={{ marginBottom: 8, fontSize: 12 }}>
                        Prediction Confidence
                    </div>
                    <Plot
                        data={[
                            {
                                x: chartData.iterations.slice(0, chartData.confidences.length),
                                y: chartData.confidences,
                                type: 'scatter',
                                mode: 'lines+markers',
                                line: { color: '#7c3aed', width: 2 },
                                marker: { size: 4 },
                            },
                        ]}
                        layout={{
                            ...plotLayout,
                            yaxis: { ...plotLayout.yaxis, range: [0, 1] },
                        }}
                        config={plotConfig}
                        style={{ width: '100%' }}
                    />
                </div>
            )}

            {/* Gradient Norms */}
            {chartData.gradNorms.length > 1 && (
                <div className="card" style={{ padding: 12 }}>
                    <div className="card-title" style={{ marginBottom: 8, fontSize: 12 }}>
                        Gradient Norm
                    </div>
                    <Plot
                        data={[
                            {
                                x: chartData.iterations.slice(0, chartData.gradNorms.length),
                                y: chartData.gradNorms,
                                type: 'bar',
                                marker: { color: 'rgba(59, 130, 246, 0.6)' },
                            },
                        ]}
                        layout={plotLayout}
                        config={plotConfig}
                        style={{ width: '100%' }}
                    />
                </div>
            )}

            {/* Elapsed time */}
            {result && (
                <div style={{ textAlign: 'center', fontSize: 11, color: 'var(--text-muted)', padding: 8 }}>
                    Completed in {result.elapsed_seconds.toFixed(2)}s • {result.total_iterations} iterations
                </div>
            )}
        </div>
    );
}
