import asyncio
import sys
from pathlib import Path
from openai import AsyncOpenAI

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
from app.core.config import get_settings


async def test_keys():
    settings = get_settings()
    print("Testing OpenRouter API Key...")
    if settings.openrouter_api_key:
        client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            default_headers={"HTTP-Referer": "https://github.com/doc-intelligence", "X-Title": "Document Intelligence"},
        )
        # Test free models
        test_models = [
            "meta-llama/llama-3.3-70b-instruct",
            "meta-llama/llama-3.1-8b-instruct:free",
            "google/gemini-2.0-flash-exp:free",
            "google/gemini-2.0-flash-thinking-exp:free",
            "qwen/qwen-2.5-72b-instruct",
            "mistralai/mistral-7b-instruct",
            "openai/gpt-4o-mini",
        ]
        for m in test_models:
            try:
                res = await client.chat.completions.create(
                    model=m,
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=10,
                )
                print(f"  [OK] OpenRouter model '{m}' works! Response: {res.choices[0].message.content.strip()}")
                break
            except Exception as e:
                print(f"  [FAIL] OpenRouter model '{m}': {e}")

    print("\nTesting CodeCraft API Key...")
    if settings.codecraft_api_key:
        client = AsyncOpenAI(
            api_key=settings.codecraft_api_key,
            base_url=settings.codecraft_base_url,
        )
        try:
            models_res = await client.models.list()
            print(f"  [OK] CodeCraft models available: {[m.id for m in models_res.data]}")
        except Exception as e:
            print(f"  CodeCraft models.list failed ({e}), testing direct completion...")
            for m in ["gpt-3.5-turbo", "gpt-4", "claude-3-haiku", "llama-3"]:
                try:
                    res = await client.chat.completions.create(
                        model=m,
                        messages=[{"role": "user", "content": "Hi"}],
                        max_tokens=10,
                    )
                    print(f"  [OK] CodeCraft model '{m}' works!")
                    break
                except Exception as err:
                    print(f"  [FAIL] CodeCraft model '{m}': {err}")

    print("\nTesting UnoRouter API Key...")
    if settings.unorouter_api_key:
        client = AsyncOpenAI(
            api_key=settings.unorouter_api_key,
            base_url=settings.unorouter_base_url,
        )
        try:
            models_res = await client.models.list()
            print(f"  [OK] UnoRouter models available: {[m.id for m in models_res.data]}")
        except Exception as e:
            print(f"  UnoRouter test: {e}")


if __name__ == "__main__":
    asyncio.run(test_keys())
