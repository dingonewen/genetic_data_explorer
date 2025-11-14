import requests
import json
from typing import Dict, Optional, List

class GeneticDataAPIClient:
    """
    Client to fetch genetic variant data from public APIs:
    - FAVOR API: Comprehensive functional annotation
    - MyVariant.info: Additional annotation and clinical data
    """
    
    def __init__(self):
        self.favor_base = "https://api.genohub.org/v1"
        self.myvariant_base = "https://myvariant.info/v1"
        self.timeout = 10
        
    def get_favor_data(self, rsid: str) -> Optional[Dict]:
        """
        Get variant annotation from FAVOR API using rsID
        
        Args:
            rsid: Variant rsID (e.g., 'rs429358')
            
        Returns:
            Dictionary with FAVOR annotation or None if failed
        """
        try:
            url = f"{self.favor_base}/rsids/{rsid}"
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                # FAVOR returns a list, usually with 1 variant
                if isinstance(data, list) and len(data) > 0:
                    # Take the first variant
                    variant = data[0]
                    
                    # Structure the response
                    result = {
                        "variant_id": rsid,
                        "source": "FAVOR",
                        "variant_vcf": variant.get('variant_vcf'),
                        "chromosome": variant.get('chromosome'),
                        "position": variant.get('position'),
                        "rsid": variant.get('rsid', rsid),
                        "gene": variant.get('genecode_comprehensive_info'),
                        "category": variant.get('genecode_comprehensive_category'),
                        "exonic_category": variant.get('genecode_comprehensive_exonic_category'),
                        "exonic_info": variant.get('genecode_comprehensive_exonic_info'),
                        "bravo_af": variant.get('bravo_af'),
                        "bravo_an": variant.get('bravo_an'),
                        "bravo_ac": variant.get('bravo_ac'),
                        "polyphen2_hdiv_score": variant.get('polyphen2_hdiv_score'),
                        "polyphen2_hvar_score": variant.get('polyphen2_hvar_score'),
                        "sift_score": variant.get('sift_score'),
                        "cadd_phred": variant.get('cadd_phred'),
                        "mutation_taster_score": variant.get('mutation_taster_score'),
                        "mutation_assessor_score": variant.get('mutation_assessor_score'),
                        "metasvm_pred": variant.get('metasvm_pred'),
                        "filter_status": variant.get('filter_status'),
                        "raw_data": variant
                    }
                    
                    return result
                
                return None
            
            elif response.status_code == 404:
                print(f"FAVOR API: rsID {rsid} not found")
                return None
            else:
                print(f"FAVOR API error: {response.status_code}")
                return None
            
        except Exception as e:
            print(f"FAVOR API exception: {e}")
            return None
    
    def get_myvariant_data(self, rsid: str) -> Optional[Dict]:
        """
        Get variant data from MyVariant.info API
        
        Args:
            rsid: Variant rsID (e.g., 'rs429358')
            
        Returns:
            Dictionary with variant data or None if failed
        """
        try:
            url = f"{self.myvariant_base}/variant/{rsid}"
            params = {
                "fields": "dbsnp,cadd,clinvar,dbnsfp"
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse and structure the data
                result = {
                    "variant_id": rsid,
                    "source": "MyVariant.info",
                    "gene": None,
                    "consequence": None,
                    "cadd_score": None,
                    "clinical_significance": None,
                    "diseases": []
                }
                
                # Extract gene name
                if 'cadd' in data:
                    cadd = data['cadd']
                    if 'gene' in cadd:
                        result['gene'] = cadd['gene'].get('genename', None)
                    result['consequence'] = cadd.get('consequence', None)
                    result['cadd_score'] = cadd.get('phred', None)
                
                # Extract clinical significance
                if 'clinvar' in data:
                    clinvar = data['clinvar']
                    result['clinical_significance'] = clinvar.get('clinical_significance', None)
                    
                    # Get disease associations
                    conditions = clinvar.get('conditions', [])
                    if isinstance(conditions, list):
                        result['diseases'] = conditions
                    elif isinstance(conditions, dict):
                        result['diseases'] = [conditions.get('name', '')]
                
                return result
            
            return None
            
        except Exception as e:
            print(f"MyVariant API exception: {e}")
            return None
    
    def get_ensembl_data(self, rsid: str) -> Optional[Dict]:
        """Get variant data from Ensembl REST API"""
        try:
            url = f"{self.ensembl_base}/variation/human/{rsid}"
            headers = {"Content-Type": "application/json"}
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                result = {
                    "variant_id": rsid,
                    "source": "Ensembl",
                    "name": data.get('name'),
                    "var_class": data.get('var_class'),
                    "most_severe_consequence": data.get('most_severe_consequence'),
                    "clinical_significance": data.get('clinical_significance', []),
                    "evidence": data.get('evidence', []),
                    "synonyms": data.get('synonyms', []),
                    "MAF": data.get('MAF'),
                    "minor_allele": data.get('minor_allele'),
                    "mappings": [],
                    "raw_data": data
                }
                
                mappings = data.get('mappings', [])
                if mappings:
                    for mapping in mappings:
                        result['mappings'].append({
                            "chromosome": mapping.get('seq_region_name'),
                            "start": mapping.get('start'),
                            "end": mapping.get('end'),
                            "strand": mapping.get('strand'),
                            "allele_string": mapping.get('allele_string'),
                            "assembly": mapping.get('assembly_name'),
                            "location": mapping.get('location')
                        })
                
                return result
            
            elif response.status_code == 404:
                print(f"Ensembl API: rsID {rsid} not found")
                return None
            else:
                print(f"Ensembl API error: {response.status_code}")
                return None
            
        except Exception as e:
            print(f"Ensembl API exception: {e}")
            return None
    


    
    def get_combined_data(self, rsid: str) -> Dict:
        """
        Get data from all APIs and combine
        
        Args:
            rsid: Variant rsID (e.g., 'rs429358')
            
        Returns:
            Dictionary with combined data from all sources
        """
        result = {
            "variant_id": rsid,
            "favor": None,
            "myvariant": None,
            "ensembl": None,
            "success": False
        }
        
        # Get FAVOR data (primary source)
        favor_data = self.get_favor_data(rsid)
        if favor_data:
            result['favor'] = favor_data
            result['success'] = True
        
        # Get MyVariant data (for clinical info)
        myvariant_data = self.get_myvariant_data(rsid)
        if myvariant_data:
            result['myvariant'] = myvariant_data
            result['success'] = True
        
        # Get Ensembl data (for genomic context)
        ensembl_data = self.get_ensembl_data(rsid)
        if ensembl_data:
            result['ensembl'] = ensembl_data
            result['success'] = True
        
        return result
    
    def load_mock_data(self, filename: str) -> Optional[Dict]:
        """
        Fallback: Load mock data if APIs fail
        
        Args:
            filename: Mock data filename in mock_data/ folder
            
        Returns:
            Dictionary with mock data or None if error
        """
        try:
            with open(f"mock_data/{filename}", "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading mock data {filename}: {e}")
            return None