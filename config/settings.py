"""
Configuration settings for the Llama 4 text extraction project.
This module loads settings from environment variables and provides
them to the rest of the application.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# The .env file should be in the project root
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'

if env_path.exists():
    load_dotenv(env_path)
    print(f"Loaded environment variables from: {env_path}")
else:
    print(f"Warning: No .env file found at {env_path}")
    print("Please create one using .env.example as a template")

# Project paths - using Path objects for cross-platform compatibility
PROJECT_ROOT = project_root
INPUT_DIR = PROJECT_ROOT / "data" / "input"
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
LOG_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
for directory in [INPUT_DIR, OUTPUT_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Google Cloud settings
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT')
LOCATION = os.getenv('GCP_LOCATION', 'us-central1')
CREDENTIALS_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# Validate critical settings
if not PROJECT_ID:
    print("Warning: GOOGLE_CLOUD_PROJECT not set in environment")
if not CREDENTIALS_PATH:
    print("Warning: GOOGLE_APPLICATION_CREDENTIALS not set in environment")
elif not Path(CREDENTIALS_PATH).exists():
    print(f"Warning: Credentials file not found at {CREDENTIALS_PATH}")

# Model settings for Llama 4
MODEL_ID = "llama-4-maverick-17b-128e-instruct-maas"
MAX_OUTPUT_TOKENS = 4096
TEMPERATURE = 0.1  # Low temperature for accurate text extraction
TOP_P = 0.95
TOP_K = 40

# Image processing settings
MAX_IMAGE_SIZE = (1024, 1024)  # Maximum dimensions for API
IMAGE_QUALITY = 85  # JPEG quality when resizing

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
