"""
Test Exa search client.
Following TDD: Write failing tests first.
Domain-specific resource discovery to enrich analysis reports.
"""

import pytest
from unittest.mock import Mock, patch
from app.services.exa_client import ExaClient


@pytest.fixture
def sample_problem_context():
    """Sample problem context."""
    return {
        "description": "Detect fraudulent credit card transactions using purchase history",
        "type": "anomaly_detection",
    }


@pytest.fixture
def sample_issues():
    """Sample detected issues from profiler."""
    return [
        {
            "category": "class_imbalance",
            "severity": "critical",
            "description": "Severe class imbalance detected (30:1 ratio)",
        },
        {
            "category": "missing_values",
            "severity": "high",
            "description": "Missing values in amount column (15%)",
        },
    ]


class TestExaClient:
    """Test the Exa search client."""

    def test_client_initialization(self):
        """Test that client initializes with API key."""
        with patch.dict("os.environ", {"EXA_API_KEY": "test-key"}):
            with patch("app.services.exa_client.Exa"):
                client = ExaClient()
                assert client.api_key == "test-key"

    def test_build_search_queries(self, sample_problem_context, sample_issues):
        """Test that search queries are built from context and issues."""
        with patch("app.services.exa_client.Exa"):
            client = ExaClient(api_key="test")
            queries = client._build_search_queries(
                sample_problem_context, sample_issues
            )

            assert isinstance(queries, list)
            assert len(queries) > 0
            # Should include problem type
            assert any("fraud" in q.lower() or "anomaly" in q.lower() for q in queries)
            # Should include issues
            assert any("imbalance" in q.lower() for q in queries)

    def test_build_queries_limits_to_max_queries(self, sample_problem_context):
        """Test that query building respects max_queries limit."""
        with patch("app.services.exa_client.Exa"):
            client = ExaClient(api_key="test")
            many_issues = [
                {
                    "category": f"issue_{i}",
                    "severity": "high",
                    "description": f"Issue {i}",
                }
                for i in range(10)
            ]

            queries = client._build_search_queries(
                sample_problem_context, many_issues, max_queries=3
            )

            assert len(queries) <= 3

    @patch("app.services.exa_client.Exa")
    def test_search_resources_calls_exa(
        self, mock_exa_class, sample_problem_context, sample_issues
    ):
        """Test that search_resources calls Exa API."""
        mock_exa = Mock()
        mock_result = Mock()
        mock_result.results = [
            Mock(
                title="SMOTE for Imbalanced Data",
                url="https://example.com/smote",
                text="Guide to SMOTE technique...",
            )
        ]
        mock_exa.search_and_contents.return_value = mock_result
        mock_exa_class.return_value = mock_exa

        client = ExaClient(api_key="test")
        results = client.search_resources(sample_problem_context, sample_issues)

        assert mock_exa.search_and_contents.called
        assert isinstance(results, list)

    @patch("app.services.exa_client.Exa")
    def test_search_resources_returns_structured_data(
        self, mock_exa_class, sample_problem_context, sample_issues
    ):
        """Test that search results are returned in structured format."""
        mock_exa = Mock()
        mock_result = Mock()
        mock_result.results = [
            Mock(
                title="Handling Class Imbalance in Fraud Detection",
                url="https://arxiv.org/paper123",
                text="This paper discusses SMOTE and other techniques...",
            ),
            Mock(
                title="Missing Value Imputation Best Practices",
                url="https://kaggle.com/notebook456",
                text="Tutorial on various imputation methods...",
            ),
        ]
        mock_exa.search_and_contents.return_value = mock_result
        mock_exa_class.return_value = mock_exa

        client = ExaClient(api_key="test")
        results = client.search_resources(sample_problem_context, sample_issues)

        assert len(results) > 0
        first_result = results[0]
        assert "title" in first_result
        assert "url" in first_result
        assert "summary" in first_result
        assert "type" in first_result  # paper, blog, kaggle, etc.
        assert "relevance_score" in first_result

    @patch("app.services.exa_client.Exa")
    def test_search_categorizes_resource_types(
        self, mock_exa_class, sample_problem_context, sample_issues
    ):
        """Test that resources are categorized by type."""
        mock_exa = Mock()
        mock_result = Mock()
        mock_result.results = [
            Mock(title="Paper", url="https://arxiv.org/123", text="..."),
            Mock(title="Blog", url="https://towardsdatascience.com/abc", text="..."),
            Mock(title="Notebook", url="https://kaggle.com/notebook", text="..."),
        ]
        mock_exa.search_and_contents.return_value = mock_result
        mock_exa_class.return_value = mock_exa

        client = ExaClient(api_key="test")
        results = client.search_resources(sample_problem_context, sample_issues)

        types = [r["type"] for r in results]
        assert "paper" in types
        assert "blog" in types
        assert "kaggle" in types

    @patch("app.services.exa_client.Exa")
    def test_search_filters_duplicates(
        self, mock_exa_class, sample_problem_context, sample_issues
    ):
        """Test that duplicate URLs are filtered out."""
        mock_exa = Mock()
        mock_result = Mock()
        mock_result.results = [
            Mock(title="Resource 1", url="https://example.com/same", text="..."),
            Mock(title="Resource 2", url="https://example.com/same", text="..."),
            Mock(title="Resource 3", url="https://example.com/different", text="..."),
        ]
        mock_exa.search_and_contents.return_value = mock_result
        mock_exa_class.return_value = mock_exa

        client = ExaClient(api_key="test")
        results = client.search_resources(sample_problem_context, sample_issues)

        urls = [r["url"] for r in results]
        assert len(urls) == len(set(urls))  # No duplicates

    @patch("app.services.exa_client.Exa")
    def test_search_limits_results(
        self, mock_exa_class, sample_problem_context, sample_issues
    ):
        """Test that results are limited to max_results."""
        mock_exa = Mock()
        mock_result = Mock()
        mock_result.results = [
            Mock(title=f"Resource {i}", url=f"https://example.com/{i}", text="...")
            for i in range(20)
        ]
        mock_exa.search_and_contents.return_value = mock_result
        mock_exa_class.return_value = mock_exa

        client = ExaClient(api_key="test")
        results = client.search_resources(
            sample_problem_context, sample_issues, max_results=5
        )

        assert len(results) <= 5

    def test_error_handling_invalid_api_key(self):
        """Test handling of invalid API key."""
        with pytest.raises(ValueError, match="API key"):
            with patch("app.services.exa_client.Exa"):
                ExaClient(api_key=None)

    @patch("app.services.exa_client.Exa")
    def test_error_handling_api_failure(
        self, mock_exa_class, sample_problem_context, sample_issues
    ):
        """Test graceful handling of API failures."""
        mock_exa = Mock()
        mock_exa.search_and_contents.side_effect = Exception("API Error")
        mock_exa_class.return_value = mock_exa

        client = ExaClient(api_key="test")
        results = client.search_resources(sample_problem_context, sample_issues)

        # Should return empty list instead of crashing
        assert isinstance(results, list)
        assert len(results) == 0
