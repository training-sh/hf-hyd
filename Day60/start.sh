#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if test -f env.sh; then source env.sh; fi
STREAMLIT_BIND_ADDRESS="${STREAMLIT_BIND_ADDRESS:-127.0.0.1}"
test -n "$STREAMLIT_BIND_ADDRESS"
exec .venv/bin/python -m streamlit run app.py --server.address="$STREAMLIT_BIND_ADDRESS" --server.port=8501 --server.headless=true --browser.gatherUsageStats=false
