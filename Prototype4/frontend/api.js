// Browser API client for model discovery and audio prediction requests.

const API_BASE = "http://127.0.0.1:8000";

export async function fetchModels() {
  const response = await fetch(`${API_BASE}/api/models`);

  if (!response.ok) {
    throw new Error("Failed to fetch models");
  }

  return await response.json();
}

export async function predictAudio(audioSource, modelId) {
  const formData = new FormData();

  if (audioSource instanceof File) {
    formData.append("audio", audioSource, audioSource.name);
  } else {
    formData.append("audio", audioSource, "recording.webm");
  }

  formData.append("model_id", modelId);

  const response = await fetch(`${API_BASE}/api/predict`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || "Prediction failed");
  }

  return await response.json();
}