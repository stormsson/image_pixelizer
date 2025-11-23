# Contract: OpenAIBackgroundRemover Service

**Service**: `src/services/openai_background_remover.py`  
**Feature**: Alternative Background Removal Method  
**Date**: 2025-01-27

## Purpose

Autonomous service class for removing image backgrounds using OpenAI Vision API. Provides automatic, one-click background removal without requiring user interaction. Can be used independently of the application or integrated with the GUI.

## Interface

### Class: `OpenAIBackgroundRemover`

```python
class OpenAIBackgroundRemover:
    """Service for removing image backgrounds using OpenAI Vision API.
    
    Autonomous class that can be used independently of the application.
    Supports flexible input formats (file path, bytes, PIL Image, NumPy array)
    and optional file saving.
    """
    
    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize OpenAI background remover with API key.
        
        Args:
            api_key: OpenAI API key. If None, loads from OPENAI_API_KEY
                environment variable.
                
        Raises:
            OpenAIBackgroundRemovalError: If API key is missing or invalid
        """
    
    def remove_background(
        self,
        image_input: Union[str, Path, bytes, PIL.Image.Image, np.ndarray],
        save_path: Optional[Union[str, Path]] = None
    ) -> Union[ImageModel, bytes, PIL.Image.Image]:
        """
        Remove background from image using OpenAI Vision API.
        
        Args:
            image_input: Image to process. Can be:
                - str: File path to image
                - Path: Path object to image
                - bytes: Raw image data
                - PIL.Image.Image: PIL Image object
                - np.ndarray: NumPy array (height, width, channels)
            save_path: Optional file path to save result. If provided,
                saves image and returns ImageModel. If None, returns
                image data without saving.
                
        Returns:
            - If save_path provided: ImageModel (for app integration)
            - If save_path None: ImageModel, bytes, or PIL.Image based on input type
            
        Raises:
            OpenAIBackgroundRemovalError: If API call fails, network error,
                rate limit, or processing error
            ValueError: If image_input is invalid (wrong format, too large,
                corrupted, dimensions exceed 2000x2000px)
        """
```

## Behavior

### Input Validation

- **Image input types**: Supports str (file path), Path, bytes, PIL.Image.Image, np.ndarray
- **File paths**: Must exist and be readable, must be valid image format (JPEG, PNG, etc.)
- **Image dimensions**: Must be within 2000x2000px limit (per existing constraints)
- **Image format**: Supports RGB and RGBA formats
- **NumPy arrays**: Must have shape (height, width, 3) or (height, width, 4)

### Processing

1. Validate API key (from parameter or environment variable)
2. Initialize OpenAI client (lazy initialization)
3. Detect and convert input image to PIL Image format
4. Validate image dimensions and format
5. Convert PIL Image to base64-encoded PNG/JPEG for API
6. Construct API request with prompt "remove the background from the attached file"
7. Call OpenAI Vision API (GPT-4 Vision model)
8. Receive text response (image analysis/instructions)
9. Parse response to extract foreground/background information
10. Create mask or processing instructions from response
11. Apply mask/processing to original image locally
12. Convert result to output format (ImageModel, bytes, or PIL Image)
13. Optionally save to file if `save_path` provided

### Output

- **Format**: Always RGBA (with alpha channel for transparency)
- **Dimensions**: Preserved from input image
- **Pixel Data**: Background pixels set to transparent (alpha = 0), subject preserved
- **Return Type**: Flexible based on use case:
  - `ImageModel`: For application integration
  - `bytes`: For autonomous use with raw data
  - `PIL.Image.Image`: For flexible image processing

### Error Handling

**OpenAIBackgroundRemovalError** (custom exception):
- Raised when API call fails, network error, rate limit, or processing error
- User message: Clear, actionable error message (e.g., "OpenAI API key not found. Please set OPENAI_API_KEY in .env file.")
- Technical message: Includes API error details for logging

**ValueError**:
- Raised when image_input is invalid (wrong format, too large, corrupted, dimensions exceed limit)
- User message: Specific validation error (e.g., "Image dimensions exceed 2000x2000px limit.")

**API Key Errors**:
- Missing key: "OpenAI API key not found. Please set OPENAI_API_KEY in .env file."
- Invalid key: "Invalid OpenAI API key. Please check your .env file."

**Network Errors**:
- Timeout: "Request timed out. Please check your internet connection and try again."
- Connection error: "Network error. Please check your internet connection and try again."

**API Errors**:
- Rate limit: "API rate limit exceeded. Please try again later."
- Quota exceeded: "API quota exceeded. Please check your OpenAI account."
- Invalid request: "Invalid API request. Please try again."

## Performance Requirements

- **Processing Time**: <5 seconds for images up to 2000x2000px (per spec SC-001)
- **API Response Time**: Depends on OpenAI API (typically 2-4 seconds)
- **Memory**: Efficient processing, no excessive memory usage
- **Threading**: Service methods are thread-safe (can be called from QThread)

## Dependencies

- **openai**: OpenAI Python SDK (>=1.0.0)
- **python-dotenv**: Environment variable loading (already in requirements.txt)
- **Pillow (PIL)**: Image format conversion (already in requirements.txt)
- **NumPy**: Array operations (already in requirements.txt)
- **ImageModel**: Existing model from `src.models.image_model` (for app integration)

## Environment Configuration

### Required Environment Variable

- `OPENAI_API_KEY`: OpenAI API key (must be set in `.env` file)

### .env.sample Template

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_api_key_here
```

### Loading

- Service loads API key from environment variable `OPENAI_API_KEY`
- Can also accept API key as constructor parameter (for testing or alternative config)
- Validates API key format (starts with "sk-") on initialization

## Testing Requirements

### Unit Tests

- Test successful background removal with all input types (file path, bytes, PIL, NumPy)
- Test API key validation (missing, invalid format, invalid key)
- Test image format conversion (all input types → PIL → base64)
- Test API request construction (prompt, image encoding)
- Test response parsing and mask creation
- Test error handling (all error scenarios with mocked API)
- Test optional file saving
- Test dimension validation (2000x2000px limit)
- Test with various image sizes (small, medium, large up to 2000x2000px)

### Integration Tests

- Test end-to-end: Load image → Remove background → Verify result (mocked API)
- Test API interaction patterns (success, rate limit, network error)
- Test integration with existing ImageModel
- Test error propagation to controller
- Test autonomous use (outside application context)

### Mocking Strategy

- Mock `openai.OpenAI` client for all tests
- Mock `client.chat.completions.create()` method
- Return controlled responses for different scenarios
- Test error handling with exception mocks

## Example Usage

### Application Integration

```python
from src.services.openai_background_remover import OpenAIBackgroundRemover
from src.models.image_model import ImageModel

remover = OpenAIBackgroundRemover()  # Loads API key from .env
processed_image = remover.remove_background(image_model)
# processed_image is ImageModel with transparent background
```

### Autonomous Use (File Path)

```python
from src.services.openai_background_remover import OpenAIBackgroundRemover

remover = OpenAIBackgroundRemover()
result = remover.remove_background("path/to/image.jpg", save_path="output.png")
# Saves to output.png, returns ImageModel
```

### Autonomous Use (Image Data, No Save)

```python
from src.services.openai_background_remover import OpenAIBackgroundRemover
from PIL import Image

remover = OpenAIBackgroundRemover()
image = Image.open("input.jpg")
result = remover.remove_background(image)  # No save_path
# Returns PIL.Image with transparent background
```

### Autonomous Use (NumPy Array)

```python
from src.services.openai_background_remover import OpenAIBackgroundRemover
import numpy as np

remover = OpenAIBackgroundRemover()
image_array = np.array(...)  # (height, width, 3) or (height, width, 4)
result = remover.remove_background(image_array)
# Returns ImageModel or PIL.Image based on input type
```

## Notes

- **Autonomous Design**: Class has no dependencies on PySide6 or GUI components
- **Flexible I/O**: Supports multiple input/output formats for different use cases
- **API Costs**: Each API call incurs costs based on OpenAI pricing
- **Rate Limits**: Subject to OpenAI API rate limits (varies by tier)
- **Internet Required**: Requires internet connection for API calls
- **Hybrid Processing**: Uses OpenAI Vision API for analysis, local processing for actual image manipulation
- **Error Messages**: All errors include user-friendly messages suitable for GUI display

