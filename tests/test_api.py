import requests
import base64
import json
import sys
import os

# Switch between local and production
BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
# For production: set env var API_BASE_URL=https://intelligent-call-centre.onrender.com

def test_api(audio_file_path: str, language: str = "Tamil"):
    if not os.path.exists(audio_file_path):
        print(f"File not found: {audio_file_path}")
        return
        
    # Read and encode
    with open(audio_file_path, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode('utf-8')
        
    url = f"{BASE_URL}/api/call-analytics"
    headers = {
        "x-api-key": "sk_track3_987654321",
        "Content-Type": "application/json"
    }
    payload = {
        "language": language,
        "audioFormat": "mp3", # Or detect from extension
        "audioBase64": encoded_string
    }
    
    print(f"Sending POST request to {url}...")
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        print("Success! Response:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_api.py <path_to_audio_file> [language]")
    else:
        lang = sys.argv[2] if len(sys.argv) > 2 else "Tamil"
        test_api(sys.argv[1], lang)
