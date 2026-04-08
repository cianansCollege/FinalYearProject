// Microphone capture flow and predict-button wiring for the frontend.

import { store } from "./store.js";
import { predictAudio } from "./api.js";
import {
  renderPrediction,
  renderError,
  renderFeedbackState,
  renderPredictionHistory,
  savePrediction,
  updatePredictionFeedback,
} from "./predictions.js";
import { updateMap, clearMapHighlight } from "./map.js";

let mediaRecorder = null;
let mediaStream = null;
let audioChunks = [];
let playbackObjectUrl = null;
let recordingStartTime = null;
let recordingTimerId = null;
let recordingAutoStopId = null;

const RECORDING_LENGTH_SECONDS = 10;

function setStatus(message) {
  document.getElementById("statusMessage").textContent = message;
}

export function initRecording() {
  const recordBtn = document.getElementById("recordBtn");
  const stopBtn = document.getElementById("stopBtn");
  const predictBtn = document.getElementById("predictBtn");
  const audioPlayback = document.getElementById("audioPlayback");
  const audioFileInput = document.getElementById("audioFile");
  const recordingCountdown = document.getElementById("recordingCountdown");

  const feedbackYesBtn = document.getElementById("feedbackYesBtn");
  const feedbackNoBtn = document.getElementById("feedbackNoBtn");
  const correctLabelSection = document.getElementById("correctLabelSection");
  const correctLabelSelect = document.getElementById("correctLabelSelect");
  const saveCorrectionBtn = document.getElementById("saveCorrectionBtn");
  const feedbackMessage = document.getElementById("feedbackMessage");

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

  function stopRecordingTimer() {
    if (recordingTimerId) {
      clearInterval(recordingTimerId);
      recordingTimerId = null;
    }
  }

  function stopAutoStopTimer() {
    if (recordingAutoStopId) {
      clearTimeout(recordingAutoStopId);
      recordingAutoStopId = null;
    }
  }

  function setCountdownDefault() {
    if (!recordingCountdown) {
      return;
    }

    recordingCountdown.textContent = `Recording length: ${RECORDING_LENGTH_SECONDS} seconds`;
    recordingCountdown.classList.remove("text-danger", "text-success");
    recordingCountdown.classList.add("text-body-secondary");
  }

  function renderRecordingTimer(elapsedSeconds) {
    if (!recordingCountdown) {
      return;
    }

    const remainingSeconds = Math.max(0, RECORDING_LENGTH_SECONDS - elapsedSeconds);

    if (remainingSeconds > 0) {
      recordingCountdown.textContent =
        `Recording: ${remainingSeconds.toFixed(1)}s remaining`;
      recordingCountdown.classList.remove("text-danger", "text-success");
      recordingCountdown.classList.add("text-body-secondary");
      return;
    }

    recordingCountdown.textContent =
      `Recording complete. Stopping automatically...`;
    recordingCountdown.classList.remove("text-danger", "text-body-secondary");
    recordingCountdown.classList.add("text-success");
  }

  function startRecordingTimer() {
    stopRecordingTimer();
    renderRecordingTimer(0);
    recordingTimerId = setInterval(() => {
      if (!recordingStartTime) {
        return;
      }
      const elapsedSeconds = (Date.now() - recordingStartTime) / 1000;
      renderRecordingTimer(elapsedSeconds);
    }, 100);
  }

  function startAutoStopTimer() {
    stopAutoStopTimer();
    recordingAutoStopId = setTimeout(() => {
      if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        recordBtn.disabled = false;
        stopBtn.disabled = true;
      }
    }, RECORDING_LENGTH_SECONDS * 1000);
  }

  setCountdownDefault();
  refreshPredictButtonState();
  renderPredictionHistory();

  recordBtn.addEventListener("click", async () => {
    try {
      mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });

      audioChunks = [];
      recordingStartTime = Date.now();
      store.latestAudioBlob = null;
      store.uploadedAudioFile = null;
      setPlaybackSource(null);

      mediaRecorder = new MediaRecorder(mediaStream);

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        stopRecordingTimer();
        stopAutoStopTimer();
        const durationSeconds = (Date.now() - recordingStartTime) / 1000;

        if (mediaStream) {
          mediaStream.getTracks().forEach((track) => track.stop());
          mediaStream = null;
        }

        if (durationSeconds + 0.05 < RECORDING_LENGTH_SECONDS) {
          if (recordingCountdown) {
            recordingCountdown.textContent =
              `Recording cancelled at ${durationSeconds.toFixed(1)}s. A full ${RECORDING_LENGTH_SECONDS}s clip is required.`;
            recordingCountdown.classList.remove("text-success", "text-body-secondary");
            recordingCountdown.classList.add("text-danger");
          }
          store.latestAudioBlob = null;
          setPlaybackSource(null);
          refreshPredictButtonState();
          setStatus(
            `Recording stopped early (${durationSeconds.toFixed(1)}s). Please record the full ${RECORDING_LENGTH_SECONDS} seconds.`
          );
          recordingStartTime = null;
          return;
        }

        if (recordingCountdown) {
          recordingCountdown.textContent =
            `Recorded ${durationSeconds.toFixed(1)}s clip.`;
          recordingCountdown.classList.remove("text-danger", "text-body-secondary");
          recordingCountdown.classList.add("text-success");
        }

        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });

        store.latestAudioBlob = audioBlob;
        store.uploadedAudioFile = null;
        setPlaybackSource(audioBlob);
        refreshPredictButtonState();

        setStatus(
          `Recording ready (${durationSeconds.toFixed(1)}s). Click Predict Accent.`
        );
        recordingStartTime = null;
      };

      mediaRecorder.start();
      startRecordingTimer();
      startAutoStopTimer();
      recordBtn.disabled = true;
      stopBtn.disabled = false;
      refreshPredictButtonState();
      setStatus(`Recording... the clip will stop automatically after ${RECORDING_LENGTH_SECONDS} seconds.`);
    } catch (error) {
      console.error(error);
      stopRecordingTimer();
      stopAutoStopTimer();
      if (mediaStream) {
        mediaStream.getTracks().forEach((track) => track.stop());
        mediaStream = null;
      }
      recordingStartTime = null;
      setCountdownDefault();
      setStatus("Could not access microphone.");
    }
  });

  stopBtn.addEventListener("click", () => {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      mediaRecorder.stop();
    }

    stopAutoStopTimer();
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
      stopRecordingTimer();
      setCountdownDefault();
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

      savePrediction(result);
      renderPrediction(result);
      renderPredictionHistory();

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

  if (feedbackYesBtn) {
    feedbackYesBtn.addEventListener("click", () => {
      const updated = updatePredictionFeedback({
        wasCorrect: true,
        correctedLabel: null,
      });

      if (!updated) {
        return;
      }

      if (correctLabelSection) {
        correctLabelSection.classList.add("d-none");
      }

      if (feedbackMessage) {
        feedbackMessage.textContent = "Thanks — marked as correct.";
      }

      renderFeedbackState(updated);
      renderPredictionHistory();
    });
  }

  if (feedbackNoBtn) {
    feedbackNoBtn.addEventListener("click", () => {
      if (correctLabelSection) {
        correctLabelSection.classList.remove("d-none");
      }

      if (feedbackMessage) {
        feedbackMessage.textContent = "Please select the correct province.";
      }
    });
  }

  if (saveCorrectionBtn) {
    saveCorrectionBtn.addEventListener("click", () => {
      const correctedLabel = correctLabelSelect?.value ?? "";

      if (!correctedLabel) {
        if (feedbackMessage) {
          feedbackMessage.textContent = "Please choose the correct province first.";
        }
        return;
      }

      const updated = updatePredictionFeedback({
        wasCorrect: false,
        correctedLabel,
      });

      if (!updated) {
        return;
      }

      if (feedbackMessage) {
        feedbackMessage.textContent =
          `Saved — marked incorrect, correct province: ${correctedLabel}.`;
      }

      renderFeedbackState(updated);
      renderPredictionHistory();
    });
  }
}
