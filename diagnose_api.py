"""
Diagnostic script to test different Llama 4 endpoint formats
This will help us figure out the correct endpoint URL
"""

import os
import requests
from google.oauth2 import service_account
import google.auth.transport.requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Configuration
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', 'alphamudramonitoringconsoleapp')
LOCATION = os.getenv('GCP_LOCATION', 'us-central1')
CREDENTIALS_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

print("Configuration:")
print(f"Project ID: {PROJECT_ID}")
print(f"Location: {LOCATION}")
print(f"Credentials: {CREDENTIALS_PATH}")
print("=" * 60)

# Set up authentication
try:
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH,
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )
    credentials.refresh(google.auth.transport.requests.Request())
    print("✓ Authentication successful")
except Exception as e:
    print(f"✗ Authentication failed: {e}")
    exit(1)

headers = {
    "Authorization": f"Bearer {credentials.token}",
    "Content-Type": "application/json"
}

# Test payload (simple text, no image)
test_payload = {
    "parameters": {
        "max_output_tokens": 100,
        "temperature": 0.1
    },
    "messages": [
        {
            "role": "user",
            "content": "Hello, please respond with 'API is working' if you can see this message."
        }
    ]
}

# Different endpoint formats to try
endpoint_formats = [
    # Format 1: Standard MaaS endpoint
    f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/meta/models/llama-4-maverick-17b-128e-instruct-maas:streamChat",
    
    # Format 2: Without -maas suffix
    f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/meta/models/llama-4-maverick-17b-128e-instruct:streamChat",
    
    # Format 3: Alternative chat endpoint
    f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/meta/models/llama-4-maverick-17b-128e-instruct-maas:chat",
    
    # Format 4: Predict endpoint
    f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/meta/models/llama-4-maverick-17b-128e-instruct-maas:predict",
    
    # Format 5: generateContent endpoint (Gemini-style)
    f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/meta/models/llama-4-maverick-17b-128e-instruct-maas:generateContent",
]

print("\nTesting different endpoint formats...")
print("=" * 60)

working_endpoint = None

for i, endpoint in enumerate(endpoint_formats, 1):
    print(f"\nTest {i}: {endpoint.split('/models/')[1]}")
    
    try:
        response = requests.post(
            endpoint, 
            headers=headers, 
            json=test_payload,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ SUCCESS! This endpoint works!")
            working_endpoint = endpoint
            # Try to get a sample response
            try:
                for line in response.iter_lines():
                    if line:
                        print(f"Response preview: {line.decode('utf-8')[:100]}...")
                        break
            except:
                pass
            break
        elif response.status_code == 404:
            print("✗ Not Found - endpoint doesn't exist")
        elif response.status_code == 403:
            print("✗ Forbidden - check permissions or license agreement")
        elif response.status_code == 400:
            print("⚠ Bad Request - endpoint exists but request format may be wrong")
        else:
            print(f"✗ Error: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("✗ Timeout - endpoint might be valid but slow")
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
if working_endpoint:
    print(f"✓ Found working endpoint!")
    print(f"Use this endpoint: {working_endpoint}")
    
    # Update the code suggestion
    model_id = working_endpoint.split('/models/')[1].split(':')[0]
    print(f"\nUpdate your settings.py with:")
    print(f'MODEL_ID = "{model_id}"')
else:
    print("✗ No working endpoint found.")
    print("\nPossible issues:")
    print("1. Llama 4 license not accepted in Model Garden")
    print("2. Vertex AI API not enabled")
    print("3. Model not available in your region")
    print("4. Billing not enabled on your project")
    
    print("\nNext steps:")
    print("1. Go to https://console.cloud.google.com/vertex-ai/model-garden")
    print("2. Search for 'Llama 4 Maverick'")
    print("3. Click on the model and accept the license")
    print("4. Make sure Vertex AI API is enabled")

# Additional diagnostics
print("\n" + "=" * 60)
print("Additional Diagnostics:")

# Test basic Vertex AI access
basic_endpoint = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}"
try:
    response = requests.get(basic_endpoint, headers={"Authorization": f"Bearer {credentials.token}"})
    if response.status_code == 200:
        print("✓ Vertex AI API is accessible")
    else:
        print(f"✗ Vertex AI API access issue: {response.status_code}")
except Exception as e:
    print(f"✗ Cannot access Vertex AI API: {e}")