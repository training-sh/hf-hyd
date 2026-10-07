"""Portable settings for a local, non-Kerberos Hadoop teaching environment."""
import getpass
from functools import lru_cache
import os
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
HDFS_BIN = os.getenv("HDFS_BIN") or shutil.which("hdfs") or str(Path(os.getenv("HADOOP_HOME", "/opt/hadoop")) / "bin/hdfs")
HDFS_USER = os.getenv("HADOOP_USER_NAME") or getpass.getuser()
HDFS_BASE = os.getenv("DAY60_HDFS_BASE", f"/user/{HDFS_USER}/day60").rstrip("/")
if not HDFS_BASE.startswith("/") or HDFS_BASE in ("", "/"):
    raise ValueError("DAY60_HDFS_BASE must be an absolute lab directory, not the HDFS root")
HDFS_FILE = HDFS_BASE + "/sales.csv"
WEBHDFS_HOST = os.getenv("WEBHDFS_HOST", "localhost")
WEBHDFS_PORT = int(os.getenv("WEBHDFS_PORT", "9870"))

@lru_cache(maxsize=None)
def hdfs_uri(path=""):
    uri = os.getenv("HDFS_URI")
    if not uri:
        uri = subprocess.run([HDFS_BIN, "getconf", "-confKey", "fs.defaultFS"], capture_output=True, text=True, check=True, timeout=30).stdout.strip()
    parsed = urlparse(uri)
    if parsed.scheme != "hdfs" or not parsed.netloc:
        raise ValueError("Set HDFS_URI to your NameNode URI, for example hdfs://localhost:9000")
    return uri.rstrip("/") + "/" + (path or HDFS_BASE).lstrip("/")
