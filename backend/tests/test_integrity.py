import hashlib
from app.services.integrity import calculate_sha256, verify_integrity

def test_calculate_sha256():
    log = "Oct 06 10:31:22 firewall01 SRC=192.168.1.10 DST=8.8.8.8"
    expected = hashlib.sha256(log.encode("utf-8")).hexdigest()
    result = calculate_sha256(log)
    assert result == expected

def test_verify_integrity():
    log = "Test raw log stream"
    h = calculate_sha256(log)
    assert verify_integrity(log, h) is True
    assert verify_integrity(log + " altered", h) is False
