# FYP
Directory for Final Year Project

## Submission

Create a clean submission bundle from the current working tree with:

```bash
./scripts/create_submission_zip.sh
```

The script writes a zip file into `submission/` and excludes bulky folders such as raw data, virtual environments, caches, and `.git`.
By default it packages `README.md`, `Prototype4/`, and `FinalReport/`.
