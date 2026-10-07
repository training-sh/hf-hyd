#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if test -f env.sh; then source env.sh; fi
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python stage_data.py --hdfs
.venv/bin/python probe_extensions.py
.venv/bin/python stage_native.py
.venv/bin/python probe_storage.py
.venv/bin/python test_iceberg_hdfs.py
.venv/bin/python verify.py
.venv/bin/python -m pip freeze > requirements.lock.txt
