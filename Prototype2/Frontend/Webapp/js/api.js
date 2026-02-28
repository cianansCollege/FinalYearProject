// api.js
// This file centralises all API calls.
// Right now it's stubbed. Later swap internals to call FastAPI.

function randomChoice(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

export async function predictStub({ audioBlob, selfReportedProvince = null, modelId = "stub@0.1.0" }) {
  // Simulate network latency
  await new Promise((r) => setTimeout(r, 250));

  const provinces = ["Connacht", "Leinster", "Munster", "Ulster"];
  const predicted = randomChoice(provinces);

  // Confidence between 0.50 and 0.95
  const confidence = Math.round((0.5 + Math.random() * 0.45) * 100) / 100;

  // Fake score distribution
  const scores = {};
  let remaining = 1.0;
  const shuffled = [...provinces].sort(() => Math.random() - 0.5);
  for (let i = 0; i < shuffled.length; i++) {
    const p = shuffled[i];
    if (i === shuffled.length - 1) {
      scores[p] = Math.max(0, Math.round(remaining * 100) / 100);
    } else {
      const v = Math.max(0, Math.round((Math.random() * remaining) * 100) / 100);
      scores[p] = v;
      remaining = Math.max(0, remaining - v);
    }
  }

  return {
    prediction_id: crypto.randomUUID(),
    predicted_province: predicted,
    confidence,
    scores,
    model: { name: "stub", version: modelId }
  };
}