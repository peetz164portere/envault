"""Tests for envault.crypto encryption/decryption utilities."""

import pytest
from envault.crypto import encrypt, decrypt


PASSWORD = "super-secret-passphrase"
PLAINTEXT = "DB_HOST=localhost\nDB_PORT=5432\nAPI_KEY=abc123"


def test_encrypt_returns_string():
    result = encrypt(PLAINTEXT, PASSWORD)
    assert isinstance(result, str)
    assert len(result) > 0


def test_encrypt_produces_different_ciphertext_each_time():
    """Each call should produce a unique ciphertext due to random salt/nonce."""
    result1 = encrypt(PLAINTEXT, PASSWORD)
    result2 = encrypt(PLAINTEXT, PASSWORD)
    assert result1 != result2


def test_decrypt_round_trip():
    encrypted = encrypt(PLAINTEXT, PASSWORD)
    decrypted = decrypt(encrypted, PASSWORD)
    assert decrypted == PLAINTEXT


def test_decrypt_wrong_password_raises():
    encrypted = encrypt(PLAINTEXT, PASSWORD)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(encrypted, "wrong-password")


def test_decrypt_corrupted_data_raises():
    encrypted = encrypt(PLAINTEXT, PASSWORD)
    # Flip a character near the end to corrupt the ciphertext
    corrupted = encrypted[:-4] + "XXXX"
    with pytest.raises(ValueError):
        decrypt(corrupted, PASSWORD)


def test_decrypt_invalid_base64_raises():
    with pytest.raises(ValueError, match="Invalid encrypted data format"):
        decrypt("!!!not-base64!!!", PASSWORD)


def test_decrypt_too_short_raises():
    import base64
    short_blob = base64.b64encode(b"tooshort").decode()
    with pytest.raises(ValueError, match="too short"):
        decrypt(short_blob, PASSWORD)


def test_encrypt_empty_string():
    encrypted = encrypt("", PASSWORD)
    decrypted = decrypt(encrypted, PASSWORD)
    assert decrypted == ""


def test_encrypt_unicode():
    unicode_text = "SECRET=héllo wörld 🔑"
    encrypted = encrypt(unicode_text, PASSWORD)
    decrypted = decrypt(encrypted, PASSWORD)
    assert decrypted == unicode_text
