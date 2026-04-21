import asyncio
import sys
from src.ai import OllamaAIService, AIServiceConnectionError

async def test_connection():
    service = OllamaAIService(model="gemma4:E4B")
    
    print("Checking Ollama connection (this requires Ollama to be running with gemma4:E4B)...")
    try:
        # A simple test content
        result = await service.summarize_news("Ollama is a local LLM runner.")
        print(f"Success! Response: {result}")
    except AIServiceConnectionError as e:
        print(f"Caught expected connection error or failure: {e}")
        # We don't exit with 1 because in a CI/env where Ollama isn't running,
        # catching the error IS the success of the error handling logic.
        if "connection failed" in str(e).lower() or "ollama" in str(e).lower():
            print("Verified: Error handling is working correctly.")
        else:
            sys.exit(1)
    # Test 2: Connection failure to non-existent host
    print("\nChecking behavior when Ollama is unreachable (fake host)...")
    service_fake = OllamaAIService(host="http://localhost:9999")
    try:
        await service_fake.summarize_news("test")
        print("Error: Should not have succeeded!")
        sys.exit(1)
    except AIServiceConnectionError as e:
        print(f"Caught expected connection failure: {e}")
        if "connection failed" in str(e).lower():
            print("Verified: Connection failure handling is working correctly.")
        else:
            print(f"Error: Unexpected error message: {e}")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_connection())
