import os
import shutil
from dotenv import load_dotenv

# Setup
if os.path.exists(".env"):
    shutil.copy(".env", ".env.bak")

with open(".env", "w") as f:
    f.write("OLLAMA_MODEL=test-model-from-env\n")

try:
    # Explicitly load in the test script to be sure
    load_dotenv(override=True)
    print(f"ENV MODEL: {os.getenv('OLLAMA_MODEL')}")
    
    from src.ai import OllamaAIService
    service = OllamaAIService()
    print(f"Detected Model: {service.model}")
    if service.model == "test-model-from-env":
        print("Verification Task 1 SUCCESS")
    else:
        print("Verification Task 1 FAILED")
finally:
    # Cleanup
    os.remove(".env")
    if os.path.exists(".env.bak"):
        shutil.move(".env.bak", ".env")
