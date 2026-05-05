"""Encryption and decryption utilities for envault using AES-GCM via cryptography library."""

import os
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32  # 256-bit


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 256-bit key from a password and salt using PBKDF2-HMAC-SHA256."""
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations=260_000,
        dklen=KEY_SIZE,
    )


def encrypt(plaintext: str, password: str) -> str:
    """Encrypt plaintext with the given password.

    Returns a base64-encoded string containing: salt + nonce + ciphertext.
    """
    salt = os.urandom(SALT_SIZE)
    nonce = os.urandom(NONCE_SIZE)
    key = derive_key(password, salt)

    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)

    blob = salt + nonce + ciphertext
    return base64.b64encode(blob).decode("utf-8")


def decrypt(encoded: str, password: str) -> str:
    """Decrypt a base64-encoded blob produced by `encrypt`.

    Raises ValueError if the password is wrong or the data is corrupted.
    """
    try:
        blob = base64.b64decode(encoded.encode("utf-8"))
    except Exception as exc:
        raise ValueError("Invalid encrypted data format.") from exc

    if len(blob) < SALT_SIZE + NONCE_SIZE + 16:  # 16 = min GCM tag
        raise ValueError("Encrypted data is too short.")

    salt = blob[:SALT_SIZE]
    nonce = blob[SALT_SIZE : SALT_SIZE + NONCE_SIZE]
    ciphertext = blob[SALT_SIZE + NONCE_SIZE :]

    key = derive_key(password, salt)
    aesgcm = AESGCM(key)

    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as exc:
        raise ValueError("Decryption failed. Wrong password or corrupted data.") from exc

    return plaintext.decode("utf-8")
