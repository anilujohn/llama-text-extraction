"""
Batch processing script for handling multiple textbook chapters.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.llama4_extractor import LocalLlama4Extractor
from config.settings import INPUT_DIR, OUTPUT_DIR
import time


def batch_process_with_delay():
    """Process images with a delay to respect API rate limits."""
    
    print("Batch Processing Script")
    print("=" * 50)
    
    # Initialize extractor
    extractor = LocalLlama4Extractor()
    
    # Get all images
    images = list(INPUT_DIR.glob("*.jpg")) + list(INPUT_DIR.glob("*.png"))
    
    print(f"Found {len(images)} images to process")
    print("Processing with 5-second delay between images...")
    
    for i, image in enumerate(images, 1):
        print(f"\n[{i}/{len(images)}] Processing {image.name}...")
        
        try:
            text = extractor.extract_text_from_image(image)
            output_file = OUTPUT_DIR / f"{image.stem}_extracted.txt"
            output_file.write_text(text, encoding='utf-8')
            print(f"✓ Saved to {output_file.name}")
            
            # Delay between requests (except for last image)
            if i < len(images):
                print("Waiting 5 seconds before next image...")
                time.sleep(5)
                
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print("\nBatch processing complete!")


if __name__ == "__main__":
    batch_process_with_delay()
