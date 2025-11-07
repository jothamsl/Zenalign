import pytest
from app.utils.pii_detector import PIIDetector


def test_detect_email_in_values():
    values = ["john.doe@example.com", "test data", "another@email.org"]
    pii_types = PIIDetector.detect_in_values(values)
    assert "email" in pii_types


def test_detect_phone_in_values():
    values = ["555-123-4567", "123-456-7890", "random text"]
    pii_types = PIIDetector.detect_in_values(values)
    assert "phone" in pii_types


def test_detect_ssn_in_values():
    values = ["123-45-6789", "normal text", "456-78-9012"]
    pii_types = PIIDetector.detect_in_values(values)
    assert "ssn" in pii_types


def test_detect_in_column_name():
    assert "email" in PIIDetector.detect_in_column_name("user_email")
    assert "phone" in PIIDetector.detect_in_column_name("phone_number")
    assert "name" in PIIDetector.detect_in_column_name("first_name")
    assert len(PIIDetector.detect_in_column_name("age")) == 0


def test_detect_combined():
    has_pii, pii_types = PIIDetector.detect("email_address", ["john@example.com", "jane@test.org"])
    assert has_pii is True
    assert "email" in pii_types


def test_no_pii():
    has_pii, pii_types = PIIDetector.detect("age", ["25", "30", "35"])
    assert has_pii is False
    assert len(pii_types) == 0
