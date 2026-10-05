"""Structure checks are free. --run accepts explicit notebook number prefixes."""
import argparse
import ast
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", nargs="*", default=[])
    args = parser.parse_args()
    import nbformat
    notebooks = sorted(ROOT.glob("[0-9][0-9]-*.ipynb"))
    for path in notebooks:
        doc = nbformat.read(path, as_version=4)
        nbformat.validate(doc)
        for idx, cell in enumerate(doc.cells):
            if cell.cell_type == "code":
                compile(cell.source, f"{path.name}:cell{idx}", "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
    for path in ROOT.rglob("*.py"):
        if ".runtime" not in path.parts:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
    print(f"PASS: structure and Python syntax for {len(notebooks)} notebooks", flush=True)
    report = ROOT / "validation" / "results.json"
    results = json.loads(report.read_text()) if report.exists() else []
    results = [r for r in results if r["notebook"][:2] not in args.run]
    for path in notebooks:
        if path.name[:2] not in args.run:
            continue
        from nbclient import NotebookClient
        doc = nbformat.read(path, as_version=4)
        start = time.monotonic()
        try:
            NotebookClient(doc, timeout=150, kernel_name="python3", resources={"metadata": {"path": str(ROOT)}}).execute()
            results.append({"notebook": path.name, "status": "passed", "seconds": round(time.monotonic()-start, 1)})
            print("PASS:", path.name, flush=True)
        except Exception as error:
            results.append({"notebook": path.name, "status": "failed", "error": str(error)[-6000:]})
            print("FAIL:", path.name, str(error)[-2500:], flush=True)
        output = ROOT / "validation"
        output.mkdir(exist_ok=True)
        nbformat.write(doc, output / path.name)
    if args.run:
        target = ROOT / "validation" / "results.json"
        target.write_text(json.dumps(results, indent=2))
        if any(r["status"] == "failed" for r in results):
            raise SystemExit(1)


if __name__ == "__main__":
    main()
