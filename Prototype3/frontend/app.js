import { fetchModels } from "./api.js";
import { store } from "./store.js";

function setStatus(message) {
  const el = document.getElementById("statusMessage");
  if (el) el.textContent = message;
}

export async function initModels() {
  const select = document.getElementById("modelSelect");

  const data = await fetchModels();
  store.models = data.models || [];

  select.innerHTML = "";

  for (const model of store.models) {
    const option = document.createElement("option");
    option.value = model.id;
    option.textContent = model.name;
    select.appendChild(option);
  }

  store.selectedModelId = store.models[0]?.id || null;
  if (store.selectedModelId) {
    select.value = store.selectedModelId;
  }

  select.addEventListener("change", (event) => {
    store.selectedModelId = event.target.value;
    setStatus(`Selected model: ${store.selectedModelId}`);
  });

  setStatus(`Selected model: ${store.selectedModelId || "none"}`);
}