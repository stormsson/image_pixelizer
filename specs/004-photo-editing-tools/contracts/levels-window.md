# Contract: LevelsWindow UI Component

**Component**: `src/views/levels_window.py`  
**Class**: `LevelsWindow`  
**Date**: 2025-01-29

## Purpose

Separate window for Image Levels tool, displaying histogram and providing sliders for adjusting tonal distribution. Communicates with MainController via signals/slots to update the main image view in real-time.

## Public API

### `__init__(controller: MainController, parent: Optional[QWidget] = None) -> None`

Initialize Levels tool window.

**Parameters**:
- `controller: MainController` - Main controller instance for image access and updates
- `parent: Optional[QWidget]` - Parent widget (optional)

**Behavior**:
- Creates QMainWindow with title "Image Levels"
- Sets up UI: histogram widget, two sliders, labels
- Connects signals/slots for controller communication
- Requests current image from controller
- Calculates and displays histogram if image is loaded
- Disables sliders if no image is loaded

### Signals

- `levels_adjusted(ImageModel)` - Emitted when levels adjustment is applied. Carries new ImageModel with adjusted pixel data.

### Slots

- `on_image_updated(ImageModel)` - Called when main image is updated. Recalculates histogram and updates display.

## UI Components

### HistogramWidget

Custom widget displaying histogram as vertical bars.

**Attributes**:
- `histogram_data: Optional[np.ndarray]` - Histogram data (256 integers)

**Methods**:
- `set_histogram_data(data: np.ndarray) -> None` - Update histogram data and trigger repaint
- `paintEvent(event: QPaintEvent) -> None` - Draw histogram bars

**Visual**:
- Dark tones on left (tone level 0), light tones on right (tone level 255)
- Vertical bars proportional to frequency
- Normalized height (max frequency = 100% of widget height)

### Sliders

Two QSlider widgets:

1. **Darks Cutoff Slider**:
   - Range: 0-100
   - Label: "Darks Cutoff"
   - Value: Percentage of darkest pixels to replace with black
   - Default: 0

2. **Lights Cutoff Slider**:
   - Range: 0-100
   - Label: "Lights Cutoff"
   - Value: Percentage of lightest pixels to replace with white
   - Default: 0

**Behavior**:
- Value change signal triggers immediate levels adjustment
- Slider value displayed as percentage (e.g., "5%")
- Both sliders can be adjusted independently

## Window Behavior

### Opening

- Menu item "Image Levels" triggers window creation
- Window opens only if image is loaded (menu item disabled otherwise)
- Window is non-modal (user can interact with main window)
- Multiple tool windows can be open simultaneously

### Closing

- Window can be closed via standard window controls
- Closing window does NOT revert adjustments (adjustments remain applied)
- No Cancel/Apply buttons (per spec, real-time updates)

### Real-time Updates

- Slider change → immediate levels adjustment → image updated → histogram updated
- Main image view updates synchronously
- Histogram widget updates to show adjusted distribution

## Integration with Controller

### Requesting Image

```python
# Window requests current image
current_image = controller.get_current_image()
if current_image:
    self._update_histogram(current_image)
```

### Applying Adjustment

```python
# Window applies levels and emits signal
adjusted_image = levels_adjuster.apply_levels(image, darks, lights)
self.levels_adjusted.emit(adjusted_image)
```

### Receiving Updates

```python
# Controller connects to window signal
window.levels_adjusted.connect(controller.apply_levels_adjustment)
```

## Testing Requirements

### GUI Tests (pytest-qt)

- `test_window_opens_on_menu_action`: Window opens when menu item selected
- `test_window_disabled_when_no_image`: Menu item disabled when no image loaded
- `test_histogram_displays_correctly`: Histogram shows correct distribution
- `test_sliders_exist`: Both sliders present with correct ranges
- `test_darks_slider_updates_image`: Adjusting darks slider updates image
- `test_lights_slider_updates_image`: Adjusting lights slider updates image
- `test_both_sliders_work_together`: Both sliders can be adjusted simultaneously
- `test_histogram_updates_on_slider_change`: Histogram updates when sliders change
- `test_window_closes_preserves_adjustments`: Closing window keeps adjustments
- `test_window_updates_on_image_change`: Window updates when main image changes

### Integration Tests

- `test_levels_window_integration`: Complete workflow from menu click to image update
- `test_multiple_windows`: Multiple tool windows can be open simultaneously

## Error Handling

- **No image loaded**: Disable sliders, show message "No image loaded"
- **Histogram calculation error**: Show error message, disable sliders
- **Levels adjustment error**: Show error message, restore previous slider values

## Performance Requirements

- Window opens within 1 second (per spec SC-001)
- Histogram calculation and display within 2 seconds (per spec SC-002)
- Slider updates image within 100ms (per spec SC-003)
- UI remains responsive during processing

## Dependencies

- `PySide6.QtWidgets` - QMainWindow, QWidget, QSlider, QVBoxLayout, QLabel
- `PySide6.QtCore` - Signal, Slot
- `PySide6.QtGui` - QPainter, QPaintEvent
- `src.controllers.main_controller` - MainController
- `src.services.levels_adjuster` - LevelsAdjuster
- `src.models.image_model` - ImageModel

## Notes

- Window follows same pattern as MainWindow (QMainWindow subclass)
- HistogramWidget is custom widget with paintEvent override
- Real-time updates require efficient histogram recalculation (cache when possible)
- Window should track current image reference to detect when main image changes
- Consider preventing duplicate windows (store reference in MainWindow)

