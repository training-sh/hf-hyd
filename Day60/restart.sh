#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if test -f streamlit.pid; then
    pid=$(cat streamlit.pid)
    if [[ ! "$pid" =~ ^[0-9]+$ ]]; then
        echo "Invalid PID file" >&2
        exit 1
    fi
    if kill -0 "$pid" 2>/dev/null; then
        process_dir=$(readlink -f "/proc/$pid/cwd")
        process_args=$(tr '\0' ' ' < "/proc/$pid/cmdline")
        if [[ "$process_dir" != "$PWD" || "$process_args" != *"streamlit run app.py"* ]]; then
            echo "PID does not identify this lab's Streamlit process; refusing to stop it" >&2
            exit 1
        fi
        kill "$pid"
        for attempt in {1..20}; do
            if ! kill -0 "$pid" 2>/dev/null; then break; fi
            sleep 1
        done
        if kill -0 "$pid" 2>/dev/null; then
            echo "Previous process has not stopped" >&2
            exit 1
        fi
    fi
fi
bash launch.sh
