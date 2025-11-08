"""
Test PII detection service.
Following TDD: Write failing tests first.
Privacy-first design (Ch. 12): detect PII before sending data to external APIs.
"""
import pytest
import pandas as pd
from app.services.pii_detector import PIIDetector


@pytest.fixture
def sample_df_with_pii():
    """Create a DataFrame with various PII types."""
    return pd.DataFrame({
        'customer_id': [1, 2, 3, 4, 5],
        'email': ['john.doe@email.com', 'jane@company.org', 'test@test.com', 'user@domain.net', 'admin@site.io'],
        'phone': ['555-123-4567', '(555) 987-6543', '555.111.2222', '5551234567', '555-999-0000'],
        'ssn': ['123-45-6789', '987-65-4321', '111-22-3333', '444-55-6666', '777-88-9999'],
        'credit_card': ['4532-1234-5678-9010', '5425-2334-3010-9903', '4111111111111111', '5500000000000004', '340000000000009'],
        'address': ['123 Main St', '456 Oak Ave', '789 Pine Rd', '321 Elm St', '654 Maple Dr'],
        'amount': [100.50, 200.75, 300.00, 150.25, 500.00]
    })


@pytest.fixture
def clean_df():
    """Create a DataFrame with no PII."""
    return pd.DataFrame({
        'product_id': [1, 2, 3, 4, 5],
        'category': ['A', 'B', 'C', 'D', 'E'],
        'price': [10.99, 20.50, 15.75, 30.00, 25.25],
        'quantity': [5, 10, 7, 3, 8]
    })


class TestPIIDetector:
    """Test the PII detection service."""
    
    def test_detector_initialization(self, sample_df_with_pii):
        """Test that detector initializes with DataFrame."""
        detector = PIIDetector(sample_df_with_pii)
        
        assert detector.df is not None
        assert detector.n_rows == 5
        assert detector.n_cols == 7
    
    def test_detect_email_addresses(self, sample_df_with_pii):
        """Test email address detection."""
        detector = PIIDetector(sample_df_with_pii)
        emails = detector.detect_emails()
        
        assert 'email' in emails
        assert emails['email']['count'] == 5
        assert emails['email']['percentage'] == 100.0
    
    def test_detect_phone_numbers(self, sample_df_with_pii):
        """Test phone number detection (various formats)."""
        detector = PIIDetector(sample_df_with_pii)
        phones = detector.detect_phone_numbers()
        
        assert 'phone' in phones
        assert phones['phone']['count'] >= 4  # At least 4 valid formats
    
    def test_detect_ssn(self, sample_df_with_pii):
        """Test SSN detection."""
        detector = PIIDetector(sample_df_with_pii)
        ssns = detector.detect_ssn()
        
        assert 'ssn' in ssns
        assert ssns['ssn']['count'] == 5
    
    def test_detect_credit_cards(self, sample_df_with_pii):
        """Test credit card detection."""
        detector = PIIDetector(sample_df_with_pii)
        cards = detector.detect_credit_cards()
        
        assert 'credit_card' in cards
        assert cards['credit_card']['count'] >= 3  # At least some valid cards
    
    def test_detect_all_pii(self, sample_df_with_pii):
        """Test comprehensive PII detection."""
        detector = PIIDetector(sample_df_with_pii)
        pii_report = detector.detect_all_pii()
        
        assert 'emails' in pii_report
        assert 'phone_numbers' in pii_report
        assert 'ssn' in pii_report
        assert 'credit_cards' in pii_report
        assert 'summary' in pii_report
        
        # Should detect PII in multiple columns
        assert pii_report['summary']['columns_with_pii'] >= 4
    
    def test_no_pii_in_clean_data(self, clean_df):
        """Test that clean data has no PII detected."""
        detector = PIIDetector(clean_df)
        pii_report = detector.detect_all_pii()
        
        assert pii_report['summary']['columns_with_pii'] == 0
        assert pii_report['summary']['total_pii_values'] == 0
    
    def test_get_pii_summary(self, sample_df_with_pii):
        """Test PII summary generation."""
        detector = PIIDetector(sample_df_with_pii)
        summary = detector.get_pii_summary()
        
        assert isinstance(summary, list)
        assert len(summary) > 0
        
        # Check structure of first item
        first_item = summary[0]
        assert 'column' in first_item
        assert 'pii_type' in first_item
        assert 'severity' in first_item
        assert 'count' in first_item
        assert 'recommendation' in first_item
    
    def test_severity_levels(self, sample_df_with_pii):
        """Test that different PII types have appropriate severity."""
        detector = PIIDetector(sample_df_with_pii)
        summary = detector.get_pii_summary()
        
        # SSN and credit cards should be critical
        ssn_items = [item for item in summary if item['pii_type'] == 'ssn']
        if ssn_items:
            assert ssn_items[0]['severity'] == 'critical'
        
        cc_items = [item for item in summary if item['pii_type'] == 'credit_card']
        if cc_items:
            assert cc_items[0]['severity'] == 'critical'
        
        # Emails might be high or medium
        email_items = [item for item in summary if item['pii_type'] == 'email']
        if email_items:
            assert email_items[0]['severity'] in ['critical', 'high', 'medium']
    
    def test_anonymization_suggestions(self, sample_df_with_pii):
        """Test that anonymization suggestions are provided."""
        detector = PIIDetector(sample_df_with_pii)
        summary = detector.get_pii_summary()
        
        for item in summary:
            assert 'recommendation' in item
            assert len(item['recommendation']) > 0
            # Should mention masking, hashing, or removal
            rec_lower = item['recommendation'].lower()
            assert any(word in rec_lower for word in ['mask', 'hash', 'remove', 'anonymize', 'drop'])
    
    def test_partial_pii_detection(self):
        """Test detection when only some values in column contain PII."""
        df = pd.DataFrame({
            'mixed_email': ['john@email.com', 'not-an-email', 'jane@company.org', 'random text', 'admin@site.io'],
            'mixed_phone': ['555-123-4567', 'abc', '(555) 987-6543', '123', '555-999-0000']
        })
        
        detector = PIIDetector(df)
        emails = detector.detect_emails()
        phones = detector.detect_phone_numbers()
        
        # Should detect partial PII
        assert 'mixed_email' in emails
        assert emails['mixed_email']['count'] == 3
        
        assert 'mixed_phone' in phones
        assert phones['mixed_phone']['count'] >= 2
