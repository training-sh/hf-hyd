---
name: invoice-review
description: Review a synthetic ecommerce invoice for required fields, arithmetic consistency and unsupported payment claims.
---

Check invoice ID, order ID, currency, subtotal, tax and total.
Check whether subtotal plus tax equals total, allowing one paisa rounding tolerance.
List missing fields rather than inventing them.
Never label an invoice paid unless explicit payment evidence is provided.
Return a short checklist with PASS, FAIL or MISSING for each check.
This skill reviews supplied data; it does not approve refunds or send messages.
