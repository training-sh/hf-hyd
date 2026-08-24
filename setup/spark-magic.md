# Spark Magic

```
source "$HOME/dataengenv/bin/activate"
```

Install the Python packages used in this setup:

```
python -m pip install --upgrade pip
```

```
python -m pip install \
  sparkmagic \
  ipywidgets
```

```
python -c 'import sparkmagic; print("sparkmagic:", sparkmagic.__version__)'
python -c 'import ipywidgets; print("ipywidgets:", ipywidgets.__version__)'
```

```
SPARKMAGIC_DIR="$(
  python -c 'import os, sparkmagic; print(os.path.dirname(sparkmagic.__file__))'
)"
```

```
echo "$SPARKMAGIC_DIR"
```

Install the dedicated PySpark kernel:

```
jupyter kernelspec install \
  "$SPARKMAGIC_DIR/kernels/pysparkkernel" \
  --user
```

Optionally install Scala Spark and SparkR kernels:

```
jupyter kernelspec install \
  "$SPARKMAGIC_DIR/kernels/sparkkernel" \
  --user
```

```
jupyter kernelspec install \
  "$SPARKMAGIC_DIR/kernels/sparkrkernel" \
  --user
```

Verify:

```
jupyter kernelspec list
```

Look for kernel names similar to:, we exepct python/Pyspark, other two are optional, we don't learn Scala and R with Spark


- pysparkkernel
- sparkkernel
- sparkrkernel


```
mkdir -p "$HOME/.sparkmagic"
```

```
tee "$HOME/.sparkmagic/config.json" >/dev/null <<'EOF'
{
  "kernel_python_credentials": {
    "username": "",
    "password": "",
    "url": "http://127.0.0.1:8998",
    "auth": "None"
  },
  "kernel_scala_credentials": {
    "username": "",
    "password": "",
    "url": "http://127.0.0.1:8998",
    "auth": "None"
  },
  "kernel_r_credentials": {
    "username": "",
    "password": "",
    "url": "http://127.0.0.1:8998",
    "auth": "None"
  },
  "authenticators": {
    "None": "sparkmagic.auth.customauth.Authenticator",
    "Basic_Access": "sparkmagic.auth.basic.Basic",
    "Kerberos": "sparkmagic.auth.kerberos.Kerberos"
  },
  "livy_session_startup_timeout_seconds": 120,
  "wait_for_idle_timeout_seconds": 120,
  "shutdown_session_on_spark_statement_errors": false,
  "cleanup_all_sessions_on_exit": true,
  "session_configs": {
    "kind": "pyspark",
    "conf": {
      "spark.app.name": "Jupyter-Sparkmagic-Livy"
    }
  }
}
EOF
```

Validate the JSON:

```
python -m json.tool \
  "$HOME/.sparkmagic/config.json" >/dev/null &&
echo "Sparkmagic configuration is valid"
```


Operational commands

Start Livy:

```
livy-server start
```

Stop Livy:

```
livy-server stop
```

Restart Livy:

```
livy-server restart
```

Check status:

```
livy-server status
ss -lntp | grep 8998
curl http://127.0.0.1:8998/sessions
```

