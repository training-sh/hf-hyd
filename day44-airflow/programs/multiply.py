"""python multiply.py --value 5 --factor 10 -> JSON dictionary on stdout."""
import argparse
import json
p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--value", type=int, required=True)
p.add_argument("--factor", type=int, default=10)
args = p.parse_args()
print(json.dumps({"input": args.value, "factor": args.factor, "result": args.value * args.factor}))
