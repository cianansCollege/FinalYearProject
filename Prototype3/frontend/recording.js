// Microphone capture flow and predict-button wiring for the frontend.

import { store } from "./store.js";
import { predictAudio } from "./api.js";
import { renderPrediction, renderError } from "./predictions.js";
import { updateMap, clearMapHighlight } from "./map.js";

let mediaRecorder = null;
let audioChunks = [];
let playbackObjectUrl = null;
let recordingStartTime = null;

function setStatus(message) {
  document.getElementById("statusMessage").textContent = message;
}

export function initRecording() {
  const recordBtn = document.getElementById("recordBtn");
  const stopBtn = document.getElementById("stopBtn");
  const predictBtn = document.getElementById("predictBtn");
  const audioPlayback = document.getElementById("audioPlayback");
  const audioFileInput = document.getElementById("audioFile");

  if (!recordBtn || !stopBtn || !predictBtn || !audioPlayback) {
    console.error("Recording controls are missing from the page.");
    return;
  }

  function setPlaybackSource(source) {
    if (playbackObjectUrl) {
      URL.revokeObjectURL(playbackObjectUrl);
      playbackObjectUrl = null;
    }

    if (!source) {
      audioPlayback.removeAttribute("src");
      audioPlayback.load();
      return;
    }

    playbackObjectUrl = URL.createObjectURL(source);
    audioPlayback.src = playbackObjectUrl;
  }

  function refreshPredictButtonState() {
    const hasAudioSource = Boolean(
      store.uploadedAudioFile || store.latestAudioBlob
    );
    predictBtn.disabled = !hasAudioSource;
  }

  refreshPredictButtonState();

  recordBtn.addEventListener("click", async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      audioChunks = [];
      recordingStartTime = Date.now();
      store.latestAudioBlob = null;
      store.uploadedAudioFile = null;
      setPlaybackSource(null);

      mediaRecorder = new MediaRecorder(stream);

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const durationSeconds = (Date.now() - recordingStartTime) / 1000;

        if (durationSeconds < 10) {
          store.latestAudioBlob = null;
          setPlaybackSource(null);
          refreshPredictButtonState();
          setStatus(
            `Recording too short (${durationSeconds.toFixed(1)}s). Minimum is 10 seconds.`
          );
          return;
        }

        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });

        store.latestAudioBlob = audioBlob;
        store.uploadedAudioFile = null;
        setPlaybackSource(audioBlob);
        refreshPredictButtonState();

        setStatus(
          `Recording ready (${durationSeconds.toFixed(1)}s). Click Predict Accent.`
        );
      };

      mediaRecorder.start();
      recordBtn.disabled = true;
      stopBtn.disabled = false;
      refreshPredictButtonState();
      setStatus("Recording... minimum length is 10 seconds.");
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

  if (audioFileInput) {
    const onFileSelected = () => {
      const file = audioFileInput.files?.[0] ?? null;

      if (!file) {
        refreshPredictButtonState();
        return;
      }

      store.uploadedAudioFile = file;
      store.latestAudioBlob = null;

      setPlaybackSource(file);
      refreshPredictButtonState();

      setStatus(`Audio file selected: ${file.name}`);
    };

    audioFileInput.addEventListener("change", onFileSelected);
    audioFileInput.addEventListener("input", onFileSelected);
  }

  predictBtn.addEventListener("click", async () => {
    if (!store.selectedModelId) {
      setStatus("No model selected.");
      return;
    }

    let audioSource = null;

    if (store.uploadedAudioFile) {
      audioSource = store.uploadedAudioFile;
    } else if (store.latestAudioBlob) {
      audioSource = store.latestAudioBlob;
    }

    if (!audioSource) {
      setStatus("No recording or uploaded audio available.");
      return;
    }

    try {
      clearMapHighlight();
      setStatus("Running prediction...");

      const result = await predictAudio(
        audioSource,
        store.selectedModelId
      );

      renderPrediction(result);

      const predictedLabel = result.label ?? result.predicted_label ?? null;
      if (predictedLabel) {
        updateMap(predictedLabel);
      }

      setStatus("Prediction complete.");
    } catch (error) {
      console.error(error);
      renderError(error.message);
      setStatus(`Prediction failed: ${error.message}`);
    }
  });
}