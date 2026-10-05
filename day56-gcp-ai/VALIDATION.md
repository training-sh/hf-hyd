# Validation on aadhi

Environment: Python 3.12, google-adk 2.10.0, google-genai 2.25.0, faiss-cpu 1.13.2.

All 37 notebooks passed notebook-format and Python syntax checks. 27 notebooks had selected runtime execution: 25 covered live Lite or local workflows; 29 and 30 exercised configuration only. No full paid course sweep or cloud deployment was performed.

The SSL bypass was separately verified with ADC refresh and one tiny Lite response. A transient DNS failure during the first callback run passed on retry. Schema, dynamic-workflow and rewind issues discovered during execution were corrected and rerun successfully. Optional MCP/A2A dependencies remain uninstalled. Live audio, grounding, provider code execution, native CLI evaluation, cache creation and compaction summarization were not exercised.

| Notebook | Verification |
|---|---|
| [01-basic-agent-and-runner.ipynb](01-basic-agent-and-runner.ipynb) | Executed successfully |
| [02-function-tools-and-order-items.ipynb](02-function-tools-and-order-items.ipynb) | Syntax checked; not executed |
| [03-structured-output-and-input-schemas.ipynb](03-structured-output-and-input-schemas.ipynb) | Executed successfully |
| [04-sessions-state-and-context.ipynb](04-sessions-state-and-context.ipynb) | Syntax checked; not executed |
| [05-sqlite-session-persistence.ipynb](05-sqlite-session-persistence.ipynb) | Executed successfully |
| [06-sequential-workflow.ipynb](06-sequential-workflow.ipynb) | Syntax checked; not executed |
| [07-parallel-workflow-and-join.ipynb](07-parallel-workflow-and-join.ipynb) | Syntax checked; not executed |
| [08-loop-workflow-and-exit.ipynb](08-loop-workflow-and-exit.ipynb) | Executed successfully |
| [09-agent-routing-and-handoffs.ipynb](09-agent-routing-and-handoffs.ipynb) | Syntax checked; not executed |
| [10-agent-as-a-tool.ipynb](10-agent-as-a-tool.ipynb) | Syntax checked; not executed |
| [11-custom-agent-deterministic-routing.ipynb](11-custom-agent-deterministic-routing.ipynb) | Syntax checked; not executed |
| [12-callbacks-and-guardrails.ipynb](12-callbacks-and-guardrails.ipynb) | Executed successfully |
| [13-plugins-and-observability.ipynb](13-plugins-and-observability.ipynb) | Executed successfully |
| [14-artifacts-and-invoice-files.ipynb](14-artifacts-and-invoice-files.ipynb) | Executed successfully |
| [15-memory-across-sessions.ipynb](15-memory-across-sessions.ipynb) | Executed successfully |
| [16-faiss-local-rag.ipynb](16-faiss-local-rag.ipynb) | Executed successfully |
| [17-document-parsing-and-multimodal.ipynb](17-document-parsing-and-multimodal.ipynb) | Executed successfully |
| [18-events-streaming-and-cancellation.ipynb](18-events-streaming-and-cancellation.ipynb) | Executed successfully |
| [19-planning-and-thinking.ipynb](19-planning-and-thinking.ipynb) | Syntax checked; not executed |
| [20-human-confirmation-before-actions.ipynb](20-human-confirmation-before-actions.ipynb) | Executed successfully |
| [21-long-running-tools.ipynb](21-long-running-tools.ipynb) | Executed successfully |
| [22-openapi-tools-local-service.ipynb](22-openapi-tools-local-service.ipynb) | Executed successfully |
| [23-mcp-tools-local-server.ipynb](23-mcp-tools-local-server.ipynb) | Syntax checked; optional dependency absent on VM |
| [24-tool-authentication.ipynb](24-tool-authentication.ipynb) | Executed successfully |
| [25-app-resumability-and-compaction.ipynb](25-app-resumability-and-compaction.ipynb) | Executed successfully |
| [26-evaluation-and-regression.ipynb](26-evaluation-and-regression.ipynb) | Executed successfully |
| [27-adk-web-api-and-deployment.ipynb](27-adk-web-api-and-deployment.ipynb) | Agent executed successfully; final CLI help checked separately |
| [28-a2a-local-agent-service.ipynb](28-a2a-local-agent-service.ipynb) | Syntax checked; optional dependency absent on VM |
| [29-grounding-and-code-execution.ipynb](29-grounding-and-code-execution.ipynb) | Configuration cells executed; cloud demo intentionally not run |
| [30-live-bidirectional-streaming.ipynb](30-live-bidirectional-streaming.ipynb) | Configuration cells executed; cloud demo intentionally not run |
| [31-adk2-graph-workflows.ipynb](31-adk2-graph-workflows.ipynb) | Executed successfully |
| [32-dynamic-workflows-and-retries.ipynb](32-dynamic-workflows-and-retries.ipynb) | Executed successfully |
| [33-agent-skills.ipynb](33-agent-skills.ipynb) | Executed successfully |
| [34-session-rewind.ipynb](34-session-rewind.ipynb) | Executed successfully |
| [35-capstone-return-review.ipynb](35-capstone-return-review.ipynb) | Executed successfully |
| [36-graph-human-input-and-resume.ipynb](36-graph-human-input-and-resume.ipynb) | Executed successfully |
| [37-custom-models-and-offline-adapters.ipynb](37-custom-models-and-offline-adapters.ipynb) | Executed successfully |
