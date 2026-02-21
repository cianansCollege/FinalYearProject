const PROVINCE_CENTROIDS = {
  Leinster: [53.18, -6.65],
  Munster: [52.13, -8.65],
  Connacht: [53.45, -9.15],
  Ulster: [54.65, -6.8]
};

function markerIconUrl(correctness) {
  if (correctness === true) return "https://maps.gstatic.com/mapfiles/ms2/micons/green-dot.png";
  if (correctness === false) return "https://maps.gstatic.com/mapfiles/ms2/micons/red-dot.png";
  return "https://maps.gstatic.com/mapfiles/ms2/micons/blue-dot.png";
}

export function createMapController(mapId) {
  const map = L.map(mapId).setView([53.4, -7.8], 6);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: "&copy; OpenStreetMap contributors"
  }).addTo(map);

  let highlightLayer = null;
  const markersById = new Map();

  function highlightProvince(province) {
    if (highlightLayer) map.removeLayer(highlightLayer);

    const latLng = PROVINCE_CENTROIDS[province];
    if (!latLng) return;

    highlightLayer = L.circle(latLng, { radius: 80000, weight: 2 }).addTo(map);
    map.panTo(latLng);
  }

  function addPredictionMarker(prediction) {
    const latLng = prediction.latlng || PROVINCE_CENTROIDS[prediction.predicted_province] || [53.4, -7.8];

    const icon = L.icon({
      iconUrl: markerIconUrl(prediction.correctness),
      iconSize: [32, 32],
      iconAnchor: [16, 32],
      popupAnchor: [0, -28]
    });

    const marker = L.marker(latLng, { icon }).addTo(map);
    marker.bindPopup(
      `<div><strong>${prediction.predicted_province}</strong></div>
       <div>Confidence: ${(prediction.confidence * 100).toFixed(1)}%</div>
       <div>Correct: ${prediction.correctness === true ? "Yes" : prediction.correctness === false ? "No" : "Unknown"}</div>`
    );

    markersById.set(prediction.id, marker);
  }

  function focusMarker(id) {
    const marker = markersById.get(id);
    if (!marker) return;
    map.setView(marker.getLatLng(), 8);
    marker.openPopup();
  }

  function clear() {
    for (const marker of markersById.values()) map.removeLayer(marker);
    markersById.clear();

    if (highlightLayer) map.removeLayer(highlightLayer);
    highlightLayer = null;
  }

  return {
    highlightProvince,
    addPredictionMarker,
    focusMarker,
    clear
  };
}
