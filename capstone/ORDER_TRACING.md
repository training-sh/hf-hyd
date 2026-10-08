# Order traces — 8 October 2026

 Database: `olist6`. Evidence boundary: `api-00033`, finished `2026-10-08T01:40:23.166737+00:00` (UTC).

These are the latest rows reconstructed by applying published API batches in numeric order, starting with the full baseline. They describe the published state, which can lag the live database. Each linked file contains the stated record ID; do not expect every order in the latest incremental file.

## How to trace an order

Source `InvoiceNo` → frozen plan `source_invoice` / `ref` → Odoo `sale.order.client_order_ref` → sales line `order_id` → picking `sale_id` → invoice line `sale_line_ids` → invoice `move_id`. Customer `partner_id` joins contact `id`; contact `ref=CUST-<CustomerID>` maps back to the source customer. Synthetic unmet orders have no Kaggle invoice/customer identity.

Order intake → confirmation and stock reservation → picking → packing → dispatch → posted customer invoice → payment and reconciliation → `ops_closed=true`. Supplier receipt → inspection → putaway supplies warehouse stock. Cancellation takes its own native cancellation path; it is not a refund inferred from a Kaggle cancellation invoice.

Business timestamps (`ops_order_at`, `scheduled_date`, `date_done`, `ops_issued_at`, `ops_paid_at`) describe simulated operations. `create_date` and `write_date` describe real replay execution. Hourly batching can round completion later. Do not confuse the two clocks.

## Completed sale

- Odoo order: **S00014**, ID **14**; reference `ECOM-536365`.
- Kaggle source invoice: `536365`; customer reference `CUST-17850`, Odoo contact ID `501`.
- Order time: `2025-07-20 12:00:00`; state `sale`; closed `True`; unmet `False`.
- Order row: [landing-zone/api-00003/jsonl/sales/orders/2026-10-07_23_39.jsonl](../landing-zone/api-00003/jsonl/sales/orders/2026-10-07_23_39.jsonl). Customer row: [landing-zone/contacts-00036/jsonl/contact-details/customers/2026-10-08_07_09.jsonl](../landing-zone/contacts-00036/jsonl/contact-details/customers/2026-10-08_07_09.jsonl). Source mapping: [workspace/rebuild/rebaseline/orders.jsonl](../workspace/rebuild/rebaseline/orders.jsonl) (find `ECOM-536365`).

Sales lines: 7. ID `1`: ordered `6.0`, delivered `6.0`, invoiced `6.0` — [landing-zone/api-00003/jsonl/sales/order-lines/2026-10-07_23_39.jsonl](../landing-zone/api-00003/jsonl/sales/order-lines/2026-10-07_23_39.jsonl); ID `2`: ordered `6.0`, delivered `6.0`, invoiced `6.0` — [landing-zone/api-00003/jsonl/sales/order-lines/2026-10-07_23_39.jsonl](../landing-zone/api-00003/jsonl/sales/order-lines/2026-10-07_23_39.jsonl); ID `3`: ordered `8.0`, delivered `8.0`, invoiced `8.0` — [landing-zone/api-00003/jsonl/sales/order-lines/2026-10-07_23_39.jsonl](../landing-zone/api-00003/jsonl/sales/order-lines/2026-10-07_23_39.jsonl) (first three shown)

| Picking ID / name | Stage | State | Scheduled / completed | File |
|---|---|---|---|---|
| 641 / WH/PICK/00001 | picking | done | 2025-07-20 12:18:01 / 2025-07-20 13:00:00 | [landing-zone/api-00003/jsonl/inventory/pickings/2026-10-07_23_39.jsonl](../landing-zone/api-00003/jsonl/inventory/pickings/2026-10-07_23_39.jsonl) |
| 657 / WH/PACK/00002 | packing | done | 2025-07-20 13:25:13 / 2025-07-20 14:00:00 | [landing-zone/api-00003/jsonl/inventory/pickings/2026-10-07_23_39.jsonl](../landing-zone/api-00003/jsonl/inventory/pickings/2026-10-07_23_39.jsonl) |
| 682 / WH/OUT/00004 | dispatch | done | 2025-07-20 14:28:50 / 2025-07-20 15:00:00 | [landing-zone/api-00003/jsonl/inventory/pickings/2026-10-07_23_39.jsonl](../landing-zone/api-00003/jsonl/inventory/pickings/2026-10-07_23_39.jsonl) |

Invoice `HIS6/2025/00001`, ID `37`: state `posted`, payment `paid`, residual `0.0`, issued `2025-07-20 15:00:00`, due `2025-07-22 23:47:29` — [landing-zone/api-00033/jsonl/invoicing/invoices/2026-10-08_07_09.jsonl](../landing-zone/api-00033/jsonl/invoicing/invoices/2026-10-08_07_09.jsonl).

Invoice join example: invoice-line ID `297`, `sale_line_ids=[1]`, `move_id=37` — [landing-zone/api-00003/jsonl/invoicing/invoice-lines/2026-10-07_23_39.jsonl](../landing-zone/api-00003/jsonl/invoicing/invoice-lines/2026-10-07_23_39.jsonl).

## Source cancellation

- Odoo order: **S00030**, ID **30**; reference `ECOM-C536379`.
- Kaggle source invoice: `C536379`; customer reference `CUST-14527`, Odoo contact ID `901`.
- Order time: `2025-07-20 13:25:49`; state `cancel`; closed `True`; unmet `False`.
- Order row: [landing-zone/api-00003/jsonl/sales/orders/2026-10-07_23_39.jsonl](../landing-zone/api-00003/jsonl/sales/orders/2026-10-07_23_39.jsonl). Customer row: [landing-zone/contacts-00036/jsonl/contact-details/customers/2026-10-08_07_09.jsonl](../landing-zone/contacts-00036/jsonl/contact-details/customers/2026-10-08_07_09.jsonl). Source mapping: [workspace/rebuild/rebaseline/orders.jsonl](../workspace/rebuild/rebaseline/orders.jsonl) (find `ECOM-C536379`).

Sales lines: 1. ID `141`: ordered `1.0`, delivered `0.0`, invoiced `0.0` — [landing-zone/api-00003/jsonl/sales/order-lines/2026-10-07_23_39.jsonl](../landing-zone/api-00003/jsonl/sales/order-lines/2026-10-07_23_39.jsonl)

No sale-linked picking appears in the published evidence for this order.

No linked customer invoice appears in the published evidence.

The source C-invoice is represented as a cancelled quotation, preserving the signed source totals in the plan. It does not establish a refund or a verified link to an earlier sale.

## Delayed completed sale

- Odoo order: **S00019**, ID **19**; reference `ECOM-536370`.
- Kaggle source invoice: `536370`; customer reference `CUST-12583`, Odoo contact ID `706`.
- Order time: `2025-07-20 12:21:44`; state `sale`; closed `True`; unmet `False`.
- Order row: [landing-zone/api-00005/jsonl/sales/orders/2026-10-08_00_09.jsonl](../landing-zone/api-00005/jsonl/sales/orders/2026-10-08_00_09.jsonl). Customer row: [landing-zone/contacts-00036/jsonl/contact-details/customers/2026-10-08_07_09.jsonl](../landing-zone/contacts-00036/jsonl/contact-details/customers/2026-10-08_07_09.jsonl). Source mapping: [workspace/rebuild/rebaseline/orders.jsonl](../workspace/rebuild/rebaseline/orders.jsonl) (find `ECOM-536370`).

Sales lines: 19. ID `27`: ordered `24.0`, delivered `24.0`, invoiced `24.0` — [landing-zone/api-00005/jsonl/sales/order-lines/2026-10-08_00_09.jsonl](../landing-zone/api-00005/jsonl/sales/order-lines/2026-10-08_00_09.jsonl); ID `28`: ordered `24.0`, delivered `24.0`, invoiced `24.0` — [landing-zone/api-00005/jsonl/sales/order-lines/2026-10-08_00_09.jsonl](../landing-zone/api-00005/jsonl/sales/order-lines/2026-10-08_00_09.jsonl); ID `29`: ordered `12.0`, delivered `12.0`, invoiced `12.0` — [landing-zone/api-00005/jsonl/sales/order-lines/2026-10-08_00_09.jsonl](../landing-zone/api-00005/jsonl/sales/order-lines/2026-10-08_00_09.jsonl) (first three shown)

| Picking ID / name | Stage | State | Scheduled / completed | File |
|---|---|---|---|---|
| 652 / WH/PICK/00009 | picking | done | 2025-07-22 11:59:19 / 2025-08-06 09:00:00 | [landing-zone/api-00004/jsonl/inventory/pickings/2026-10-07_23_54.jsonl](../landing-zone/api-00004/jsonl/inventory/pickings/2026-10-07_23_54.jsonl) |
| 4240 / WH/PACK/00755 | packing | done | 2025-08-09 03:40:37 / 2025-08-09 04:00:00 | [landing-zone/api-00005/jsonl/inventory/pickings/2026-10-08_00_09.jsonl](../landing-zone/api-00005/jsonl/inventory/pickings/2026-10-08_00_09.jsonl) |
| 4756 / WH/OUT/00879 | dispatch | done | 2025-08-12 08:12:08 / 2025-08-12 09:00:00 | [landing-zone/api-00005/jsonl/inventory/pickings/2026-10-08_00_09.jsonl](../landing-zone/api-00005/jsonl/inventory/pickings/2026-10-08_00_09.jsonl) |

Invoice `HIS3/2025/00108`, ID `1820`: state `posted`, payment `paid`, residual `0.0`, issued `2025-08-12 09:00:00`, due `2025-08-13 08:34:11` — [landing-zone/api-00033/jsonl/invoicing/invoices/2026-10-08_07_09.jsonl](../landing-zone/api-00033/jsonl/invoicing/invoices/2026-10-08_07_09.jsonl).

Invoice join example: invoice-line ID `19220`, `sale_line_ids=[27]`, `move_id=1820` — [landing-zone/api-00005/jsonl/invoicing/invoice-lines/2026-10-08_00_09.jsonl](../landing-zone/api-00005/jsonl/invoicing/invoice-lines/2026-10-08_00_09.jsonl).

Observed order-to-dispatch delay: **22.86 days**, calculated from the exported order time and dispatch completion.

Projected delivery `2025-08-14 05:42:21`, projected delay **24.722650 days** — [workspace/rebuild/rebaseline/projected_fulfilment.csv](../workspace/rebuild/rebaseline/projected_fulfilment.csv). This is a planning projection; the picking completion above is the observed exported event. Ordinary delayed orders are not subject to the 14-day unmet expiry.

## Pending sale

- Odoo order: **S05946**, ID **5946**; reference `ECOM-548728`.
- Kaggle source invoice: `548728`; customer reference `CUST-13198`, Odoo contact ID `110`.
- Order time: `2025-12-09 10:51:55`; state `sale`; closed `False`; unmet `False`.
- Order row: [landing-zone/api-00030/jsonl/sales/orders/2026-10-08_06_24.jsonl](../landing-zone/api-00030/jsonl/sales/orders/2026-10-08_06_24.jsonl). Customer row: [landing-zone/contacts-00036/jsonl/contact-details/customers/2026-10-08_07_09.jsonl](../landing-zone/contacts-00036/jsonl/contact-details/customers/2026-10-08_07_09.jsonl). Source mapping: [workspace/rebuild/rebaseline/orders.jsonl](../workspace/rebuild/rebaseline/orders.jsonl) (find `ECOM-548728`).

Sales lines: 67. ID `98622`: ordered `4.0`, delivered `4.0`, invoiced `4.0` — [landing-zone/api-00030/jsonl/sales/order-lines/2026-10-08_06_24.jsonl](../landing-zone/api-00030/jsonl/sales/order-lines/2026-10-08_06_24.jsonl); ID `98623`: ordered `5.0`, delivered `5.0`, invoiced `5.0` — [landing-zone/api-00030/jsonl/sales/order-lines/2026-10-08_06_24.jsonl](../landing-zone/api-00030/jsonl/sales/order-lines/2026-10-08_06_24.jsonl); ID `98624`: ordered `12.0`, delivered `12.0`, invoiced `12.0` — [landing-zone/api-00030/jsonl/sales/order-lines/2026-10-08_06_24.jsonl](../landing-zone/api-00030/jsonl/sales/order-lines/2026-10-08_06_24.jsonl) (first three shown)

| Picking ID / name | Stage | State | Scheduled / completed | File |
|---|---|---|---|---|
| 23532 / WH/PICK/04790 | picking | done | 2025-12-30 11:12:18 / 2026-02-01 07:00:00 | [landing-zone/api-00022/jsonl/inventory/pickings/2026-10-08_04_24.jsonl](../landing-zone/api-00022/jsonl/inventory/pickings/2026-10-08_04_24.jsonl) |
| 33529 / WH/PACK/06399 | packing | done | 2026-03-02 17:04:32 / 2026-03-02 18:00:00 | [landing-zone/api-00026/jsonl/inventory/pickings/2026-10-08_05_24.jsonl](../landing-zone/api-00026/jsonl/inventory/pickings/2026-10-08_05_24.jsonl) |
| 39772 / WH/OUT/07636 | dispatch | done | 2026-04-05 08:56:37 / 2026-04-05 09:00:00 | [landing-zone/api-00030/jsonl/inventory/pickings/2026-10-08_06_24.jsonl](../landing-zone/api-00030/jsonl/inventory/pickings/2026-10-08_06_24.jsonl) |

Invoice `HIS7/2026/00516`, ID `19833`: state `posted`, payment `not_paid`, residual `879.99`, issued `2026-04-05 09:00:00`, due `2026-06-02 20:24:31` — [landing-zone/api-00033/jsonl/invoicing/invoices/2026-10-08_07_09.jsonl](../landing-zone/api-00033/jsonl/invoicing/invoices/2026-10-08_07_09.jsonl).

Invoice join example: invoice-line ID `255429`, `sale_line_ids=[98622]`, `move_id=19833` — [landing-zone/api-00030/jsonl/invoicing/invoice-lines/2026-10-08_06_24.jsonl](../landing-zone/api-00030/jsonl/invoicing/invoice-lines/2026-10-08_06_24.jsonl).

This order is not closed at the export boundary. Use picking states and invoice residual/payment state above to distinguish warehouse work from a payment wait; absence of an exported invoice alone does not prove a stock shortage.

## Unmet demand expired after 14 days

- Odoo order: **S01734**, ID **1734**; reference `UNMET-0015`.
- Kaggle source invoice: `none (synthetic)`; customer reference `CUST-UNMET-0015`, Odoo contact ID `1397`.
- Order time: `2025-08-22 02:55:33`; state `cancel`; closed `True`; unmet `True`.
- Order row: [landing-zone/api-00007/jsonl/sales/orders/2026-10-08_00_39.jsonl](../landing-zone/api-00007/jsonl/sales/orders/2026-10-08_00_39.jsonl). Customer row: [landing-zone/contacts-00036/jsonl/contact-details/customers/2026-10-08_07_09.jsonl](../landing-zone/contacts-00036/jsonl/contact-details/customers/2026-10-08_07_09.jsonl). Source mapping: [workspace/rebuild/rebaseline/orders.jsonl](../workspace/rebuild/rebaseline/orders.jsonl) (find `UNMET-0015`).

Sales lines: 1. ID `26785`: ordered `4.0`, delivered `0.0`, invoiced `0.0` — [landing-zone/api-00007/jsonl/sales/order-lines/2026-10-08_00_39.jsonl](../landing-zone/api-00007/jsonl/sales/order-lines/2026-10-08_00_39.jsonl)

| Picking ID / name | Stage | State | Scheduled / completed | File |
|---|---|---|---|---|
| 6242 / WH/PICK/01395 | picking | cancel | 2025-08-22 03:00:33 / False | [landing-zone/api-00007/jsonl/inventory/pickings/2026-10-08_00_39.jsonl](../landing-zone/api-00007/jsonl/inventory/pickings/2026-10-08_00_39.jsonl) |

No linked customer invoice appears in the published evidence.

This explicitly marked synthetic demand follows the 14-day cancellation policy. It must close without delivery or customer invoicing and release any reservations; final verification checks all 60 such orders.

## Payment and WAL trace limits

The invoice payment state and residual above are direct exported evidence. To identify the exact payment, join invoice receivable journal-line IDs to `payments/allocations.debit_move_id` / `credit_move_id`, then the payment journal entry (`payments/payments.move_id`). The current business API invoice-line extract may omit receivable journal lines, so customer ID or matching amount alone is not a reliable payment join. Use allowed `account_move_line`, `account_partial_reconcile`, and `account_payment` WAL events or a read-only database query for that bridge. No unverified payment ID is asserted here.

WAL JSONL rows carry `table`, `operation`, `lsn`, `transaction_id`, and `decoded_text`. Find `sale_order` rows by the Odoo integer order ID; find `res_partner` by the contact ID; follow the related IDs listed above. BEGIN/COMMIT are included in event totals. WAL is incremental and captures allowed-table inserts, updates and deletes; it is not an order snapshot.
