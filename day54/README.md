# Day54 - Tokens, Retrieval, Order Chat, and Agentic Analytics

Use the existing notebook environment and Google Application Default Credentials (ADC). Each notebook begins with only its required library installs. Run from Day54 so shared files and helper modules resolve.

| Notebook | What it demonstrates |
| --- | --- |
| [540_TokenIntroduction.ipynb](540_TokenIntroduction.ipynb) | Gemini tokens, token pieces, reconstruction, and an optional cloud count |
| [541_Faiss.ipynb](541_Faiss.ipynb) | Numeric vectors, cosine similarity, semantic product search, and a saved FAISS bundle |
| [542_OrderChatPrivacy.ipynb](542_OrderChatPrivacy.ipynb) | Explicit Python routing, customer-scoped orders/items, system context, history and summary |
| [543_AgenticAI.ipynb](543_AgenticAI.ipynb) | Model-selected functions combining MySQL, FAISS, chat history and pandas |

## Shared configuration and data

Google model, project, and location settings are shared in `course_config.py`. The local MySQL connection is in `commerce_data.py` and uses the requested root/root credentials with database `order_db`.

The [shared dataset](data/README.md) contains 20 products, 10 orders, 18 order lines, 22 units, and six explicitly staged chat examples. Product IDs connect the FAISS catalogue to MySQL purchases. Original order totals are preserved; line items reconcile exactly. Sale prices represent historical prices, not necessarily current catalogue prices.

Run the updated [SQL schema](sql/542_order_db.sql) once if the products and order-items tables do not yet exist. The 542 and 543 notebooks show the `mysql -u root -p` and `SOURCE` commands. Seeds insert missing records and reject conflicting existing fixture values.

## Notebook handoffs

1. 541 reads `data/products.json` and writes `output/541_faiss/semantic/` after successful Google embedding calls. Its index, metadata, and catalogue hash are used by 543. Re-export an older bundle that lacks the shared catalogue hash.
2. 542 joins the same products to order items while keeping customer-scoped SQL. After its model scenarios and final summary succeed, it exports `output/542_order_chat/C001.json`.
3. 543 uses that chat export when present, or explicitly labels the staged fallback. Its analyst/warehouse-manager role can read all orders; 542 retains its separate customer-support privacy behavior.

The 543 agent exposes six read-only functions: catalogue lookup, order lookup, order-item lookup, pandas sales metrics, conversation history, and FAISS product search. Its trace prints function names, arguments, results, and the final answer. The model has no arbitrary SQL/Python executor. Each question is limited to eight model rounds and twelve function calls.

The semantic bundle requires actual embedding calls in 541. SQL and pandas examples can run before that bundle exists. Agent examples require live access to the configured generation model. See [541_RAG_HANDOFF.md](541_RAG_HANDOFF.md) for the retrieval file contract.

## Verified behavior

- All four notebook schemas and Python cell syntax validate.
- 540's local example reconstructs its input exactly: 16 words and 19 tokens. SentencePiece is pinned to 0.2.1 because 0.2.2 removed an API used by this SDK.
- 541's numeric distance, cosine calculations and numeric persistence pass local execution checks.
- The updated schema and shared seed ran against local MySQL 8. All 10 order headers reconcile with line quantities and historical prices. Repeated seeds insert zero rows.
- pandas returns 22 units, INR 24,892.50 revenue, 2.2 units per order, and P018 as the most-sold product with 10 units.
- 542's customer-scoped joins and ten scenarios pass with intercepted model requests. No other customer's records enter those requests.
- 543's FAISS filtering and joins are checked with synthetic vectors in temporary files. Multi-step/multi-call agent tests check argument validation, function-response IDs, model metadata, follow-up history, missing tools and call limits.

Live Gemini generation and embedding quality have not been verified in this workspace. Test responses and synthetic vectors are not saved as real notebook output. Execution checks used Windows; Ubuntu CPU library installation was not separately exercised.

For a repeatable validation run, use `python tests/validate_543.py` with the notebook libraries and `nbformat` available. This checks the local MySQL fixture and intercepts all model calls.
