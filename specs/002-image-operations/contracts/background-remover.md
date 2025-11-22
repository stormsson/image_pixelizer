# Contract: BackgroundRemover Service

**Service**: `src/services/background_remover.py`  
**Feature**: Image Operations in Controls Panel  
**Date**: 2025-01-27

## Purpose

Service for removing image backgrounds using the rembg AI model. Processes images to detect and remove backgrounds, making them transparent while preserving the main subject.

## Interface

### Class: `BackgroundRemover`

```python
class BackgroundRemover:
    """Service for removing image backgrounds using rembg AI model."""
    
    def remove_background(self, image: ImageModel) -> ImageModel:
        """
        Remove background from image using rembg AI model.
        
        Args:
            image: ImageModel to process
            
        Returns:
            New ImageModel with background removed (transparent alpha channel)
            
        Raises:
            BackgroundRemovalError: If processing fails
            ValueError: If image is invalid
        """
```

## Behavior

### Input Validation

- **Image must be valid**: `ImageModel` with valid `pixel_data`, `width`, `height`
- **Image dimensions**: Must be within 2000x2000px limit (enforced by existing ImageModel validation)
- **Image format**: Supports RGB and RGBA formats

### Processing

1. Convert `ImageModel.pixel_data` (NumPy array) to PIL Image
2. Call `rembg.remove()` with PIL Image
3. Convert result back to NumPy array
4. Ensure result has alpha channel (RGBA format)
5. Create new `ImageModel` with processed pixel data
6. Preserve original dimensions and format metadata

### Output

- **Format**: Always RGBA (with alpha channel for transparency)
- **Dimensions**: Preserved from input image
- **Pixel Data**: Background pixels set to transparent (alpha = 0), subject preserved

### Error Handling

**BackgroundRemovalError** (custom exception):
- Raised when rembg processing fails
- User message: "Failed to remove background. Please try again or use a different image."
- Technical message: Includes rembg error details for logging

**ValueError**:
- Raised when image is None or invalid
- User message: "Invalid image. Please load an image first."

**ImportError** (handled at module level):
- If rembg not installed, provide clear error message
- User message: "Background removal requires rembg library. Please install it."

## Performance Requirements

- **Processing Time**: <5 seconds for images up to 2000x2000px (per spec SC-001)
- **Memory**: Efficient processing, no excessive memory usage
- **Threading**: Service methods are thread-safe (can be called from QThread)

## Dependencies

- **rembg**: AI background removal library
- **Pillow (PIL)**: Image format conversion
- **NumPy**: Array operations
- **ImageModel**: Existing model from `src.models.image_model`

## Testing Requirements

### Unit Tests

- Test successful background removal (RGB input → RGBA output)
- Test successful background removal (RGBA input → RGBA output)
- Test error handling (invalid image, rembg failure)
- Test dimension preservation
- Test alpha channel creation
- Test with various image sizes (small, medium, large up to 2000x2000px)
- Test rembg import error handling

### Integration Tests

- Test end-to-end: Load image → Remove background → Verify result
- Test with existing pixelization/color reduction applied
- Test error propagation to controller

## Example Usage

```python
from src.services.background_remover import BackgroundRemover
from src.models.image_model import ImageModel

remover = BackgroundRemover()
processed_image = remover.remove_background(image_model)
# processed_image has transparent background, same dimensions
```

## Notes

- First use of rembg will download model (~100MB), may take time
- Model is cached after first download
- Processing is CPU/GPU intensive - use threading for UI responsiveness
- Result always has alpha channel even if input was RGB

