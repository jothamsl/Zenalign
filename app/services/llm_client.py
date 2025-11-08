"""
LLM Client for generating AI-powered recommendations.
Context-aware prompts following Ch. 5 orchestration principles.
Privacy-first: Only aggregated/anonymized data sent (Ch. 12).
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class LLMClient:
    """
    OpenAI client for generating problem-context-aware recommendations.
    
    Following principles:
    - Ch. 5: Context-driven orchestration (problem description guides prompts)
    - Ch. 12: Privacy-first (only aggregated data, NO raw PII)
    - Ch. 4: Modular tool with clear interface
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = 'gpt-4o'):
        """
        Initialize LLM client.
        
        Args:
            api_key: OpenAI API key (reads from env if not provided)
            model: Model to use (default: gpt-4o for best quality)
            
        Raises:
            ValueError: If API key is not provided or found in environment
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")
        
        self.model = model
        self.client = OpenAI(api_key=self.api_key)
        
        logger.info(f"Initialized LLM client with model: {model}")
    
    def _build_prompt(
        self,
        problem_context: Dict[str, str],
        profile: Dict[str, Any],
        pii_report: Dict[str, Any]
    ) -> str:
        """
        Build problem-context-aware prompt with aggregated data only.
        
        Privacy-first: NO raw data values, only aggregated statistics.
        
        Args:
            problem_context: {'description': str, 'type': str}
            profile: Profiling results (quality scores, issues)
            pii_report: PII detection summary
            
        Returns:
            Prompt string for LLM
        """
        # Extract key info
        problem_desc = problem_context.get('description', '')
        problem_type = problem_context.get('type', 'unknown')
        
        quality_scores = profile.get('quality_scores', {})
        missing_values = profile.get('missing_values', {})
        class_imbalance = profile.get('class_imbalance', {})
        outliers = profile.get('outliers', {})
        shape = profile.get('shape', {})
        
        pii_summary = pii_report.get('summary', {})
        
        # Build structured prompt
        prompt = f"""You are a data quality expert helping with ML dataset preparation.

PROBLEM CONTEXT:
- Description: {problem_desc}
- Problem Type: {problem_type}
- Dataset Size: {shape.get('rows', 'unknown')} rows × {shape.get('columns', 'unknown')} columns

QUALITY ASSESSMENT:
- Overall Quality Score: {quality_scores.get('overall', 0):.2f}/1.00
- Completeness: {quality_scores.get('completeness', 0):.2f} ({len(missing_values)} columns with missing values)
- Consistency: {quality_scores.get('consistency', 0):.2f}
- Validity: {quality_scores.get('validity', 0):.2f}

DATA QUALITY ISSUES:
"""
        
        # Add missing values info
        if missing_values:
            prompt += "\nMissing Values:\n"
            for col, info in list(missing_values.items())[:5]:  # Top 5
                prompt += f"- {col}: {info['percentage']:.1f}% missing ({info['count']} values)\n"
        
        # Add class imbalance info
        if class_imbalance:
            prompt += "\nClass Imbalance:\n"
            for col, info in list(class_imbalance.items())[:5]:
                prompt += f"- {col}: {info['imbalance_ratio']:.1f}:1 ratio (minority class: {info['minority_percentage']:.1f}%)\n"
        
        # Add outliers info
        if outliers:
            prompt += "\nOutliers Detected:\n"
            for col, info in list(outliers.items())[:5]:
                prompt += f"- {col}: {info['count']} outliers ({info['percentage']:.1f}%)\n"
        
        # Add PII warning
        if pii_summary.get('columns_with_pii', 0) > 0:
            prompt += f"\n⚠️ PRIVACY WARNING:\n"
            prompt += f"- {pii_summary['columns_with_pii']} columns contain PII (sensitive data)\n"
            prompt += f"- {pii_summary.get('total_pii_values', 0)} total PII values detected\n"
            prompt += f"- Recommendation: Anonymize or remove PII before model training\n"
        
        prompt += f"""
TASK:
Generate specific, actionable recommendations for improving this dataset for {problem_type} tasks.
Focus on issues most critical for {problem_type} (e.g., class imbalance is critical for classification/anomaly detection).

Provide recommendations in JSON format with this structure:
{{
    "recommendations": [
        {{
            "category": "data_quality|preprocessing|feature_engineering|privacy|modeling",
            "issue": "brief_issue_name",
            "severity": "critical|high|medium|low",
            "suggestion": "Specific actionable suggestion",
            "code_example": "Python code snippet (pandas/sklearn)"
        }}
    ],
    "priority_actions": ["Top 3-5 actions in order"],
    "overall_assessment": "Brief 1-2 sentence summary"
}}

Respond ONLY with valid JSON. No markdown, no explanations outside the JSON.
"""
        
        return prompt
    
    def generate_recommendations(
        self,
        problem_context: Dict[str, str],
        profile: Dict[str, Any],
        pii_report: Dict[str, Any],
        max_tokens: int = 1500,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate AI-powered recommendations using OpenAI.
        
        Args:
            problem_context: Problem description and type
            profile: Dataset profiling results
            pii_report: PII detection results
            max_tokens: Maximum tokens for response
            temperature: Sampling temperature (0-1)
            
        Returns:
            Structured recommendations dict
        """
        logger.info(f"Generating recommendations for {problem_context.get('type')} problem")
        
        try:
            # Build prompt with aggregated data only
            prompt = self._build_prompt(problem_context, profile, pii_report)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data science expert specializing in dataset quality and ML preparation. Provide precise, actionable recommendations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                response_format={"type": "json_object"}  # Enforce JSON response
            )
            
            # Parse response
            content = response.choices[0].message.content
            recommendations = json.loads(content)
            
            logger.info(f"Generated {len(recommendations.get('recommendations', []))} recommendations")
            
            return recommendations
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            return {
                'error': 'Failed to parse recommendations',
                'recommendations': [],
                'priority_actions': [],
                'overall_assessment': 'Error generating recommendations'
            }
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return {
                'error': str(e),
                'recommendations': [],
                'priority_actions': [],
                'overall_assessment': 'Error generating recommendations due to API failure'
            }
