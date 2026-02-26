import React from 'react';
import Editor from '@monaco-editor/react';
import { Code2 } from 'lucide-react';

const DEFAULT_TEMPLATE = `# ═══════════════════════════════════════════════════
# Custom Adversarial Attack
# ═══════════════════════════════════════════════════
# Available variables:
#   classifier  - ART PyTorchClassifier (wrapped model)
#   model       - Raw PyTorch model
#   image       - Input image as numpy array (C, H, W)
#   x           - Input image as batch (1, C, H, W)
#   true_label  - Ground truth label (int)
#   original_prediction - Model prediction array
#   params      - Dict of your custom parameters
#
# Available functions:
#   report_iteration(iteration, image=, loss=, metrics=, prediction=)
#     → Call this to stream intermediate results to the visualizer
#
# Set 'result' variable to your final adversarial image (numpy array)
# ═══════════════════════════════════════════════════

import numpy as np

# Get parameters (these can be customized via the UI)
eps = params.get('eps', 0.3)
num_iterations = int(params.get('num_iterations', 10))

# Your custom attack logic here
x_adv = x.copy()

for i in range(num_iterations):
    # === Replace with your attack algorithm ===
    noise = np.random.uniform(-eps, eps, x.shape).astype(np.float32)
    x_adv = np.clip(x + noise, 0.0, 1.0)
    
    # Get current prediction
    preds = classifier.predict(x_adv)
    pred_label = int(np.argmax(preds[0]))
    pred_conf = float(np.max(preds[0]))
    
    # Report this iteration to the visualizer
    report_iteration(
        iteration=i,
        image=x_adv[0],
        loss=float(1.0 - pred_conf),
        prediction={"label": pred_label, "confidence": pred_conf},
        metrics={"linf": float(np.max(np.abs(x_adv - x)))}
    )
    
    # Check if attack succeeded
    if pred_label != true_label:
        print(f"Attack succeeded at iteration {i}!")
        break

# Set result to final adversarial image
result = x_adv
print(f"Final prediction: {pred_label} (conf: {pred_conf:.3f})")
`;

export default function CodeEditor({
    code,
    onCodeChange,
    onRun,
    running = false,
    output = '',
}) {
    return (
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div className="card-header" style={{ margin: 0 }}>
                <div className="card-title">
                    <Code2 size={14} className="card-title-icon" />
                    Custom Attack Code
                </div>
                <button
                    className="btn btn-primary btn-sm"
                    onClick={onRun}
                    disabled={running}
                >
                    {running ? (
                        <>
                            <div className="loading-spinner" style={{ width: 12, height: 12 }} />
                            Running…
                        </>
                    ) : (
                        <>▶ Run Attack</>
                    )}
                </button>
            </div>

            <div className="editor-container">
                <Editor
                    height="400px"
                    defaultLanguage="python"
                    value={code || DEFAULT_TEMPLATE}
                    onChange={(val) => onCodeChange(val)}
                    theme="vs-dark"
                    options={{
                        minimap: { enabled: false },
                        fontSize: 13,
                        fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
                        lineNumbers: 'on',
                        scrollBeyondLastLine: false,
                        wordWrap: 'on',
                        padding: { top: 12 },
                        smoothScrolling: true,
                        cursorBlinking: 'smooth',
                        renderLineHighlight: 'all',
                        bracketPairColorization: { enabled: true },
                    }}
                />
            </div>

            {output && (
                <div>
                    <label className="form-label" style={{ marginBottom: 6 }}>Output</label>
                    <div className="log-output">
                        {output.split('\n').map((line, i) => (
                            <div
                                key={i}
                                className={
                                    line.includes('Error') || line.includes('error')
                                        ? 'log-line-error'
                                        : line.includes('succeeded') || line.includes('Success')
                                            ? 'log-line-success'
                                            : ''
                                }
                            >
                                {line}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

export { DEFAULT_TEMPLATE };
