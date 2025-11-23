# Quickstart: Alternative Background Removal Method

**Feature**: Alternative Background Removal Method  
**Date**: 2025-01-27

## Overview

This feature adds an automatic background removal method using OpenAI Vision API. Users can remove backgrounds with a single click, without needing to select points manually. The implementation includes an autonomous service class that can be used independently of the application.

## Prerequisites

1. **OpenAI API Key**: You need an OpenAI API key to use this feature
   - Sign up at https://platform.openai.com/
   - Create an API key in your account settings
   - Copy the API key (starts with "sk-")

2. **Python Environment**: Python 3.11+ with required dependencies

## Setup Steps

### 1. Install Dependencies

```bash
pip install openai>=1.0.0
```

Note: `python-dotenv`, `Pillow`, and `NumPy` are already in requirements.txt.

### 2. Configure API Key

Create a `.env` file in the project root (if it doesn't exist):

```bash
# Copy the sample file
cp .env.sample .env

# Edit .env and add your API key
OPENAI_API_KEY=sk-your-actual-api-key-here
```

**Important**: The `.env` file is gitignored and should never be committed.

### 3. Verify Setup

Test the service class directly:

```python
from src.services.openai_background_remover import OpenAIBackgroundRemover

# Initialize (loads API key from .env)
remover = OpenAIBackgroundRemover()

# Test with an image file
result = remover.remove_background("path/to/test-image.jpg")
print(f"Background removed! Result: {result}")
```

## Usage

### In the Application

1. **Load an image** using the existing "Load Image" button
2. **Click "Remove Background (Automatic)"** button in the controls panel
3. Wait for processing (typically 2-5 seconds)
4. View the result with transparent background
5. **Save** the image if desired (supports PNG with transparency)

### Autonomous Use (Outside Application)

The `OpenAIBackgroundRemover` class can be used independently:

```python
from src.services.openai_background_remover import OpenAIBackgroundRemover

# Initialize
remover = OpenAIBackgroundRemover(api_key="sk-your-key")  # Or load from .env

# Option 1: File path input, save to file
result = remover.remove_background("input.jpg", save_path="output.png")

# Option 2: File path input, get image data
result = remover.remove_background("input.jpg")  # Returns ImageModel or PIL.Image

# Option 3: PIL Image input
from PIL import Image
image = Image.open("input.jpg")
result = remover.remove_background(image)  # Returns PIL.Image

# Option 4: NumPy array input
import numpy as np
image_array = np.array(...)  # Your image data
result = remover.remove_background(image_array)  # Returns ImageModel
```

## Features

### Automatic Processing

- **One-click operation**: No point selection required
- **Fast processing**: Typically completes in 2-5 seconds
- **No user interaction**: Fully automatic background detection

### Flexible Input/Output

- **Input formats**: File path, bytes, PIL Image, NumPy array
- **Output formats**: ImageModel (for app), bytes, PIL Image (for autonomous use)
- **Optional saving**: Can save directly to file or return image data

### Error Handling

- **Clear error messages**: User-friendly messages for all error scenarios
- **API key validation**: Checks for missing/invalid keys on initialization
- **Network error handling**: Graceful handling of connection issues
- **Rate limit handling**: Clear messages when API limits are exceeded

## Troubleshooting

### "OpenAI API key not found"

- Check that `.env` file exists in project root
- Verify `OPENAI_API_KEY` is set in `.env`
- Ensure `.env` file is not in `.gitignore` exclusion (it should be ignored, but file should exist)

### "Invalid OpenAI API key"

- Verify API key starts with "sk-"
- Check that API key is correct (no extra spaces)
- Ensure API key is active in your OpenAI account

### "Network error"

- Check internet connection
- Verify OpenAI API is accessible
- Try again after a few moments

### "API rate limit exceeded"

- You've hit your OpenAI API rate limit
- Wait a few minutes and try again
- Check your OpenAI account for rate limit details

### Processing takes too long

- Large images (close to 2000x2000px) may take longer
- Network latency can affect API response time
- Typical processing: 2-5 seconds for standard images

## Comparison with Interactive Method

| Feature | Automatic (OpenAI) | Interactive (rembg) |
|---------|-------------------|---------------------|
| **Speed** | Fast (2-5 seconds) | Moderate (3-8 seconds) |
| **Accuracy** | Good (75% typical cases) | Excellent (90% typical cases) |
| **User Input** | None (one click) | Point selection required |
| **Best For** | Quick results, clear subjects | Precise control, complex images |
| **Internet** | Required | Not required (local processing) |
| **Cost** | API costs apply | Free (local processing) |

## Next Steps

- See [spec.md](./spec.md) for full feature specification
- See [plan.md](./plan.md) for implementation details
- See [contracts/openai-background-remover.md](./contracts/openai-background-remover.md) for API documentation

## Support

For issues or questions:
- Check error messages for specific guidance
- Verify API key configuration
- Check OpenAI API status
- Review troubleshooting section above

