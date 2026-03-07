// Prediction rendering helpers for success and error states in the UI.

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
      const pct =
        typeof item.p === "number" ? `${(item.p * 100).toFixed(1)}%` : "-";
      li.textContent = `${item.label}: ${pct}`;
      probList.appendChild(li);
    }
  }
}

export function renderError(message) {
  document.getElementById("resultModel").textContent = "-";
  document.getElementById("resultLabel").textContent = `Error: ${message}`;
  document.getElementById("resultConfidence").textContent = "-";
  document.getElementById("probList").innerHTML = "";
}
