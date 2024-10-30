# test_api.py
import requests
import json
from datetime import datetime

def test_endpoints():
    BASE_URL = "http://localhost:5002"
    
    def print_response(name, response):
        print(f"\n=== {name} Test at {datetime.now()} ===")
        print(f"Status Code: {response.status_code}")
        try:
            data = response.json()
            # Print metrics nicely formatted
            if 'metrics' in data:
                print("\nMetrics:")
                for key, value in data['metrics'].items():
                    print(f"{key}: {value}")
        except Exception as e:
            print(f"Error parsing response: {e}")
            print("Raw response:", response.text)

    # Test pretest endpoint
    print("\nTesting /api/pretest endpoint...")
    pretest_response = requests.post(
        f"{BASE_URL}/api/pretest",
        json={
            "system_prompt": "Sort these words alphabetically",
            "show_details": True
        }
    )
    print_response("Pretest", pretest_response)

    # Test test_prompt endpoint
    print("\nTesting /api/test_prompt endpoint...")
    test_response = requests.post(
        f"{BASE_URL}/api/test_prompt",
        json={
            "system_prompt": "Sort these words alphabetically",
            "num_examples": 5
        }
    )
    print_response("Full Test", test_response)

if __name__ == "__main__":
    test_endpoints()