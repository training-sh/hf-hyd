"""Run from Day54 with the notebook libraries and local MySQL available.
Seeds only missing fixture rows; intercepts all model/embedding requests.
"""
import ast
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
os.chdir(BASE)

import faiss
import mysql.connector
import nbformat
import numpy as np
from google.genai import types


def execute_cells(filename, tags):
    notebook = nbformat.read(BASE / filename, as_version=4)
    namespace = {}
    with contextlib.redirect_stdout(io.StringIO()):
        for cell in notebook.cells:
            if cell.cell_type == "code" and cell.metadata.get("tags", [None])[0] in tags:
                exec(compile(cell.source, filename, "exec"), namespace)
    return namespace


for path in BASE.glob("54*.ipynb"):
    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    for cell in notebook.cells:
        if cell.cell_type == "code" and not cell.source.startswith("%"):
            ast.parse(cell.source)
print("PASS: all four notebook schemas and code syntax")

connection = mysql.connector.connect(host="127.0.0.1", port=3306, user="root", password="root")
cursor = connection.cursor()
for statement in (BASE / "sql/542_order_db.sql").read_text().split(";"):
    if statement.strip():
        cursor.execute(statement)
connection.commit()
cursor.close()
connection.close()

ns = execute_cells("543_AgenticAI.ipynb", {"definition", "database", "example"})
summary = ns["sales_summary"]()
assert summary["matching_orders"] == 10
assert summary["total_units"] == 22
assert summary["average_units_per_matching_order"] == 2.2
assert summary["most_sold_product_ids"] == ["P018"]
assert summary["top_products"][0]["units_sold"] == 10
assert ns["sales_summary"](product_ids=[])["matching_orders"] == 0
assert ns["sales_summary"](product_ids=["P020"])["total_units"] == 0
assert ns["get_order_items"](order_id="O1002")["count"] == 2
assert ns["get_products"](product_ids=[])["count"] == 0
assert ns["seed_commerce"]() == {"products": 0, "orders": 0, "order_items": 0}
assert len(ns["reconcile_database"]()) == 10
for name, args in [
    ("get_orders", {"customer_id": "C001' OR 1=1"}),
    ("sales_summary", {"top_n": True}),
    ("sales_summary", {"top_n": 2.5}),
    ("get_products", {"category": "unknown"}),
    ("get_products", {"extra": 1}),
    ("search_products", {"query": "x", "max_price": float("nan")}),
]:
    assert ns["execute_tool"](name, args)["status"] == "error"
assert set(ns["sales_summary"](product_ids=["P007", "P014"])["most_sold_product_ids"]) == {"P007", "P014"}
print("PASS: live MySQL, repeatable seeds, line/header reconciliation, pandas metrics, tied leaders and argument checks")
print("Expected metrics:", json.dumps(summary))

# Re-run 542's real scoped queries; do not export intercepted model replies.
customer = execute_cells("542_OrderChatPrivacy.ipynb", {"local", "database"})
assert len(customer["fetch_my_order_items"]()) == 5
assert customer["fetch_my_order_items"]("O1004") == []
assert customer["fetch_my_orders"]("O1004' OR '1'='1") == []
assert customer["my_facts"]["calculations"]["total_amount"] == "4798.50"
captured_customer = []

class CustomerClient:
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    @property
    def models(self):
        return self
    def generate_content(self, **kwargs):
        captured_customer.append(copy.deepcopy(kwargs))
        return SimpleNamespace(text="Intercepted validation response; not Gemini output.")

customer["make_client"] = CustomerClient
with contextlib.redirect_stdout(io.StringIO()):
    notebook = nbformat.read(BASE / "542_OrderChatPrivacy.ipynb", as_version=4)
    for cell in notebook.cells:
        if cell.cell_type == "code" and cell.metadata.get("tags") == ["scenario"]:
            exec(cell.source, customer)
assert len(captured_customer) == 5
assert len(customer["transcript"]) == 10
for call in captured_customer:
    text = "\n".join(p.text or "" for c in call["contents"] for p in c.parts)
    assert all(value not in text for value in ["O1004", "C002", "charu@example.com", "root"])
assert '"order_items"' in captured_customer[3]["contents"][-1].parts[0].text
print("PASS: 542 customer-scoped joins and all ten scenarios with intercepted model requests")

# Execute 541 local cells against the shared catalogue.
retrieval = execute_cells("541_Faiss.ipynb", {"local"})
assert np.allclose(retrieval["manual_cosines"], [1, 1, 1 / np.sqrt(2), 0, -1])
assert len(retrieval["products"]) == 20
print("PASS: 541 local numeric/cosine exercises and shared catalogue")

# Actual FAISS operations with explicitly synthetic embeddings, isolated from real outputs.
original_client = ns["make_client"]
with tempfile.TemporaryDirectory(prefix="day54-543-") as temporary:
    os.chdir(temporary)
    folder = Path("output/541_faiss/semantic")
    folder.mkdir(parents=True)
    catalogue = ns["load_data"]("products.json")
    records = [dict(p, document=p["description"]) for p in catalogue]
    rng = np.random.default_rng(543)
    vectors = rng.normal(size=(20, 4)).astype("float32")
    faiss.normalize_L2(vectors)
    index = faiss.IndexFlatIP(4)
    index.add(vectors)
    manifest = {
        "schema_version": 1, "catalogue_sha256": ns["catalogue_digest"](catalogue),
        "normalized": True, "metric": "cosine_via_inner_product", "dimensions": 4,
        "product_count": 20, "row_product_ids": [p["product_id"] for p in records],
        "embedding_model": "synthetic-validation-only", "embedding_location": "test",
        "query_task": "RETRIEVAL_QUERY",
    }
    # Export through the actual 541 cell, then consume that exact bundle in 543.
    export_ns = dict(retrieval, semantic_index=index, product_embeddings=vectors,
                     query_vector=vectors[5:6].copy(), query_text="Synthetic validation query",
                     EMBEDDING_MODEL="synthetic-validation-only", EMBEDDING_LOCATION="test",
                     EMBEDDING_DIMENSIONS=4)
    export_cell = next(c for c in nbformat.read(BASE / "541_Faiss.ipynb", as_version=4).cells
                       if c.cell_type == "code" and '"catalogue_sha256"' in c.source)
    with contextlib.redirect_stdout(io.StringIO()):
        exec(export_cell.source, export_ns)
    manifest = json.loads((folder / "manifest.json").read_text())
    assert manifest["catalogue_sha256"] == ns["catalogue_digest"](catalogue)
    embedding_requests = []

    class EmbeddingClient(CustomerClient):
        def __init__(self, **kwargs):
            assert kwargs["location"] == "test"
        def embed_content(self, **kwargs):
            embedding_requests.append(kwargs)
            return SimpleNamespace(embeddings=[SimpleNamespace(values=vectors[5].tolist())])

    ns["make_client"] = EmbeddingClient
    matches = ns["search_products"]("rain hiking", category="hiking", max_price=3000)["matches"]
    assert matches[0]["product_id"] == "P006"
    assert {p["product_id"] for p in matches} == {"P006", "P007", "P009"}
    assert embedding_requests[0]["model"] == "synthetic-validation-only"
    assert ns["sales_summary"](product_ids=[p["product_id"] for p in matches])["total_units"] == 6
    assert ns["search_products"]("rain hiking", max_price=1)["matches"] == []
    manifest["catalogue_sha256"] = "stale"
    (folder / "manifest.json").write_text(json.dumps(manifest))
    assert ns["execute_tool"]("search_products", {"query": "rain"})["status"] == "error"
    assert "staged" in ns["get_order_chat_history"]("C001")["source"]
    export = Path("output/542_order_chat/C001.json")
    export.parent.mkdir(parents=True)
    export.write_text(json.dumps({"schema_version": 1, "customer_id": "C001", "source": "test export", "turns": [{"question": "test", "answer": "test"}]}))
    assert ns["get_order_chat_history"]("C001")["source"] == "test export"
    assert ns["execute_tool"]("get_order_chat_history", {"customer_id": "../C001"})["status"] == "error"
    os.chdir(BASE)
ns["make_client"] = original_client
print("PASS: FAISS search/filter/join, stale-bundle error, staged/exported history selection; synthetic vectors only")

# Exercise the actual agent loop with protocol-shaped Gemini responses.
def tool_part(name, arguments, call_id):
    return types.Part(function_call=types.FunctionCall(name=name, args=arguments, id=call_id), thought_signature=b"opaque-test-signature")


def model_response(parts):
    return types.GenerateContentResponse(candidates=[types.Candidate(content=types.Content(role="model", parts=parts))])

responses = [
    model_response([tool_part("get_orders", {"customer_id": "C001"}, "one"), tool_part("get_order_items", {"order_id": "O1002"}, "two")]),
    model_response([tool_part("sales_summary", {}, "three"), tool_part("get_order_chat_history", {"customer_id": "C001"}, "four")]),
    model_response([types.Part.from_text(text="Validation final answer")]),
]
captured = []

class AgentClient(CustomerClient):
    def generate_content(self, **kwargs):
        captured.append(copy.deepcopy(kwargs["contents"]))
        return responses.pop(0)

ns["make_client"] = AgentClient
with contextlib.redirect_stdout(io.StringIO()):
    assert ns["run_agent"]("Validate order analysis") == "Validation final answer"
assert len(captured) == 3
assert captured[1][1].parts[0].thought_signature == b"opaque-test-signature"
assert [p.function_response.id for p in captured[1][2].parts] == ["one", "two"]
assert all(p.function_response.response["status"] == "ok" for p in captured[1][2].parts)
completed = copy.deepcopy(ns["agent_history"])
responses[:] = [model_response([types.Part.from_text(text="Validation follow-up")])]
with contextlib.redirect_stdout(io.StringIO()):
    ns["run_agent"]("Continue")
assert len(captured[-1]) == len(completed) + 1
completed = copy.deepcopy(ns["agent_history"])
ns["MAX_TOOL_CALLS"] = 1
responses[:] = [model_response([tool_part("get_orders", {}, "five"), tool_part("sales_summary", {}, "six")])]
with contextlib.redirect_stdout(io.StringIO()):
    assert ns["run_agent"]("Exercise call cap") is None
assert ns["agent_history"] == completed
ns["MAX_TOOL_CALLS"] = 12
ns["MAX_MODEL_ROUNDS"] = 1
responses[:] = [model_response([tool_part("missing_tool", {}, "seven")])]
with contextlib.redirect_stdout(io.StringIO()):
    assert ns["run_agent"]("Exercise round cap") is None
assert ns["agent_history"] == completed
print("PASS: multi-round/multi-call protocol, call IDs, opaque metadata, follow-up history and loop limits")
print("No live Gemini generation or embedding calls were made; no simulated outputs were saved in notebooks.")
