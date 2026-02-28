export function createPredictionController(controller) {
  const {
    predList,
    btnClear,
    currentProvinceEl,
    currentConfidenceEl,
    btnFeedbackRight,
    btnFeedbackWrong,
    onSelect,
    onClear,
    onChange = () => {}
  } = controller;

  const predictions = [];

  function setCurrentResult(prediction) {
    currentProvinceEl.textContent = prediction.predicted_province;
    currentConfidenceEl.textContent = `${(prediction.confidence * 100).toFixed(1)}%`;

    btnFeedbackRight.disabled = false;
    btnFeedbackWrong.disabled = false;
    btnFeedbackRight.dataset.predId = prediction.id;
    btnFeedbackWrong.dataset.predId = prediction.id;
  }

  function renderPredList() {
    predList.innerHTML = "";

    if (predictions.length === 0) {
      predList.innerHTML = '<div class="text-muted p-3">No predictions yet.</div>';
      return;
    }

    for (const prediction of predictions.slice().reverse()) {
      const item = document.createElement("button");
      item.type = "button";
      item.className = "list-group-item list-group-item-action";

      const correctText =
        prediction.correctness === true ? "Yes" :
        prediction.correctness === false ? "No" :
        "Unknown";

      item.innerHTML = `
        <div class="d-flex justify-content-between align-items-start">
          <div>
            <div class="fw-semibold">${prediction.predicted_province}</div>
            <div class="small text-muted">Confidence: ${(prediction.confidence * 100).toFixed(1)}%</div>
            <div class="small text-muted">Correct: ${correctText}</div>
            <div class="small text-muted">Feedback: ${prediction.user_feedback || "—"}</div>
          </div>
          <span class="badge text-bg-dark">${new Date(prediction.created_at).toLocaleTimeString()}</span>
        </div>
        <div class="mt-2">
          <audio class="audio-mini" controls src="${prediction.audio_url}"></audio>
        </div>
      `;

      item.addEventListener("click", () => {
        setCurrentResult(prediction);
        onSelect(prediction);
      });

      predList.appendChild(item);
    }
  }

  function setUserFeedback(predId, feedback) {
    const prediction = predictions.find((item) => item.id === predId);
    if (!prediction) return;
    prediction.user_feedback = feedback;
    renderPredList();
  }

  btnFeedbackRight.addEventListener("click", () => {
    const id = btnFeedbackRight.dataset.predId;
    if (id) setUserFeedback(id, "right");
  });

  btnFeedbackWrong.addEventListener("click", () => {
    const id = btnFeedbackWrong.dataset.predId;
    if (id) setUserFeedback(id, "wrong");
  });

  btnClear.addEventListener("click", () => {
    predictions.length = 0;

    currentProvinceEl.textContent = "—";
    currentConfidenceEl.textContent = "—";
    btnFeedbackRight.disabled = true;
    btnFeedbackWrong.disabled = true;

    onClear();
    renderPredList();
  });

  renderPredList();

  return {
    add(prediction) {
      predictions.push(prediction);
      setCurrentResult(prediction);
      renderPredList();
    }
  };
}
