import React, { useState } from 'react';
import CodeEditor, { DEFAULT_TEMPLATE } from '../components/CodeEditor';
import { runSandbox } from '../utils/api';
import { Code2, Terminal } from 'lucide-react';

export default function Sandbox() {
    const [code, setCode] = useState(DEFAULT_TEMPLATE);
    const [running, setRunning] = useState(false);
    const [output, setOutput] = useState('');
    const [result, setResult] = useState(null);

    const handleRun = async () => {
        setRunning(true);
        setOutput('');
        setResult(null);
        try {
            const res = await runSandbox(code, 60);
            setResult(res);
            let combinedOutput = '';
            if (res.stdout) combinedOutput += res.stdout;
            if (res.stderr) combinedOutput += '\n' + res.stderr;
            setOutput(combinedOutput.trim());
        } catch (err) {
            setOutput(`Error: ${err.response?.data?.detail || err.message}`);
        }
        setRunning(false);
    };

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1 className="page-title">Code Sandbox</h1>
                    <p className="page-subtitle">
                        Write and test custom adversarial attack algorithms
                    </p>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: 20 }}>
                <CodeEditor
                    code={code}
                    onCodeChange={setCode}
                    onRun={handleRun}
                    running={running}
                    output={output}
                />

                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                    <div className="card">
                        <div className="card-header">
                            <div className="card-title">
                                <Terminal size={14} className="card-title-icon" />
                                Execution Info
                            </div>
                        </div>
                        {result ? (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: 13 }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <span style={{ color: 'var(--text-muted)' }}>Status</span>
                                    <span className={`badge ${result.success ? 'badge-success' : 'badge-danger'}`}>
                                        {result.success ? 'Success' : 'Failed'}
                                    </span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <span style={{ color: 'var(--text-muted)' }}>Elapsed</span>
                                    <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)' }}>
                                        {result.elapsed_seconds.toFixed(3)}s
                                    </span>
                                </div>
                            </div>
                        ) : (
                            <div className="empty-state" style={{ padding: 20 }}>
                                <Code2 size={24} style={{ opacity: 0.3 }} />
                                <span className="empty-state-text">Run code to see results</span>
                            </div>
                        )}
                    </div>

                    <div className="card">
                        <div className="card-title" style={{ marginBottom: 12 }}>
                            📖 Quick Reference
                        </div>
                        <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.8 }}>
                            <div><code style={{ color: 'var(--accent-cyan)' }}>classifier</code> — ART PyTorchClassifier</div>
                            <div><code style={{ color: 'var(--accent-cyan)' }}>model</code> — Raw PyTorch model</div>
                            <div><code style={{ color: 'var(--accent-cyan)' }}>image</code> — Input (C,H,W) numpy</div>
                            <div><code style={{ color: 'var(--accent-cyan)' }}>x</code> — Batched input (1,C,H,W)</div>
                            <div><code style={{ color: 'var(--accent-cyan)' }}>true_label</code> — Ground truth int</div>
                            <div><code style={{ color: 'var(--accent-cyan)' }}>params</code> — Custom parameters dict</div>
                            <div style={{ marginTop: 8, borderTop: '1px solid var(--border-subtle)', paddingTop: 8 }}>
                                <code style={{ color: 'var(--accent-purple)' }}>report_iteration()</code> — Stream results
                            </div>
                            <div>
                                <code style={{ color: 'var(--accent-purple)' }}>result</code> — Set to final adversarial image
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
