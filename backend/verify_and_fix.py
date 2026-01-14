import os
import sys
from pathlib import Path
from dotenv import load_dotenv

print("=" * 60)
print("VERIFYING API KEY SETUP")
print("=" * 60)

# Try multiple paths
paths_to_try = [
    Path(__file__).parent / ".env",
    Path(__file__).parent.parent / "backend" / ".env",
    Path(".env"),
]

env_path = None
for path in paths_to_try:
    if path.exists():
        env_path = path
        print(f"Found .env at: {path}")
        break

if not env_path:
    print("ERROR: .env file not found!")
    print("Looking in:")
    for p in paths_to_try:
        print(f"  - {p} (exists: {p.exists()})")
    sys.exit(1)

# Read and display .env content
print(f"\n.env file content:")
with open(env_path, 'r') as f:
    content = f.read().strip()
    print(f"  Length: {len(content)} characters")
    print(f"  First 50 chars: {content[:50]}...")
    print(f"  Last 20 chars: ...{content[-20:]}")
    
    # Check format
    if not content.startswith("OPENAI_API_KEY="):
        print("\nERROR: .env file doesn't start with 'OPENAI_API_KEY='")
        print("Fix: Add 'OPENAI_API_KEY=' at the beginning")
        sys.exit(1)
    
    if " " in content.split("=")[0]:
        print("\nERROR: Spaces found around '='")
        print("Fix: Remove spaces, use: OPENAI_API_KEY=...")
        sys.exit(1)

# Load environment
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("\nERROR: API key not loaded!")
    print("Check .env file format")
    sys.exit(1)

print(f"\nAPI Key loaded successfully!")
print(f"  Key starts with: {api_key[:20]}...")
print(f"  Key length: {len(api_key)}")

# Test OpenAI API
print("\n" + "=" * 60)
print("TESTING OPENAI API")
print("=" * 60)

try:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    
    print("Making test API call...")
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "user", "content": "Say hello"}
        ]
    )
    
    print("SUCCESS! API key works!")
    print(f"Response: {response.output_text}")
    
except Exception as e:
    print(f"API CALL FAILED!")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    
    if "401" in str(e) or "api_key" in str(e).lower():
        print("\nThis means your API key is INVALID or EXPIRED")
        print("Solution: Create a NEW key from https://platform.openai.com/api-keys")
    elif "429" in str(e):
        print("\nRate limit exceeded - wait a moment and try again")
    else:
        print("\nUnknown error - check your OpenAI account status")

print("\n" + "=" * 60)
