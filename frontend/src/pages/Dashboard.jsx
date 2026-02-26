import React, { useState, useEffect, useCallback } from 'react';
import DatasetNavigator from '../components/DatasetNavigator';
import ModelSelector from '../components/ModelSelector';
import AttackControls from '../components/AttackControls';
import ParameterDashboard from '../components/ParameterDashboard';
import AttackVisualizer from '../components/AttackVisualizer';
import MetricsPanel from '../components/MetricsPanel';
import ImageComparison from '../components/ImageComparison';
import CodeEditor, { DEFAULT_TEMPLATE } from '../components/CodeEditor';
import useAttackWebSocket from '../hooks/useAttackWebSocket';
import { fetchDatasets, fetchDatasetInfo, fetchModels, fetchAttacks, runAttack, runCustomAttack } from '../utils/api';

export default function Dashboard() {
    // Data
    const [datasets, setDatasets] = useState([]);
    const [models, setModels] = useState([]);
    const [attacks, setAttacks] = useState([]);

    // Selections
    const [selectedDataset, setSelectedDataset] = useState('mnist');
    const [selectedModel, setSelectedModel] = useState('simple_cnn_mnist');
    const [selectedAttack, setSelectedAttack] = useState('fgsm');
    const [sampleIndex, setSampleIndex] = useState(0);
    const [samples, setSamples] = useState([]);

    // Parameters
    const [params, setParams] = useState({});
    const [customParams, setCustomParams] = useState([]);

    // Mode
    const [mode, setMode] = useState('builtin');
    const [customCode, setCustomCode] = useState(DEFAULT_TEMPLATE);

    // Attack state
    const [status, setStatus] = useState('idle');
    const [frames, setFrames] = useState([]);
    const [result, setResult] = useState(null);
    const [output, setOutput] = useState('');
    const [loadingData, setLoadingData] = useState(false);

    // Load initial data
    useEffect(() => {
        const loadData = async () => {
            setLoadingData(true);
            try {
                const [ds, ms, atks] = await Promise.all([
                    fetchDatasets().catch(() => []),
                    fetchModels().catch(() => []),
                    fetchAttacks().catch(() => []),
                ]);
                setDatasets(ds);
                setModels(ms);
                setAttacks(atks);
            } catch (err) {
                console.error('Failed to load initial data:', err);
            }
            setLoadingData(false);
        };
        loadData();
    }, []);

    // Load samples when dataset changes
    useEffect(() => {
        if (!selectedDataset) return;
        fetchDatasetInfo(selectedDataset)
            .then((info) => setSamples(info.sample_images || []))
            .catch(() => setSamples([]));
    }, [selectedDataset]);

    // Set default params when attack changes
    useEffect(() => {
        const attack = attacks.find((a) => a.name === selectedAttack);
        if (attack) {
            const defaults = {};
            attack.params.forEach((p) => {
                defaults[p.name] = p.default;
            });
            setParams(defaults);
        }
    }, [selectedAttack, attacks]);

    // Get current attack param definitions
    const currentAttackInfo = attacks.find((a) => a.name === selectedAttack);
    const attackParamDefs = currentAttackInfo?.params || [];

    // Run attack
    const handleRunAttack = useCallback(async () => {
        setStatus('running');
        setFrames([]);
        setResult(null);
        setOutput('');

        try {
            let res;
            if (mode === 'custom') {
                res = await runCustomAttack({
                    code: customCode,
                    dataset: selectedDataset,
                    model: selectedModel,
                    sample_index: sampleIndex,
                    params: params,
                    custom_params: customParams,
                });
            } else {
                res = await runAttack({
                    attack_type: selectedAttack,
                    dataset: selectedDataset,
                    model: selectedModel,
                    sample_index: sampleIndex,
                    params: params,
                    targeted: params.targeted || false,
                });
            }

            setFrames(res.frames || []);
            setResult(res);
            setStatus('complete');
        } catch (err) {
            console.error('Attack failed:', err);
            setOutput(`Error: ${err.response?.data?.detail || err.message}`);
            setStatus('error');
        }
    }, [mode, customCode, selectedAttack, selectedDataset, selectedModel, sampleIndex, params, customParams]);

    const originalImage = result?.original_image_base64 ||
        (samples.length > sampleIndex ? samples[sampleIndex] : null);

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1 className="page-title">Attack Laboratory</h1>
                    <p className="page-subtitle">
                        Design, execute, and analyze adversarial attacks in real-time
                    </p>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <div className={`status-dot ${status}`} />
                    <span style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'capitalize' }}>
                        {status}
                    </span>
                </div>
            </div>

            <div className="dashboard-grid">
                {/* Left Panel — Config */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 0, overflowY: 'auto' }}>
                    <DatasetNavigator
                        datasets={datasets}
                        selectedDataset={selectedDataset}
                        onSelectDataset={setSelectedDataset}
                        samples={samples}
                        selectedSampleIndex={sampleIndex}
                        onSelectSample={setSampleIndex}
                        loading={loadingData}
                    />

                    <ModelSelector
                        models={models}
                        selectedModel={selectedModel}
                        onSelectModel={setSelectedModel}
                    />

                    <AttackControls
                        attacks={attacks}
                        selectedAttack={selectedAttack}
                        onSelectAttack={setSelectedAttack}
                        onRun={handleRunAttack}
                        onCancel={() => setStatus('idle')}
                        status={status}
                        mode={mode}
                        onModeChange={setMode}
                    />

                    <ParameterDashboard
                        attackType={mode === 'builtin' ? selectedAttack : 'custom'}
                        attackParams={mode === 'builtin' ? attackParamDefs : []}
                        params={params}
                        onParamChange={setParams}
                        customParams={customParams}
                        onCustomParamsChange={setCustomParams}
                    />
                </div>

                {/* Center — Visualization */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12, overflow: 'auto' }}>
                    {mode === 'custom' && (
                        <CodeEditor
                            code={customCode}
                            onCodeChange={setCustomCode}
                            onRun={handleRunAttack}
                            running={status === 'running'}
                            output={output}
                        />
                    )}

                    <AttackVisualizer
                        frames={frames}
                        originalImage={originalImage}
                        status={status}
                    />

                    {result && (
                        <ImageComparison
                            originalBase64={result.original_image_base64}
                            adversarialBase64={result.adversarial_image_base64}
                        />
                    )}
                </div>

                {/* Right Panel — Metrics */}
                <div style={{ overflowY: 'auto' }}>
                    <MetricsPanel frames={frames} result={result} />
                </div>
            </div>
        </div>
    );
}
