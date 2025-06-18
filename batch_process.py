"""
Batch processing script for handling multiple textbook chapters with token tracking.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.llama4_extractor import LocalLlama4Extractor
from config.settings import INPUT_DIR, OUTPUT_DIR
import time
import logging

# Set up logging for batch processing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def batch_process_with_delay():
    """Process images with a delay to respect API rate limits and track tokens."""
    
    print("Batch Processing Script with Token Tracking")
    print("=" * 60)
    
    # Initialize extractor
    extractor = LocalLlama4Extractor()
    
    # Get all images
    images = list(INPUT_DIR.glob("*.jpg")) + list(INPUT_DIR.glob("*.png"))
    
    print(f"Found {len(images)} images to process")
    print("Processing with 5-second delay between images...")
    
    # Track token usage per file
    token_summary = []
    
    for i, image in enumerate(images, 1):
        print(f"\n[{i}/{len(images)}] Processing {image.name}...")
        
        try:
            text, token_usage = extractor.extract_text_from_image(image)
            output_file = OUTPUT_DIR / f"{image.stem}_extracted.txt"
            output_file.write_text(text, encoding='utf-8')
            
            print(f"✓ Saved to {output_file.name}")
            print(f"  Token usage - Input: {token_usage['input_tokens']}, Output: {token_usage['output_tokens']}, Total: {token_usage['total_tokens']}")
            
            # Store token info
            token_summary.append({
                "file": image.name,
                "input": token_usage['input_tokens'],
                "output": token_usage['output_tokens'],
                "total": token_usage['total_tokens']
            })
            
            # Delay between requests (except for last image)
            if i < len(images):
                print("Waiting 5 seconds before next image...")
                time.sleep(5)
                
        except Exception as e:
            print(f"✗ Error: {e}")
            logger.error(f"Failed to process {image.name}: {e}")
    
    # Display final summary
    print("\n" + "="*60)
    print("BATCH PROCESSING COMPLETE!")
    print("="*60)
    
    # Calculate totals
    total_input = sum(item['input'] for item in token_summary)
    total_output = sum(item['output'] for item in token_summary)
    total_tokens = sum(item['total'] for item in token_summary)
    
    print(f"\nToken Usage Summary:")
    print(f"- Total input tokens: {total_input:,}")
    print(f"- Total output tokens: {total_output:,}")
    print(f"- Total tokens used: {total_tokens:,}")
    
    if len(token_summary) > 0:
        print(f"\nAverages per image:")
        print(f"- Average input tokens: {total_input / len(token_summary):,.2f}")
        print(f"- Average output tokens: {total_output / len(token_summary):,.2f}")
        print(f"- Average total tokens: {total_tokens / len(token_summary):,.2f}")
    
    # Cost estimation
    estimated_cost = total_tokens / 1_000_000 * 0.075
    print(f"\nEstimated total cost: ${estimated_cost:.4f}")
    print(f"Average cost per page: ${estimated_cost / len(token_summary):.4f}" if len(token_summary) > 0 else "")
    
    # Save detailed token report
    token_report_file = OUTPUT_DIR / "batch_token_report.txt"
    with open(token_report_file, 'w', encoding='utf-8') as f:
        f.write("Batch Processing Token Report\n")
        f.write("=" * 60 + "\n\n")
        f.write("Per-File Token Usage:\n")
        f.write("-" * 40 + "\n")
        
        for item in token_summary:
            f.write(f"{item['file']}:\n")
            f.write(f"  Input tokens: {item['input']:,}\n")
            f.write(f"  Output tokens: {item['output']:,}\n")
            f.write(f"  Total tokens: {item['total']:,}\n\n")
        
        f.write("\nSummary Statistics:\n")
        f.write("-" * 40 + "\n")
        f.write(f"Total files processed: {len(token_summary)}\n")
        f.write(f"Total input tokens: {total_input:,}\n")
        f.write(f"Total output tokens: {total_output:,}\n")
        f.write(f"Total tokens used: {total_tokens:,}\n")
        
        if len(token_summary) > 0:
            f.write(f"\nAverage input tokens per file: {total_input / len(token_summary):,.2f}\n")
            f.write(f"Average output tokens per file: {total_output / len(token_summary):,.2f}\n")
            f.write(f"Average total tokens per file: {total_tokens / len(token_summary):,.2f}\n")
        
        f.write(f"\nEstimated total cost: ${estimated_cost:.4f}\n")
        if len(token_summary) > 0:
            f.write(f"Average cost per page: ${estimated_cost / len(token_summary):.4f}\n")
    
    print(f"\nDetailed token report saved to: {token_report_file}")


if __name__ == "__main__":
    batch_process_with_delay()