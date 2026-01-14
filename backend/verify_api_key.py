"""Quick script to verify OpenAI API key is loaded correctly"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# Get API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key and env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and line.startswith("OPENAI_API_KEY="):
                api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                break

if not api_key:
    print("❌ ERROR: OPENAI_API_KEY not found!")
    print(f"   Check if {env_path} exists and contains: OPENAI_API_KEY=sk-proj-...")
    exit(1)

api_key = api_key.strip()

if not api_key.startswith("sk-"):
    print(f"❌ ERROR: Invalid API key format! Should start with 'sk-'")
    print(f"   Got: {api_key[:20]}...")
    exit(1)

print(f"✅ API Key found!")
print(f"   Length: {len(api_key)} characters")
print(f"   Starts with: {api_key[:10]}...")
print(f"   Format: Valid")

# Test with OpenAI client
try:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    
    # Simple test call
    print("\n🔄 Testing API key with OpenAI...")
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[{"role": "user", "content": "Say 'Hello'"}],
        temperature=0.7,
        max_output_tokens=10
    )
    
    if response and hasattr(response, 'output_text'):
        print(f"✅ API Key is VALID and working!")
        print(f"   Test response: {response.output_text[:50]}...")
    else:
        print("⚠️  API call succeeded but response format unexpected")
        
except Exception as e:
    error_msg = str(e)
    if "401" in error_msg or "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
        print(f"❌ API Key is INVALID or expired!")
        print(f"   Error: {error_msg[:100]}")
        print(f"   Please check your API key in {env_path}")
    elif "429" in error_msg:
        print(f"⚠️  Rate limit exceeded (key is valid but quota exceeded)")
    else:
        print(f"⚠️  Error testing API: {error_msg[:100]}")

print("\n✅ Verification complete!")
