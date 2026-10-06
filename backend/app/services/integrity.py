import hashlib

def calculate_sha256(raw_log: str) -> str:
    """
    Computes the SHA-256 cryptographic hash of a raw log string.
    Ensures bit-for-bit lossless integrity verification.
    """
    if raw_log is None:
        raw_log = ""
    # Encode as UTF-8 bytes to compute deterministic sha256
    return hashlib.sha256(raw_log.encode('utf-8')).hexdigest()

def verify_integrity(raw_log: str, expected_sha256: str) -> bool:
    """
    Verifies that the raw log has not been tampered with by comparing
    its recomputed SHA-256 digest against the stored expected hash.
    """
    if not expected_sha256:
        return False
    computed = calculate_sha256(raw_log)
    return computed.lower() == expected_sha256.lower()
