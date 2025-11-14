import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api_client import GeneticDataAPIClient
import json

def test_final_client():
    """Test the final API client"""
    
    client = GeneticDataAPIClient()
    
    print("=" * 60)
    print("Testing Final Genetic Data API Client")
    print("=" * 60)
    
    variants = ["rs429358", "rs7412"]
    
    for rsid in variants:
        print(f"\n{'=' * 60}")
        print(f"Querying: {rsid}")
        print(f"{'=' * 60}")
        
        data = client.get_combined_data(rsid)
        
        if data['success']:
            print(f"\n✅ Successfully retrieved data")
            
            # FAVOR data
            if data['favor']:
                fv = data['favor']
                print(f"\n🧬 FAVOR Data:")
                print(f"  VCF: {fv['variant_vcf']}")
                print(f"  Gene: {fv['gene']}")
                print(f"  Category: {fv['category']}")
                print(f"  Exonic Type: {fv['exonic_category']}")
                print(f"  BRAVO AF: {fv['bravo_af']}")
                print(f"  PolyPhen2 HDIV: {fv['polyphen2_hdiv_score']}")
                print(f"  CADD PHRED: {fv['cadd_phred']}")
            
            # MyVariant data
            if data['myvariant']:
                mv = data['myvariant']
                print(f"\n📊 MyVariant.info Data:")
                print(f"  Gene: {mv['gene']}")
                print(f"  Consequence: {mv['consequence']}")
                print(f"  Clinical Sig: {mv['clinical_significance']}")
                if mv['diseases']:
                    print(f"  Diseases: {', '.join(mv['diseases'])}")
        else:
            print(f"\n❌ Failed to retrieve data")

if __name__ == "__main__":
    test_final_client()
