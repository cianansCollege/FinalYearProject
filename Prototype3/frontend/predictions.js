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
      li.textContent = `${item.label}: ${(item.p * 100).toFixed(1)}%`;
      probList.appendChild(li);
    }
  }
}

export function renderError(message) {
  document.getElementById("resultLabel").textContent = `Error: ${message}`;
}