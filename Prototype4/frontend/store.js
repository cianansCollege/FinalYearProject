// Shared client-side state for models, selected model, and recorded audio.

export const store = {
  models: [],
  selectedModelId: null,
  latestAudioBlob: null,
  uploadedAudioFile: null,
  predictions: [],
  currentPredictionId: null,
};