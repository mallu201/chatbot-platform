import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
print(f"Looking for .env at: {env_path}")
print(f".env exists: {env_path.exists()}")

if env_path.exists():
    print(f"\n.env file content:")
    content = env_path.read_text()
    print(content)
    print(f"\n---")

load_dotenv(dotenv_path=env_path)

api_key = os.getenv("OPENAI_API_KEY")
print(f"\nAPI Key found: {bool(api_key)}")
if api_key:
    print(f"Key starts with: {api_key[:20]}...")
    print(f"Key length: {len(api_key)}")
else:
    print("ERROR: API key not found!")
    print("\nMake sure .env file has:")
    print("OPENAI_API_KEY=sk-proj-...")
