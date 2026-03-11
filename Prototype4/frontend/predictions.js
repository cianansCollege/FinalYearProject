// Prediction rendering helpers for success and error states in the UI.

import { store } from "./store.js";

function generatePredictionId() {
  return `pred_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

export function savePrediction(result) {
  const prediction = {
    id: generatePredictionId(),
    timestamp: new Date().toISOString(),
    modelId: result.model_id ?? null,
    predictedLabel: result.label ?? null,
    confidence: typeof result.confidence === "number" ? result.confidence : null,
    probabilities: Array.isArray(result.probs) ? result.probs : [],
    wasCorrect: null,
    correctedLabel: null,
  };

  store.predictions.unshift(prediction);
  store.currentPredictionId = prediction.id;

  return prediction;
}

export function updatePredictionFeedback({ wasCorrect, correctedLabel = null }) {
  const prediction = store.predictions.find(
    (item) => item.id === store.currentPredictionId
  );

  if (!prediction) {
    return null;
  }

  prediction.wasCorrect = wasCorrect;
  prediction.correctedLabel = correctedLabel;

  return prediction;
}

export function renderPrediction(result) {
  document.getElementById("resultModel").textContent = result.model_id || "-";
  document.getElementById("resultLabel").textContent = result.label || "-";

  document.getElementById("resultConfidence").textContent =
    typeof result.confidence === "number"
      ? `${(result.confidence * 100).toFixed(1)}%`
      : "-";

  const probList = document.getElementById("probList");
  probList.innerHTML = "";

  if (Array.isArray(result.probs)) {
    for (const item of result.probs) {
      const li = document.createElement("li");
      li.className = "list-group-item d-flex justify-content-between align-items-center";

      const labelEl = document.createElement("span");
      labelEl.textContent = item.label ?? "-";

      const pctEl = document.createElement("span");
      pctEl.className = "fw-semibold";
      const pct =
        typeof item.p === "number" ? `${(item.p * 100).toFixed(1)}%` : "-";
      pctEl.textContent = pct;

      li.append(labelEl, pctEl);
      probList.appendChild(li);
    }
  }

  const feedbackSection = document.getElementById("feedbackSection");
  const correctLabelSection = document.getElementById("correctLabelSection");
  const feedbackMessage = document.getElementById("feedbackMessage");
  const correctLabelSelect = document.getElementById("correctLabelSelect");

  if (feedbackSection) {
    feedbackSection.classList.remove("d-none");
  }

  if (correctLabelSection) {
    correctLabelSection.classList.add("d-none");
  }

  if (feedbackMessage) {
    feedbackMessage.textContent = "";
  }

  if (correctLabelSelect) {
    correctLabelSelect.value = "";
  }
}

export function renderError(message) {
  document.getElementById("resultModel").textContent = "-";
  document.getElementById("resultLabel").textContent = `Error: ${message}`;
  document.getElementById("resultConfidence").textContent = "-";
  document.getElementById("probList").innerHTML = "";

  const feedbackSection = document.getElementById("feedbackSection");
  const correctLabelSection = document.getElementById("correctLabelSection");
  const feedbackMessage = document.getElementById("feedbackMessage");

  if (feedbackSection) {
    feedbackSection.classList.add("d-none");
  }

  if (correctLabelSection) {
    correctLabelSection.classList.add("d-none");
  }

  if (feedbackMessage) {
    feedbackMessage.textContent = "";
  }
}