"""
Simple test script to verify the setup and test single image extraction with token counting.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.llama4_extractor import LocalLlama4Extractor
from config.settings import INPUT_DIR, OUTPUT_DIR


def test_single_image():
    """Test extraction on a single image with token usage display."""
    
    print("Simple Text Extraction Test with Token Counting")
    print("=" * 60)
    
    # Look for a test image
    test_images = list(INPUT_DIR.glob("*.jpg")) + list(INPUT_DIR.glob("*.png"))
    
    if not test_images:
        print(f"\nNo test images found in {INPUT_DIR}")
        print("Please add a scanned textbook page to test.")
        return
    
    # Use the first image found
    test_image = test_images[0]
    print(f"\nUsing test image: {test_image.name}")
    
    try:
        # Create extractor
        print("\nInitializing extractor...")
        extractor = LocalLlama4Extractor()
        
        # Extract text
        print(f"\nExtracting text from {test_image.name}...")
        text, token_usage = extractor.extract_text_from_image(test_image)
        
        # Display token usage
        print("\n" + "="*50)
        print("TOKEN USAGE:")
        print("="*50)
        print(f"Input tokens: {token_usage['input_tokens']}")
        print(f"Output tokens: {token_usage['output_tokens']}")
        print(f"Total tokens: {token_usage['total_tokens']}")
        
        # Estimate cost (approximate)
        estimated_cost = token_usage['total_tokens'] / 1_000_000 * 0.075
        print(f"Estimated cost for this image: ${estimated_cost:.6f}")
        
        # Display results
        print("\n" + "="*50)
        print("EXTRACTED TEXT:")
        print("="*50)
        print(text[:500] + "..." if len(text) > 500 else text)
        print("="*50)
        
        # Save to file
        output_file = OUTPUT_DIR / f"{test_image.stem}_test.txt"
        output_file.write_text(text, encoding='utf-8')
        print(f"\nFull text saved to: {output_file}")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_single_image()