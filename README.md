# Adversarial ML Visualization & Evaluation Platform

A **research-oriented** full-stack web platform for **designing, testing, and benchmarking adversarial attack algorithms**. Built-in ART attacks serve as baselines; the core purpose is enabling researchers to write and evaluate novel attack algorithms with real-time visualization.

## Architecture

```
backend/    → FastAPI + ART (Python)
frontend/   → React + Vite (JavaScript)
```

## Quick Start

### Prerequisites
- **Python 3.10+** with pip
- **Node.js 18+** with npm
- **CUDA** (optional, for GPU acceleration)

### Backend Setup
```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Open **http://localhost:5173** in your browser.

## Features

- **5 Built-in Evasion Attacks**: FGSM, PGD, C&W, DeepFool, Square Attack (via ART)
- **Custom Attack Code Editor**: Monaco Editor with `report_iteration()` API for streaming results
- **Real-time Visualization**: Step-by-step frame playback with scrubber timeline
- **Metrics Dashboard**: L₀/L₂/L∞ norms, PSNR, SSIM, confidence tracking
- **Image Comparison**: Before/after slider for pixel-level inspection
- **Live Charts**: Plotly.js loss curves, gradient norms, confidence decay
- **CUDA Support**: Auto-detects GPU for accelerated attacks

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, ART 1.18, PyTorch |
| Frontend | React 18, Vite, Plotly.js |
| Code Editor | Monaco Editor |
| Image Compare | react-compare-slider |
| Communication | WebSocket + REST |

## Project Structure

```
attack-visualizer/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Settings (CUDA, paths)
│   │   ├── core/
│   │   │   ├── schemas.py       # Pydantic models
│   │   │   └── summary_writer.py # ART frame capture
│   │   ├── routers/             # API endpoints
│   │   ├── services/            # Business logic
│   │   └── ws/                  # WebSocket handlers
│   ├── requirements.txt
│   └── .gitignore
├── frontend/
│   ├── src/
│   │   ├── components/          # React UI components
│   │   ├── pages/               # Dashboard, Sandbox, Benchmark
│   │   ├── hooks/               # WebSocket hook
│   │   └── utils/               # API client
│   ├── package.json
│   └── .gitignore
├── .gitignore
└── README.md
```

## License

MIT
