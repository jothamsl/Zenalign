import re
from typing import List, Tuple


class PIIDetector:
    """Regex-based PII detection for common patterns."""
    
    # Patterns for common PII
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    PHONE_PATTERN = re.compile(r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b')
    SSN_PATTERN = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
    CREDIT_CARD_PATTERN = re.compile(r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b')
    
    # Column name heuristics
    PII_COLUMN_KEYWORDS = {
        'email': ['email', 'e-mail', 'mail'],
        'phone': ['phone', 'mobile', 'tel', 'telephone', 'cell'],
        'ssn': ['ssn', 'social_security', 'national_id', 'nationalid'],
        'credit_card': ['credit_card', 'cc', 'card_number'],
        'name': ['name', 'first_name', 'last_name', 'full_name', 'firstname', 'lastname'],
        'address': ['address', 'street', 'location', 'home_address'],
        'dob': ['dob', 'birth_date', 'birthdate', 'date_of_birth'],
        'ip_address': ['ip', 'ip_address', 'ipaddress'],
    }
    
    @classmethod
    def detect_in_column_name(cls, column_name: str) -> List[str]:
        """Check if column name suggests PII."""
        detected = []
        col_lower = column_name.lower()
        for pii_type, keywords in cls.PII_COLUMN_KEYWORDS.items():
            if any(kw in col_lower for kw in keywords):
                detected.append(pii_type)
        return detected
    
    @classmethod
    def detect_in_values(cls, values: List[str]) -> List[str]:
        """Check sample values for PII patterns."""
        detected_types = set()
        sample = [str(v) for v in values if v is not None][:100]
        
        for val in sample:
            if cls.EMAIL_PATTERN.search(val):
                detected_types.add('email')
            if cls.PHONE_PATTERN.search(val):
                detected_types.add('phone')
            if cls.SSN_PATTERN.search(val):
                detected_types.add('ssn')
            if cls.CREDIT_CARD_PATTERN.search(val):
                detected_types.add('credit_card')
        
        return list(detected_types)
    
    @classmethod
    def detect(cls, column_name: str, sample_values: List[str]) -> Tuple[bool, List[str]]:
        """
        Detect PII in a column.
        Returns (has_pii, list_of_pii_types)
        """
        pii_types = []
        
        # Check column name
        name_pii = cls.detect_in_column_name(column_name)
        pii_types.extend(name_pii)
        
        # Check values
        value_pii = cls.detect_in_values(sample_values)
        pii_types.extend(value_pii)
        
        # Deduplicate
        pii_types = list(set(pii_types))
        
        return len(pii_types) > 0, pii_types
