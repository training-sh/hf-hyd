#!/usr/bin/env bash
# Run only before a fresh load, not between incremental changes.
set -euo pipefail

DB="cdc_scd_db"
if [[ ! "$DB" =~ ^[a-zA-Z][a-zA-Z0-9_]{0,63}$ ]]; then
    echo "Invalid database name" >&2
    exit 1
fi

# Check HDFS connectivity before testing whether the target directories exist.
hdfs dfs -ls / >/dev/null
for target in "hdfs:///bronze/$DB" "hdfs:///warehouse/$DB"; do
    printf 'Reset target: %s\n' "$target"
    if hdfs dfs -test -e "$target"; then
        hdfs dfs -rm -r "$target"
    else
        status=$?
        if [ "$status" -ne 1 ]; then
            exit "$status"
        fi
        printf 'Target does not exist; nothing to delete.\n'
    fi
done
printf 'Restart Spark kernels, then run notebook 2 followed by notebook 3.\n'
