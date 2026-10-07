"""Explicit HDFS-URI -> WebHDFS transport adapter for the Day60 cluster."""
import os
from urllib.parse import urlparse

from fsspec.implementations.webhdfs import WebHDFS
from pyiceberg.io.fsspec import FsspecFileIO
from config import HDFS_USER, WEBHDFS_HOST, WEBHDFS_PORT, hdfs_uri


class HdfsViaWebHDFS(WebHDFS):
    protocol = "hdfs"

    @classmethod
    def _strip_protocol(cls, path):
        parsed = urlparse(str(path))
        if parsed.scheme:
            if parsed.scheme != "hdfs" or parsed.netloc not in ("", urlparse(hdfs_uri()).netloc):
                raise ValueError("HDFS URI does not match the configured NameNode")
            return parsed.path
        return str(path)


def hdfs_filesystem():
    return HdfsViaWebHDFS(host=WEBHDFS_HOST, port=WEBHDFS_PORT, user=HDFS_USER)


class IcebergHdfsFileIO(FsspecFileIO):
    def get_fs(self, scheme, hostname=None):
        if scheme == "hdfs":
            return hdfs_filesystem()
        return super().get_fs(scheme, hostname)
