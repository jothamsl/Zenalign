"""
Exa search client for finding domain-specific resources.
Searches for papers, blogs, Kaggle notebooks based on problem context.
"""

import os
import logging
from typing import Dict, List, Any, Optional

try:
    from exa_py import Exa

    EXA_AVAILABLE = True
except ImportError:
    EXA_AVAILABLE = False
    Exa = None

logger = logging.getLogger(__name__)


class ExaClient:
    """
    Exa search client for discovering relevant resources.
    Searches for:
    - Research papers (arXiv, IEEE, ACM)
    - Technical blogs (Medium, Towards Data Science)
    - Kaggle notebooks
    - Stack Overflow discussions
    - GitHub repositories
    - Tweets
    - News articles
    - PDFs
    - Reddit discussions
    - Hugging Face models/notebooks
    - YouTube videos/tutorials
    - LinkedIn articles/profiles
    Based on problem context and detected data quality issues.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Exa client.
        Args:
            api_key: Exa API key (reads from env if not provided)
        Raises:
            ValueError: If API key is not provided or found in environment
        """
        self.api_key = api_key or os.getenv("EXA_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Exa API key must be provided or set in EXA_API_KEY environment variable"
            )
        if EXA_AVAILABLE and Exa:
            self.client = Exa(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("exa-py not installed, searches will be mocked")
        logger.info("Initialized Exa client")

    def _categorize_resource_type(self, url: str) -> str:
        """
        Categorize resource type based on URL.
        Args:
            url: Resource URL
        Returns:
            Resource type: 'paper', 'blog', 'kaggle', 'stackoverflow', 'github', 'tweet', 'news', 'pdf', 'reddit', 'huggingface', 'youtube', 'linkedin', 'other'
        """
        url_lower = url.lower()
        if any(
            domain in url_lower
            for domain in ["arxiv.org", "ieee", "acm.org", "openreview", "papers"]
        ):
            return "paper"
        elif "kaggle.com" in url_lower:
            return "kaggle"
        elif "stackoverflow.com" in url_lower or "stackexchange.com" in url_lower:
            return "stackoverflow"
        elif "github.com" in url_lower:
            return "github"
        elif any(
            domain in url_lower
            for domain in ["medium.com", "towardsdatascience.com", "blog", "dev.to"]
        ):
            return "blog"
        elif "twitter.com" in url_lower or "x.com" in url_lower:
            return "tweet"
        elif any(
            domain in url_lower
            for domain in ["nytimes.com", "bbc.com", "news", "cnn.com"]
        ):
            return "news"
        elif ".pdf" in url_lower:
            return "pdf"
        elif "reddit.com" in url_lower:
            return "reddit"
        elif "huggingface.co" in url_lower:
            return "huggingface"
        elif "youtube.com" in url_lower or "youtu.be" in url_lower:
            return "youtube"
        elif "linkedin.com" in url_lower:
            return "linkedin"
        else:
            return "other"

    def _build_search_queries(
        self,
        problem_context: Dict[str, str],
        issues: List[Dict[str, Any]],
        max_queries: int = 5,
    ) -> List[str]:
        """
        Build search queries from problem context and issues.
        Improved to better incorporate full user description.
        Args:
            problem_context: {'description': str, 'type': str}
            issues: List of detected issues
            max_queries: Maximum number of queries to generate
        Returns:
            List of search query strings
        """
        queries = []
        problem_desc = problem_context.get("description", "").strip()
        problem_type = problem_context.get("type", "").strip()

        if not problem_desc:
            problem_desc = problem_type

        # Base query using full description
        base_query = f"{problem_desc} machine learning best practices"
        queries.append(base_query)

        # Variant for domain knowledge
        queries.append(f"{problem_desc} domain knowledge overview tutorials")

        # Variant for practitioner approaches
        queries.append(
            f"{problem_desc} practitioner approaches case studies kaggle notebooks"
        )

        # Issue-specific queries
        for issue in issues[: max_queries - len(queries)]:
            category = issue.get("category", "").lower()
            issue_desc = category.replace("_", " ")
            if "imbalance" in category:
                issue_query = f"{problem_desc} handling {issue_desc} SMOTE techniques oversampling"
            elif "missing" in category:
                issue_query = (
                    f"{problem_desc} {issue_desc} imputation methods best practices"
                )
            elif "outlier" in category:
                issue_query = f"{problem_desc} {issue_desc} detection robust methods"
            elif "privacy" in category or "pii" in category:
                issue_query = (
                    f"{problem_desc} data {issue_desc} anonymization GDPR compliance"
                )
            else:
                issue_query = (
                    f"{problem_desc} handling {issue_desc} in machine learning"
                )
            queries.append(issue_query)

        # Dedup and limit
        queries = list(dict.fromkeys(queries))[:max_queries]
        logger.info(
            f"Generated {len(queries)} search queries based on description: {problem_desc[:100]}..."
        )
        return queries

    def search_resources(
        self,
        problem_context: Dict[str, str],
        issues: List[Dict[str, Any]],
        max_results: int = 20,
        num_results_per_query: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant resources based on context and issues.
        Updated to use multiple categories for diversity (papers, news, tweets, github, etc.).
        Uses neural search for broader relevance.
        Args:
            problem_context: Problem description and type
            issues: Detected data quality issues
            max_results: Maximum total results to return
            num_results_per_query: Results per search query
        Returns:
            List of resource dicts with title, url, summary, type, relevance_score
        """
        logger.info(
            f"Searching for resources related to {problem_context.get('description', 'unknown')[:50]}..."
        )
        try:
            # Build search queries
            queries = self._build_search_queries(problem_context, issues)

            # Define categories for diversity
            categories = [
                None,
                "research paper",
                "news",
                "tweet",
                "github",
                "pdf",
            ]  # None for general

            all_results = []
            seen_urls = set()

            for query in queries:
                for category in categories:
                    try:
                        if self.client:
                            # Real Exa search with neural type (text-only for reliability)
                            logger.debug(
                                f"Executing Exa search for query: '{query}' category: {category}"
                            )
                            response = self.client.search_and_contents(
                                query,
                                num_results=min(
                                    num_results_per_query, 10
                                ),  # Cap per call
                                text=True,
                                type="neural",
                                category=category,
                            )
                            logger.debug(
                                f"Exa returned {len(response.results)} results for query: '{query}' category: {category}"
                            )
                            for result in response.results:
                                url = result.url
                                # Skip duplicates
                                if url in seen_urls:
                                    continue
                                seen_urls.add(url)
                                # Categorize resource
                                resource_type = self._categorize_resource_type(url)
                                # Use text for summary
                                summary = (
                                    result.text[:300] + "..."
                                    if hasattr(result, "text")
                                    and result.text
                                    and len(result.text) > 300
                                    else result.text
                                    if hasattr(result, "text") and result.text
                                    else "No summary available"
                                )
                                # Create resource dict
                                resource = {
                                    "title": result.title or "Untitled",
                                    "url": url,
                                    "summary": summary,
                                    "type": resource_type,
                                    "relevance_score": 0.8,  # Default relevance score since Exa doesn't provide one
                                    "query": query,
                                    "category": category or "general",
                                }
                                all_results.append(resource)
                        else:
                            # Mock results for testing (when exa-py not installed)
                            logger.warning(
                                f"Exa client not available, returning mock results for query: '{query}' category: {category}"
                            )
                            mock_resources = [
                                {
                                    "title": f"Mock {category or 'General'} Resource 1 for {query}",
                                    "url": "https://example.com/mock1",
                                    "summary": "This is a mock summary for testing purposes.",
                                    "type": category or "other",
                                    "relevance_score": 0.8,
                                    "query": query,
                                    "category": category or "general",
                                },
                                {
                                    "title": f"Mock {category or 'General'} Resource 2 for {query}",
                                    "url": "https://example.com/mock2",
                                    "summary": "Another mock summary.",
                                    "type": category or "other",
                                    "relevance_score": 0.7,
                                    "query": query,
                                    "category": category or "general",
                                },
                            ]
                            all_results.extend(mock_resources)
                    except Exception as e:
                        logger.warning(
                            f"Search failed for query '{query}' category {category}: {str(e)}"
                        )
                        continue

            # Sort by relevance score descending and limit results
            all_results.sort(key=lambda x: x["relevance_score"], reverse=True)
            all_results = all_results[:max_results]

            logger.info(
                f"Found {len(all_results)} unique resources from diverse sources"
            )
            return all_results
        except Exception as e:
            logger.error(f"Error searching resources: {e}")
            return []
