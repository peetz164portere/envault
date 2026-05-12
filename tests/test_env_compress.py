"""Tests for envault.env_compress."""

import pytest
from envault.env_compress import (
    CompressError,
    compress_env,
    decompress_env,
    compression_ratio,
)


def test_compress_returns_string():
    data = {"KEY": "value", "FOO": "bar"}
    result = compress_env(data)
    assert isinstance(result, str)
    assert len(result) > 0


def test_decompress_round_trip():
    data = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc123"}
    blob = compress_env(data)
    recovered = decompress_env(blob)
    assert recovered == data


def test_compress_empty_dict():
    result = compress_env({})
    assert isinstance(result, str)


def test_decompress_empty_dict_round_trip():
    blob = compress_env({})
    assert decompress_env(blob) == {}


def test_compress_large_data_is_smaller():
    data = {f"KEY_{i}": "x" * 100 for i in range(50)}
    blob = compress_env(data)
    import base64, gzip, json
    raw_len = len(json.dumps(data, separators=(",", ":")).encode())
    compressed_len = len(gzip.decompress(base64.b64decode(blob)))
    # blob should encode something smaller than raw for repetitive data
    assert len(base64.b64decode(blob)) < raw_len


def test_compress_non_dict_raises():
    with pytest.raises(CompressError):
        compress_env(["not", "a", "dict"])  # type: ignore


def test_decompress_invalid_base64_raises():
    with pytest.raises(CompressError):
        decompress_env("!!!not-valid-base64!!!")


def test_decompress_empty_string_raises():
    with pytest.raises(CompressError):
        decompress_env("")


def test_decompress_corrupt_data_raises():
    import base64
    garbage = base64.b64encode(b"not gzip data at all").decode()
    with pytest.raises(CompressError):
        decompress_env(garbage)


def test_compression_ratio_returns_float():
    data = {"LONG_KEY": "repeated_value" * 20}
    ratio = compression_ratio(data)
    assert isinstance(ratio, float)
    assert 0.0 < ratio < 1.5


def test_compression_ratio_empty_raises():
    with pytest.raises(CompressError):
        compression_ratio({})
