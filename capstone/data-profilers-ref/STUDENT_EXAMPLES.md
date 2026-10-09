# Student examples

See README.md for the current data_profilers package and independent notebook flags.
The three notebooks use the included complex Olist/Odoo samples in datasets/.
Schema profiling and parser profiling are separate from business validation.
Explore first, inspect schema differences and malformed records, then try actual
Great Expectations rules. No profiler changes or routes business records.

Source provenance, IDs and hashes are in datasets/olist-samples.json. The clean
samples retain original values; altered copies intentionally contain invalid or
missing IDs, invalid monetary values, malformed relationship shapes and broken
JSON. Earlier good/bad counts in provenance refer to the legacy conversion API,
not the parser-corrupt counts or GX expectation counts of these notebooks.

The current package and notebooks are separate working files. The previously
created student ZIP remains unchanged by explicit request.
