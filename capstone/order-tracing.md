
traced order S08303, source reference ECOM-555007. It was fully delivered and paid: 144 units, USD 204.62.


```
INITIAL ORDER / QUOTATION
api-001: sales/orders
Order ID 8303 | S08303 | state=draft
             |
             v
CONFIRMED ORDER
api-006 and api-007: sales/orders
Same order ID 8303 | state=sale
             |
             +--> sales/order-lines
             |    Line 136751: product 2184, quantity 48
             |    Line 136752: product 2183, quantity 96
             |
             v
DELIVERY COMPLETED — 12 Feb 2026
inventory/pickings
Picking 8174 | WH/OUT/07357 | origin=S08303 | state=done
             |
             +--> inventory/moves
             |    Move 164823 --> sale line 136751 --> 48 delivered
             |    Move 164824 --> sale line 136752 --> 96 delivered
             |
             v
INVOICE POSTED
invoicing/invoices
Invoice 16216 | HIS4/2026/00407 | invoice_origin=S08303
USD 204.62 | state=posted
             |
             +--> invoicing/invoice-lines
             |    Invoice lines 190877 / 190878
             |    sale_line_ids --> 136751 / 136752
             |
             v
PAYMENT RECEIVED — 13 Feb 2026
payments/payments
Payment 8106 | state=paid | amount=204.62
Accounting move 16291 | PHIB4/2026/00407
             |
             v
PAYMENT RECONCILED
payments/allocations: allocation 8108, amount=204.62
Invoice: payment_state=paid | amount_residual=0
```


```
| What to inspect | File path and starting line | Reference |
| --- | --- | --- |
| Initial quotation | `api-001/jsonl/sales/orders/2026-10-07_13_36.jsonl` — line `8077` | `id=8303`, `state=draft` |
| Confirmed order | `api-007/jsonl/sales/orders/2026-10-07_14_38.jsonl` — line `2` | `id=8303`, `state=sale` |
| Ordered quantities and discounts | `api-007/jsonl/sales/order-lines/2026-10-07_14_38.jsonl` — line `3` | `order_id[0]=8303`; two rows |
| Delivery document | `api-007/jsonl/inventory/pickings/2026-10-07_14_38.jsonl` — line `1` | `id=8174`, `origin=S08303` |
| Stock movement per order line | `api-007/jsonl/inventory/moves/2026-10-07_14_38.jsonl` — line `1` | `sale_line_id` links to the order lines |
| Actual movement quantities | `api-007/jsonl/inventory/move-lines/2026-10-07_14_38.jsonl` — line `1` | `move_id` links to the stock moves |
| Invoice and paid status | `api-007/jsonl/invoicing/invoices/2026-10-07_14_38.jsonl` — line `8090` | `id=16216`, `invoice_origin=S08303` |
| Invoice-to-order-line links | `api-007/jsonl/invoicing/invoice-lines/2026-10-07_14_38.jsonl` — line `1` | `move_id[0]=16216`, `sale_line_ids` |
| Payment | `api-007/jsonl/payments/payments/2026-10-07_14_38.jsonl` — line `1` | `id=8106`, `move_id[0]=16291` |
| Payment allocation | `api-007/jsonl/payments/allocations/2026-10-07_14_38.jsonl` — line `3` | `id=8108` |

```
