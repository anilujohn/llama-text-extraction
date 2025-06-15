# Troubleshooting Guide

## Common Issues and Solutions

### 1. Environment Issues

**Problem**: "No module named 'google.cloud'"
**Solution**: 
- Make sure you've activated your conda environment: `conda activate llama-textract`
- Install requirements: `pip install -r requirements.txt`

### 2. Authentication Issues

**Problem**: "Could not automatically determine credentials"
**Solution**:
- Check that your .env file has the correct path to your credentials JSON
- Ensure the JSON file exists at that location
- The path should use forward slashes (/) or double backslashes (\\)

### 3. API Issues

**Problem**: "403 Forbidden" or "Permission denied"
**Solution**:
- Verify Vertex AI API is enabled in your Google Cloud project
- Check that your service account has the necessary permissions
- Ensure you've accepted the Llama license in Model Garden

### 4. Image Processing Issues

**Problem**: "Error preparing image"
**Solution**:
- Check that your image file is not corrupted
- Ensure the image is in a supported format (JPG, PNG, etc.)
- Try with a smaller or different image

### 5. No Output

**Problem**: Extraction runs but no text is produced
**Solution**:
- Check the logs folder for detailed error messages
- Verify the image contains readable text
- Try with a clearer, higher-resolution scan

## Getting Help

If you're still stuck:

1. Check the logs in the `logs/` folder
2. Run the test script: `python tests/test_single_image.py`
3. Verify your setup with Google Cloud CLI: `gcloud config list`
