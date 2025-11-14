import requests
import json
from typing import Dict, Optional, List

class GeneticDataAPIClient:
    """
    Client to fetch genetic variant data from public APIs:
    - FAVOR API: Comprehensive functional annotation
    - MyVariant.info: Additional annotation and clinical data
    - Ensembl REST API: Genomic context and population data
    """

    def __init__(self):
        self.favor_base = "https://api.genohub.org/v1"
        self.myvariant_base = "https://myvariant.info/v1"
        self.ensembl_base = "https://rest.ensembl.org"
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
    
    def query_gene_to_rsid(self, gene_symbol: str) -> Optional[str]:
        """
        Query MyVariant.info to find the most clinically relevant variant for a gene

        Args:
            gene_symbol: Gene symbol (e.g., 'APOE', 'BRCA1')

        Returns:
            rsID of the most relevant variant or None if not found
        """
        try:
            # First, try a simple predefined mapping for common genes
            GENE_MAPPING = {
                'APOE': 'rs429358',      # Alzheimer's disease risk
                'BRCA1': 'rs80357906',   # Breast cancer pathogenic
                'BRCA2': 'rs80359550',   # Breast cancer pathogenic
                'TP53': 'rs28934576',    # Li-Fraumeni syndrome
                'CFTR': 'rs113993960',   # Cystic fibrosis
                'HBB': 'rs334',          # Sickle cell disease
                'MTHFR': 'rs1801133',    # Folate metabolism
                'F5': 'rs6025',          # Factor V Leiden
                'HFE': 'rs1800562',      # Hemochromatosis
                'LDLR': 'rs28942080'     # Familial hypercholesterolemia
            }

            gene_upper = gene_symbol.upper()
            if gene_upper in GENE_MAPPING:
                result = GENE_MAPPING[gene_upper]
                print(f"[GENE QUERY] Found predefined variant for {gene_upper}: {result}")
                return result

            # If not in predefined list, try API query
            url = f"{self.myvariant_base}/query"
            params = {
                'q': f'cadd.gene.genename:{gene_upper}',
                'fields': 'dbsnp.rsid,clinvar.clinical_significance',
                'size': 20
            }

            response = requests.get(url, params=params, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                hits = data.get('hits', [])

                if not hits:
                    print(f"[GENE QUERY] No variants found for gene: {gene_symbol}")
                    return None

                # Priority: Pathogenic > Likely pathogenic > Other
                pathogenic_variants = []
                likely_pathogenic = []
                other_variants = []

                for hit in hits:
                    rsid = hit.get('dbsnp', {}).get('rsid')
                    if not rsid:
                        continue

                    # Get clinical significance
                    significance_raw = hit.get('clinvar', {}).get('clinical_significance', '')

                    # Handle both string and list formats
                    if isinstance(significance_raw, list):
                        significance = ' '.join(significance_raw).lower()
                    else:
                        significance = str(significance_raw).lower()

                    if 'pathogenic' in significance and 'likely' not in significance:
                        pathogenic_variants.append(rsid)
                    elif 'likely pathogenic' in significance:
                        likely_pathogenic.append(rsid)
                    else:
                        other_variants.append(rsid)

                # Return highest priority variant
                if pathogenic_variants:
                    result = pathogenic_variants[0]
                    print(f"[GENE QUERY] Found pathogenic variant for {gene_symbol}: {result}")
                    return result
                elif likely_pathogenic:
                    result = likely_pathogenic[0]
                    print(f"[GENE QUERY] Found likely pathogenic variant for {gene_symbol}: {result}")
                    return result
                elif other_variants:
                    result = other_variants[0]
                    print(f"[GENE QUERY] Found variant for {gene_symbol}: {result}")
                    return result
                else:
                    # Fallback: return first hit with rsid
                    for hit in hits:
                        rsid = hit.get('dbsnp', {}).get('rsid')
                        if rsid:
                            print(f"[GENE QUERY] Found variant (no clinical data) for {gene_symbol}: {rsid}")
                            return rsid

                    return None
            else:
                print(f"[GENE QUERY] API error: {response.status_code}")
                return None

        except Exception as e:
            print(f"[GENE QUERY EXCEPTION] {type(e).__name__}: {str(e)}")
            return None

    def get_ensembl_data(self, rsid: str) -> Optional[Dict]:
        """Get variant data from Ensembl REST API"""
        try:
            url = f"{self.ensembl_base}/variation/human/{rsid}"
            # Ensembl requires proper headers for API access
            headers = {
                'Accept': 'application/json',
                'User-Agent': 'GeneticDataExplorer/1.0 (Educational project; contact: student@university.edu)'
            }

            print(f"[DEBUG] Ensembl URL: {url}")
            response = requests.get(url, headers=headers, timeout=self.timeout)
            print(f"[DEBUG] Ensembl status code: {response.status_code}")

            # Check for rate limiting (429 Too Many Requests)
            if response.status_code == 429:
                retry_after = response.headers.get('Retry-After', '60')
                print(f"[ENSEMBL] Rate limited. Retry after {retry_after} seconds")
                return None

            if response.status_code == 200:
                data = response.json()
                print(f"[DEBUG] Ensembl data keys: {list(data.keys())[:10]}")

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

                print(f"[DEBUG] Ensembl result successful with {len(result['mappings'])} mappings")
                return result

            elif response.status_code == 404:
                print(f"[ENSEMBL] rsID {rsid} not found (404)")
                return None
            else:
                print(f"[ENSEMBL ERROR] Status {response.status_code}: {response.text[:200]}")
                return None

        except Exception as e:
            print(f"[ENSEMBL EXCEPTION] {type(e).__name__}: {str(e)}")
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