# Google ADK: ecommerce notebooks

37 numbered, self-contained Python notebooks for **ADK 2.10.0**, using orders,
customers, products, order items, invoices and returns. Start with
[01-basic-agent-and-runner.ipynb](01-basic-agent-and-runner.ipynb).
See [NOTEBOOKS.md](NOTEBOOKS.md) for the complete sequence and cost notes.

Open this folder in Jupyter on `aadhi` and select the existing `dataengenv`
Python kernel. Run each notebook top to bottom. No activation or login cells
are included. Sessions are isolated per notebook; in-memory data disappears
when the kernel ends. All data is synthetic. No examples send emails, charge
cards, deploy services or create a managed vector database.

## Shared configuration

Edit [config.json](config.json), then restart the kernel:

- Project: `gen-lang-client-0367558705`.
- Backend: Vertex AI using your existing Application Default Credentials.
- Location: `global`; model: `gemini-2.5-flash-lite`.
- Small output limits and at most 10 model calls per invocation.
- `skip_ssl_validation`: defaults to `true` for your requested corporate-proxy
  workaround. This bypasses certificate validation for Gemini HTTP and ADC
  refresh. Set it to `false` outside this training setup. A trusted corporate
  CA bundle via `ca_bundle` is also supported when bypass is disabled.
- Existing `HTTPS_PROXY`/`HTTP_PROXY` settings are honored. For local service
  labs, include `127.0.0.1,localhost` in `NO_PROXY` when using a proxy.
- `enable_optional_cloud_demos`: defaults to `false`. Only notebooks 29 and
  30 use this switch. Live streaming also requires an available `live_model`
  and supported location; Lite is not a Live audio model.

Environment overrides: `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`,
`GEMINI_MODEL`, `ADK_SKIP_SSL_VALIDATION`, `ADK_CA_BUNDLE`.
Never put tokens or ADC JSON in notebooks or this directory.

`course.py` handles only configuration, service creation and event printing.
Teaching examples define their agents, tools and workflows inside the notebooks.
The ADK 2.10 Gemini transport is configured through `client_kwargs`.

## Cost and dependencies

Most notebooks make 1–5 short Lite calls. Parallel agents still consume tokens
for each branch. Loops are capped. FAISS uses local hashed word-count vectors;
there is no hosted vector store, no embedding API bill and no model download.
These lexical vectors are deliberately simple; semantic search is an extension.
SQLite, local HTTP, deterministic graph demos and local index operations have
no model charges. PDF parsing makes one multimodal Lite call.

Core dependencies are already on `aadhi`. Reference versions are in
`requirements-reference.txt`; do not reinstall the environment to start.
MCP (23) and A2A (28) explain optional dependencies and report a clear skip if
they are missing. The optional built-in tools use Flash where Lite does not
support the capability. No code silently switches to an expensive model.

## Coverage and scope

Covered: LLM agents, typed tools, schemas, instructions, context, sessions,
state scopes, SQLite, sequential/parallel/loop workflows, handoffs, AgentTool,
custom agents, callbacks, plugins, events, usage tracking, artifacts, memory,
FAISS RAG, multimodal PDF extraction, SSE, cancellation, planning, confirmation,
long-running tools, OpenAPI, bearer authentication, MCP, A2A, App policies,
compaction/cache configuration, evaluation, local Web/API packaging, Live
queue code, ADK 2 graphs, dynamic workflows, retry configuration, skills,
session rewind, graph human-input/resume, custom model adapters, and an
integrated return-review capstone.

This is a practical feature-family course, not every integration or every
option in ADK. The following require external infrastructure or additional
accounts and are intentionally not provisioned: managed agents, managed memory,
Vertex RAG, BigQuery/Spanner/AlloyDB tools, GCS artifacts, OAuth provider setup,
Cloud Run/GKE/Agent Engine deployment, paid telemetry exporters, third-party
models, and LLM-judge/user-simulation evaluation. Local substitutes and extension
points are explained where relevant. Cache and compaction policies are configured
without forcing paid cache creation or summarization in the default run.

## Files and local services

- `data/`: small ecommerce fixture and sample PDF invoice.
- `local_rag.py`: FAISS index and deterministic local vectorizer.
- `local_api.py`, `mcp_server.py`, `a2a_server.py`: teaching services.
- `shop_app/`: agent package for `adk web`, `adk api_server` and `adk eval`.
- `evals/`: native ADK evaluation case and tool-trajectory-only criteria.
- `.runtime/`: generated local databases, indexes, audio and logs (ignored).
- `build_notebooks.py`: standard-library generator used to maintain the lessons.
- `validate_course.py`: lightweight structure checks and explicitly selected
  execution; it does not run the full paid course automatically.

For ADK Web, from this directory run `adk web --host 127.0.0.1 --port 8000 .`.
From your workstation, forward with
`ssh -i ~/.ssh/gopsub -L 8000:127.0.0.1:8000 ajivaka@aadhi`, then open
`http://127.0.0.1:8000`. SSH needs its normal host-key verification; the SSL
workaround here concerns Python HTTPS requests through corporate proxies.

## Troubleshooting

- 401/403: check the existing ADC account, project access and Vertex AI API;
  TLS bypass does not fix IAM or billing permissions.
- 404 model: change the configured model/location to one enabled in the project.
- 429: wait and reduce calls; examples do not retry in an unbounded loop.
- Certificate failure: use the CA bundle or the explicit SSL bypass, then
  restart the kernel. A firewall blocking WebSockets needs separate resolution.
- Import mismatch: use the inspected ADK 2.10.0 environment. APIs differ from
  older tutorials; do not mix version-specific examples.
- Missing optional dependency: follow that notebook's one-time installation note.

Official references: [ADK documentation](https://adk.dev/),
[ADK Python source](https://github.com/google/adk-python),
[Gemini Flash-Lite](https://ai.google.dev/gemini-api/docs/models/gemini-2.5-flash-lite).
