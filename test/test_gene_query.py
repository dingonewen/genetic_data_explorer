import pytest
from unittest.mock import patch, MagicMock
from src.api_client import GeneticDataAPIClient


class TestGeneQuery:
    """Test gene symbol to rsID conversion functionality"""

    @pytest.fixture
    def client(self):
        return GeneticDataAPIClient()

    def test_query_gene_predefined_apoe(self, client):
        """Test predefined mapping for APOE gene"""
        result = client.query_gene_to_rsid("APOE")
        assert result == "rs429358"

    def test_query_gene_predefined_brca1(self, client):
        """Test predefined mapping for BRCA1 gene"""
        result = client.query_gene_to_rsid("BRCA1")
        assert result == "rs80357906"

    def test_query_gene_predefined_tp53(self, client):
        """Test predefined mapping for TP53 gene"""
        result = client.query_gene_to_rsid("TP53")
        assert result == "rs28934576"

    def test_query_gene_case_insensitive(self, client):
        """Test that gene query is case-insensitive"""
        result_upper = client.query_gene_to_rsid("APOE")
        result_lower = client.query_gene_to_rsid("apoe")
        result_mixed = client.query_gene_to_rsid("Apoe")

        assert result_upper == result_lower == result_mixed == "rs429358"

    @patch('requests.get')
    def test_query_gene_api_fallback(self, mock_get, client):
        """Test API fallback for non-predefined genes"""
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'hits': [
                {
                    'dbsnp': {'rsid': 'rs12345'},
                    'clinvar': {'clinical_significance': 'Pathogenic'}
                }
            ]
        }
        mock_get.return_value = mock_response

        result = client.query_gene_to_rsid("UNKNOWN_GENE")

        # Should attempt API call
        mock_get.assert_called_once()
        assert result == 'rs12345'

    @patch('requests.get')
    def test_query_gene_no_results(self, mock_get, client):
        """Test handling when no variants found for gene"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'hits': []}
        mock_get.return_value = mock_response

        result = client.query_gene_to_rsid("NONEXISTENT_GENE")
        assert result is None

    @patch('requests.get')
    def test_query_gene_api_error(self, mock_get, client):
        """Test handling of API errors"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = client.query_gene_to_rsid("SOME_GENE")
        assert result is None

    @patch('requests.get')
    def test_query_gene_priority_pathogenic(self, mock_get, client):
        """Test that pathogenic variants are prioritized"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'hits': [
                {
                    'dbsnp': {'rsid': 'rs11111'},
                    'clinvar': {'clinical_significance': 'Benign'}
                },
                {
                    'dbsnp': {'rsid': 'rs22222'},
                    'clinvar': {'clinical_significance': 'Pathogenic'}
                },
                {
                    'dbsnp': {'rsid': 'rs33333'},
                    'clinvar': {'clinical_significance': 'Likely pathogenic'}
                }
            ]
        }
        mock_get.return_value = mock_response

        result = client.query_gene_to_rsid("TEST_GENE")

        # Should return pathogenic variant (rs22222), not the first hit (rs11111)
        assert result == 'rs22222'