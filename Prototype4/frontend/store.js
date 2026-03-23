const STORAGE_KEY = "fyp_predictions";

function loadStoredPredictions() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch (e) {
    console.error("Failed to load stored predictions", e);
    return [];
  }
}

function saveStoredPredictions(predictions) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(predictions));
  } catch (e) {
    console.error("Failed to save predictions", e);
  }
}

export const store = {
  models: [],
  selectedModelId: null,
  latestAudioBlob: null,
  uploadedAudioFile: null,

  predictions: loadStoredPredictions(),
  currentPredictionId: null,

  persist() {
    saveStoredPredictions(this.predictions);
  }
};