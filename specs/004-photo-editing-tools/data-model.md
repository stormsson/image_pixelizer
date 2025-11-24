# Data Model: Photographic Editing Tools

**Date**: 2025-01-29  
**Feature**: Photographic Editing Tools - Image Levels

## Entities

### LevelsAdjuster

Represents the service class for adjusting image levels (tonal distribution).

**Attributes**:
- None (static methods or instance methods without state)

**Methods**:
- `calculate_histogram(image: ImageModel) -> np.ndarray`: Calculate histogram of tonal distribution
- `apply_levels(image: ImageModel, darks_cutoff: float, lights_cutoff: float) -> ImageModel`: Apply levels adjustment

**State**:
- Stateless service class (similar to `ColorReducer`, `Pixelizer`)

**Validation Rules**:
- `darks_cutoff` must be in range [0.0, 100.0]
- `lights_cutoff` must be in range [0.0, 100.0]
- Image must be valid ImageModel instance
- Histogram calculation requires non-empty image

**State Transitions**:
- N/A (stateless service)

**Relationships**:
- Processes `ImageModel` instances (input and output)
- Uses NumPy for histogram calculation and pixel manipulation

### HistogramData

Represents the calculated histogram data for an image.

**Attributes**:
- `bins: np.ndarray` - Array of 256 integers representing frequency counts for each tone level (0-255)
- `max_frequency: int` - Maximum frequency value (for normalization)
- `total_pixels: int` - Total number of pixels in image

**State**:
- Immutable after calculation

**Validation Rules**:
- `bins` must have length 256
- All values in `bins` must be >= 0
- `max_frequency` must be >= 0
- `total_pixels` must equal sum of `bins`

**State Transitions**:
- Calculated once from image → remains constant until image changes

**Relationships**:
- Derived from `ImageModel.pixel_data`
- Used by `HistogramWidget` for visualization

### LevelsAdjustmentParameters

Represents the current state of levels adjustment.

**Attributes**:
- `darks_cutoff: float` - Percentage of darkest pixels to replace (0.0-100.0)
- `lights_cutoff: float` - Percentage of lightest pixels to replace (0.0-100.0)
- `darks_threshold: int` - Calculated tone level threshold for darks (0-255)
- `lights_threshold: int` - Calculated tone level threshold for lights (0-255)

**State**:
- Updated when sliders change
- Used to apply levels adjustment to image

**Validation Rules**:
- `darks_cutoff` and `lights_cutoff` must be in range [0.0, 100.0]
- `darks_threshold` and `lights_threshold` must be in range [0, 255]
- `darks_threshold` should be <= `lights_threshold` (logically, darks are darker than lights)

**State Transitions**:
- Initial: `darks_cutoff=0.0, lights_cutoff=0.0` (no adjustment)
- Slider change → parameters update → thresholds recalculated → image adjusted

**Relationships**:
- Used by `LevelsAdjuster.apply_levels()` to transform image
- Stored in operation history for undo/redo

### LevelsWindow

Represents the tool window for Image Levels adjustment.

**Attributes**:
- `controller: MainController` - Reference to main controller
- `histogram_widget: HistogramWidget` - Widget displaying histogram
- `darks_slider: QSlider` - Slider for darks cutoff (0-100)
- `lights_slider: QSlider` - Slider for lights cutoff (0-100)
- `current_image: Optional[ImageModel]` - Reference to current image being edited
- `histogram_data: Optional[HistogramData]` - Cached histogram data

**State**:
- `Open` - Window is visible and active
- `Closed` - Window is closed (adjustments remain applied)

**Validation Rules**:
- Window can only be opened when image is loaded
- Sliders must be in range [0, 100]
- Histogram data must be calculated before display

**State Transitions**:
- `Closed` → `Open` (when menu item selected and image loaded)
- `Open` → `Closed` (when window closed, adjustments remain applied)

**Relationships**:
- Communicates with `MainController` via signals/slots
- Displays data from `HistogramData`
- Updates `ImageModel` via controller

### HistogramWidget

Represents the custom widget for displaying histogram visualization.

**Attributes**:
- `histogram_data: Optional[HistogramData]` - Data to display
- `normalized_bins: np.ndarray` - Normalized frequencies (0.0-1.0) for drawing

**State**:
- `Empty` - No data to display
- `Displaying` - Showing histogram bars

**Validation Rules**:
- `histogram_data` must be valid before drawing
- `normalized_bins` must have length 256

**State Transitions**:
- `Empty` → `Displaying` (when histogram_data set)
- `Displaying` → `Displaying` (when data updates)

**Relationships**:
- Displays `HistogramData`
- Part of `LevelsWindow` UI

## Data Flow

### Levels Adjustment Flow

1. User selects "Image Levels" from menu
2. `MainWindow` creates `LevelsWindow` instance
3. `LevelsWindow` requests current image from controller
4. `LevelsWindow` calls `LevelsAdjuster.calculate_histogram()` to get histogram data
5. `HistogramWidget` displays histogram bars
6. User adjusts sliders
7. `LevelsWindow` calls `LevelsAdjuster.apply_levels()` with current slider values
8. `LevelsAdjuster` calculates percentile thresholds from histogram
9. `LevelsAdjuster` applies pixel mapping (darks → 0, lights → 255)
10. `LevelsAdjuster` returns new `ImageModel` with adjusted pixel data
11. `LevelsWindow` emits signal to controller to update image
12. Controller updates `ImageModel` and emits `image_updated` signal
13. Main image view updates to show adjusted result
14. Controller adds operation to history

### Histogram Calculation Flow

1. `LevelsWindow` receives image from controller
2. Convert RGB/RGBA to grayscale (luminance calculation)
3. `LevelsAdjuster.calculate_histogram()` uses `np.histogram()` with 256 bins
4. Create `HistogramData` with bins, max_frequency, total_pixels
5. Normalize bins for display (divide by max_frequency)
6. `HistogramWidget` receives normalized data
7. `HistogramWidget.paintEvent()` draws bars proportional to normalized frequencies

### Real-time Update Flow

1. User moves slider (darks or lights)
2. `LevelsWindow` receives slider value change signal
3. `LevelsWindow` immediately calls `LevelsAdjuster.apply_levels()` with new values
4. `LevelsAdjuster` applies adjustment and returns new `ImageModel`
5. `LevelsWindow` emits signal to controller
6. Controller updates image and emits `image_updated`
7. Main view updates
8. `LevelsWindow` recalculates histogram from adjusted image
9. `HistogramWidget` updates display

## State Management

### Service State

The `LevelsAdjuster` maintains no state (stateless service class).

### Window State

The `LevelsWindow` maintains:
- Current image reference (updated when main image changes)
- Cached histogram data (recalculated when image changes)
- Current slider values (updated on user interaction)

### Application State

The application maintains (existing + new):
- One `ImageModel` instance (current loaded image)
- One `LevelsWindow` instance (when tool is open)
- Operation history (tracks levels adjustments with parameters)

### State Updates

- Menu click → Window opens → Histogram calculated → Display shown
- Slider change → Levels applied → Image updated → Histogram updated
- Window close → Adjustments remain → Image state preserved
- Undo operation → Previous image state restored → Histogram recalculated if window open

## Error States

### No Image Loaded

- **State**: No image available for levels adjustment
- **Handling**: Menu item disabled or window shows message

### Invalid Slider Values

- **State**: Slider value out of range [0, 100]
- **Handling**: Slider widget enforces range, validation in service method

### Histogram Calculation Error

- **State**: Failed to calculate histogram (empty image, invalid data)
- **Handling**: Display error message, disable sliders

### Levels Application Error

- **State**: Failed to apply levels adjustment (invalid parameters, memory error)
- **Handling**: Display error message, restore previous image state

## Data Validation Summary

| Entity | Validation Rules | Error Handling |
|--------|-----------------|----------------|
| LevelsAdjuster | Slider values in [0.0, 100.0], valid ImageModel | Raise ValueError with specific issue |
| HistogramData | 256 bins, non-negative values, sum equals total_pixels | Validate in calculation method |
| LevelsAdjustmentParameters | Cutoff values in range, thresholds in [0, 255] | Validate in service method |
| LevelsWindow | Image loaded before opening, valid histogram data | Disable/enable UI elements, show messages |
| HistogramWidget | Valid histogram_data before drawing | Check for None, show empty state |

