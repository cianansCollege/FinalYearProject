# FastAPI entrypoint exposing health, model listing, and prediction endpoints.

from __future__ import annotations

import uuid

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from registry import get_model, list_models
import plugins  # noqa: F401


app = FastAPI(title="Prototype3 Accent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/models")
def api_models() -> dict:
    return {"models": list_models()}


@app.post("/api/predict")
async def api_predict(
    audio: UploadFile = File(...),
    model_id: str = Form(...),
) -> dict:
    try:
        model = get_model(model_id)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    audio_bytes = await audio.read()

    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio upload")

    result = model.predict(audio_bytes)

    return {
        "request_id": str(uuid.uuid4()),
        "model_id": model_id,
        **result,
    }
