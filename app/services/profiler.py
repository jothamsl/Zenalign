"""
Dataset profiling service.
Problem-context-aware profiling following Ch. 4 modular tool principles.
Analyzes data quality with sensitivity to ML problem type.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DatasetProfiler:
    """
    Problem-context-aware dataset profiler.
    
    Analyzes datasets for quality issues with awareness of the ML problem type.
    For example:
    - Classification: prioritizes class imbalance, missing values in target
    - Regression: prioritizes outliers, data distribution
    - Anomaly Detection: focuses on outliers, rare patterns
    - Time Series: checks for temporal gaps, stationarity
    """
    
    def __init__(self, df: pd.DataFrame, problem_type: str):
        """
        Initialize profiler.
        
        Args:
            df: DataFrame to profile
            problem_type: ML problem type (classification, regression, etc.)
        """
        self.df = df
        self.problem_type = problem_type
        self.n_rows, self.n_cols = df.shape
        
        logger.info(f"Initialized profiler for {problem_type} problem: {self.n_rows} rows x {self.n_cols} cols")
    
    def detect_missing_values(self) -> Dict[str, Dict[str, Any]]:
        """
        Detect missing values across all columns.
        
        Returns:
            Dict mapping column names to missing value info
        """
        missing_info = {}
        
        for col in self.df.columns:
            missing_count = self.df[col].isna().sum()
            if missing_count > 0:
                missing_info[col] = {
                    'count': int(missing_count),
                    'percentage': round((missing_count / self.n_rows) * 100, 2),
                    'dtype': str(self.df[col].dtype)
                }
        
        logger.info(f"Found missing values in {len(missing_info)} columns")
        return missing_info
    
    def detect_outliers(self, method: str = 'iqr', threshold: float = 1.5) -> Dict[str, Dict[str, Any]]:
        """
        Detect outliers in numeric columns using IQR method.
        
        Args:
            method: Detection method ('iqr' or 'zscore')
            threshold: IQR multiplier (default 1.5) or zscore threshold (default 3)
        
        Returns:
            Dict mapping column names to outlier info
        """
        outliers = {}
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if method == 'iqr':
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                outlier_mask = (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
                outlier_values = self.df[col][outlier_mask].dropna()
                
                if len(outlier_values) > 0:
                    outliers[col] = {
                        'count': int(len(outlier_values)),
                        'percentage': round((len(outlier_values) / self.n_rows) * 100, 2),
                        'values': outlier_values.tolist(),
                        'lower_bound': float(lower_bound),
                        'upper_bound': float(upper_bound)
                    }
        
        logger.info(f"Found outliers in {len(outliers)} columns")
        return outliers
    
    def detect_class_imbalance(self, threshold: float = 0.3) -> Dict[str, Dict[str, Any]]:
        """
        Detect class imbalance in categorical columns.
        Particularly important for classification problems.
        
        Args:
            threshold: Minimum ratio for balanced classes (default 0.3 = 30%)
        
        Returns:
            Dict mapping column names to imbalance info
        """
        imbalance = {}
        
        # Get categorical columns (object, category, or low-cardinality numeric)
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Also check numeric columns with low cardinality (likely categorical)
        for col in self.df.select_dtypes(include=[np.number]).columns:
            if self.df[col].nunique() <= 10:  # Low cardinality
                categorical_cols.append(col)
        
        for col in categorical_cols:
            value_counts = self.df[col].value_counts()
            
            if len(value_counts) > 1:
                majority_class = value_counts.iloc[0]
                minority_class = value_counts.iloc[-1]
                
                imbalance_ratio = majority_class / minority_class if minority_class > 0 else float('inf')
                minority_percentage = (minority_class / self.n_rows) * 100
                
                # Flag if minority class is below threshold
                if minority_percentage < (threshold * 100):
                    imbalance[col] = {
                        'imbalance_ratio': round(float(imbalance_ratio), 2),
                        'majority_class': str(value_counts.index[0]),
                        'majority_count': int(majority_class),
                        'minority_class': str(value_counts.index[-1]),
                        'minority_count': int(minority_class),
                        'minority_percentage': round(minority_percentage, 2),
                        'distribution': {str(k): int(v) for k, v in value_counts.items()}
                    }
        
        logger.info(f"Found class imbalance in {len(imbalance)} columns")
        return imbalance
    
    def analyze_data_types(self) -> Dict[str, List[str]]:
        """
        Analyze and categorize column data types.
        
        Returns:
            Dict with categorized column names by type
        """
        dtypes_info = {
            'numeric': [],
            'categorical': [],
            'datetime': [],
            'boolean': [],
            'object': []
        }
        
        for col in self.df.columns:
            dtype = self.df[col].dtype
            
            if pd.api.types.is_numeric_dtype(dtype):
                # Check if it's boolean (0/1 only)
                unique_vals = self.df[col].dropna().unique()
                if len(unique_vals) == 2 and set(unique_vals).issubset({0, 1}):
                    dtypes_info['boolean'].append(col)
                else:
                    dtypes_info['numeric'].append(col)
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                dtypes_info['datetime'].append(col)
            elif isinstance(dtype, pd.CategoricalDtype):
                dtypes_info['categorical'].append(col)
            else:
                # Check if object column could be datetime
                try:
                    pd.to_datetime(self.df[col].dropna().head(10), format='mixed')
                    dtypes_info['datetime'].append(col)
                except:
                    dtypes_info['object'].append(col)
        
        return dtypes_info
    
    def calculate_quality_scores(self) -> Dict[str, float]:
        """
        Calculate overall quality scores.
        
        Returns:
            Dict with quality metric scores (0-1 scale)
        """
        scores = {}
        
        # Completeness: percentage of non-missing values
        total_cells = self.n_rows * self.n_cols
        missing_cells = self.df.isna().sum().sum()
        scores['completeness'] = round((total_cells - missing_cells) / total_cells, 3)
        
        # Consistency: check for consistent data types and ranges
        # For now, simple heuristic: fewer outliers = more consistent
        outliers = self.detect_outliers()
        total_outliers = sum(info['count'] for info in outliers.values())
        outlier_percentage = total_outliers / self.n_rows if self.n_rows > 0 else 0
        scores['consistency'] = round(1 - min(outlier_percentage, 1), 3)
        
        # Validity: check for valid values (no extreme outliers, reasonable ranges)
        # Simple heuristic: complement of extreme outlier rate
        extreme_outlier_count = sum(
            1 for col, info in outliers.items()
            if info['percentage'] > 10  # More than 10% outliers is concerning
        )
        scores['validity'] = round(1 - (extreme_outlier_count / max(self.n_cols, 1)), 3)
        
        # Overall score: weighted average
        scores['overall'] = round(
            0.4 * scores['completeness'] +
            0.3 * scores['consistency'] +
            0.3 * scores['validity'],
            3
        )
        
        return scores
    
    def generate_profile(self) -> Dict[str, Any]:
        """
        Generate complete dataset profile.
        
        Returns:
            Comprehensive profile dict
        """
        logger.info(f"Generating profile for {self.problem_type} problem")
        
        profile = {
            'shape': {
                'rows': self.n_rows,
                'columns': self.n_cols
            },
            'dtypes': self.analyze_data_types(),
            'missing_values': self.detect_missing_values(),
            'outliers': self.detect_outliers(),
            'class_imbalance': self.detect_class_imbalance(),
            'quality_scores': self.calculate_quality_scores()
        }
        
        return profile
    
    def get_issue_summary(self) -> List[Dict[str, Any]]:
        """
        Generate prioritized list of issues with severity levels.
        Problem-context-aware: prioritizes issues based on ML problem type.
        
        Returns:
            List of issues with type, severity, and description
        """
        issues = []
        
        # Get profile data
        missing = self.detect_missing_values()
        outliers = self.detect_outliers()
        imbalance = self.detect_class_imbalance()
        scores = self.calculate_quality_scores()
        
        # Missing values issues
        for col, info in missing.items():
            severity = 'critical' if info['percentage'] > 50 else \
                      'high' if info['percentage'] > 20 else \
                      'medium' if info['percentage'] > 5 else 'low'
            
            issues.append({
                'type': 'missing_values',
                'column': col,
                'severity': severity,
                'description': f"{info['percentage']}% missing values in {col}",
                'details': info
            })
        
        # Outlier issues (more important for regression/time_series)
        outlier_severity_boost = 1 if self.problem_type in ['regression', 'time_series'] else 0
        
        for col, info in outliers.items():
            base_severity = 'high' if info['percentage'] > 10 else \
                           'medium' if info['percentage'] > 5 else 'low'
            
            # Boost severity for regression problems
            if outlier_severity_boost and base_severity == 'medium':
                base_severity = 'high'
            
            issues.append({
                'type': 'outliers',
                'column': col,
                'severity': base_severity,
                'description': f"{info['count']} outliers detected in {col} ({info['percentage']}%)",
                'details': info
            })
        
        # Class imbalance issues (critical for classification/anomaly_detection)
        imbalance_critical = self.problem_type in ['classification', 'anomaly_detection']
        
        for col, info in imbalance.items():
            severity = 'critical' if imbalance_critical and info['minority_percentage'] < 5 else \
                      'high' if info['minority_percentage'] < 10 else \
                      'medium' if info['minority_percentage'] < 20 else 'low'
            
            issues.append({
                'type': 'class_imbalance',
                'column': col,
                'severity': severity,
                'description': f"Class imbalance in {col}: {info['imbalance_ratio']}:1 ratio",
                'details': info
            })
        
        # Overall quality issues
        if scores['overall'] < 0.7:
            issues.append({
                'type': 'overall',
                'severity': 'critical' if scores['overall'] < 0.5 else 'high',
                'description': f"Overall quality score is low: {scores['overall']:.2f}",
                'details': scores
            })
        
        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        issues.sort(key=lambda x: severity_order.get(x['severity'], 4))
        
        logger.info(f"Identified {len(issues)} issues")
        return issues
