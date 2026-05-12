"""Optional compression for vault exports and backups."""

import gzip
import json
import base64
from typing import Dict


class CompressError(Exception):
    pass


def compress_env(data: Dict[str, str]) -> str:
    """Serialize and gzip-compress an env dict, returning a base64 string."""
    if not isinstance(data, dict):
        raise CompressError("data must be a dict")
    try:
        raw = json.dumps(data, separators=(",", ":")).encode("utf-8")
        compressed = gzip.compress(raw, compresslevel=9)
        return base64.b64encode(compressed).decode("ascii")
    except Exception as exc:
        raise CompressError(f"compression failed: {exc}") from exc


def decompress_env(blob: str) -> Dict[str, str]:
    """Decompress a base64-encoded gzipped env blob back to a dict."""
    if not blob or not isinstance(blob, str):
        raise CompressError("blob must be a non-empty string")
    try:
        compressed = base64.b64decode(blob.encode("ascii"))
        raw = gzip.decompress(compressed)
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict):
            raise CompressError("decompressed data is not a dict")
        return data
    except CompressError:
        raise
    except Exception as exc:
        raise CompressError(f"decompression failed: {exc}") from exc


def compression_ratio(data: Dict[str, str]) -> float:
    """Return the compression ratio (compressed / original) as a float."""
    if not data:
        raise CompressError("data must be non-empty to compute ratio")
    raw = json.dumps(data, separators=(",", ":")).encode("utf-8")
    compressed = gzip.compress(raw, compresslevel=9)
    return len(compressed) / len(raw)
