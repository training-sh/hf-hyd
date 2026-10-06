# Capstone / Internship Project Planning Framework

The document provided for a reference, not that must influence ones creativity and problem solving skills. 
Use this as grain of salt, for a reference..

## 1. Start with the Business Requirement

Do **not** start the project by immediately building Bronze, Silver, and Gold pipelines.

Start by understanding:

- What business problem are we trying to solve?
- Who are the stakeholders?
- What decisions do they need to make?
- What KPIs will help them make those decisions?
- What data is required to calculate those KPIs?

The overall approach should be:

```text
Business Problem
      ↓
Stakeholders
      ↓
Business Questions
      ↓
KPIs
      ↓
Facts + Dimensions
      ↓
Source Data Requirements
      ↓
Source-to-Target Mapping
      ↓
Landing
      ↓
Bronze
      ↓
Silver
      ↓
Gold
      ↓
Analytics / Dashboard / AI
      ↓
Business Decisions
```

---

# 2. Example KPI: Top-Selling Products

Consider the following business requirement:

> Identify top-selling products and understand their sales, growth, profitability, regional performance, category performance, and supplier contribution.

## Stakeholders

Possible stakeholders include:

- Marketing Manager
- Sales Manager
- Warehouse Operations Manager
- Procurement Manager
- Business Management

Different stakeholders may use the same KPI for different decisions.

For example:

**Marketing Manager**

- Which products should be promoted?
- Which products are growing?
- Which regions should be targeted?
- Are seasonal campaigns improving sales?

**Warehouse Manager**

- Which products move quickly?
- Which products require higher stock availability?
- Which products have declining demand?

**Procurement Manager**

- Which products need to be reordered?
- Which suppliers provide high-demand products?
- Which products generate better margins?

---

# 3. Business Questions

Before building the pipeline, identify the questions that the dashboard should answer.

Examples:

- What are the top-selling products?
- Which products generate the highest revenue?
- Which products generate the highest profit?
- Which products are growing or declining?
- Which regions generate the highest sales?
- Which categories perform best?
- Which suppliers contribute to high-selling products?
- How do sales change by day, week, month, quarter, or year?
- Does seasonality affect product sales?
- How did products perform during New Year, Diwali, Christmas, or other events?
- Is the average selling price increasing or decreasing?
- Are we acquiring more customers for a particular product?

---

# 4. Define the KPIs

Example primary KPI:

```text
Product Sales Revenue
```

Formula:

```text
Sales Revenue = SUM(Quantity × Selling Price - Discount)
```

Additional KPIs can include:

```text
Quantity Sold

Order Count

Customer Count

Average Selling Price

Total Cost

Profit

Profit Margin %

Revenue Growth %

Customer Growth %
```

Example formulas:

```text
Profit = Sales Revenue - Cost

Profit Margin % = (Profit / Sales Revenue) × 100

Revenue Growth % =
(Current Period Revenue - Previous Period Revenue)
--------------------------------------------------- × 100
              Previous Period Revenue
```

---

# 5. Determine How the KPI Will Be Analyzed

The KPI alone is not sufficient.

We also need to determine how stakeholders want to analyze it.

```text
                   Product Sales
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ↓                ↓                ↓
      Region          Category        Supplier
        │
        └────────────────┬────────────────┘
                         ↓
                        Date
                         │
             ┌───────────┼───────────┐
             ↓           ↓           ↓
            Day         Week        Month
                                     │
                                     ↓
                                  Quarter
                                     │
                                     ↓
                                    Year
                                     │
                                     ↓
                               Season / Event
```

Examples of season/event analysis:

- New Year
- Diwali
- Christmas
- Summer
- Weekend
- Festival Campaign
- Promotional Period

These analysis requirements help identify the required **dimensions**.

---

# 6. Define the Fact Grain

Before creating a fact table, clearly define:

> **What does ONE ROW in the fact table represent?**

Example:

```text
Fact Table: fact_order_item

Grain:

ONE ROW =
one product
in one order line
for one customer
on one transaction
at one point in time
```

Example structure:

```text
fact_order_item
------------------------------
order_line_key
order_id

date_key
customer_key
product_key
region_key
supplier_key

quantity
unit_price
discount_amount
sales_amount
cost_amount
profit_amount
```

Derived measures:

```text
sales_amount =
(quantity × unit_price) - discount_amount

profit_amount =
sales_amount - cost_amount
```

---

# 7. Identify Facts and Business Processes

Do not automatically treat every source entity as a dimension.

For example:

```text
Orders
Invoices
Payments
Inventory Movements
Deliveries
```

These represent **business processes or transactions**.

Depending on the analytical requirements, separate fact tables may be required.

Examples:

```text
fact_order_item

fact_invoice_item

fact_payment

fact_inventory_movement

fact_delivery
```

The grain of every fact table must be clearly documented.

---

# 8. Identify Dimensions

From the business questions and KPI slicing requirements, identify the dimensions.

Example:

```text
                     fact_order_item
                            │
       ┌────────────┬───────┼────────┬────────────┐
       ↓            ↓       ↓        ↓            ↓
   dim_date    dim_product  dim_customer  dim_region  dim_supplier
```

## Product Dimension

```text
dim_product
----------------
product_key
product_id
product_name
category
subcategory
brand
```

## Customer Dimension

```text
dim_customer
----------------
customer_key
customer_id
customer_name
customer_segment
```

## Region Dimension

```text
dim_region
----------------
region_key
country
state
city
region
```

## Supplier Dimension

```text
dim_supplier
----------------
supplier_key
supplier_id
supplier_name
```

## Date Dimension

```text
dim_date
----------------
date_key
date
day
day_of_week
week
month
quarter
year
season
special_event
```

---

# 9. Identify Required Source Data

Only after understanding the KPI, facts, and dimensions should we determine what source data is required.

Example sources:

```text
Orders          → order.jsonl

Order Lines     → order_line.jsonl

Products        → products.csv

Customers       → customers.csv

Suppliers       → suppliers.csv

Invoices        → invoices.jsonl

Payments        → payments.jsonl
```

The actual project may obtain this information from:

- JSON / JSONL
- CSV
- Database tables
- REST APIs
- WAL / CDC
- Kafka
- External datasets

---

# 10. Create Source-to-Target Mapping

Students should document where every important analytical field originates.

| Business Requirement | Source | Target |
|---|---|---|
| Quantity Sold | Order Line | `fact_order_item.quantity` |
| Selling Price | Order Line | `fact_order_item.unit_price` |
| Sales Revenue | Derived | `fact_order_item.sales_amount` |
| Cost | Product/Purchase | `fact_order_item.cost_amount` |
| Profit | Derived | `fact_order_item.profit_amount` |
| Product | Product | `dim_product` |
| Category | Product | `dim_product.category` |
| Customer | Order/Customer | `dim_customer` |
| Region | Customer Address | `dim_region` |
| Supplier | Product/Purchase | `dim_supplier` |
| Transaction Date | Order | `dim_date` |

The flow is:

```text
KPI
 ↓
Facts + Dimensions
 ↓
Required Fields
 ↓
Source Systems
 ↓
Source-to-Target Mapping
```

---

# 11. Landing Zone

Raw source files first arrive in the landing zone.

Example:

```text
landing/
│
├── orders/
│   └── orders_2026_01_01.jsonl
│
├── products/
│   └── products_2026_01_01.csv
│
├── customers/
│   └── customers_2026_01_01.csv
│
└── invoices/
    └── invoices_2026_01_01.jsonl
```

The landing zone represents data received from the source before major processing.

---

# 12. Landing → Bronze

PySpark can read and validate the incoming data.

```text
Source
   │
   ↓
Landing Zone
   │
   ↓
PySpark
   │
   ├──────────────────────┐
   │                      │
   ↓                      ↓
Valid Records       Invalid / Corrupt
   │                      │
   ↓                      ↓
Bronze              Quarantine / Bad
```

Example:

```text
landing/
    orders/
        orders_2026_01_01.jsonl

bronze/
    orders/
        year=2026/
            month=01/
                day=01/

quarantine/
    orders/
        year=2026/
            month=01/
                day=01/
```

Bronze should remain relatively close to the original source.

Useful metadata can be added:

```text
source_file

ingestion_timestamp

batch_id

source_system

record_timestamp
```

---

# 13. Bronze → Silver

Silver represents cleaned, validated, standardized, and integrated data.

Typical processing:

```text
BRONZE
   │
   ↓
Schema Validation
   │
   ↓
Data Type Conversion
   │
   ↓
Null Handling
   │
   ↓
Deduplication
   │
   ↓
Business Rule Validation
   │
   ↓
Standardization
   │
   ↓
Reference Data Enrichment
   │
   ↓
Merge / Upsert
   │
   ↓
SILVER
```

Example Silver datasets:

```text
silver/
│
├── orders/
├── order_items/
├── customers/
├── products/
├── suppliers/
├── invoices/
└── payments/
```

Students can demonstrate both processing models where appropriate:

```text
Batch Processing

Bronze
   ↓
Silver
```

and:

```text
Streaming / Incremental Processing

Bronze
   ↓
Merge / Upsert
   ↓
Silver
```

---

# 14. Silver → Gold

Gold should be designed based on the **business requirements identified at the beginning of the project**.

Example:

```text
SILVER
   │
   ↓
GOLD DATA MODEL
   │
   ├── fact_order_item
   │
   ├── dim_product
   │
   ├── dim_customer
   │
   ├── dim_region
   │
   ├── dim_supplier
   │
   └── dim_date
```

Gold can also contain business-oriented aggregated datasets.

Examples:

```text
gold_product_daily_sales

gold_product_weekly_sales

gold_product_monthly_sales

gold_regional_product_sales

gold_category_sales

gold_supplier_performance
```

---

# 15. Gold Serving Layer

Gold data can be exposed through different technologies.

Example:

```text
                     GOLD
                       │
          ┌────────────┼────────────┐
          │            │            │
          ↓            ↓            ↓
        MySQL       Parquet      Snowflake
                       │
                       ↓
                    DuckDB
```

The project does not need to use every technology.

Choose the serving technology based on the project requirements.

---

# 16. Dashboard Layer

Example technology:

```text
Streamlit
   │
   ↓
Python
   │
   ├── Pandas
   ├── DuckDB
   ├── MySQL
   ├── Parquet
   └── Snowflake Python Connector
```

The dashboard should answer the original stakeholder questions.

---

# 17. Product Performance Dashboard

Example dashboard filters:

```text
Product
[ Backpack ▼ ]

Region
[ All ▼ ]

Category
[ All ▼ ]

Supplier
[ All ▼ ]

Period
[ Today ] [ This Week ] [ This Month ] [ This Year ]

Custom Date Range
[ 01-Jan-2026 ] → [ 31-Dec-2026 ]
```

---

# 18. KPI Widgets

Example widgets:

```text
┌────────────────────┐
│ Sales Revenue      │
│ ₹12.4M             │
│ +14% YoY           │
└────────────────────┘

┌────────────────────┐
│ Units Sold         │
│ 18,421             │
│ +8% YoY            │
└────────────────────┘

┌────────────────────┐
│ Profit             │
│ ₹2.8M              │
│ +17% YoY           │
└────────────────────┘

┌────────────────────┐
│ Customers          │
│ 4,521              │
│ +6% YoY            │
└────────────────────┘
```

---

# 19. Product Sales Growth

Use a line chart when analyzing change over time.

```text
Sales Revenue
     │
     │                       ╭──────
     │                 ╭─────╯
     │           ╭─────╯
     │      ╭────╯
     │──────╯
     └──────────────────────────────→ Time
          Jan  Feb  Mar  Apr  May
```

```text
X-axis = Time

Y-axis = SUM(Sales Revenue)
```

The time unit may be:

- Daily
- Weekly
- Monthly
- Quarterly
- Yearly

---

# 20. Product Price Change

Example:

```text
Average Price
     │
     │       █
     │   █   █       █
     │   █   █   █   █
     │   █   █   █   █
     └────────────────────→ Time
        Jan Feb Mar Apr
```

```text
X-axis = Time

Y-axis = AVG(Selling Price)
```

This can help identify whether price changes affect product demand.

---

# 21. Additional Dashboard Visualizations

Possible visualizations include:

| Requirement | Suggested Visualization |
|---|---|
| Product Revenue Growth | Line Chart |
| Top-Selling Products | Bar Chart |
| Product Price Change | Line / Bar Chart |
| Regional Sales | Bar Chart / Map |
| Category Contribution | Pie / Donut / Bar |
| Supplier Performance | Bar Chart / Table |
| Customer Growth | Line Chart / KPI |
| Profit Margin | Bar Chart / KPI |
| Product Comparison | Table / Bar Chart |

Not every KPI requires a time dimension.

For example:

```text
Top 10 Products by Revenue
```

can simply use:

```text
X-axis = Product

Y-axis = Revenue
```

---

# 22. Complete End-to-End Flow

```text
                    BUSINESS GOAL
                          │
                          ↓
                     STAKEHOLDERS
                          │
                          ↓
                  BUSINESS QUESTIONS
                          │
                          ↓
                         KPI
                          │
               ┌──────────┴──────────┐
               │                     │
               ↓                     ↓
           MEASURES              ANALYSIS BY
        Revenue                  Product
        Quantity                 Customer
        Profit                   Region
        Margin                   Category
        Growth                   Supplier
                                 Date
               │                     │
               └──────────┬──────────┘
                          ↓
                    DEFINE GRAIN
                          ↓
                 FACTS + DIMENSIONS
                          ↓
                  REQUIRED FIELDS
                          ↓
                   SOURCE MAPPING
                          ↓
              JSONL / CSV / DB / API / WAL
                          ↓
                       LANDING
                          ↓
                  ┌───────┴────
