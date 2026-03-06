import { store } from "./store.js";
import { predictAudio } from "./api.js";
import { renderPrediction, renderError } from "./predictions.js";
import { updateMap } from "./map.js";

export async function runPrediction() {
  if (!store.latestAudioBlob) {
    throw new Error("No audio recorded");
  }
  if (!store.selectedModelId) {
    throw new Error("No model selected");
  }

  const result = await predictAudio(store.latestAudioBlob, store.selectedModelId);
  renderPrediction(result);
  updateMap(result.label);
}