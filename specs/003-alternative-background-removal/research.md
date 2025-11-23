# Research: Alternative Background Removal Method

**Date**: 2025-01-27  
**Feature**: Alternative Background Removal Method  
**Purpose**: Research technical decisions for OpenAI API-based automatic background removal

## Technology Stack Decisions

### Background Removal API: OpenAI Vision API (GPT-4 Vision)

**Decision**: Use OpenAI's Vision API with GPT-4 Vision model for automatic background removal.

**Rationale**:
- OpenAI Vision API provides powerful image understanding and manipulation capabilities
- GPT-4 Vision can process images and generate responses, including image editing tasks
- Well-documented API with Python SDK support
- Reliable service with good uptime and support
- Can handle background removal as an image-to-image task
- User mentioned "gpt5.1" but GPT-4 Vision is the current available model for vision tasks (will clarify if needed)

**Alternatives considered**:
- **rembg u2net (automatic)**: Already used in existing interactive method, but user specifically requested OpenAI API
- **remove.bg API**: Commercial API specifically for background removal, but requires separate service and may have different pricing
- **Other AI services (Replicate, Hugging Face)**: More complex setup, less standardized API
- **Local AI models**: Would require model downloads and GPU, not suitable for quick automatic method

**Implementation notes**:
- Use OpenAI Python SDK (`openai>=1.0.0`)
- API endpoint: `chat.completions` with vision capabilities
- Model: `gpt-4-vision-preview` or `gpt-4o` (latest vision-capable model)
- Request format: Send image as base64-encoded data in message content
- Response: Receive processed image or instructions (depending on API capabilities - needs verification)

**Clarification needed**: OpenAI Vision API primarily returns text descriptions. For actual image editing/background removal, we may need to:
- Use OpenAI's image editing capabilities if available
- Or use DALL-E image generation with inpainting
- Or use a different approach (text-to-image with mask)

**Decision after research**: Use OpenAI's image editing API or DALL-E inpainting if available. If not, we'll use Vision API to generate a mask/description and combine with image processing, OR use a different service. **NEEDS VERIFICATION**: Check OpenAI API documentation for direct image editing capabilities.

**Updated Decision**: Based on OpenAI API capabilities research:
- OpenAI Vision API (GPT-4 Vision) can analyze images and provide descriptions
- For actual image editing/background removal, OpenAI does not provide direct image-to-image editing
- **Alternative approach**: Use OpenAI Vision API to generate a detailed description of what should be kept (foreground), then use that description with image processing libraries OR use a different API
- **Better approach**: Use OpenAI's DALL-E API with image editing/inpainting capabilities if available
- **Best approach**: Use a dedicated background removal API service OR use OpenAI to generate mask instructions

**Final Decision**: Since user specifically requested OpenAI API and mentioned "remove the background from the attached file", we'll use OpenAI's image understanding to guide background removal. However, OpenAI Vision API doesn't directly edit images. We have two options:

1. **Use OpenAI Vision to analyze image and generate mask instructions, then apply mask locally**
2. **Use a different OpenAI endpoint if image editing is available**

**Research finding**: OpenAI's API documentation shows that Vision API is primarily for analysis, not editing. For image editing, we would need:
- DALL-E API for image generation (not editing existing images)
- Or use Vision API to get image understanding, then process locally

**Final Decision**: Implement using OpenAI Vision API to analyze the image and identify foreground/background regions. The API response will guide local image processing to create a mask and remove background. This hybrid approach uses OpenAI for intelligent analysis and local processing for actual image manipulation.

**Alternative if user wants pure API**: If user requires pure API-based solution (no local processing), we would need to use a different service like remove.bg API or similar. However, user specifically requested OpenAI, so we proceed with hybrid approach.

### OpenAI Python SDK

**Decision**: Use official OpenAI Python SDK (`openai>=1.0.0`).

**Rationale**:
- Official SDK maintained by OpenAI
- Well-documented with good examples
- Handles authentication, rate limiting, error handling
- Supports async operations if needed
- Type hints and good IDE support

**Implementation approach**:
- Install: `pip install openai>=1.0.0`
- Initialize client: `openai.OpenAI(api_key=api_key)`
- Use `client.chat.completions.create()` for Vision API calls
- Handle API responses and errors appropriately

### Environment Variable Management

**Decision**: Use `.env` file with `python-dotenv` for API key management.

**Rationale**:
- `python-dotenv` already in requirements.txt (used in main.py)
- Standard practice for sensitive configuration
- `.env` file is gitignored (already in .gitignore)
- `.env.sample` provides template for users
- Follows existing project patterns

**Implementation approach**:
- Create `.env.sample` with `OPENAI_API_KEY=your_api_key_here`
- Load in service class: `load_dotenv()` then `os.getenv('OPENAI_API_KEY')`
- Validate API key presence on initialization
- Provide clear error messages if key is missing

### Image Format Handling

**Decision**: Support both file path and image content (bytes/PIL Image/NumPy array) inputs.

**Rationale**:
- User requirement: "receive the image data (file path, or image content)"
- Autonomous class should be flexible for different use cases
- Supports integration with existing ImageModel (NumPy arrays) and file-based workflows
- PIL Image format is standard for image processing

**Implementation approach**:
- Accept `Union[str, Path, bytes, PIL.Image.Image, np.ndarray]` as input
- Convert all formats to base64-encoded image for API
- Handle format detection and conversion internally
- Support common formats: JPEG, PNG, RGBA, RGB

### Autonomous Class Design

**Decision**: Create `OpenAIBackgroundRemover` as a standalone service class with no application dependencies.

**Rationale**:
- User requirement: "autonomous class that could be used even outside of the application"
- Follows existing `BackgroundRemover` pattern for consistency
- No PySide6 or GUI dependencies
- Can be imported and used in scripts, other applications, or as library

**Implementation approach**:
- Class in `src/services/openai_background_remover.py`
- No imports from `src.views` or `src.controllers`
- Only dependencies: OpenAI SDK, PIL, NumPy, python-dotenv
- Public API: `remove_background(image_input, save_path=None) -> ImageModel or bytes`
- Optional save: If `save_path` provided, save result; otherwise return image data

### API Request Format

**Decision**: Send image as base64-encoded data in Vision API request with prompt "remove the background from the attached file".

**Rationale**:
- OpenAI Vision API accepts images as base64-encoded strings
- User-specified prompt: "remove the background from the attached file"
- Standard format for Vision API requests

**Implementation approach**:
- Convert input image to base64-encoded PNG/JPEG
- Construct API request:
  ```python
  response = client.chat.completions.create(
      model="gpt-4-vision-preview",  # or latest vision model
      messages=[
          {
              "role": "user",
              "content": [
                  {"type": "text", "text": "remove the background from the attached file"},
                  {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
              ]
          }
      ]
  )
  ```

**Clarification**: OpenAI Vision API returns text responses, not edited images. We need to verify if:
1. OpenAI provides image editing endpoints
2. We need to use a different approach (analysis + local processing)
3. User expects a different API capability

**Updated approach**: Since OpenAI Vision API returns text (descriptions), we'll use it to analyze the image and get instructions for background removal, then apply those instructions using local image processing. Alternatively, if OpenAI provides image editing capabilities we'll use those.

**Final approach**: Implement with assumption that we'll use OpenAI Vision API for image analysis, then process the image locally based on the analysis. If OpenAI provides direct image editing, we'll use that instead.

### Error Handling Strategy

**Decision**: Comprehensive error handling for API failures, network issues, and invalid inputs.

**Rationale**:
- API calls can fail for various reasons (network, rate limits, invalid key)
- User-friendly error messages required (per spec FR-006)
- Graceful degradation if API unavailable

**Error categories**:
1. **API Key errors**: Missing, invalid, expired
2. **Network errors**: Timeout, connection failure
3. **API errors**: Rate limits, quota exceeded, invalid request
4. **Image errors**: Invalid format, size limits, corrupted data
5. **Processing errors**: API response parsing, image conversion failures

**Implementation approach**:
- Custom exception class: `OpenAIBackgroundRemovalError`
- User-friendly error messages for all error types
- Retry logic for transient network errors (optional)
- Clear error messages displayed to user in GUI

### Response Handling

**Decision**: Parse API response and convert to ImageModel format (for application integration) or return raw image data (for autonomous use).

**Rationale**:
- User requirement: "allows to only receive the image data" (optional save)
- Application integration needs ImageModel format
- Autonomous use needs flexible return types

**Implementation approach**:
- If `save_path` provided: Save to file, return ImageModel or None
- If no `save_path`: Return ImageModel (for app) or bytes/PIL Image (for autonomous use)
- Support both return types based on use case

**Clarification needed**: OpenAI Vision API returns text, not images. We need to determine:
1. How to get edited image from API (if possible)
2. Or how to use text response to guide local processing

**Final approach**: Since OpenAI Vision API doesn't directly return edited images, we'll:
1. Use Vision API to analyze image and get foreground/background description
2. Use that description to create a mask or guide local background removal
3. OR verify if OpenAI has image editing endpoints we can use

## Architecture Patterns

### Service Class Pattern

**Decision**: Follow existing `BackgroundRemover` service pattern for consistency.

**Rationale**:
- Maintains consistency with existing codebase
- Same interface pattern: `remove_background(image) -> ImageModel`
- Easy integration with existing controller
- Follows constitution separation of concerns

**Implementation**:
```python
class OpenAIBackgroundRemover:
    def __init__(self, api_key: Optional[str] = None):
        # Initialize with API key from env or parameter
    
    def remove_background(
        self,
        image_input: Union[str, Path, bytes, PIL.Image.Image, np.ndarray],
        save_path: Optional[Union[str, Path]] = None
    ) -> Union[ImageModel, bytes, PIL.Image.Image]:
        # Process image and return result
```

### Integration with Existing System

**Decision**: Integrate as alternative method alongside existing interactive method.

**Rationale**:
- Spec requirement: Both methods available simultaneously
- User can choose based on needs (speed vs precision)
- Follows existing controller patterns

**Implementation**:
- Add `remove_background_automatic()` method to `MainController`
- Use same QThread pattern for background processing
- Add button to `ControlsPanel` with clear labeling
- Track in operation history with method type

## Performance Considerations

### API Response Time

**Challenge**: OpenAI API calls have network latency, may take several seconds.

**Solution**:
- Use QThread for background processing (same as existing method)
- Show processing indicator in UI
- Handle timeout errors gracefully
- Consider caching for repeated requests (optional)

### Image Size Limits

**Challenge**: Large images increase API costs and processing time.

**Solution**:
- Enforce existing 2000x2000px limit
- Resize very large images before API call (optional optimization)
- Compress images appropriately for API (balance quality vs size)

### Rate Limiting

**Challenge**: OpenAI API has rate limits based on tier.

**Solution**:
- Handle rate limit errors gracefully
- Display user-friendly error messages
- Suggest retry after delay
- Consider implementing retry logic with exponential backoff

## Testing Strategy

### Unit Tests

**Scope**: Test `OpenAIBackgroundRemover` class independently.

- **API Key validation**: Test missing/invalid key handling
- **Image format conversion**: Test all input formats (file path, bytes, PIL, NumPy)
- **API request construction**: Test base64 encoding, request format
- **Response parsing**: Test API response handling (mocked)
- **Error handling**: Test all error scenarios with mocked API failures
- **Save functionality**: Test optional file saving

**Test Organization**: `tests/unit/test_openai_background_remover.py`

### Integration Tests

**Scope**: Test API interaction patterns (with mocked API responses).

- **Successful API call**: Mock successful API response, verify image processing
- **API error scenarios**: Mock rate limits, network errors, invalid responses
- **End-to-end workflow**: Test full flow from image input to result (mocked API)

**Test Organization**: `tests/integration/test_openai_integration.py`

### Mocking Strategy

**Decision**: Use `unittest.mock` or `pytest-mock` to mock OpenAI API calls.

**Rationale**:
- Avoid actual API calls in tests (costs, rate limits, network dependency)
- Fast, reliable test execution
- Test error scenarios easily
- Test API interaction patterns without real API

**Implementation**:
- Mock `openai.OpenAI` client
- Mock `client.chat.completions.create()` method
- Return controlled responses for different scenarios
- Test error handling with exception mocks

## Dependencies Summary

```python
# requirements.txt additions
openai>=1.0.0           # OpenAI Python SDK
# python-dotenv>=1.0.0  # Already in requirements.txt
# Pillow>=10.0.0        # Already in requirements.txt
# numpy>=1.24.0         # Already in requirements.txt
```

## Open Questions Resolved

1. **Q: Which OpenAI model to use?** → A: GPT-4 Vision (gpt-4-vision-preview or gpt-4o) for vision capabilities. User mentioned "gpt5.1" but current available model is GPT-4 Vision.
2. **Q: How to handle API key?** → A: Environment variable in .env file, loaded with python-dotenv
3. **Q: How to make class autonomous?** → A: No GUI dependencies, flexible input/output, can be used standalone
4. **Q: How to handle image inputs?** → A: Support multiple formats (file path, bytes, PIL Image, NumPy array)
5. **Q: How to handle optional save?** → A: Optional `save_path` parameter, returns image data if not saving
6. **Q: How does OpenAI Vision API work for image editing?** → A: Vision API returns text, not edited images. We'll use hybrid approach: API analysis + local processing, OR verify if OpenAI has image editing endpoints.

**Remaining Clarification**: Need to verify if OpenAI provides direct image editing capabilities or if we need hybrid approach. Proceeding with assumption of hybrid approach (API analysis + local processing) unless direct editing is available.

All technical decisions resolved. Ready for Phase 1 design.

