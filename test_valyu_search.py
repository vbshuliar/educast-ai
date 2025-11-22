"""
Test Valyu.ai search() method to debug API key issues
"""

import os
from dotenv import load_dotenv
from valyu import Valyu

load_dotenv()

print("Testing Valyu.ai API Key...")
print("=" * 60)

api_key = os.getenv('VALYU_API_KEY')
print(f"API Key found: {api_key[:10]}... (first 10 chars)")
print()

# Initialize Valyu
valyu = Valyu(api_key=api_key)
print("✓ Valyu SDK initialized")
print()

# Test 1: Try search() method
print("Test 1: search() method")
print("-" * 60)
try:
    response = valyu.search(
        "quantum computing",
        max_num_results=5
    )
    print(f"Response type: {type(response)}")
    print(f"Response: {response}")
    if hasattr(response, '__dict__'):
        print(f"Attributes: {response.__dict__}")
except Exception as e:
    print(f"Error: {e}")

print()

# Test 2: Try answer() method
print("Test 2: answer() method")
print("-" * 60)
try:
    response = valyu.answer(query="What is quantum computing?")
    print(f"Response type: {type(response)}")
    print(f"Response: {response}")
    if hasattr(response, '__dict__'):
        print(f"Attributes: {response.__dict__}")
except Exception as e:
    print(f"Error: {e}")
