// Frontend bootstrap that initializes model loading and recording controls.

import { fetchModels } from "./api.js?v=20260410e";
import { store } from "./store.js?v=20260410e";
import { initRecording } from "./recording.js?v=20260410e";
import { initMap, resetMapView } from "./map.js?v=20260410e";
import { clearPredictionResults } from "./predictions.js?v=20260410e";


function setStatus(message) {
  document.getElementById("statusMessage").textContent = message;
}

async function initModels() {
  const modelSelect = document.getElementById("modelSelect");

  try {
    setStatus("Loading models...");
    const data = await fetchModels();

    const rawModels = Array.isArray(data.models) ? data.models : [];

    const models = rawModels.map((model) => {
      if (typeof model === "string") {
        return { id: model, name: model };
      }
      return {
        id: model.id,
        name: model.name ?? model.id,
      };
    });

    store.models = models;
    modelSelect.innerHTML = "";

    if (models.length === 0) {
      const option = document.createElement("option");
      option.value = "";
      option.textContent = "No models available";
      modelSelect.appendChild(option);
      store.selectedModelId = null;
      setStatus("No models found.");
      return;
    }

    for (const model of models) {
      const option = document.createElement("option");
      option.value = model.id;
      option.textContent = model.name;
      modelSelect.appendChild(option);
    }

    store.selectedModelId = models[0].id;
    modelSelect.value = store.selectedModelId;

    modelSelect.addEventListener("change", (event) => {
      store.selectedModelId = event.target.value;
      setStatus(`Selected model: ${store.selectedModelId}`);
    });

    setStatus(`Selected model: ${store.selectedModelId}`);
  } catch (error) {
    console.error(error);
    setStatus("Failed to load models.");
  }
}

async function initApp() {
  try {
    await initMap();
  } catch (error) {
    console.error("Map failed to load:", error);
  }

  await initModels();
  initRecording();

  const resetMapBtn = document.getElementById("resetMapBtn");
  if (resetMapBtn) {
    resetMapBtn.addEventListener("click", () => {
      resetMapView();
    });
  }

  const clearHistoryBtn = document.getElementById("clearHistoryBtn");
  if (clearHistoryBtn) {
    clearHistoryBtn.addEventListener("click", () => {
      clearPredictionResults();
      setStatus("Previous prediction results cleared.");
    });
  }
}

initApp();
