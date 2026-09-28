# Basic Python AI labs on GCP

A simple hello world level AI project for brainstorming AI related technologies. Data is staged.

Eight starter notebooks, approximately 4-5 hours plus exercises. Prerequisites: basic Python functions, lists and dictionaries. All files belong in this AI folder; launch Jupyter here so local imports work. No passwords, tokens or service-account keys are included.

We may use PluralSight or HF account depends on that works well, less restrictive. 

## Start here

New to the Google Cloud console? Follow the [GCP getting-started guide](GCP_GETTING_STARTED.md) for project selection/creation, API and IAM setup, a first Studio prompt, local or hosted notebook setup, and a UI-to-notebook map for all eight modules.

1. Sign into your active Pluralsight sandbox in a separate browser profile. Check its remaining time and assigned project. The configured project is `gcp-ai-sandb-111-123456673`; update `course_config.py` when the sandbox changes.
2. Use local Python 3.10+ and Google Cloud CLI, or upload this entire folder to a Python notebook environment provided by your lab. A lab-provided notebook avoids creating a new paid Workbench instance. Do not assume that every Pluralsight sandbox permits Vertex AI, all models, or all regions.
3. In a terminal inside this folder, create the Python environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

4. For **local Windows execution**, authenticate using the sandbox account in the browser opened by gcloud:

```powershell
gcloud auth login
gcloud config set project gcp-ai-sandb-403-96741179
gcloud auth application-default login
gcloud auth application-default set-quota-project gcp-ai-sandb-403-96741179
```

The first login authenticates CLI commands; the application-default login authenticates Python. The quota-project command can fail if the lab account lacks service usage permissions. Use the project and identity supplied by the lab; consult its instructions if access is restricted. Never paste the account password into a notebook or configuration file.

5. Confirm the Vertex AI API is enabled in the sandbox console. If disabled and the lab allows enabling it:

```powershell
gcloud services enable aiplatform.googleapis.com --project=gcp-ai-sandb-403-96741179
```

6. Launch Jupyter:

```powershell
.\.venv\Scripts\python.exe -m jupyterlab
```

Open `00_setup_and_first_call.ipynb` and run its cells in order. On Linux/Cloud Shell, use `.venv/bin/python` instead of the Windows executable path. In a lab-provided hosted notebook, use its Python kernel and install with `%pip install -r requirements.txt`; restart the kernel after installation. A hosted service account must have the required model access. Run notebook 00 to check ADC before adding another authentication method.

## Learning path

| Notebook | What you build | Approximate model traffic per run |
| --- | --- | --- |
| 00 | Authentication check and first Gemini response | 1 generation |
| 01 | Prompt comparisons, chat and streaming | 5 generations |
| 02 | Token counts, usage and a context budget | 1 generation and up to 10 token counts |
| 03 | Validated JSON and image understanding | 2 generations |
| 04 | Vector similarity and semantic search | 6 embedding inputs |
| 05 | Chunked RAG with citations and abstention | Small index, 2 query embeddings, 2 generations |
| 06 | Agent with search and arithmetic tools | Small index, up to 5 model turns and 6 tool calls |
| 07 | Retrieval and answer evaluation, capstone | Small index, 9 query embeddings, 4 generations |

Each notebook explains the concept, gives runnable examples and ends with exercises. Notebooks 04-07 build small in-memory indexes independently; restarting or rerunning them repeats embedding requests. Calls consume the sandbox's quota and may incur usage charges under its terms. No storage buckets, deployments or managed vector indexes are created by the notebooks.

## Model settings

Edit `course_config.py`, or set its environment variables before launching Jupyter. Generation uses `global`; embeddings use `us-central1`. Change either if your lab imposes regional restrictions.

The default `gemini-2.5-flash` is a teaching baseline, not a claim that it is the latest model or enabled in your lab. Google's lifecycle page checked on September 18, 2026 lists its retirement as October 20, 2026. Set `GEMINI_MODEL` to a supported replacement when needed and rerun the labs to verify behavior. Embeddings use `gemini-embedding-001` with 768 dimensions. Do not mix vectors from different models or dimensions.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Local helper module not found | Launch Jupyter from AI and keep the helper files beside the notebooks. |
| Credentials missing / 401 | Authenticate ADC as the sandbox user; browser console login alone is insufficient. |
| Permission denied / 403 | Project, lab expiry, API enablement and lab-provided IAM/model restrictions. |
| Model not found / 404 | Model lifecycle, spelling, endpoint region and sandbox availability. |
| Resource exhausted / 429 | Wait, reduce calls and check lab quotas. |
| No text / truncated answer | Inspect finish reasons and usage; increase output budget cautiously if needed. |
| Import or SDK error | Confirm Jupyter uses the environment where requirements were installed. |

Dependencies have broad compatibility bounds; this is not a locked, cloud-tested environment. After a successful sandbox run, you may save `python -m pip freeze > requirements-tested.txt` from that environment for reproducibility.

## What has been verified

All eight notebooks passed JSON/basic-structure checks and all 28 code cells passed Python syntax checks. Offline chunking and cosine-similarity checks passed. Full nbformat schema validation was blocked by a permission error in the existing environment's regex dependency; use the clean environment above. Live model access, sandbox IAM and model output require running notebook 00 with valid credentials. The included dataset is entirely fictional. The vector index is an exact NumPy search intended to make retrieval mechanics visible.

## Official references

- [Google Gen AI SDK](https://googleapis.github.io/python-genai/)
- [SDK source and examples](https://github.com/googleapis/python-genai)
- [GCP Gemini quickstart](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/start/quickstart)
- [Text embeddings](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/embeddings/get-text-embeddings)
- [Function calling](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/function-calling)
- [Model versions and lifecycle](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/learn/model-versions)

Some current Google documentation redirects Vertex AI pages to Gemini Enterprise Agent Platform branding. These labs use the Google Gen AI SDK's Vertex AI client interface and GCP ADC authentication.
