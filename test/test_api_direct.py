import requests

def test_favor_direct():
    """Direct test without importing api_client"""
    
    rsid = "rs429358"
    url = f"https://api.genohub.org/v1/rsids/{rsid}"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                variant = data[0]
                print(f"\nGene: {variant.get('genecode_comprehensive_info')}")
                print(f"Category: {variant.get('genecode_comprehensive_category')}")
                print(f"BRAVO AF: {variant.get('bravo_af')}")
                print(f"\n✅ API works!")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_favor_direct()
