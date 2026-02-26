import React from 'react';
import { Activity, Construction } from 'lucide-react';

export default function Benchmark() {
    return (
        <div>
            <div className="page-header">
                <div>
                    <h1 className="page-title">Benchmark</h1>
                    <p className="page-subtitle">
                        Compare attack performance across methods and parameters
                    </p>
                </div>
            </div>

            <div className="card" style={{ maxWidth: 600, margin: '60px auto', textAlign: 'center' }}>
                <div className="empty-state">
                    <Construction size={48} style={{ color: 'var(--accent-purple)', opacity: 0.5 }} />
                    <h3 style={{ fontSize: 18, fontWeight: 600, color: 'var(--text-primary)' }}>
                        Coming Soon
                    </h3>
                    <p style={{ color: 'var(--text-secondary)', fontSize: 13, maxWidth: 400, lineHeight: 1.6 }}>
                        The benchmarking dashboard will allow you to run batch experiments,
                        compare multiple attack algorithms side-by-side, and generate
                        publication-ready performance tables with L<sub>p</sub> norms, PSNR,
                        SSIM, and success rates.
                    </p>
                    <div className="metrics-grid" style={{ marginTop: 20, maxWidth: 400 }}>
                        <div className="metric-card">
                            <span className="metric-label">Attacks</span>
                            <span className="metric-value">5</span>
                            <span className="metric-unit">built-in</span>
                        </div>
                        <div className="metric-card">
                            <span className="metric-label">Metrics</span>
                            <span className="metric-value">6</span>
                            <span className="metric-unit">tracked</span>
                        </div>
                        <div className="metric-card">
                            <span className="metric-label">Status</span>
                            <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--accent-orange)' }}>Phase 2</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
