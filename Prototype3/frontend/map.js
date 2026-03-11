// Province card highlight helpers for displaying the predicted label.

let map;
let provinceLayers = {};
let geojsonLayer;

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

export async function initMap() {
  map = L.map("map").setView([53.4, -8.2], 6);

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
      const name = feature.properties.name;
      provinceLayers[name] = layer;

      layer.bindTooltip(name);
    }
  }).addTo(map);
}

export function updateMap(label) {
  clearMapHighlight();

  const layer = provinceLayers[label];

  if (!layer) return;

  layer.setStyle(highlightStyle);
  map.fitBounds(layer.getBounds(), { padding: [40, 40] });
}

export function clearMapHighlight() {
  Object.values(provinceLayers).forEach((layer) => {
    layer.setStyle(defaultStyle);
  });
}