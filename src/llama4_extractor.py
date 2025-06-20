"""
Llama 4 Text Extractor - Updated with correct endpoint and token counting
This module extracts text from scanned textbook pages using Vertex AI's Llama 4.
"""

import os
import sys
import json
import base64
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from PIL import Image
import io

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import our configuration
from config.settings import *

# Import Google Cloud libraries
try:
    from google.cloud import aiplatform
    from google.oauth2 import service_account
    import google.auth
    import requests
except ImportError as e:
    print(f"Error importing required libraries: {e}")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)

# Set up logging
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_DIR / 'extraction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LocalLlama4Extractor:
    """
    A simplified text extractor that reads images from local folders.
    This version is designed for ease of use and testing.
    """
    
    def __init__(self):
        """Initialize the extractor with Google Cloud credentials."""
        
        logger.info("Initializing Llama 4 Text Extractor...")
        
        # Check for required configuration
        if not PROJECT_ID:
            raise ValueError("GOOGLE_CLOUD_PROJECT not set. Please update your .env file.")
        
        if not CREDENTIALS_PATH or not Path(CREDENTIALS_PATH).exists():
            raise ValueError(f"Credentials file not found at {CREDENTIALS_PATH}")
        
        # Initialize Vertex AI
        logger.info(f"Using project: {PROJECT_ID}")
        logger.info(f"Using location: {LOCATION}")
        
        aiplatform.init(
            project=PROJECT_ID,
            location=LOCATION,
            credentials=service_account.Credentials.from_service_account_file(
                CREDENTIALS_PATH
            )
        )
        
        # Set up authentication for direct API calls
        self.credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_PATH,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        
        # Use the generateContent endpoint which exists (based on diagnostic results)
        self.endpoint = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/meta/models/{MODEL_ID}:generateContent"
        
        # Initialize token tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_api_calls = 0
        
        logger.info("Initialization complete!")
    
    def prepare_image(self, image_path: Path) -> str:
        """
        Prepare an image for the API by resizing and encoding it.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded string of the image
        """
        logger.info(f"Preparing image: {image_path}")
        
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                    logger.debug("Converted image to RGB")
                
                # Resize if too large
                if img.size[0] > MAX_IMAGE_SIZE[0] or img.size[1] > MAX_IMAGE_SIZE[1]:
                    img.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
                    logger.debug(f"Resized image to: {img.size}")
                
                # Save to bytes
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=IMAGE_QUALITY)
                buffer.seek(0)
                
                # Encode to base64
                encoded = base64.b64encode(buffer.read()).decode('utf-8')
                logger.info(f"Image prepared successfully. Size: {len(encoded)} bytes")
                
                return encoded
                
        except Exception as e:
            logger.error(f"Error preparing image: {e}")
            raise
    
    def extract_text_from_image(self, image_path: Path) -> Tuple[str, Dict[str, int]]:
        """
        Extract text from a single image file with token counting.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (extracted text, token usage dict)
        """
        
        logger.info(f"Starting text extraction for: {image_path.name}")
        
        # Prepare the image
        encoded_image = self.prepare_image(image_path)
        
        # Create the prompt for text extraction
        extraction_prompt = """Extract ALL text from this scanned textbook page.

IMPORTANT INSTRUCTIONS:
1. Extract the text EXACTLY as it appears on the page
2. Maintain all original formatting including:
   - Paragraph breaks
   - Section headings
   - Bullet points or numbered lists
   - Indentation
3. Do NOT add any commentary or explanations
4. Do NOT describe images or diagrams
5. ONLY output the actual text content from the page

Begin extraction now:"""
        
        # Prepare the API request for generateContent endpoint
        request_body = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": extraction_prompt
                        },
                        {
                            "inlineData": {
                                "mimeType": "image/jpeg",
                                "data": encoded_image
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": MAX_OUTPUT_TOKENS,
                "temperature": TEMPERATURE,
                "topP": TOP_P,
                "topK": TOP_K
            }
        }
        
        # Get authentication token
        self.credentials.refresh(google.auth.transport.requests.Request())
        
        # Make the API request
        headers = {
            "Authorization": f"Bearer {self.credentials.token}",
            "Content-Type": "application/json"
        }
        
        logger.info("Sending request to Llama 4 API...")
        
        try:
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=request_body
            )
            
            if response.status_code != 200:
                logger.error(f"API error: {response.status_code} - {response.text}")
                raise Exception(f"API request failed: {response.status_code}")
            
            # Parse response
            response_data = response.json()
            
            # Extract text from response
            extracted_text = ""
            if "candidates" in response_data:
                for candidate in response_data["candidates"]:
                    if "content" in candidate and "parts" in candidate["content"]:
                        for part in candidate["content"]["parts"]:
                            if "text" in part:
                                extracted_text += part["text"]
            
            # Extract token usage information
            token_usage = {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0
            }
            
            if "usageMetadata" in response_data:
                usage = response_data["usageMetadata"]
                token_usage["input_tokens"] = usage.get("promptTokenCount", 0)
                token_usage["output_tokens"] = usage.get("candidatesTokenCount", 0)
                token_usage["total_tokens"] = usage.get("totalTokenCount", 0)
                
                # Log token usage for this API call
                logger.info(f"Token Usage for {image_path.name}:")
                logger.info(f"  - Input tokens: {token_usage['input_tokens']}")
                logger.info(f"  - Output tokens: {token_usage['output_tokens']}")
                logger.info(f"  - Total tokens: {token_usage['total_tokens']}")
                
                # Update cumulative totals
                self.total_input_tokens += token_usage["input_tokens"]
                self.total_output_tokens += token_usage["output_tokens"]
                self.total_api_calls += 1
            else:
                logger.warning("No token usage metadata found in API response")
            
            logger.info(f"Successfully extracted {len(extracted_text)} characters")
            return extracted_text.strip(), token_usage
            
        except Exception as e:
            logger.error(f"Error during text extraction: {e}")
            raise
    
    def process_folder(self, input_folder: Optional[Path] = None, 
                      output_folder: Optional[Path] = None) -> Dict[str, str]:
        """
        Process all images in a folder and save extracted text.
        
        Args:
            input_folder: Folder containing images (defaults to INPUT_DIR)
            output_folder: Folder to save text files (defaults to OUTPUT_DIR)
            
        Returns:
            Dictionary mapping image filenames to extracted text
        """
        
        # Use default folders if not specified
        input_folder = input_folder or INPUT_DIR
        output_folder = output_folder or OUTPUT_DIR
        
        # Get all image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}
        image_files = [f for f in input_folder.iterdir() 
                      if f.suffix.lower() in image_extensions]
        
        if not image_files:
            logger.warning(f"No image files found in {input_folder}")
            return {}
        
        logger.info(f"Found {len(image_files)} images to process")
        
        results = {}
        token_summary = []
        
        # Process each image
        for i, image_file in enumerate(image_files, 1):
            logger.info(f"\nProcessing image {i}/{len(image_files)}: {image_file.name}")
            
            try:
                # Extract text and get token usage
                extracted_text, token_usage = self.extract_text_from_image(image_file)
                
                # Save to file
                output_file = output_folder / f"{image_file.stem}_extracted.txt"
                output_file.write_text(extracted_text, encoding='utf-8')
                
                logger.info(f"Saved extracted text to: {output_file}")
                results[image_file.name] = extracted_text
                
                # Store token usage for summary
                token_summary.append({
                    "file": image_file.name,
                    "input_tokens": token_usage["input_tokens"],
                    "output_tokens": token_usage["output_tokens"],
                    "total_tokens": token_usage["total_tokens"]
                })
                
            except Exception as e:
                logger.error(f"Failed to process {image_file.name}: {e}")
                results[image_file.name] = f"ERROR: {str(e)}"
        
        # Log overall token usage summary
        logger.info("\n" + "="*60)
        logger.info("TOKEN USAGE SUMMARY:")
        logger.info("="*60)
        logger.info(f"Total API calls: {self.total_api_calls}")
        logger.info(f"Total input tokens: {self.total_input_tokens}")
        logger.info(f"Total output tokens: {self.total_output_tokens}")
        logger.info(f"Total tokens used: {self.total_input_tokens + self.total_output_tokens}")
        
        if self.total_api_calls > 0:
            logger.info(f"Average input tokens per call: {self.total_input_tokens / self.total_api_calls:.2f}")
            logger.info(f"Average output tokens per call: {self.total_output_tokens / self.total_api_calls:.2f}")
        
        # Estimate cost (approximate - adjust based on actual pricing)
        # Example pricing: $0.075 per 1M tokens
        estimated_cost = (self.total_input_tokens + self.total_output_tokens) / 1_000_000 * 0.075
        logger.info(f"Estimated cost: ${estimated_cost:.4f}")
        logger.info("="*60)
        
        # Create detailed summary file
        summary_file = output_folder / "extraction_summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("Text Extraction Summary\n")
            f.write("=" * 50 + "\n\n")
            
            # File processing results
            f.write("Processing Results:\n")
            f.write("-" * 30 + "\n")
            for filename, status in results.items():
                if status.startswith("ERROR"):
                    f.write(f"❌ {filename}: {status}\n")
                else:
                    f.write(f"✅ {filename}: Extracted {len(status)} characters\n")
            
            # Token usage details
            f.write("\n\nToken Usage Details:\n")
            f.write("-" * 30 + "\n")
            for item in token_summary:
                f.write(f"{item['file']}:\n")
                f.write(f"  Input tokens: {item['input_tokens']}\n")
                f.write(f"  Output tokens: {item['output_tokens']}\n")
                f.write(f"  Total: {item['total_tokens']}\n\n")
            
            # Overall summary
            f.write("\nOverall Token Usage:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total API calls: {self.total_api_calls}\n")
            f.write(f"Total input tokens: {self.total_input_tokens}\n")
            f.write(f"Total output tokens: {self.total_output_tokens}\n")
            f.write(f"Total tokens used: {self.total_input_tokens + self.total_output_tokens}\n")
            
            if self.total_api_calls > 0:
                f.write(f"Average input tokens per call: {self.total_input_tokens / self.total_api_calls:.2f}\n")
                f.write(f"Average output tokens per call: {self.total_output_tokens / self.total_api_calls:.2f}\n")
            
            f.write(f"\nEstimated cost: ${estimated_cost:.4f}\n")
        
        logger.info(f"\nProcessing complete! Summary saved to: {summary_file}")
        return results


def main():
    """Main function to demonstrate usage."""
    
    print("Llama 4 Text Extractor - Local Version with Token Counting")
    print("=" * 60)
    
    try:
        # Create extractor instance
        extractor = LocalLlama4Extractor()
        
        # Check for images in input folder
        image_files = list(INPUT_DIR.glob("*.jpg")) + list(INPUT_DIR.glob("*.png"))
        
        if not image_files:
            print(f"\nNo images found in {INPUT_DIR}")
            print("Please add some scanned textbook pages to the input folder.")
            return
        
        print(f"\nFound {len(image_files)} images in {INPUT_DIR}")
        
        # Process all images
        print("\nStarting text extraction...")
        results = extractor.process_folder()
        
        print("\nExtraction complete!")
        print(f"Check {OUTPUT_DIR} for extracted text files.")
        print(f"Check {LOG_DIR} for detailed token usage information.")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nPlease check:")
        print("1. Your .env file has correct values")
        print("2. Your Google Cloud credentials file exists")
        print("3. You have installed all required packages")


if __name__ == "__main__":
    main()