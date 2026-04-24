import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock

# Add src to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from src.models import NewsDTO
from src.core.i18n import get_text
from src.ai.ollama_service import OllamaAIService

async def test_full_localized_prompts():
    print("Testing Full Localized AI Prompts...")
    
    # Test Vietnamese Summarizer Prompt
    vi_prompt = get_text("prompt_summarizer", "vi", content="Bản tin Python")
    print(f"\n[VI Prompt Preview]:\n{vi_prompt}")
    assert "Nhiệm vụ: Tóm tắt" in vi_prompt
    assert "KHÔNG thêm phân tích" in vi_prompt
    
    # Test English Summarizer Prompt
    en_prompt = get_text("prompt_summarizer", "en", content="Python News")
    print(f"\n[EN Prompt Preview]:\n{en_prompt}")
    assert "Task: Summarize" in en_prompt
    assert "Constraint: Do NOT" in en_prompt
    
    print("\n✓ Full localized AI prompts test passed!")

async def main():
    await test_full_localized_prompts()

if __name__ == "__main__":
    asyncio.run(main())
