"""Generate deterministic fictional sales and optionally stage them in HDFS."""
import argparse
import random
import subprocess
from datetime import date, timedelta

import duckdb
import pandas as pd

from config import ROOT, HDFS_BIN, HDFS_FILE


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hdfs", action="store_true")
    args = parser.parse_args()
    rng = random.Random(60)
    rows = []
    for i in range(1, 5001):
        quantity = rng.randint(1, 8)
        revenue = round(quantity * rng.uniform(150, 2500), 2)
        rows.append((i, date(2026, 1, 1) + timedelta(days=rng.randrange(180)),
                     rng.choice(["North", "South", "East", "West"]),
                     rng.choice(["Electronics", "Furniture", "Office", "Clothing"]),
                     quantity, revenue, round(revenue * rng.uniform(.08, .35), 2)))
    frame = pd.DataFrame(rows, columns=["order_id", "order_date", "region", "category", "quantity", "revenue", "profit"])
    (ROOT / "data").mkdir(exist_ok=True)
    csv_path = ROOT / "data/sales.csv"
    frame.to_csv(csv_path, index=False)
    with duckdb.connect() as con:
        con.register("sales", frame)
        target = str(ROOT / "data/sales.parquet").replace("'", "''")
        con.execute(f"COPY sales TO '{target}' (FORMAT PARQUET)")
    if args.hdfs:
        directory = HDFS_FILE.rsplit("/", 1)[0]
        subprocess.run([HDFS_BIN, "dfs", "-mkdir", "-p", directory], check=True, timeout=60)
        subprocess.run([HDFS_BIN, "dfs", "-put", "-f", str(csv_path), HDFS_FILE], check=True, timeout=60)
    print(f"Staged {len(frame)} rows locally" + (f" and in {HDFS_FILE}" if args.hdfs else ""))


if __name__ == "__main__":
    main()
