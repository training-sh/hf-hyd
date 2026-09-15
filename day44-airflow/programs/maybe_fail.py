"""Choose normal completion, sys.exit(7), or an unhandled Python exception."""
import argparse
import json
import sys
p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--mode", choices=["success", "exit", "crash"], required=True)
args = p.parse_args()
if args.mode == "exit":
    print("Requested failure: exiting with code 7", file=sys.stderr)
    sys.exit(7)
if args.mode == "crash":
    raise RuntimeError("Demonstration of an unhandled exception")
print(json.dumps({"status": "ok", "message": "Program finished normally"}))
sys.exit(0)
