from apps.api.config import settings
import os

print(f"Working Directory: {os.getcwd()}")
print(f"MISTRAL_API_KEY from settings: {'[SET]' if settings.MISTRAL_API_KEY else '[NOT SET]'}")
if settings.MISTRAL_API_KEY:
    # Just show first 4 characters for verification without leaking
    print(f"Key starts with: {settings.MISTRAL_API_KEY[:4]}...")
else:
    print("MISTRAL_API_KEY is empty in settings.")

# Check if .env exists
if os.path.exists(".env"):
    print(".env file found in root.")
else:
    print(".env file NOT found in root.")
