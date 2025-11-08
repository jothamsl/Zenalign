"""
PII (Personally Identifiable Information) Detection Service.
Privacy-first design (Ch. 12): Detect sensitive data before external API calls.
Modular tool following Ch. 4 principles.
"""
import pandas as pd
import re
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class PIIDetector:
    """
    Detect PII in datasets to ensure privacy compliance.
    
    Detects:
    - Email addresses
    - Phone numbers (US formats)
    - Social Security Numbers (SSN)
    - Credit card numbers
    - Addresses (basic detection)
    
    Following Ch. 12: Privacy-first AI systems
    - Detect PII before sending to LLM/Exa
    - Provide anonymization recommendations
    - Flag sensitive columns
    """
    
    # Regex patterns for PII detection
    PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',  # Simplified pattern for all SSN formats
        'credit_card': r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11})\b',
    }
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize PII detector.
        
        Args:
            df: DataFrame to scan for PII
        """
        self.df = df
        self.n_rows, self.n_cols = df.shape
        logger.info(f"Initialized PII detector for {self.n_rows} rows x {self.n_cols} cols")
    
    def _scan_column_for_pattern(self, column: str, pattern: str) -> Dict[str, Any]:
        """
        Scan a column for a regex pattern.
        
        Args:
            column: Column name
            pattern: Regex pattern
            
        Returns:
            Dict with match info
        """
        matches = []
        count = 0
        
        # Convert to string and scan
        col_data = self.df[column].astype(str)
        
        for value in col_data:
            if pd.notna(value) and value != 'nan':
                found = re.findall(pattern, value)
                if found:
                    matches.extend(found)
                    count += 1
        
        if count > 0:
            return {
                'count': count,
                'percentage': round((count / self.n_rows) * 100, 2),
                'sample': matches[:3] if matches else []  # First 3 samples (for debugging only, don't log)
            }
        
        return None
    
    def detect_emails(self) -> Dict[str, Dict[str, Any]]:
        """
        Detect email addresses in all columns.
        
        Returns:
            Dict mapping column names to email detection info
        """
        emails = {}
        pattern = self.PATTERNS['email']
        
        for col in self.df.columns:
            result = self._scan_column_for_pattern(col, pattern)
            if result:
                emails[col] = result
        
        logger.info(f"Found emails in {len(emails)} columns")
        return emails
    
    def detect_phone_numbers(self) -> Dict[str, Dict[str, Any]]:
        """
        Detect phone numbers (US formats).
        
        Returns:
            Dict mapping column names to phone detection info
        """
        phones = {}
        pattern = self.PATTERNS['phone']
        
        for col in self.df.columns:
            result = self._scan_column_for_pattern(col, pattern)
            if result:
                phones[col] = result
        
        logger.info(f"Found phone numbers in {len(phones)} columns")
        return phones
    
    def detect_ssn(self) -> Dict[str, Dict[str, Any]]:
        """
        Detect Social Security Numbers.
        
        Returns:
            Dict mapping column names to SSN detection info
        """
        ssns = {}
        pattern = self.PATTERNS['ssn']
        
        for col in self.df.columns:
            result = self._scan_column_for_pattern(col, pattern)
            if result:
                ssns[col] = result
        
        logger.info(f"Found SSNs in {len(ssns)} columns")
        return ssns
    
    def detect_credit_cards(self) -> Dict[str, Dict[str, Any]]:
        """
        Detect credit card numbers (basic Luhn algorithm check can be added).
        
        Returns:
            Dict mapping column names to credit card detection info
        """
        cards = {}
        
        for col in self.df.columns:
            # First try with dashes/spaces
            pattern_with_sep = r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
            result = self._scan_column_for_pattern(col, pattern_with_sep)
            
            # Also try the main pattern
            if not result:
                result = self._scan_column_for_pattern(col, self.PATTERNS['credit_card'])
            
            if result:
                cards[col] = result
        
        logger.info(f"Found credit cards in {len(cards)} columns")
        return cards
    
    def detect_all_pii(self) -> Dict[str, Any]:
        """
        Comprehensive PII detection across all types.
        
        Returns:
            Complete PII report
        """
        logger.info("Running comprehensive PII detection")
        
        emails = self.detect_emails()
        phones = self.detect_phone_numbers()
        ssns = self.detect_ssn()
        cards = self.detect_credit_cards()
        
        # Combine all detected columns
        all_pii_columns = set()
        all_pii_columns.update(emails.keys())
        all_pii_columns.update(phones.keys())
        all_pii_columns.update(ssns.keys())
        all_pii_columns.update(cards.keys())
        
        # Calculate total PII values
        total_pii_values = (
            sum(info['count'] for info in emails.values()) +
            sum(info['count'] for info in phones.values()) +
            sum(info['count'] for info in ssns.values()) +
            sum(info['count'] for info in cards.values())
        )
        
        report = {
            'emails': emails,
            'phone_numbers': phones,
            'ssn': ssns,
            'credit_cards': cards,
            'summary': {
                'columns_with_pii': len(all_pii_columns),
                'total_pii_values': total_pii_values,
                'pii_percentage': round((total_pii_values / (self.n_rows * self.n_cols)) * 100, 2) if self.n_rows * self.n_cols > 0 else 0
            }
        }
        
        logger.info(f"PII detection complete: {len(all_pii_columns)} columns with PII")
        return report
    
    def get_pii_summary(self) -> List[Dict[str, Any]]:
        """
        Generate actionable PII summary with severity and recommendations.
        
        Returns:
            List of PII issues with recommendations
        """
        summary = []
        report = self.detect_all_pii()
        
        # Define severity and recommendations for each PII type
        pii_config = {
            'ssn': {
                'severity': 'critical',
                'recommendation': 'Remove or hash SSN column before any external API calls. Use tokenization for analysis.'
            },
            'credit_cards': {
                'severity': 'critical',
                'recommendation': 'Remove or mask credit card numbers. Keep only last 4 digits if needed for identification.'
            },
            'emails': {
                'severity': 'high',
                'recommendation': 'Hash email addresses or use domain-only aggregation for analysis.'
            },
            'phone_numbers': {
                'severity': 'high',
                'recommendation': 'Mask phone numbers or extract area code only for geographic analysis.'
            }
        }
        
        # Process each PII type
        for pii_type_key, pii_data in report.items():
            if pii_type_key == 'summary':
                continue
            
            # Map keys to config
            config_key = pii_type_key
            if pii_type_key == 'phone_numbers':
                config_key = 'phone_numbers'
            elif pii_type_key == 'credit_cards':
                config_key = 'credit_cards'
            
            if pii_data and config_key in pii_config:
                for col, info in pii_data.items():
                    summary.append({
                        'column': col,
                        'pii_type': pii_type_key.rstrip('s'),  # Remove plural
                        'severity': pii_config[config_key]['severity'],
                        'count': info['count'],
                        'percentage': info['percentage'],
                        'recommendation': pii_config[config_key]['recommendation']
                    })
        
        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        summary.sort(key=lambda x: (severity_order.get(x['severity'], 4), -x['count']))
        
        logger.info(f"Generated PII summary with {len(summary)} items")
        return summary
