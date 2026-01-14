import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("OPENAI_API_KEY")
print(f"Using API key: {api_key[:20]}...{api_key[-10:] if api_key else 'None'}")

if not api_key:
    print("ERROR: No API key found!")
    exit(1)

client = OpenAI(api_key=api_key)

try:
    print("\nTesting OpenAI API call...")
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "user",
                "content": "Say hello"
            }
        ]
    )
    print("SUCCESS!")
    print(f"Response: {response.output_text}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}")
    print(f"Message: {str(e)}")
    if "401" in str(e) or "api_key" in str(e).lower():
        print("\nThis means your API key is INVALID or EXPIRED.")
        print("Go to https://platform.openai.com/api-keys and create a NEW key.")
