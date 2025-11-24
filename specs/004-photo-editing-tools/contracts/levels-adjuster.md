# Contract: LevelsAdjuster Service

**Service**: `src/services/levels_adjuster.py`  
**Class**: `LevelsAdjuster`  
**Date**: 2025-01-29

## Purpose

Service class for calculating image histograms and applying levels adjustments (tonal distribution modification). Provides stateless methods for histogram calculation and levels adjustment operations.

## Public API

### `calculate_histogram(image: ImageModel) -> np.ndarray`

Calculate histogram of tonal distribution for an image.

**Parameters**:
- `image: ImageModel` - Image to analyze. Must have valid pixel_data.

**Returns**:
- `np.ndarray` - Array of 256 integers representing frequency counts for each tone level (0-255). Shape: (256,). dtype: np.int32.

**Behavior**:
- Converts RGB/RGBA image to grayscale using luminance formula: `0.299*R + 0.587*G + 0.114*B`
- Calculates histogram using `np.histogram()` with 256 bins (one per tone level)
- Returns frequency counts for each bin (tone level 0-255)
- For RGBA images, alpha channel is ignored (histogram based on RGB luminance only)

**Raises**:
- `ValueError`: If image is None, pixel_data is invalid, or image is empty

**Example**:
```python
from src.services.levels_adjuster import LevelsAdjuster
from src.models.image_model import ImageModel

adjuster = LevelsAdjuster()
histogram = adjuster.calculate_histogram(image_model)
# histogram[0] = count of pixels with tone level 0 (black)
# histogram[255] = count of pixels with tone level 255 (white)
```

### `apply_levels(image: ImageModel, darks_cutoff: float, lights_cutoff: float) -> ImageModel`

Apply levels adjustment to image by clipping highlights and shadows.

**Parameters**:
- `image: ImageModel` - Image to adjust. Must have valid pixel_data.
- `darks_cutoff: float` - Percentage of darkest pixels to replace with black (0.0-100.0). 0.0 = no change, 100.0 = all pixels become black.
- `lights_cutoff: float` - Percentage of lightest pixels to replace with white (0.0-100.0). 0.0 = no change, 100.0 = all pixels become white.

**Returns**:
- `ImageModel` - New ImageModel instance with adjusted pixel_data. Original pixel_data is preserved in original_pixel_data. All other attributes (width, height, format, has_alpha) are copied from input.

**Behavior**:
1. Calculate histogram on luminance values
2. Find percentile thresholds:
   - `darks_threshold`: Tone level at which `darks_cutoff`% of pixels are darker
   - `lights_threshold`: Tone level at which `lights_cutoff`% of pixels are lighter
3. Create mapping:
   - Pixels with luminance <= `darks_threshold` → set RGB to (0, 0, 0)
   - Pixels with luminance >= `lights_threshold` → set RGB to (255, 255, 255)
   - Pixels between thresholds → unchanged
4. Apply mapping to RGB channels, preserve alpha channel if present
5. Return new ImageModel with adjusted pixel_data

**Raises**:
- `ValueError`: If image is None, pixel_data is invalid, darks_cutoff or lights_cutoff not in [0.0, 100.0]

**Example**:
```python
from src.services.levels_adjuster import LevelsAdjuster

adjuster = LevelsAdjuster()
# Replace darkest 5% with black, lightest 10% with white
adjusted_image = adjuster.apply_levels(image_model, darks_cutoff=5.0, lights_cutoff=10.0)
```

## Implementation Details

### Histogram Calculation

- Use `np.histogram()` with `bins=256` and `range=(0, 256)`
- Convert RGB/RGBA to grayscale: `luminance = 0.299*R + 0.587*G + 0.114*B`
- For RGBA images, use only RGB channels for luminance calculation
- Return integer counts (np.int32)

### Levels Adjustment Algorithm

1. Calculate histogram on luminance
2. Find cumulative distribution to determine percentile thresholds
3. Use NumPy boolean indexing for efficient pixel replacement:
   ```python
   # Create luminance mask
   luminance = 0.299 * rgb[:,:,0] + 0.587 * rgb[:,:,1] + 0.114 * rgb[:,:,2]
   # Apply darks cutoff
   result[luminance <= darks_threshold] = [0, 0, 0]
   # Apply lights cutoff
   result[luminance >= lights_threshold] = [255, 255, 255]
   ```
4. Preserve alpha channel: copy from original if present

## Testing Requirements

### Unit Tests

- `test_calculate_histogram_basic`: Calculate histogram for simple test image
- `test_calculate_histogram_uniform`: Histogram for uniform color image (all pixels same tone)
- `test_calculate_histogram_rgba`: Histogram calculation preserves alpha, uses RGB for luminance
- `test_calculate_histogram_empty`: Error handling for empty/invalid image
- `test_apply_levels_darks_only`: Apply only darks cutoff
- `test_apply_levels_lights_only`: Apply only lights cutoff
- `test_apply_levels_both`: Apply both cutoffs simultaneously
- `test_apply_levels_zero_cutoffs`: No change when both cutoffs are 0.0
- `test_apply_levels_max_cutoffs`: All pixels become black/white when cutoffs are 100.0
- `test_apply_levels_preserves_alpha`: Alpha channel preserved during adjustment
- `test_apply_levels_invalid_parameters`: Error handling for invalid cutoff values
- `test_apply_levels_creates_new_image`: Returns new ImageModel, doesn't modify original

### Integration Tests

- `test_levels_adjustment_workflow`: Complete workflow from histogram calculation to adjustment application
- `test_levels_with_previous_operations`: Levels adjustment works on image with previous modifications (pixelization, color reduction, etc.)

## Error Handling

- **Invalid image**: Raise `ValueError` with message "Invalid image: [specific issue]"
- **Invalid cutoff values**: Raise `ValueError` with message "darks_cutoff and lights_cutoff must be between 0.0 and 100.0"
- **Empty image**: Raise `ValueError` with message "Cannot calculate histogram for empty image"
- **Memory errors**: Let propagate (handled at controller level)

## Performance Requirements

- Histogram calculation: < 500ms for 2000x2000px images
- Levels adjustment: < 100ms for 2000x2000px images (per spec SC-003)
- Memory: Minimal overhead, creates one new ImageModel instance

## Dependencies

- `numpy` - For histogram calculation and array operations
- `src.models.image_model` - ImageModel class

## Notes

- Service is stateless (no instance variables)
- Methods can be static or instance methods (designer's choice)
- Follows same pattern as `ColorReducer` and `Pixelizer` services
- Histogram calculation is separate from adjustment to allow caching

