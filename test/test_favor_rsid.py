import requests
import json

def test_favor_rsids_endpoint():
    """Test FAVOR API with correct rsID endpoint - handle list response"""
    
    print("=" * 60)
    print("Testing FAVOR API - /v1/rsids/ endpoint")
    print("=" * 60)
    
    rsids = ["rs429358", "rs7412", "rs3865444"]
    
    for rsid in rsids:
        print(f"\n{'=' * 60}")
        print(f"Testing: {rsid}")
        print(f"{'=' * 60}")
        
        url = f"https://api.genohub.org/v1/rsids/{rsid}"
        
        try:
            response = requests.get(url, timeout=10)
            print(f"URL: {url}")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response is a list
                if isinstance(data, list):
                    print(f"\n✅ SUCCESS! Got {len(data)} variant(s)")
                    
                    # Process each variant in the list
                    for i, variant in enumerate(data):
                        print(f"\n--- Variant {i+1}/{len(data)} ---")
                        print(f"Variant VCF: {variant.get('variant_vcf', 'N/A')}")
                        print(f"rsID: {variant.get('rsid', 'N/A')}")
                        print(f"Chromosome: {variant.get('chromosome', 'N/A')}")
                        print(f"Position: {variant.get('position', 'N/A')}")
                        print(f"Ref > Alt: {variant.get('reference', 'N/A')} > {variant.get('alternative', 'N/A')}")
                        print(f"Gene: {variant.get('genecode_comprehensive_info', 'N/A')}")
                        print(f"Category: {variant.get('genecode_comprehensive_category', 'N/A')}")
                        print(f"Exonic Type: {variant.get('genecode_comprehensive_exonic_category', 'N/A')}")
                        print(f"BRAVO AF: {variant.get('bravo_af', 'N/A')}")
                        print(f"PolyPhen2 HDIV: {variant.get('polyphen2_hdiv_score', 'N/A')}")
                        print(f"SIFT Score: {variant.get('sift_score', 'N/A')}")
                        print(f"CADD PHRED: {variant.get('cadd_phred', 'N/A')}")
                    
                    # Show first variant's available fields
                    if len(data) > 0:
                        print(f"\nAvailable fields in response: {len(data[0])} total")
                        print(f"Sample keys: {list(data[0].keys())[:20]}")
                
                elif isinstance(data, dict):
                    print(f"\n✅ SUCCESS! Got single variant (dict)")
                    print(f"Data: {json.dumps(data, indent=2)[:500]}")
                else:
                    print(f"Unexpected response type: {type(data)}")
                
            elif response.status_code == 404:
                print(f"❌ Not found: rsID may not exist in database")
            else:
                print(f"❌ Failed: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_favor_rsids_endpoint()