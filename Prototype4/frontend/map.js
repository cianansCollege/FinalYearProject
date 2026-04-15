let map;
let provinceLayers = {};
let geojsonLayer;
let mapReady = false;

const defaultStyle = {
  color: "#6c757d",
  weight: 1,
  fillColor: "#dee2e6",
  fillOpacity: 0.5
};

const highlightStyle = {
  color: "#0d6efd",
  weight: 2,
  fillColor: "#0d6efd",
  fillOpacity: 0.6
};

const INITIAL_CENTER = [53.4, -8.2];
const INITIAL_ZOOM = 7;

function normalizeName(value) {
  return String(value || "").trim().toLowerCase();
}

function getRegionsToHighlight(modelId, label) {
  const cleanLabel = String(label || "").trim();

  if (modelId === "wav2vec_ulster_vs_rest_rf") {
    if (cleanLabel === "Ulster") return ["Ulster"];
    if (cleanLabel === "Rest") return ["Leinster", "Munster", "Connacht"];
  }

  if (modelId === "wav2vec_leinster_vs_rest_logreg") {
    if (cleanLabel === "Leinster") return ["Leinster"];
    if (cleanLabel === "Rest") return ["Ulster", "Munster", "Connacht"];
  }

  if (modelId === "wav2vec_ulster_leinster_rest_logreg") {
    if (cleanLabel === "Ulster") return ["Ulster"];
    if (cleanLabel === "Leinster") return ["Leinster"];
    if (cleanLabel === "Rest") return ["Munster", "Connacht"];
  }

  if (
    modelId === "wav2vec_province_4way_logreg" ||
    modelId === "mfcc_logreg_v1_01"
  ) {
    if (["Ulster", "Leinster", "Munster", "Connacht"].includes(cleanLabel)) {
      return [cleanLabel];
    }
  }

  return [];
}

export async function initMap() {
  map = L.map("map").setView(INITIAL_CENTER, INITIAL_ZOOM);

  L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
      attribution: "&copy; OpenStreetMap contributors"
    }
  ).addTo(map);

  const response = await fetch("/static/data/provinces.geojson");
  const geojson = await response.json();

  geojsonLayer = L.geoJSON(geojson, {
    style: defaultStyle,
    onEachFeature: (feature, layer) => {
      const name = feature.properties.NAME;
      provinceLayers[normalizeName(name)] = layer;
      layer.bindTooltip(name);
    }
  }).addTo(map);

  mapReady = true;
}

export function updateMap(modelId, label) {
  clearMapHighlight();

  const regions = getRegionsToHighlight(modelId, label);

  regions.forEach((regionName) => {
    const layer = provinceLayers[normalizeName(regionName)];
    if (layer) {
      layer.setStyle(highlightStyle);
    }
  });
}

export function resetMapView() {
  if (!mapReady || !map) {
    return;
  }

  map.setView(INITIAL_CENTER, INITIAL_ZOOM);
}

export function clearMapHighlight() {
  Object.values(provinceLayers).forEach((layer) => {
    layer.setStyle(defaultStyle);
  });
}