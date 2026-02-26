import axios from 'axios';

const api = axios.create({
    baseURL: '/api',
    timeout: 120000,
    headers: { 'Content-Type': 'application/json' },
});

// ── Datasets ──────────────────────────────────────────────────────────────────
export const fetchDatasets = () => api.get('/datasets/').then(r => r.data);
export const fetchDatasetInfo = (name) => api.get(`/datasets/${name}`).then(r => r.data);
export const fetchSample = (dataset, index) =>
    api.get(`/datasets/${dataset}/sample/${index}`).then(r => r.data);

// ── Models ────────────────────────────────────────────────────────────────────
export const fetchModels = () => api.get('/models/').then(r => r.data);
export const fetchModelInfo = (name) => api.get(`/models/${name}`).then(r => r.data);

// ── Attacks ───────────────────────────────────────────────────────────────────
export const fetchAttacks = () => api.get('/attacks/').then(r => r.data);
export const runAttack = (config) => api.post('/attacks/run', config).then(r => r.data);
export const runCustomAttack = (config) => api.post('/attacks/run-custom', config).then(r => r.data);

// ── Metrics ───────────────────────────────────────────────────────────────────
export const fetchMetricsInfo = () => api.get('/metrics/').then(r => r.data);

// ── Sandbox ───────────────────────────────────────────────────────────────────
export const runSandbox = (code, timeout = 60) =>
    api.post('/sandbox/run', { code, timeout }).then(r => r.data);

// ── Health ────────────────────────────────────────────────────────────────────
export const checkHealth = () => api.get('/health').then(r => r.data);

export default api;
