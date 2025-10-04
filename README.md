# GreenHeart.ai 🌱

An AI-powered agriculture assistant API that helps farmers and gardeners identify plant diseases and recommend optimal crops for their specific conditions.

## Project Overview

GreenHeart.ai provides two main features exposed as REST endpoints:

- Leaf Disease Analyzer — analyze a leaf image (YOLOv8/OpenCV) and return detected issues, an annotated image, and recommendations.
- Crop Recommendation System — take soil and environmental sensor data and return personalized crop recommendations (uses Google Generative AI).

This repository contains a FastAPI application (`app.py`) and utility modules in `utils/` that perform inference, prompt building, and sensor-data formatting.

## Quickstart — run locally (Windows)

These steps get the API running on your Windows machine (cmd.exe / PowerShell). The project already includes a virtual environment under the `greenheart/` folder in this repo; you can either use that or create a fresh one.

1) (Optional) Create a new venv (recommended) and activate it (cmd):

```bat
python -m venv .venv
.\.venv\Scripts\activate
```

PowerShell activate:

```powershell
.\.venv\Scripts\Activate.ps1
```

If you want to use the included virtualenv inside `greenheart/`, activate:

```bat
.\greenheart\Scripts\activate
```

2) Install Python dependencies (from repo root):

```bat
pip install -r requirements.txt
```

Note: Some dependencies (torch, ultralytics) are large. If you have a GPU-enabled system you may want to install a CUDA-enabled PyTorch wheel per PyTorch's instructions.

3) Create a `.env` with your Google Generative API key:

```text
GOOGLE_API_KEY=your_api_key_here
```

Important: do not commit your `.env` or secrets to git. Rotate the key if it was accidentally exposed.

4) Run the server (development):

```bat
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The interactive documentation will be available at: http://localhost:8000/docs

If you prefer the Docker route, see the Docker section below.

## Endpoints (current)

The running API exposes these main endpoints:

- GET / — basic welcome
- GET /health — health check
- POST /api/v1/analyze-leaf — upload a leaf image (multipart/form-data) and receive analysis and an annotated image (base64)
- POST /api/v1/recommend-crops — send sensor data (JSON) and receive crop recommendations
- GET /favicon.ico — favicon route (present but minimal)

Example curl (Windows cmd.exe):

```bat
curl -X GET "http://localhost:8000/health" -H "accept: application/json"
```

Example analyze (replace `<image.jpg>` with a path):

```bat
curl -X POST "http://localhost:8000/api/v1/analyze-leaf" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@<image.jpg>"
```

Example recommend-crops payload (save as `payload.json` and post):

```bat
curl -X POST "http://localhost:8000/api/v1/recommend-crops" -H "Content-Type: application/json" -d @payload.json
```

## Docker

The `Dockerfile` builds a container and starts Uvicorn on port 8080 by default. Build and run (Linux/macOS or Docker Desktop on Windows):

```bash
docker build -t greenheart.ai:latest .
docker run -p 8080:8080 --env-file .env greenheart.ai:latest
```

When running in Docker the server listens on port 8080 (as defined in the `Dockerfile`).

## Using the included `cors_test.html`

Open `cors_test.html` in your browser and enter your API URL (e.g. `http://localhost:8000`) when prompted. It has three quick tests for health, crop recommendation, and leaf analysis.

## Files of interest

- `app.py` — main FastAPI application (this is the module you should point Uvicorn at: `app:app`).
- `requirements.txt` — Python dependencies.
- `models/model.pt` — trained YOLOv8 model used by `utils/inference.py` (keep this file present if you want local inference).
- `utils/` — utility modules (inference, prompt building, sensor formatting, response formatting).

## Environment variables

- `GOOGLE_API_KEY` — required by the Google Generative AI calls. Put it in `.env` or your environment.

## Troubleshooting

- ModuleNotFoundError: No module named 'fastapi'
  - Activate the appropriate virtual environment and run: `pip install -r requirements.txt`.

- Uvicorn reload/reloader issues on Windows
  - If the auto-reloader causes issues, try running without `--reload` or run via: `python -m uvicorn app:app --host 0.0.0.0 --port 8000`.

- GPU / Torch
  - If you rely on CUDA/GPU for `torch`, install the appropriate wheel for your CUDA version before installing the rest of `requirements.txt`.

## Security note

The `.env` in this repository currently contains a Google API key. If that key is real, rotate it immediately and remove the key from any shared or public place. Keep `.env` in `.gitignore` (already present).

## Contributing

Contributions welcome — open an issue or submit a pull request. For larger changes, please open an issue first to discuss design and testing strategy.

## License

This project is released under the MIT License. See `LICENSE` for details.

## Acknowledgments

- Dataset contributors
- PyTorch, FastAPI, Ultralytics, and Google Generative AI communities
