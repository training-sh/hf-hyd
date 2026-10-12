# Papermill

Papermill can be used to execute Jupyter notebooks from the command line or from orchestration tools such as Apache Airflow.

Unlike a normal Python program, a Jupyter notebook does not directly use command-line arguments through `argparse` when executed with Papermill.

Papermill provides its own parameter mechanism.

A Jupyter code cell can be tagged with:

```text
parameters
```

Variables defined in this cell can then be overridden from the command line using the `-p` option.

For example:

```bash
papermill parameter-handling.ipynb \
  output/parameter-handling-output.ipynb \
  -p BATCH_ID batch_001 \
  -p CUSTOMERS_LANDING_PATH data/landing/customers \
  -p CUSTOMERS_BRONZE_PATH data/bronze/customers
```

Papermill does not modify the original `parameters` cell. Instead, it inserts a new cell immediately after it with the tag:

```text
injected-parameters
```

The values supplied through `-p` are written into this injected cell and override the default values defined in the original `parameters` cell.

The executed notebook, including the injected parameter values and execution results, is written to the specified output `.ipynb` file.
