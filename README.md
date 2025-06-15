# Llama 4 Text Extraction Project

This project uses Google Cloud Vertex AI and the Llama 4 model to extract text from scanned textbook pages.

## Quick Start

1. **Activate your conda environment:**
   ```
   conda activate llama-textract
   ```

2. **Install dependencies:**
   ```
   cd path/to/this/project
   pip install -r requirements.txt
   ```

3. **Configure your settings:**
   - Edit the `.env` file with your Google Cloud project ID
   - Add the path to your Google Cloud credentials JSON file

4. **Add images to process:**
   - Place scanned textbook pages in `data/input/`
   - Supported formats: JPG, PNG, BMP, GIF, TIFF

5. **Run the extraction:**
   ```
   python src/llama4_extractor.py
   ```

6. **Find your results:**
   - Extracted text files will be in `data/output/`
   - Each image gets its own text file

## Project Structure

```
llama-text-extraction/
├── src/                    # Source code
│   └── llama4_extractor.py # Main extraction logic
├── data/
│   ├── input/             # Put your images here
│   └── output/            # Extracted text appears here
├── config/                # Configuration files
│   └── settings.py        # Project settings
├── tests/                 # Test scripts
│   └── test_single_image.py
├── logs/                  # Application logs
├── docs/                  # Documentation
├── .env                   # Your configuration (don't share this!)
├── requirements.txt       # Python packages needed
└── README.md             # This file
```

## Testing Your Setup

Run the test script to verify everything works:
```
python tests/test_single_image.py
```

## Tips for Best Results

1. **Image Quality**: Higher resolution scans (300 DPI or more) give better results
2. **Clear Text**: Ensure text is readable and not too blurry
3. **Page Layout**: Works best with standard textbook layouts
4. **File Size**: Images are automatically resized if too large

## Troubleshooting

If you encounter errors:

1. **"GOOGLE_CLOUD_PROJECT not set"**: Update your .env file
2. **"Credentials file not found"**: Check the path in .env
3. **"No module named..."**: Run `pip install -r requirements.txt`
4. **API errors**: Verify your Google Cloud project has Vertex AI enabled

## Cost Considerations

- Each page costs approximately $0.075 to process
- Monitor your usage in the Google Cloud Console
- Consider using batch processing for large documents
