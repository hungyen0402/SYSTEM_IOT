import requests
import json

try:
    print("Testing chart-data API...")
    response = requests.get('http://localhost:5000/api/chart-data', timeout=5)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("API Response structure:")
        print(f"- Labels count: {len(data.get('labels', []))}")
        print(f"- Datasets count: {len(data.get('datasets', []))}")
        
        if data.get('labels'):
            print(f"- Sample labels: {data['labels'][:5]}...")
            
        if data.get('datasets'):
            for i, dataset in enumerate(data['datasets']):
                print(f"- Dataset {i+1}: {dataset.get('label', 'Unknown')} - {len(dataset.get('data', []))} data points")
                if dataset.get('data'):
                    print(f"  Sample data: {dataset['data'][:5]}...")
        
        print("\nAPI working correctly!")
    else:
        print(f"Error: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("Error: Cannot connect to server. Is the app running?")
except Exception as e:
    print(f"Error: {e}")