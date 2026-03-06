import { store } from "./store.js";
import { predictAudio } from "./api.js";
import { renderPrediction, renderError } from "./predictions.js";
import { updateMap, clearMapHighlight } from "./map.js";

let mediaRecorder = null;
let audioChunks = [];

function setStatus(message) {
  document.getElementById("statusMessage").textContent = message;
}

export function initRecording() {
  const recordBtn = document.getElementById("recordBtn");
  const stopBtn = document.getElementById("stopBtn");
  const predictBtn = document.getElementById("predictBtn");
  const audioPlayback = document.getElementById("audioPlayback");

  recordBtn.addEventListener("click", async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      audioChunks = [];
      mediaRecorder = new MediaRecorder(stream);

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
        store.latestAudioBlob = audioBlob;

        audioPlayback.src = URL.createObjectURL(audioBlob);
        predictBtn.disabled = false;

        setStatus("Recording ready. Click Predict Accent.");
      };

      mediaRecorder.start();
      recordBtn.disabled = true;
      stopBtn.disabled = false;
      predictBtn.disabled = true;
      setStatus("Recording...");
    } catch (error) {
      console.error(error);
      setStatus("Could not access microphone.");
    }
  });

  stopBtn.addEventListener("click", () => {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      mediaRecorder.stop();
    }

    recordBtn.disabled = false;
    stopBtn.disabled = true;
  });

  predictBtn.addEventListener("click", async () => {
    if (!store.latestAudioBlob) {
      setStatus("No recording available.");
      return;
    }

    if (!store.selectedModelId) {
      setStatus("No model selected.");
      return;
    }

    try {
      clearMapHighlight();
      setStatus("Running prediction...");

      const result = await predictAudio(
        store.latestAudioBlob,
        store.selectedModelId
      );

      renderPrediction(result);
      updateMap(result.label);
      setStatus("Prediction complete.");
    } catch (error) {
      console.error(error);
      renderError(error.message);
      setStatus(`Prediction failed: ${error.message}`);
    }
  });
}