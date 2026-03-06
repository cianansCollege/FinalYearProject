# app.py exposes /api/models and /api/predict

from __future__ import annotations

import uuid

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from registry import get_model, list_models
import plugins  # noqa: F401


app = FastAPI(title="Prototype3 Accent API")


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

    wav_bytes = await audio.read()
    result = model.predict(wav_bytes)

    return {
        "request_id": str(uuid.uuid4()),
        "model_id": model_id,
        **result,
    }