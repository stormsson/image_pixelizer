# Data Model: Image Pixelizer Application

**Date**: 2025-01-27  
**Feature**: Image Pixelizer Application

## Entities

### Image

Represents the loaded image file with its pixel data, dimensions, and processed state.

**Attributes**:
- `width: int` - Image width in pixels
- `height: int` - Image height in pixels
- `pixel_data: np.ndarray` - NumPy array of shape (height, width, 3) or (height, width, 4) for RGB/RGBA
- `original_pixel_data: np.ndarray` - Original unprocessed image data (for reset/undo)
- `format: str` - Original image format (JPEG, PNG, etc.)
- `has_alpha: bool` - Whether image has alpha channel (transparency)

**Validation Rules**:
- `width` and `height` must be > 0
- Maximum dimensions: 2000 x 2000 pixels (per spec edge case)
- `pixel_data` must be valid NumPy array with shape (height, width, channels)
- Channels must be 3 (RGB) or 4 (RGBA)

**State Transitions**:
- `None` → `Loaded` (after successful file load)
- `Loaded` → `Pixelized` (after pixelization applied)
- `Pixelized` → `ColorReduced` (after color reduction applied)
- `*` → `Loaded` (reset to original)

**Relationships**:
- Has one `ImageStatistics` (computed from current pixel_data)
- Used by `PixelizationSettings` and `ColorReductionSettings` for processing

### ImageStatistics

Computed information about the current image state, displayed in status bar.

**Attributes**:
- `distinct_color_count: int` - Number of unique colors in current image
- `width: int` - Current image width (matches Image.width)
- `height: int` - Current image height (matches Image.height)
- `hover_hex_color: Optional[str]` - HEX color code of pixel under mouse cursor (None when mouse not over image)

**Computation**:
- `distinct_color_count`: Count unique RGB/RGBA tuples in pixel_data
- `hover_hex_color`: Convert RGB values at mouse position to HEX format (e.g., "#FF5733")
- Updated automatically when image pixel_data changes or mouse position changes
- Computed efficiently using NumPy operations

**Validation Rules**:
- `distinct_color_count` must be >= 1
- `width` and `height` must match associated Image dimensions
- `hover_hex_color` must be None or valid HEX format string (e.g., "#RRGGBB" or "#RRGGBBAA")

**Relationships**:
- Belongs to one `Image` (computed from Image.pixel_data)

### PixelizationSettings

Configuration for pixelization effect, controlled by pixel size slider.

**Attributes**:
- `pixel_size: int` - Size of each pixel block (1 to maximum, e.g., 1-50)
- `is_enabled: bool` - Whether pixelization is currently applied

**Validation Rules**:
- `pixel_size` must be >= 1
- `pixel_size` maximum value should provide meaningful effect (e.g., 50 pixels)
- When `pixel_size` is 1, no pixelization effect (per spec edge case)

**State Transitions**:
- `pixel_size` changes trigger image reprocessing
- `is_enabled` toggles effect on/off

**Relationships**:
- Applied to one `Image` (modifies Image.pixel_data)

### ColorReductionSettings

Configuration for color reduction effect, controlled by sensitivity slider.

**Attributes**:
- `sensitivity: float` - Color similarity threshold (0.0 to 1.0 or similar range)
- `is_enabled: bool` - Whether color reduction is currently applied

**Validation Rules**:
- `sensitivity` must be in valid range (e.g., 0.0 to 1.0)
- Higher sensitivity = more aggressive color merging = fewer colors
- Lower sensitivity = less aggressive merging = more colors preserved

**State Transitions**:
- `sensitivity` changes trigger image reprocessing
- `is_enabled` toggles effect on/off

**Relationships**:
- Applied to one `Image` (modifies Image.pixel_data after pixelization)

## Data Flow

### Image Loading Flow

1. User selects image file via file dialog
2. `ImageLoader` validates file format and size
3. `ImageLoader` loads image using Pillow
4. Convert to NumPy array
5. Create `Image` entity with pixel_data
6. Compute initial `ImageStatistics`
7. Display in main content area

### Image Processing Flow

1. User adjusts pixel size slider
2. `PixelizationSettings.pixel_size` updated
3. `Pixelizer` service processes `Image.pixel_data`
4. Update `Image.pixel_data` with processed result
5. Recompute `ImageStatistics`
6. Update UI display

1. User adjusts sensitivity slider
2. `ColorReductionSettings.sensitivity` updated
3. `ColorReducer` service processes `Image.pixel_data`
4. Update `Image.pixel_data` with processed result
5. Recompute `ImageStatistics`
6. Update UI display

### Processing Order

1. Load original image → `Image.original_pixel_data`
2. Apply pixelization → `Image.pixel_data` (from original)
3. Apply color reduction → `Image.pixel_data` (from pixelized)

This order ensures color reduction works on pixelized blocks, producing better visual results.

## State Management

### Application State

The application maintains:
- One `Image` instance (current loaded image)
- One `PixelizationSettings` instance
- One `ColorReductionSettings` instance
- One `ImageStatistics` instance (computed from current Image, includes hover HEX color)
- Mouse position state (tracked by ImageView widget, updates ImageStatistics.hover_hex_color)

### State Updates

- Slider changes → Settings model updated → Service processes → Image model updated → Statistics recomputed → View updated
- Mouse hover → ImageView detects position → Extract pixel color → Update ImageStatistics.hover_hex_color → Status bar updated
- Mouse leaves image → ImageStatistics.hover_hex_color set to None → Status bar reverts to normal stats
- Save action → ImageSaver service → Convert pixel_data to PIL Image → Save as PNG → User confirmation
- All updates flow through Controller to maintain MVC separation

## Error States

### Invalid Image

- **State**: Image loading failed
- **Attributes**: `error_message: str`
- **Handling**: Display error to user, allow retry

### Processing Error

- **State**: Image processing failed
- **Attributes**: `error_message: str`, `last_valid_state: Image`
- **Handling**: Revert to last valid state, display error, allow retry

## Data Validation Summary

| Entity | Validation Rules | Error Handling |
|--------|-----------------|----------------|
| Image | Dimensions > 0, max 2000x2000, valid array shape | Show error, reject file |
| PixelizationSettings | pixel_size >= 1, within range | Clamp to valid range |
| ColorReductionSettings | sensitivity in valid range | Clamp to valid range |
| ImageStatistics | Computed values match image, HEX format valid | Recompute on image change or mouse move |

