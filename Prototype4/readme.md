# Prototype4: Plug-and-Play Accent Mapper

Prototype4 is a full-stack prototype for Irish accent/province prediction from audio.
It includes:

- A FastAPI backend with plugin-based models
- A browser frontend for recording/uploading audio and viewing results
- Map highlighting, prediction history, and user feedback capture

## Project Structure

```text
Prototype4/
  backend/
    app.py                   # FastAPI app + routes
    plugin_loader.py         # Registers model plugins
    registry.py              # In-memory model registry
    plugins/
      dummy_model.py         # Deterministic test model
      mfcc_logreg_v1_01.py   # MFCC + Logistic Regression model plugin
    services/
      audio.py               # Audio decode/normalize/resample helpers
      features.py            # MFCC feature extraction
    artifacts/               # Trained model artifacts (.joblib)
    requirements.txt
  frontend/
    index.html
    app.js
    api.js
    recording.js
    predictions.js
    map.js
    store.js
    style.css
    data/provinces.geojson
  testing/
    SystemTests.xlsx
```

## Requirements

- Python 3.10+ (3.11/3.12 recommended)
- `pip`
- `ffmpeg` recommended (used as robust fallback for audio conversion)

## Quick Start

1. Open a terminal and go to backend:

```bash
cd /Users/cianan/Documents/College/GitHub/FYP/Prototype4/backend
```

2. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the server:

```bash
uvicorn app:app --reload
```

5. Open in browser:

- App: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Health: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)
- Models: [http://127.0.0.1:8000/api/models](http://127.0.0.1:8000/api/models)
- API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## How to Use the UI

1. Select a model from the dropdown.
2. Record audio (minimum 10 seconds) or upload an audio file.
3. Click `Predict Accent`.
4. Review:
   - Current prediction and confidence
   - Class probability breakdown
   - Map highlight
   - Prediction history
5. Provide feedback:
   - `Yes` if correct
   - `No` and choose the correct province if incorrect

## API Endpoints

### `GET /api/health`

Returns service status.

Example response:

```json
{
  "status": "ok"
}
```

### `GET /api/models`

Returns registered model metadata.

Example response:

```json
{
  "models": [
    {
      "id": "dummy_v1",
      "name": "Dummy Model (v1)",
      "description": "Test model for end-to-end frontend/backend integration."
    }
  ]
}
```

### `POST /api/predict`

Multipart form-data:

- `audio` (file)
- `model_id` (string)

Example response:

```json
{
  "request_id": "uuid",
  "model_id": "dummy_v1",
  "label": "Leinster",
  "confidence": 0.68,
  "probs": [
    { "label": "Leinster", "p": 0.68 },
    { "label": "Munster", "p": 0.17 }
  ]
}
```

## Model Plugin System

Plugins implement the `ModelPlugin` interface in `backend/plugins/base.py`.
Registration happens in `backend/plugin_loader.py`, and runtime lookup happens through `backend/registry.py`.

Current plugins:

- `dummy_v1`: deterministic output based on audio byte length (for integration testing)
- `mfcc_logreg_v1_01`: real model using MFCC summary features + logistic regression

## Data + State Notes

- Frontend state is in `frontend/store.js`.
- Prediction history and feedback are currently client-side only (in-memory).
- State resets on full page reload.

## Troubleshooting

- Browser shows stale JS/CSS:
  - Hard refresh with `Cmd + Shift + R` (macOS)
- `Failed to load models`:
  - Confirm backend is running on `127.0.0.1:8000`
  - Check terminal logs for plugin load errors
- `Unsupported or unreadable audio format`:
  - Install `ffmpeg` and retry
  - Try `.wav` input to isolate format issues
- Microphone recording fails:
  - Ensure browser microphone permission is granted
- `ModuleNotFoundError` during startup:
  - Activate virtualenv and reinstall `requirements.txt`

## Development Notes

- Frontend assets are served by FastAPI from `/static`.
- No separate frontend build step is required.
- `testing/SystemTests.xlsx` contains manual/system test tracking.
