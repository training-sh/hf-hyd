"""Shared local MySQL seed data for notebooks 542 and 543."""
import hashlib
import json
from decimal import Decimal
from pathlib import Path
import mysql.connector

BASE_DIR = Path(__file__).resolve().parent
DB_CONFIG = {
    "host": "127.0.0.1", "port": 3306, "user": "root", "password": "root",
    "database": "order_db", "connection_timeout": 5,
}


def open_database():
    return mysql.connector.connect(**DB_CONFIG)


def load_data(name):
    return json.loads((BASE_DIR / "data" / name).read_text(encoding="utf-8"))


def catalogue_digest(products):
    encoded = json.dumps(products, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_seed_data():
    products = load_data("products.json")
    orders = load_data("orders.json")
    items = load_data("order_items.json")
    product_ids = {p["product_id"] for p in products}
    order_ids = {o["order_id"] for o in orders}
    assert len(product_ids) == len(products) == 20
    assert len(order_ids) == len(orders) == 10
    assert len({i["order_item_id"] for i in items}) == len(items)
    assert len({(i["order_id"], i["product_id"]) for i in items}) == len(items)
    for item in items:
        assert item["product_id"] in product_ids and item["order_id"] in order_ids
        assert item["quantity"] > 0 and Decimal(item["unit_price"]) >= 0
    for order in orders:
        lines = [i for i in items if i["order_id"] == order["order_id"]]
        assert sum(i["quantity"] for i in lines) == order["items_count"]
        assert sum((Decimal(i["unit_price"]) * i["quantity"] for i in lines), Decimal("0")) == Decimal(order["total_amount"])
    return {"products": len(products), "orders": len(orders), "order_lines": len(items),
            "units": sum(i["quantity"] for i in items)}


def seed_commerce():
    """Insert missing fixture rows; reject conflicting rows rather than overwrite them."""
    validate_seed_data()
    specs = [
        ("products", "products.json", ["product_id", "name", "brand", "category", "price_inr",
         "capacity_l", "weight_g", "height_cm", "width_cm", "depth_cm", "description"]),
        ("orders", "orders.json", ["order_id", "customer_id", "customer_email", "total_amount", "items_count"]),
        ("order_items", "order_items.json", ["order_item_id", "order_id", "product_id", "quantity", "unit_price"]),
    ]
    counts = {}
    connection = open_database()
    cursor = connection.cursor(dictionary=True)
    try:
        for table, filename, columns in specs:
            inserted = 0
            for row in load_data(filename):
                # Identifiers come only from the fixed specs above; values are parameterized.
                cursor.execute(f"SELECT {', '.join(columns)} FROM {table} WHERE {columns[0]} = %s",
                               (row[columns[0]],))
                existing = cursor.fetchone()
                if existing:
                    for column in columns:
                        expected = row[column]
                        actual = existing[column]
                        if isinstance(actual, Decimal):
                            expected = Decimal(str(expected))
                        if actual != expected:
                            raise ValueError(f"Existing {table} row {row[columns[0]]} differs from the fixture; no overwrite performed.")
                    continue
                placeholders = ", ".join(["%s"] * len(columns))
                cursor.execute(f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
                               tuple(row[column] for column in columns))
                inserted += 1
            counts[table] = inserted
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()
    return counts


def reconcile_database():
    connection = open_database()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT o.order_id, o.items_count AS header_units, o.total_amount AS header_amount, "
            "COALESCE(SUM(i.quantity), 0) AS line_units, "
            "COALESCE(SUM(i.quantity * i.unit_price), 0) AS line_amount "
            "FROM orders o LEFT JOIN order_items i ON i.order_id = o.order_id "
            "GROUP BY o.order_id, o.items_count, o.total_amount ORDER BY o.order_id"
        )
        rows = cursor.fetchall()
        for row in rows:
            if row["header_units"] != row["line_units"] or row["header_amount"] != row["line_amount"]:
                raise ValueError(f"Order {row['order_id']} does not reconcile with its line items.")
        return rows
    finally:
        cursor.close()
        connection.close()
