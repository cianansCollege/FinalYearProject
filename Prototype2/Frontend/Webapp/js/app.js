import { createMapController } from "./map.js";
import { createRecorder } from "./recording.js";
import { createPredictionController } from "./predictions.js";

function computeCorrectness(predicted, selfReported) {
  if (!selfReported) return null;
  return predicted === selfReported;
}

async function fakePredict() {
  const provinces = ["Leinster", "Munster", "Connacht", "Ulster"];
  const predicted = provinces[Math.floor(Math.random() * provinces.length)];
  const confidence = 0.55 + Math.random() * 0.4;
  return { predicted_province: predicted, confidence };
}

const mapController = createMapController("map");

const recorder = createRecorder({
  btnStart: document.getElementById("btnStart"),
  btnStop: document.getElementById("btnStop"),
  btnRetake: document.getElementById("btnRetake"),
  btnSubmit: document.getElementById("btnSubmit"),
  recStatus: document.getElementById("recStatus"),
  recProgress: document.getElementById("recProgress"),
  timeLimitEl: document.getElementById("timeLimit"),
  audioPreview: document.getElementById("audioPreview")
});

const predictionController = createPredictionController({
  predList: document.getElementById("predList"),
  btnClear: document.getElementById("btnClear"),
  currentProvinceEl: document.getElementById("currentProvince"),
  currentConfidenceEl: document.getElementById("currentConfidence"),
  btnFeedbackRight: document.getElementById("btnFeedbackRight"),
  btnFeedbackWrong: document.getElementById("btnFeedbackWrong"),
  onSelect: (prediction) => {
    mapController.highlightProvince(prediction.predicted_province);
    mapController.focusMarker(prediction.id);
  },
  onClear: () => {
    mapController.clear();
  }
});

const btnSubmit = document.getElementById("btnSubmit");
const selfProvince = document.getElementById("selfProvince");

btnSubmit.addEventListener("click", async () => {
  const { blob: audioBlob, url: audioUrl } = recorder.getAudio();
  if (!audioBlob || !audioUrl) return;

  const data = await fakePredict();
  const selfReport = selfProvince.value || null;

  const prediction = {
    id: crypto.randomUUID(),
    created_at: Date.now(),
    predicted_province: data.predicted_province,
    confidence: data.confidence,
    self_reported_province: selfReport,
    correctness: computeCorrectness(data.predicted_province, selfReport),
    user_feedback: null,
    audio_url: audioUrl,
    latlng: null
  };

  predictionController.add(prediction);
  mapController.highlightProvince(prediction.predicted_province);
  mapController.addPredictionMarker(prediction);
});
