# Data Model: Alternative Background Removal Method

**Date**: 2025-01-27  
**Feature**: Alternative Background Removal Method

## Entities

### OpenAIBackgroundRemover

Represents the service class for automatic background removal using OpenAI Vision API.

**Attributes**:
- `api_key: Optional[str]` - OpenAI API key (loaded from environment or provided)
- `client: Optional[OpenAI]` - OpenAI API client instance (initialized on first use)

**State**:
- `_initialized: bool` - Whether API client has been initialized
- `_api_key_valid: bool` - Whether API key is valid (checked on initialization)

**Validation Rules**:
- `api_key` must be non-empty string if provided
- API key must be valid OpenAI API key format (starts with "sk-")
- Client initialization must succeed before processing images

**State Transitions**:
- `Uninitialized` → `Initialized` (after successful API key validation and client creation)
- `Initialized` → `Error` (if API key invalid or client creation fails)
- `Error` → `Initialized` (if API key updated and revalidated)

**Relationships**:
- Processes `ImageModel` instances (converts to/from for application integration)
- Uses `OpenAI` client for API communication
- Can save results to file system (optional)

### Image Input (Union Type)

Represents flexible image input formats supported by the service.

**Types**:
- `str` - File path to image file
- `Path` - Path object to image file
- `bytes` - Raw image data as bytes
- `PIL.Image.Image` - PIL Image object
- `np.ndarray` - NumPy array (shape: height, width, channels)

**Validation Rules**:
- File paths must exist and be readable
- Bytes must be valid image data
- PIL Images must be in RGB or RGBA mode
- NumPy arrays must have shape (height, width, 3) or (height, width, 4)
- Maximum dimensions: 2000x2000px (per existing constraints)

**Conversion Flow**:
1. Detect input type
2. Convert to PIL Image (standard format)
3. Validate dimensions and format
4. Convert to base64 for API
5. Process via API
6. Convert response to output format

### API Request

Represents the structure of OpenAI Vision API request.

**Attributes**:
- `model: str` - Model identifier (e.g., "gpt-4-vision-preview", "gpt-4o")
- `messages: List[Dict]` - Message content with text prompt and image
- `max_tokens: Optional[int]` - Maximum tokens in response (optional)
- `temperature: Optional[float]` - Response randomness (optional, default 0.7)

**Message Structure**:
```python
{
    "role": "user",
    "content": [
        {"type": "text", "text": "remove the background from the attached file"},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
    ]
}
```

**Validation Rules**:
- Model must be valid vision-capable model
- Image must be base64-encoded PNG or JPEG
- Prompt text must be non-empty
- Image size must be within API limits

### API Response

Represents the structure of OpenAI Vision API response.

**Attributes**:
- `response_text: str` - Text response from API (image analysis/instructions)
- `usage: Dict` - API usage information (tokens used)
- `model: str` - Model used for response

**Note**: OpenAI Vision API returns text, not edited images. The response will contain analysis or instructions that guide local image processing.

**Processing Flow**:
1. Receive text response from API
2. Parse response for foreground/background information
3. Use information to create mask or guide local processing
4. Apply mask/processing to original image
5. Return processed image with transparent background

### Background Removal Result

Represents the output of background removal operation.

**Output Formats** (flexible based on use case):
- `ImageModel` - For application integration (matches existing pattern)
- `bytes` - Raw image data (for autonomous use)
- `PIL.Image.Image` - PIL Image object (for flexible use)
- File path - If `save_path` provided, saved to file

**Attributes** (for ImageModel output):
- `width: int` - Image width (preserved from input)
- `height: int` - Image height (preserved from input)
- `pixel_data: np.ndarray` - Processed pixel data with transparent background (RGBA)
- `original_pixel_data: np.ndarray` - Original unprocessed data (for undo)
- `format: str` - Image format (typically "PNG" for transparency)
- `has_alpha: bool` - Always True after background removal

**Validation Rules**:
- Dimensions must match input image
- Pixel data must have alpha channel (RGBA)
- Transparent areas should have alpha = 0
- Foreground areas should have alpha = 255

## Data Flow

### Background Removal Flow (Application Integration)

1. User clicks "Remove Background (Automatic)" button
2. Controller calls `remove_background_automatic()` method
3. Controller creates `OpenAIBackgroundRemover` instance (or reuses existing)
4. Controller passes `ImageModel` to service
5. Service converts `ImageModel.pixel_data` to base64-encoded image
6. Service constructs API request with prompt and image
7. Service calls OpenAI Vision API
8. Service receives text response (analysis/instructions)
9. Service parses response and creates mask/processing instructions
10. Service applies mask/processing to original image locally
11. Service creates new `ImageModel` with processed pixel data
12. Service returns `ImageModel` to controller
13. Controller updates image display
14. Controller adds operation to undo history

### Background Removal Flow (Autonomous Use)

1. User creates `OpenAIBackgroundRemover` instance
2. User calls `remove_background(image_input, save_path=None)`
3. Service detects input type and converts to PIL Image
4. Service validates image (dimensions, format)
5. Service converts to base64 for API
6. Service calls OpenAI Vision API
7. Service receives response and processes image
8. Service returns result in requested format:
   - If `save_path` provided: Save to file, return `ImageModel` or `None`
   - If no `save_path`: Return `ImageModel`, `bytes`, or `PIL.Image` based on input type

### Error Flow

1. Service validates API key (if missing/invalid → `OpenAIBackgroundRemovalError`)
2. Service validates image input (if invalid → `ValueError`)
3. Service calls API (if network error → `OpenAIBackgroundRemovalError` with retry suggestion)
4. Service receives API response (if error → `OpenAIBackgroundRemovalError` with user message)
5. Service processes response (if parsing fails → `OpenAIBackgroundRemovalError`)
6. Service applies processing (if processing fails → `OpenAIBackgroundRemovalError`)
7. All errors include user-friendly messages for GUI display

## State Management

### Service State

The `OpenAIBackgroundRemover` maintains:
- API client instance (lazy initialization)
- API key validation status
- Error state (if initialization failed)

### Application State

The application maintains (existing + new):
- One `ImageModel` instance (current loaded image)
- One `BackgroundRemover` instance (existing interactive method)
- One `OpenAIBackgroundRemover` instance (new automatic method)
- Operation history (tracks both methods with type identifier)

### State Updates

- Button click → Controller method → Service processes → ImageModel updated → UI updated
- Error occurs → Service raises exception → Controller catches → Error signal emitted → UI displays error
- Processing completes → ImageModel updated → Operation added to history → Undo button enabled

## Error States

### Missing API Key

- **State**: API key not found in environment or parameter
- **Attributes**: `error_message: str = "OpenAI API key not found. Please set OPENAI_API_KEY in .env file."`
- **Handling**: Display error to user, provide instructions for setup

### Invalid API Key

- **State**: API key format invalid or authentication failed
- **Attributes**: `error_message: str = "Invalid OpenAI API key. Please check your .env file."`
- **Handling**: Display error, suggest checking API key

### Network Error

- **State**: API request failed due to network issues
- **Attributes**: `error_message: str = "Network error. Please check your internet connection and try again."`
- **Handling**: Display error, allow retry

### API Rate Limit

- **State**: API rate limit exceeded
- **Attributes**: `error_message: str = "API rate limit exceeded. Please try again later."`
- **Handling**: Display error, suggest waiting before retry

### Invalid Image Input

- **State**: Image input is invalid (wrong format, too large, corrupted)
- **Attributes**: `error_message: str = "Invalid image. Please check the image file."`
- **Handling**: Display error, allow user to select different image

### Processing Error

- **State**: Image processing after API call failed
- **Attributes**: `error_message: str = "Failed to process image. Please try again."`
- **Handling**: Display error, allow retry or suggest using interactive method

## Data Validation Summary

| Entity | Validation Rules | Error Handling |
|--------|-----------------|----------------|
| OpenAIBackgroundRemover | API key present and valid, client initialized | Raise OpenAIBackgroundRemovalError with user message |
| Image Input | Valid format, dimensions <= 2000x2000, readable | Raise ValueError with specific issue |
| API Request | Valid model, base64 image, non-empty prompt | Raise OpenAIBackgroundRemovalError if API call fails |
| API Response | Valid response format, parseable content | Raise OpenAIBackgroundRemovalError if parsing fails |
| Background Removal Result | Valid dimensions, RGBA format, alpha channel present | Validate before returning, raise error if invalid |

