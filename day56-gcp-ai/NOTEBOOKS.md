# Notebook index

| Notebook | Topic | Default cost |
|---|---|---|
| [01-basic-agent-and-runner](01-basic-agent-and-runner.ipynb) | Your first ecommerce agent | 1 small Lite call |
| [02-function-tools-and-order-items](02-function-tools-and-order-items.ipynb) | Function tools and business calculations | Lite model calls |
| [03-structured-output-and-input-schemas](03-structured-output-and-input-schemas.ipynb) | Structured invoice extraction | 2 small Lite calls |
| [04-sessions-state-and-context](04-sessions-state-and-context.ipynb) | Conversation, state and tool context | About 3 Lite calls |
| [05-sqlite-session-persistence](05-sqlite-session-persistence.ipynb) | Persistent sessions with SQLite | 1 Lite call; local SQLite |
| [06-sequential-workflow](06-sequential-workflow.ipynb) | Sequential invoice workflow | About 4 Lite calls |
| [07-parallel-workflow-and-join](07-parallel-workflow-and-join.ipynb) | Parallel checks and a join | About 5 Lite calls |
| [08-loop-workflow-and-exit](08-loop-workflow-and-exit.ipynb) | Bounded review loops | 1–2 Lite calls |
| [09-agent-routing-and-handoffs](09-agent-routing-and-handoffs.ipynb) | Specialist agents and handoffs | About 3 Lite calls |
| [10-agent-as-a-tool](10-agent-as-a-tool.ipynb) | Agents as tools | About 4 Lite calls |
| [11-custom-agent-deterministic-routing](11-custom-agent-deterministic-routing.ipynb) | Custom BaseAgent orchestration | 1 Lite call |
| [12-callbacks-and-guardrails](12-callbacks-and-guardrails.ipynb) | Lifecycle callbacks and guardrails | 0 calls for blocked text; about 2 for tool guard |
| [13-plugins-and-observability](13-plugins-and-observability.ipynb) | App-wide plugins and usage | Lite model calls |
| [14-artifacts-and-invoice-files](14-artifacts-and-invoice-files.ipynb) | Versioned artifacts | Lite model calls |
| [15-memory-across-sessions](15-memory-across-sessions.ipynb) | Memory across conversations | About 3 Lite calls; no managed memory charges |
| [16-faiss-local-rag](16-faiss-local-rag.ipynb) | Local FAISS retrieval-augmented generation | About 2 Lite calls; FAISS and vectors are local |
| [17-document-parsing-and-multimodal](17-document-parsing-and-multimodal.ipynb) | Parse a PDF invoice with Gemini Lite | 1 Lite multimodal call |
| [18-events-streaming-and-cancellation](18-events-streaming-and-cancellation.ipynb) | Events, streaming and cancellation | 1 streamed Lite call |
| [19-planning-and-thinking](19-planning-and-thinking.ipynb) | Planning and bounded reasoning | Several bounded Lite calls |
| [20-human-confirmation-before-actions](20-human-confirmation-before-actions.ipynb) | Human confirmation for refunds | Lite model calls |
| [21-long-running-tools](21-long-running-tools.ipynb) | Long-running fulfillment jobs | Lite model calls |
| [22-openapi-tools-local-service](22-openapi-tools-local-service.ipynb) | OpenAPI tools against a local API | About 2 Lite calls; local HTTP server |
| [23-mcp-tools-local-server](23-mcp-tools-local-server.ipynb) | MCP tools with a local server | Optional: about 2 Lite calls |
| [24-tool-authentication](24-tool-authentication.ipynb) | Tool authentication and credentials | Lite model calls |
| [25-app-resumability-and-compaction](25-app-resumability-and-compaction.ipynb) | App configuration, compaction and caching | 1 Lite call by default; cache construction only |
| [26-evaluation-and-regression](26-evaluation-and-regression.ipynb) | Evaluate tool use and factual output | About 2 Lite calls; native eval is explicit opt-in |
| [27-adk-web-api-and-deployment](27-adk-web-api-and-deployment.ipynb) | Package an agent for ADK Web and API | About 2 Lite calls; no cloud deployment |
| [28-a2a-local-agent-service](28-a2a-local-agent-service.ipynb) | Agent-to-Agent protocol | Optional: remote Lite calls on the same VM |
| [29-grounding-and-code-execution](29-grounding-and-code-execution.ipynb) | Built-in search and code execution | Construction free; optional Flash and grounding charges |
| [30-live-bidirectional-streaming](30-live-bidirectional-streaming.ipynb) | Live audio and bidirectional sessions | No default call; optional Live model audio billing |
| [31-adk2-graph-workflows](31-adk2-graph-workflows.ipynb) | ADK 2 graphs and typed data | Zero model calls |
| [32-dynamic-workflows-and-retries](32-dynamic-workflows-and-retries.ipynb) | Dynamic orchestration and retry policy | Zero model calls |
| [33-agent-skills](33-agent-skills.ipynb) | Reusable skills for agents | Several bounded Lite calls |
| [34-session-rewind](34-session-rewind.ipynb) | Rewind session history | 2 small Lite calls |
| [35-capstone-return-review](35-capstone-return-review.ipynb) | Capstone: ecommerce return review | About 3 Lite calls; local FAISS |
| [36-graph-human-input-and-resume](36-graph-human-input-and-resume.ipynb) | Pause a graph and resume with human input | Zero model calls |
| [37-custom-models-and-offline-adapters](37-custom-models-and-offline-adapters.ipynb) | Custom model adapters and offline execution | Zero model calls |
