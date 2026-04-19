# Physical Architecture Diagram

This diagram describes the deployed `Prototype4` runtime as a physical system.
It focuses on where components live and how they communicate, rather than on
the detailed software call flow.

```mermaid
flowchart LR
  user["User"]

  subgraph workstation["User Workstation / Demo Host"]
    subgraph browser["Web Browser"]
      ui["Single-Page UI<br/>HTML, CSS, JavaScript"]
      capture["Audio Input<br/>Microphone or File Upload"]
      history["Browser localStorage<br/>Prediction history + feedback"]
      map["Leaflet Map UI<br/>Province highlighting"]
    end

    subgraph backend["Local FastAPI Service"]
      app["FastAPI app<br/>Serves / and /static"]
      api["REST endpoints<br/>/api/health<br/>/api/models<br/>/api/predict"]
      registry["Plugin loader + registry"]
      audio["Audio preprocessing<br/>soundfile, librosa, ffmpeg fallback<br/>16 kHz mono, first 10 s"]
      features["Feature layer<br/>MFCC summaries or wav2vec embeddings"]
      plugins["Inference plugins<br/>MFCC logistic regression<br/>Wav2Vec classifiers"]
    end

    files["Local filesystem<br/>Frontend assets, GeoJSON, .joblib artifacts"]
    mic["Microphone / audio file"]
  end

  subgraph external["External Dependencies"]
    osm["OpenStreetMap tile server"]
    cdn["CDN assets<br/>Bootstrap + Leaflet"]
    hf["Hugging Face model hub/cache<br/>facebook/wav2vec2-base on first use"]
  end

  user --> ui
  mic --> capture
  capture --> ui
  ui <--> history
  ui --> map

  ui -->|"GET /, /static assets"| app
  ui -->|"GET /api/models"| api
  ui -->|"POST /api/predict<br/>audio + model_id"| api

  app --> files
  api --> registry
  registry --> plugins
  plugins --> audio
  plugins --> features
  plugins --> files
  app --> ui
  api --> ui

  map -->|"Tile requests"| osm
  ui -->|"CSS/JS libraries"| cdn
  features -.->|"Initial wav2vec model download"| hf
```

## Notes

- The browser and FastAPI backend both run on the same workstation during the
  current prototype/demo setup.
- The frontend is served directly by FastAPI, so there is no separate frontend
  build server in the deployed prototype.
- Prediction history and user feedback are stored in browser `localStorage`,
  not in a backend database.
- Model binaries and map data are loaded from the local filesystem under
  `Prototype4/backend/artifacts` and `Prototype4/frontend/data`.
- Wav2Vec-based plugins can require internet access the first time the shared
  encoder is loaded, after which it is cached locally by the Python runtime.

## Suggested Figure Caption

Physical architecture of the deployed Prototype4 accent-classification
prototype. A browser-based client captures or uploads audio, communicates with a
local FastAPI backend for model selection and inference, stores result history
in browser localStorage, and depends on locally stored model artifacts plus a
small number of third-party services for map tiles, CDN frontend libraries, and
the initial wav2vec model download.
