const STORAGE_KEY = "fyp_predictions_v1";

export function loadPredictions() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed;
  } catch {
    return [];
  }
}

export function savePredictions(predictions) {
  const trimmed = predictions.slice(-50);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
}

export function clearPredictions() {
  localStorage.removeItem(STORAGE_KEY);
}