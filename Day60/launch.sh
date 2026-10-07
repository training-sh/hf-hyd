#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if test -f env.sh; then source env.sh; fi
STREAMLIT_BIND_ADDRESS="${STREAMLIT_BIND_ADDRESS:-127.0.0.1}"
export STREAMLIT_BIND_ADDRESS
if curl --noproxy '*' --silent --fail "http://${STREAMLIT_BIND_ADDRESS}:8501/_stcore/health" >/dev/null; then
    echo "Port 8501 already has a healthy service; inspect before starting another."
    exit 1
fi
nohup bash start.sh > streamlit.log 2>&1 < /dev/null &
echo $! > streamlit.pid
for attempt in {1..20}; do
    if curl --noproxy '*' --silent --fail "http://${STREAMLIT_BIND_ADDRESS}:8501/_stcore/health"; then
        echo
        echo "Day60 Streamlit started; PID $(cat streamlit.pid)"
        exit 0
    fi
    sleep 1
done
tail -50 streamlit.log
exit 1
