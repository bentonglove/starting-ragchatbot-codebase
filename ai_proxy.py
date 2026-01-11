# 測試Antropic 節點
import os

import anthropic
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(override=True)
base_url = os.getenv("ANTHROPIC_BASE_URL", "")
model = os.getenv("ANTHROPIC_MODEL", "").strip('"')
api_key = os.getenv("ANTHROPIC_API_KEY", "")

print(f"MODEL: {model}")
print(f"BASE_URL: {base_url}")
print(f"API_KEY set: {bool(api_key)}")
print()

client = (
    anthropic.Anthropic(api_key=api_key, base_url=base_url)
    if base_url
    else anthropic.Anthropic(api_key=api_key)
)

try:
    response = client.messages.create(
        model=model,
        max_tokens=200,
        messages=[
            {"role": "user", "content": "你是哪個 LLM 身分啊？ 你的知識點在哪個日期？"}
        ],
    )
    print("Success!")
    print(f"Response: {response.content[0].text}")
except anthropic.APIStatusError as e:
    print(f"Status: {e.status_code}")
    print(f"Response: {e.response.text}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
