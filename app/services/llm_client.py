import logging
import json
from typing import Dict, Any, Optional
from openai import OpenAI
from app.config import validate_required_keys
from app.models.schemas import DatasetProfile, AnalysisRequest

logger = logging.getLogger(__name__)


class LLMClient:
    """OpenAI client for dataset analysis."""
    
    def __init__(self, api_key: str):
        """Initialize with API key. Raises RuntimeError if key missing."""
        if not api_key:
            raise RuntimeError(
                "ERROR: Missing required environment variable: OPENAI_API_KEY\n"
                "ACTION: export OPENAI_API_KEY=your_key_here and re-run. No fallback will be used."
            )
        self.client = OpenAI(api_key=api_key)
        logger.info("LLM client initialized")
    
    def _sanitize_profile_for_llm(self, profile: DatasetProfile) -> Dict[str, Any]:
        """
        Remove raw data and sensitive info from profile before sending to LLM.
        Only send aggregates and statistics.
        """
        sanitized = profile.model_dump()
        
        # For columns with PII, mask the top categories
        for col in sanitized["columns"]:
            if col["pii_detected"] and col["top_categories"]:
                col["top_categories"] = [
                    {"value": "[REDACTED]", "count": item["count"]}
                    for item in col["top_categories"]
                ]
        
        return sanitized
    
    def analyze_dataset(
        self,
        profile: DatasetProfile,
        request: AnalysisRequest
    ) -> Dict[str, Any]:
        """
        Send sanitized profile to OpenAI for analysis.
        Returns structured recommendations.
        """
        logger.info(f"Analyzing dataset {request.dataset_id} with OpenAI GPT-5")
        
        # Sanitize profile
        sanitized_profile = self._sanitize_profile_for_llm(profile)
        
        # Build prompt
        prompt = self._build_analysis_prompt(sanitized_profile, request)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert data scientist and ML consultant. Analyze the dataset profile "
                            "in the context of the user's ML problem description. Provide structured recommendations "
                            "in JSON format. Focus on: data quality issues, missing data patterns, potential biases, "
                            "PII concerns, feature engineering opportunities, and dataset suitability for their "
                            "specific use case. Recommend appropriate ML approaches and preprocessing steps."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            logger.info("Received LLM response")
            
            # Parse JSON response
            recommendations = json.loads(content)
            return recommendations
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise RuntimeError(
                f"ERROR: OpenAI API call failed: {str(e)}\n"
                "ACTION: Verify OPENAI_API_KEY is valid and you have API access."
            )
    
    def _build_analysis_prompt(
        self,
        profile: Dict[str, Any],
        request: AnalysisRequest
    ) -> str:
        """Build the analysis prompt with natural language problem description."""
        return f"""I need help analyzing a dataset for the following machine learning problem:

USER'S PROBLEM DESCRIPTION:
"{request.problem_description}"

DATASET PROFILE:
- Total Rows: {profile['total_rows']}
- Total Columns: {profile['total_columns']}
- Quality Score: {profile['quality_score']}/100
- PII Detected: {profile['pii_summary']['pii_detected']}
- PII Columns: {profile['pii_summary']['pii_columns']}

Target Column (if specified): {request.target_column or 'Not specified'}
Protected Columns (if any): {request.protected_columns or 'None'}

COLUMN DETAILS:
{json.dumps(profile['columns'], indent=2)}

Based on the user's problem description and the dataset profile, provide a comprehensive analysis in the following JSON structure:

{{
  "problem_understanding": "Your interpretation of what ML problem they're trying to solve",
  "recommended_approach": "Specific ML approach(es) recommended (e.g., classification, regression, clustering, etc.)",
  "overall_quality": "excellent|good|fair|poor",
  "quality_issues": ["list of specific data quality issues found"],
  "missing_data_assessment": "detailed assessment of missing data patterns and their impact",
  "pii_concerns": "description of PII risks and compliance considerations",
  "bias_risks": ["potential sources of bias that could affect their specific use case"],
  "feature_engineering_suggestions": ["specific feature engineering ideas based on their problem"],
  "recommendations": ["prioritized, actionable recommendations tailored to their problem"],
  "suitability_assessment": "how well this dataset fits their stated problem and what's missing",
  "suggested_preprocessing": ["preprocessing steps specific to their use case"],
  "potential_challenges": ["challenges they might face with this data for their problem"],
  "success_metrics": ["suggested metrics to evaluate their solution"]
}}

IMPORTANT: Tailor all recommendations specifically to the user's problem description. Be concrete and actionable."""


def get_llm_client(api_key: str) -> LLMClient:
    """Factory function to create LLM client with validation."""
    if not api_key:
        raise RuntimeError(
            "ERROR: Missing required environment variable: OPENAI_API_KEY\n"
            "ACTION: export OPENAI_API_KEY=your_key_here and re-run. No fallback will be used."
        )
    return LLMClient(api_key)
