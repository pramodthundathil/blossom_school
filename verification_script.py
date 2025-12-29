import requests
import json

url = "http://127.0.0.1:8000/admissions/create/"
headers = {"X-Requested-With": "XMLHttpRequest"}
data = {}  # Empty data to trigger validation errors

try:
    response = requests.post(url, headers=headers, data=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    
    if response.status_code == 400:
        try:
            json_response = response.json()
            print("JSON Response received successfully.")
            print(f"Success: {json_response.get('success')}")
            print(f"Errors present: {'errors' in json_response}")
            if 'errors' in json_response:
                print(f"Error keys: {list(json_response['errors'].keys())}")
        except json.JSONDecodeError:
            print("Failed to decode JSON response.")
            print(response.text[:200])
    else:
        print(f"Unexpected status code: {response.status_code}")

except Exception as e:
    print(f"Request failed: {e}")
