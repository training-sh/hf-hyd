"""python add.py --a 2 --b 3 -> JSON dictionary on stdout."""
import argparse
import json
p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--a", type=int, required=True)
p.add_argument("--b", type=int, required=True)
args = p.parse_args()
# Keep stdout machine-readable; diagnostic messages can go to stderr.
print(json.dumps({"a": args.a, "b": args.b, "sum": args.a + args.b}))
