# Report File Checklist

This is a curated list of the repo files most worth referencing, citing, screenshotting, or attaching in the final report.
It is intentionally selective: it focuses on implementation, evaluation, testing, and supporting evidence, and leaves out raw data, virtual environments, caches, and other bulky files that do not belong in the report.

## 1. Main Report Files

- `FinalReport/Submission1.docx`
  Main report document.
- `FinalReport/Final Report Template 2025 V1.dotx`
  Report template if you need to check formatting against the official structure.

## 2. Architecture, Planning, and High-Level Design

- `FinalReport/Diagrams/SystemFlow.pptx`
  Source file for the system architecture / flow diagram.
- `FinalReport/Diagrams/PhysicalArchitecture.md`
  Mermaid source for the deployed physical architecture diagram.
- `FinalReport/Diagrams/FinalReportGanttChart.png`
  Gantt chart image for project planning/timeline sections.
- `FinalReport/Diagrams/FinalReportGanttChart.gantt`
  Editable source for the Gantt chart.
- `Prototype4/readme.md`
  High-level summary of the deployed prototype, API, UI flow, and project structure.

## 3. Core Backend Files to Discuss in the Implementation Section

- `Prototype4/backend/app.py`
  Main FastAPI entrypoint and API route definitions.
- `Prototype4/backend/plugin_loader.py`
  Model registration logic for the plugin-based architecture.
- `Prototype4/backend/registry.py`
  Runtime model registry.
- `Prototype4/backend/schemas.py`
  Request/response schema definitions.
- `Prototype4/backend/services/audio.py`
  Audio loading, decoding, validation, and preprocessing.
- `Prototype4/backend/services/features.py`
  MFCC feature extraction logic.
- `Prototype4/backend/services/wav2vec_features.py`
  Wav2Vec embedding extraction logic.
- `Prototype4/backend/plugins/base.py`
  Shared plugin interface used by all deployed models.

## 4. Model Files Worth Mentioning

- `Prototype4/backend/plugins/mfcc_logreg_v1_01.py`
  Deployed MFCC + logistic regression model plugin.
- `Prototype4/backend/plugins/wav2vec_ulster_vs_rest_rf.py`
  Deployed Wav2Vec Ulster-vs-rest model plugin.
- `Prototype4/backend/plugins/wav2vec_leinster_vs_rest_logreg.py`
  Deployed Wav2Vec Leinster-vs-rest model plugin.
- `Prototype4/backend/plugins/wav2vec_ulster_leinster_rest_logreg.py`
  Deployed 3-class Wav2Vec model plugin.
- `Prototype4/backend/plugins/wav2vec_province_4way_logreg.py`
  Deployed 4-class Wav2Vec model plugin.
- `Prototype4/backend/training/train_mfcc_logreg_v1_01.py`
  MFCC model training pipeline.
- `Prototype4/backend/training/train_wav2vec_deploy.py`
  Wav2Vec training/deployment pipeline.

## 5. Frontend Files Worth Mentioning

- `Prototype4/frontend/index.html`
  Main interface structure.
- `Prototype4/frontend/app.js`
  UI bootstrap and orchestration.
- `Prototype4/frontend/api.js`
  Frontend-to-backend request handling.
- `Prototype4/frontend/recording.js`
  Microphone recording and upload flow.
- `Prototype4/frontend/predictions.js`
  Prediction rendering and probability display.
- `Prototype4/frontend/map.js`
  Province highlighting and map behaviour.
- `Prototype4/frontend/store.js`
  Frontend state management.
- `Prototype4/frontend/style.css`
  Main UI styling.
- `Prototype4/frontend/data/provinces.geojson`
  Map boundary data used by the UI.

## 6. Testing and Validation Evidence

- `Prototype4/testing/SystemTests.xlsx`
  Manual/system testing checklist for the prototype.
- `FinalReport/Evidence/SystemTestList/SystemTests.xlsx`
  Report-side copy of the system test evidence.
- `FinalReport/Evidence/Images/Testing/file_upload_shorter_than_10secs_frontend.png`
  Frontend validation example for short file rejection.
- `FinalReport/Evidence/Images/Testing/file_upload_shorter_than_10secs_swagger.png`
  API-level validation example for the same case.
- `FinalReport/Evidence/Images/FullSystemRunthrough/`
  End-to-end screenshots showing the full user flow through the system.
- `FinalReport/Evidence/JSON/wav2vec_ulster_vs_rest_response_200.json`
  Example successful API response for appendix/evidence use.
- `FinalReport/Evidence/JSON/wav2vec_ulster_vs_rest_response_200_png.png`
  Screenshot version of the sample API response.

## 7. Results, Tables, and Figures for the Evaluation Section

- `FinalReport/Evidence/irish_pop_provinces.xlsx`
  Province population figures used for context and comparison.
- `FinalReport/Evidence/speaker_counts.xlsx`
  Speaker/sample count summary.
- `FinalReport/Evidence/wav2vec_vs_mfcc.xlsx`
  High-level model comparison sheet.
- `FinalReport/Evidence/wav2vec_vs_mfcc/irish_model_summary_charts.xlsx`
  Charts comparing Irish MFCC model results.
- `FinalReport/Evidence/wav2vec_vs_mfcc/wav2vec_irish_summary.xlsx`
  Wav2Vec summary sheet.
- `FinalReport/Evidence/wav2vec_vs_mfcc/ wav2vec_vs_mfcc_ba_f1.png`
  Comparison figure for Balanced Accuracy and F1.
- `FinalReport/Evidence/machine_learning_metric_equations.png`
  Metric formula figure for methodology/evaluation background.
- `FinalReport/Evidence/Images/Class_Sample_Summaries_Irish/`
  Dataset/task composition figures.
- `FinalReport/Evidence/Images/Irish Wav2Vec/`
  Wav2Vec results figures.
- `FinalReport/Evidence/Images/wav2vec_summary_chart_ulster_vs_Rest.png`
  Summary figure for the Ulster-vs-rest task.
- `FinalReport/Evidence/Images/TrainingWav2Vec_terminal1.png`
- `FinalReport/Evidence/Images/TrainingWav2Vec_terminal2.png`
- `FinalReport/Evidence/Images/TrainingWav2Vec_terminal3.png`
  Training evidence screenshots if you want appendix proof of runs.

## 8. Experiment Files Worth Citing in Methodology or Appendix

- `Experiments/AutoModels/scripts/run_batch.py`
- `Experiments/AutoModels/scripts/model_defs.py`
- `Experiments/AutoModels/scripts/task_defs.py`
- `Experiments/AutoModels/scripts/pipeline_utils.py`
  Core MFCC experiment automation files.
- `Experiments/AutoModels/results/irish_model_summary.csv`
- `Experiments/AutoModels/results/irish_model_summary_charts.xlsx`
  MFCC experiment outputs used to build tables/charts.
- `Experiments/AutoWav2VecIrish/scripts/run_batch.py`
- `Experiments/AutoWav2VecIrish/scripts/model_defs.py`
- `Experiments/AutoWav2VecIrish/scripts/task_defs.py`
- `Experiments/AutoWav2VecIrish/scripts/pipeline_utils_wav2vec.py`
  Core Wav2Vec experiment automation files.
- `Experiments/AutoWav2VecIrish/results/wav2vec_irish_summary.csv`
- `Experiments/AutoWav2VecIrish/results/wav2vec_irish_summary.xlsx`
  Wav2Vec experiment outputs used to build results tables/charts.
- `Experiments/AutoGlobalModels_cleaned/results/global_model_summary_cleaned_with_ni.xlsx`
  Cross-dataset/global comparison results if discussed in the report.
- `Experiments/ExperimentWriteUps/1_ClassProvinceBaseline.md`
- `Experiments/ExperimentWriteUps/2_Expanded_MFCC_Distributional_Features.md`
- `Experiments/ExperimentWriteUps/3_UlsterVsRest.md`
- `Experiments/ExperimentWriteUps/4_UlsterLeinsterRest.md`
- `Experiments/ExperimentWriteUps/5_DAIL_vs_NI.md`
  Concise experiment notes that are useful for reconstructing methodology and rationale while writing.

## 9. Code Screenshots / Snippets Already Prepared for the Report

- `FinalReport/Evidence/Images/Code/final_plugin_loader.png`
  Prepared code figure for the plugin registration logic.
- `FinalReport/Evidence/Images/Code/services_audio_fx_load_audio_from_bytes.png`
  Prepared code figure for audio preprocessing.
- `FinalReport/Evidence/Code/AutoModels_scripts_run_batch_py.png`
  Prepared figure for the experiment runner code.

## 10. Reference Material to Cite, Not Attach as Main Report Content

- `FinalReport/Evidence/Papers/`
  Background papers and supporting literature.
- `FinalReport/Examples/Artificial intelligent voice assistant Final project report: Angesh Kumar Chanderdip.pdf`
  Example report for structure/style comparison only.

## 11. Files That Should Not Be Included in the Report

- `Data/`
  Raw datasets belong in storage/submission bundles only if explicitly required, not in the report.
- `Prototype4/.venv/`
- `Prototype4/backend/.venv/`
- `Prototype4/backend/venv/`
  Virtual environments should never be included in a report.
- `__pycache__/`, `.pytest_cache/`, `.DS_Store`
  Generated files with no report value.
- `.joblib` model binaries
  Mention them in text if needed for reproducibility, but do not embed them in the report.
- Audio files and raw archives
  Too large and not useful in the written document unless specifically requested as supplementary material.

## Short Version: Minimum Set to Keep Beside You While Writing

If you only want the smallest useful working set, keep these open:

- `FinalReport/Submission1.docx`
- `FinalReport/Diagrams/SystemFlow.pptx`
- `FinalReport/Diagrams/FinalReportGanttChart.png`
- `Prototype4/readme.md`
- `Prototype4/backend/app.py`
- `Prototype4/backend/plugin_loader.py`
- `Prototype4/backend/services/audio.py`
- `Prototype4/backend/services/wav2vec_features.py`
- `Prototype4/backend/training/train_mfcc_logreg_v1_01.py`
- `Prototype4/backend/training/train_wav2vec_deploy.py`
- `Prototype4/frontend/recording.js`
- `Prototype4/frontend/predictions.js`
- `Prototype4/testing/SystemTests.xlsx`
- `FinalReport/Evidence/wav2vec_vs_mfcc.xlsx`
- `FinalReport/Evidence/speaker_counts.xlsx`
- `FinalReport/Evidence/Images/FullSystemRunthrough/`
- `FinalReport/Evidence/Images/Irish Wav2Vec/`
