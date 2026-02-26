import { useRef, useState, useCallback } from 'react';

/**
 * Custom hook for WebSocket-based attack streaming.
 * Manages connection, frame buffering, and status.
 */
export default function useAttackWebSocket() {
    const wsRef = useRef(null);
    const [status, setStatus] = useState('idle'); // idle | connecting | running | complete | error
    const [frames, setFrames] = useState([]);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const connect = useCallback(() => {
        return new Promise((resolve, reject) => {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/attack`;

            const ws = new WebSocket(wsUrl);
            wsRef.current = ws;
            setStatus('connecting');
            setFrames([]);
            setResult(null);
            setError(null);

            ws.onopen = () => {
                setStatus('connected');
                resolve(ws);
            };

            ws.onmessage = (event) => {
                const msg = JSON.parse(event.data);

                switch (msg.type) {
                    case 'started':
                        setStatus('running');
                        break;
                    case 'frame':
                        setFrames(prev => [...prev, msg.data]);
                        break;
                    case 'complete':
                        setStatus('complete');
                        setResult(msg.data);
                        break;
                    case 'error':
                        setStatus('error');
                        setError(msg.message);
                        break;
                    case 'pong':
                        break;
                    default:
                        console.log('Unknown WS message:', msg);
                }
            };

            ws.onerror = (err) => {
                setStatus('error');
                setError('WebSocket connection failed');
                reject(err);
            };

            ws.onclose = () => {
                if (status === 'running') {
                    setStatus('error');
                    setError('Connection closed unexpectedly');
                }
            };
        });
    }, []);

    const send = useCallback((data) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(data));
        }
    }, []);

    const runAttack = useCallback(async (config) => {
        try {
            let ws = wsRef.current;
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                ws = await connect();
            }
            setStatus('running');
            setFrames([]);
            setResult(null);
            setError(null);
            ws.send(JSON.stringify(config));
        } catch (err) {
            setStatus('error');
            setError(err.message);
        }
    }, [connect]);

    const disconnect = useCallback(() => {
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
        setStatus('idle');
    }, []);

    const reset = useCallback(() => {
        setFrames([]);
        setResult(null);
        setError(null);
        setStatus('idle');
    }, []);

    return {
        status,
        frames,
        result,
        error,
        connect,
        send,
        runAttack,
        disconnect,
        reset,
    };
}
