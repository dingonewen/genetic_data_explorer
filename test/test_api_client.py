"""
Unit tests for GeneticDataAPIClient

Tests API integration, data parsing, and error handling.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api_client import GeneticDataAPIClient


@pytest.fixture
def client():
    """Create API client instance for testing"""
    return GeneticDataAPIClient()


@pytest.fixture
def mock_favor_response():
    """Mock FAVOR API successful response"""
    return {
        "chromosome": "19",
        "position": "44908684",
        "ref_allele": "T",
        "alt_allele": "C",
        "rsid": "rs429358",
        "variant_vcf": "19-44908684-T-C",
        "cadd_phred": 15.36,
        "polyphen2_hdiv_score": 0.999,
        "polyphen2_hvar_score": 0.995,
        "sift_score": 0.01,
        "bravo_an": 264690,
        "bravo_ac": 38853,
        "bravo_af": 0.1467,
        "filter_status": "PASS",
        "genecode_comprehensive_exonic_category": "missense",
        "genecode_comprehensive_info": "APOE",  # Correct field name
        "mutation_taster_score": 0.81,
        "mutation_assessor_score": 2.64,
        "metasvm_pred": "T"
    }


@pytest.fixture
def mock_myvariant_response():
    """Mock MyVariant.info API successful response"""
    return {
        "_id": "rs429358",
        "cadd": {
            "gene": {"genename": "APOE"},
            "consequence": "missense_variant",
            "phred": 15.36
        },
        "clinvar": {
            "clinical_significance": "Pathogenic",
            "conditions": [
                {"name": "Alzheimer disease"},
                {"name": "Hyperlipoproteinemia"}
            ]
        }
    }


@pytest.fixture
def mock_ensembl_response():
    """Mock Ensembl REST API successful response"""
    return {
        "name": "rs429358",
        "var_class": "SNP",
        "most_severe_consequence": "missense_variant",
        "clinical_significance": ["Pathogenic"],
        "evidence": ["Frequency", "1000Genomes", "ESP", "ExAC"],
        "synonyms": ["CM920001", "VAR_000652"],
        "MAF": "0.15",
        "minor_allele": "C",
        "mappings": [
            {
                "seq_region_name": "19",
                "start": 44908684,
                "end": 44908684,
                "strand": 1,
                "allele_string": "T/C",
                "assembly_name": "GRCh38",
                "location": "19:44908684-44908684"
            }
        ]
    }


class TestFAVORAPI:
    """Test FAVOR API integration"""

    def test_get_favor_data_success(self, client, mock_favor_response):
        """Test successful FAVOR API call"""
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = [mock_favor_response]

            result = client.get_favor_data("rs429358")

            assert result is not None
            assert result['variant_id'] == 'rs429358'
            assert result['gene'] == 'APOE'
            assert result['cadd_phred'] == 15.36
            assert result['chromosome'] == '19'
            assert result['bravo_af'] == 0.1467

    def test_get_favor_data_404(self, client):
        """Test FAVOR API 404 response (variant not found)"""
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 404

            result = client.get_favor_data("rs999999999")

            assert result is None

    def test_get_favor_data_exception(self, client):
        """Test FAVOR API network exception handling"""
        with patch('requests.get', side_effect=Exception("Network timeout")):
            result = client.get_favor_data("rs429358")

            assert result is None


class TestMyVariantAPI:
    """Test MyVariant.info API integration"""

    def test_get_myvariant_data_success(self, client, mock_myvariant_response):
        """Test successful MyVariant API call"""
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_myvariant_response

            result = client.get_myvariant_data("rs429358")

            assert result is not None
            assert result['variant_id'] == 'rs429358'
            assert result['gene'] == 'APOE'
            assert result['clinical_significance'] == 'Pathogenic'
            assert len(result['diseases']) == 2
            # diseases is a list of dicts with 'name' field
            assert result['diseases'][0]['name'] == 'Alzheimer disease'
            assert result['diseases'][1]['name'] == 'Hyperlipoproteinemia'

    def test_get_myvariant_data_404(self, client):
        """Test MyVariant API 404 response (variant not found)"""
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 404

            result = client.get_myvariant_data("rs999999")

            assert result is None

    def test_get_myvariant_data_exception(self, client):
        """Test MyVariant API exception handling"""
        with patch('requests.get', side_effect=Exception("Connection error")):
            result = client.get_myvariant_data("rs429358")

            assert result is None


class TestEnsemblAPI:
    """Test Ensembl REST API integration"""

    def test_get_ensembl_data_success(self, client, mock_ensembl_response):
        """Test successful Ensembl API call"""
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_ensembl_response

            result = client.get_ensembl_data("rs429358")

            assert result is not None
            assert result['variant_id'] == 'rs429358'
            assert result['var_class'] == 'SNP'
            assert result['most_severe_consequence'] == 'missense_variant'
            assert len(result['mappings']) == 1
            assert result['mappings'][0]['chromosome'] == '19'
            assert 'Pathogenic' in result['clinical_significance']

    def test_get_ensembl_data_404(self, client):
        """Test Ensembl API 404 response (variant not found)"""
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 404

            result = client.get_ensembl_data("rs999999")

            assert result is None

    def test_get_ensembl_data_429_rate_limit(self, client):
        """Test Ensembl API rate limiting (429 Too Many Requests)"""
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 429
            mock_get.return_value.headers = {'Retry-After': '60'}

            result = client.get_ensembl_data("rs429358")

            assert result is None

    def test_get_ensembl_data_exception(self, client):
        """Test Ensembl API exception handling"""
        with patch('requests.get', side_effect=Exception("Request timeout")):
            result = client.get_ensembl_data("rs429358")

            assert result is None


class TestCombinedData:
    """Test combined data from multiple APIs"""

    def test_get_combined_data_all_success(self, client):
        """Test successful data merge from all 3 APIs"""
        with patch.object(client, 'get_favor_data', return_value={'gene': 'APOE', 'cadd_phred': 15.36}), \
             patch.object(client, 'get_myvariant_data', return_value={'clinical_significance': 'Pathogenic'}), \
             patch.object(client, 'get_ensembl_data', return_value={'var_class': 'SNP'}):

            result = client.get_combined_data("rs429358")

            assert result['success'] is True
            assert result['variant_id'] == 'rs429358'
            assert result['favor'] is not None
            assert result['myvariant'] is not None
            assert result['ensembl'] is not None
            assert result['favor']['gene'] == 'APOE'

    def test_get_combined_data_partial_success(self, client):
        """Test data merge when some APIs fail (FAVOR + Ensembl work, MyVariant fails)"""
        with patch.object(client, 'get_favor_data', return_value={'gene': 'APOE'}), \
             patch.object(client, 'get_myvariant_data', return_value=None), \
             patch.object(client, 'get_ensembl_data', return_value={'var_class': 'SNP'}):

            result = client.get_combined_data("rs429358")

            assert result['success'] is True  # Success if at least one API works
            assert result['favor'] is not None
            assert result['myvariant'] is None
            assert result['ensembl'] is not None

    def test_get_combined_data_all_fail(self, client):
        """Test when all APIs fail"""
        with patch.object(client, 'get_favor_data', return_value=None), \
             patch.object(client, 'get_myvariant_data', return_value=None), \
             patch.object(client, 'get_ensembl_data', return_value=None):

            result = client.get_combined_data("rs999999")

            assert result['success'] is False
            assert result['favor'] is None
            assert result['myvariant'] is None
            assert result['ensembl'] is None