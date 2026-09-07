"""Recreate the D381 samples locally; never connects to Snowflake.

Run: python D38_SnowFlake/data/stage_practical/generate_samples.py
Optional binary dependencies: python -m pip install pyarrow fastavro
Re-running overwrites only this generator's named sample files.
"""
import csv
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
ROWS = [
    {"order_id": 101, "customer": "Asha", "city": "Chennai", "amount": 1250.50},
    {"order_id": 102, "customer": "Ravi", "city": "Bengaluru", "amount": 800.00},
    {"order_id": 103, "customer": "Meena", "city": "Hyderabad", "amount": 1499.50},
]


def generate():
    for name in ("csv", "json", "xml", "avro", "parquet", "raw"):
        (ROOT / name).mkdir(parents=True, exist_ok=True)
    with (ROOT / "csv/orders.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(ROWS[0]))
        writer.writeheader()
        writer.writerows(ROWS)
    events = [dict(row, channel="web", items=[{"sku": "BOOK", "qty": 1}]) for row in ROWS]
    (ROOT / "json/orders.json").write_text(json.dumps(events, indent=2) + "\n", encoding="utf-8")
    root = ET.Element("orders")
    for row in ROWS:
        order = ET.SubElement(root, "order", {"id": str(row["order_id"])})
        for name in ("customer", "city", "amount"):
            ET.SubElement(order, name).text = str(row[name])
    ET.indent(root, space="  ")
    ET.ElementTree(root).write(ROOT / "xml/orders.xml", encoding="utf-8", xml_declaration=True)
    (ROOT / "raw/notes.txt").write_text("Stage practical sample\nBatch: D381\nExpected orders: 3\n", encoding="utf-8")
    schema = {"type": "record", "name": "Order", "namespace": "training",
              "fields": [{"name": "order_id", "type": "long"},
                         {"name": "customer", "type": "string"},
                         {"name": "city", "type": "string"},
                         {"name": "amount", "type": "double"}]}
    (ROOT / "avro/orders.avsc").write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    try:
        from fastavro import writer, parse_schema
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError:
        print("CSV, JSON, XML, TXT and Avro schema created. Install pyarrow and fastavro for binaries.")
        return
    with (ROOT / "avro/orders.avro").open("wb") as f:
        writer(f, parse_schema(schema), ROWS, codec="null")
    pq.write_table(pa.Table.from_pylist(ROWS), ROOT / "parquet/orders.parquet", compression="snappy")
    print("Created CSV, JSON, XML, Avro, Parquet, and raw text samples in", ROOT)


if __name__ == "__main__":
    generate()
