# Shared commerce dataset

All brands, orders, customers, and conversation examples are fictional. The files connect notebooks 541, 542, and 543 through stable IDs.

| File | Contents | Used by |
| --- | --- | --- |
| `products.json` | 20 backpacks; IDs P001-P020; current catalogue prices, descriptions, brands and measurements | 541 FAISS, 542/543 MySQL |
| `orders.json` | 10 order headers; IDs O1001-O1010; six customers with 3, 2, 2, 1, 1, 1 orders | 542/543 |
| `order_items.json` | 18 lines with product ID, quantity, and historical unit price | 542/543 |
| `order_chat_history.json` | Six explicitly staged fictional conversations, one per customer | 543 fallback history |

Each order has one or more order items. Each item references one catalogue product. `order_item_id` identifies a line; `quantity` is the number of units on it. There are 22 units across 18 lines. Twelve catalogue products have no sales in this sample.

All money is INR. Order amounts and historical unit prices are stored as two-decimal JSON strings and MySQL DECIMAL values. Current catalogue prices are not used to recompute past order revenue. Historical sale prices can differ from current catalogue prices. No tax, shipping, returns, dates, or stock quantities are included.

For every order:

- `items_count = sum(order_items.quantity)`
- `total_amount = sum(order_items.quantity * order_items.unit_price)`

The shared seed helper verifies these relationships before inserting data. It inserts only missing records and rejects conflicts with existing fixture rows; it does not overwrite them.

## Expected analytical results

| Metric | Value |
| --- | --- |
| Orders | 10 |
| Order lines | 18 |
| Units | 22 |
| Revenue | INR 24,892.50 |
| Average units per order | 2.2 |
| Average distinct products per order | 1.8 |
| Average order value | INR 2,489.25 |
| Most-sold product | P018, Junior Light 15: 10 units across 6 orders |
| C001 total | 3 orders, 6 units, INR 4,798.50 |

542 exports its executed chat to `output/542_order_chat/C001.json`. 543 prefers that export and otherwise labels its staged fallback. Conversation claims do not replace SQL purchase facts.
