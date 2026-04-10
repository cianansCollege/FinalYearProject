// Prediction rendering helpers for success and error states in the UI.

import { store } from "./store.js?v=20260410e";
import { updateMap, clearMapHighlight } from "./map.js?v=20260410e";

function generatePredictionId() {
  return `pred_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

function formatConfidencePct(confidence) {
  return typeof confidence === "number" ? `${(confidence * 100).toFixed(1)}%` : "-";
}

function formatHistoryTimestamp(timestamp) {
  if (!timestamp) {
    return "-";
  }

  const parsed = new Date(timestamp);
  if (Number.isNaN(parsed.getTime())) {
    return String(timestamp);
  }

  return parsed.toLocaleString();
}

function formatFeedbackStatus(prediction) {
  if (prediction.wasCorrect === true) {
    return "Feedback: Correct";
  }

  if (prediction.wasCorrect === false) {
    if (prediction.correctedLabel) {
      return `Feedback: Incorrect \u2192 ${prediction.correctedLabel}`;
    }
    return "Feedback: Incorrect";
  }

  return "Feedback: Pending";
}

function setFeedbackButtonState(button, isActive) {
  if (!button) {
    return;
  }

  button.classList.toggle("active", isActive);
  button.setAttribute("aria-pressed", isActive ? "true" : "false");
}

function resetFeedbackUI() {
  const feedbackSection = document.getElementById("feedbackSection");
  const feedbackPlaceholder = document.getElementById("feedbackPlaceholder");
  const correctLabelSection = document.getElementById("correctLabelSection");
  const feedbackMessage = document.getElementById("feedbackMessage");
  const correctLabelSelect = document.getElementById("correctLabelSelect");
  const feedbackYesBtn = document.getElementById("feedbackYesBtn");
  const feedbackNoBtn = document.getElementById("feedbackNoBtn");

  if (feedbackSection) {
    feedbackSection.classList.add("d-none");
  }

  if (feedbackPlaceholder) {
    feedbackPlaceholder.classList.remove("d-none");
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

  setFeedbackButtonState(feedbackYesBtn, false);
  setFeedbackButtonState(feedbackNoBtn, false);
}

export function renderFeedbackState(prediction = null) {
  const feedbackSection = document.getElementById("feedbackSection");
  const feedbackPlaceholder = document.getElementById("feedbackPlaceholder");
  const correctLabelSection = document.getElementById("correctLabelSection");
  const feedbackMessage = document.getElementById("feedbackMessage");
  const correctLabelSelect = document.getElementById("correctLabelSelect");
  const feedbackYesBtn = document.getElementById("feedbackYesBtn");
  const feedbackNoBtn = document.getElementById("feedbackNoBtn");

  if (!feedbackSection || !feedbackPlaceholder) {
    return;
  }

  feedbackSection.classList.remove("d-none");
  feedbackPlaceholder.classList.add("d-none");

  setFeedbackButtonState(feedbackYesBtn, prediction?.wasCorrect === true);
  setFeedbackButtonState(feedbackNoBtn, prediction?.wasCorrect === false);

  if (prediction?.wasCorrect === true) {
    if (correctLabelSection) {
      correctLabelSection.classList.add("d-none");
    }
    if (correctLabelSelect) {
      correctLabelSelect.value = "";
    }
    if (feedbackMessage) {
      feedbackMessage.textContent = "Saved feedback: marked as correct.";
    }
    return;
  }

  if (prediction?.wasCorrect === false) {
    if (correctLabelSection) {
      correctLabelSection.classList.remove("d-none");
    }
    if (correctLabelSelect) {
      correctLabelSelect.value = prediction.correctedLabel ?? "";
    }
    if (feedbackMessage) {
      feedbackMessage.textContent = prediction.correctedLabel
        ? `Saved feedback: marked incorrect, correct province: ${prediction.correctedLabel}.`
        : "Saved feedback: marked incorrect.";
    }
    return;
  }

  if (correctLabelSection) {
    correctLabelSection.classList.add("d-none");
  }
  if (correctLabelSelect) {
    correctLabelSelect.value = "";
  }
  if (feedbackMessage) {
    feedbackMessage.textContent = "";
  }
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
  store.persist();

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

  store.persist();

  return prediction;
}

export function renderPrediction(result) {
  document.getElementById("resultModel").textContent = result.model_id || "-";
  document.getElementById("resultLabel").textContent = result.label || "-";

  document.getElementById("resultConfidence").textContent =
    formatConfidencePct(result.confidence);

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

  renderFeedbackState(result);
}

export function renderPredictionHistory() {
  const historyPlaceholder = document.getElementById("predictionHistoryPlaceholder");
  const historyList = document.getElementById("predictionHistoryList");
  const clearHistoryBtn = document.getElementById("clearHistoryBtn");

  if (!historyPlaceholder || !historyList) {
    return;
  }

  if (clearHistoryBtn) {
    clearHistoryBtn.disabled = !Array.isArray(store.predictions) || store.predictions.length === 0;
  }

  if (!Array.isArray(store.predictions) || store.predictions.length === 0) {
    historyPlaceholder.classList.remove("d-none");
    historyList.classList.add("d-none");
    historyList.innerHTML = "";
    return;
  }

  historyPlaceholder.classList.add("d-none");
  historyList.classList.remove("d-none");
  historyList.innerHTML = "";

  for (const prediction of store.predictions) {
    const item = document.createElement("div");
    item.style.cursor = "pointer";

    item.addEventListener("click", () => {
      restorePrediction(prediction.id);
    });

    item.className = "border rounded p-2 mb-2";
    item.classList.add(
      prediction.id === store.currentPredictionId
        ? "border-primary"
        : "border-secondary-subtle"
    );

    const topRow = document.createElement("div");
    topRow.className = "d-flex justify-content-between align-items-center gap-2";

    const labelEl = document.createElement("span");
    labelEl.className = "fw-semibold";
    labelEl.textContent = prediction.predictedLabel ?? "-";

    const confidenceEl = document.createElement("span");
    confidenceEl.className = "small";
    confidenceEl.textContent = formatConfidencePct(prediction.confidence);

    topRow.append(labelEl, confidenceEl);

    const metaEl = document.createElement("div");
    metaEl.className = "small text-body-secondary mt-1";
    metaEl.textContent = `${formatHistoryTimestamp(prediction.timestamp)} \u00b7 ${
      prediction.modelId ?? "Unknown model"
    }`;

    const feedbackEl = document.createElement("div");
    feedbackEl.className = "small mt-1";
    feedbackEl.textContent = formatFeedbackStatus(prediction);

    item.append(topRow, metaEl, feedbackEl);
    historyList.appendChild(item);
  }
}

export function clearPredictionResults() {
  store.clearPredictions();

  document.getElementById("resultModel").textContent = "-";
  document.getElementById("resultLabel").textContent = "-";
  document.getElementById("resultConfidence").textContent = "-";
  document.getElementById("probList").innerHTML = "";

  resetFeedbackUI();
  clearMapHighlight();
  renderPredictionHistory();
}

export function renderError(message) {
  document.getElementById("resultModel").textContent = "-";
  document.getElementById("resultLabel").textContent = `Error: ${message}`;
  document.getElementById("resultConfidence").textContent = "-";
  document.getElementById("probList").innerHTML = "";

  resetFeedbackUI();
}

export function restorePrediction(predictionId) {
  const prediction = store.predictions.find(
    (p) => p.id === predictionId
  );

  if (!prediction) return;

  store.currentPredictionId = predictionId;

  // Restore result UI
  renderPrediction({
    model_id: prediction.modelId,
    label: prediction.predictedLabel,
    confidence: prediction.confidence,
    probs: prediction.probabilities,
    wasCorrect: prediction.wasCorrect,
    correctedLabel: prediction.correctedLabel,
  });

  // Restore map
  clearMapHighlight();
  if (prediction.predictedLabel) {
    updateMap(prediction.predictedLabel);
  }

  // Re-render history to highlight selected
  renderPredictionHistory();
}
