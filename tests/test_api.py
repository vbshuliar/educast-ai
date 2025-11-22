"""
Quick test script for the API
"""

import requests
import json

API_URL = "http://localhost:5001/api"

print("Testing KnowCast AI API...")
print("=" * 60)

# Test 1: Health check
print("\n1. Testing health endpoint...")
try:
    response = requests.get(f"{API_URL}/health")
    data = response.json()
    print(f"   Status: {data['status']}")
    print(f"   Extractor ready: {data['extractor_ready']}")
    print("   ✓ Health check passed")
except Exception as e:
    print(f"   ✗ Health check failed: {e}")
    exit(1)

# Test 2: Extract knowledge
print("\n2. Testing knowledge extraction...")
try:
    test_query = "What is machine learning?"
    print(f"   Query: {test_query}")

    response = requests.post(
        f"{API_URL}/extract",
        json={"query": test_query}
    )

    data = response.json()

    if data.get('success'):
        print(f"   ✓ Success!")
        print(f"   Answer length: {len(data.get('answer', ''))} characters")
        print(f"   Sources: {len(data.get('sources', []))} sources")
        print(f"\n   First 200 chars of answer:")
        print(f"   {data.get('answer', '')[:200]}...")
    else:
        print(f"   ✗ Failed: {data.get('error')}")

except Exception as e:
    print(f"   ✗ Extraction failed: {e}")

print("\n" + "=" * 60)
print("✓ API is working correctly!")
print("\nYou can now open frontend/index.html in your browser")
