"""
Simple test script to verify all imports work correctly
"""

print("Testing imports...")
print("-" * 60)

try:
    import os
    print("✓ os")
except ImportError as e:
    print(f"✗ os: {e}")

try:
    import sys
    print("✓ sys")
except ImportError as e:
    print(f"✗ sys: {e}")

try:
    import json
    print("✓ json")
except ImportError as e:
    print(f"✗ json: {e}")

try:
    from typing import Dict, List, Optional
    print("✓ typing")
except ImportError as e:
    print(f"✗ typing: {e}")

try:
    from dotenv import load_dotenv
    print("✓ python-dotenv")
except ImportError as e:
    print(f"✗ python-dotenv: {e}")
    print("   Install with: pip3 install python-dotenv")

try:
    from valyu import Valyu
    print("✓ valyu SDK")
    print(f"   Valyu class: {Valyu}")
except ImportError as e:
    print(f"✗ valyu SDK: {e}")
    print("   Install with: pip3 install valyu")

print("-" * 60)
print("\n✅ All imports successful!")
print("\nYou can now use knowledge_extraction.py")
print("Just make sure to set your VALYU_API_KEY in .env file")
