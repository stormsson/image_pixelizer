# Quickstart: Photographic Editing Tools - Image Levels

**Date**: 2025-01-29  
**Feature**: Image Levels Tool

## Overview

The Image Levels tool allows users to adjust the tonal distribution of images by clipping highlights and shadows. This guide demonstrates the basic usage and integration patterns.

## Basic Usage

### Opening the Tool

1. Load an image using "File > Load Image..." (or Ctrl+O)
2. Select "Photographic Editing Tools > Image Levels" from the menu bar
3. A new window opens displaying the image's histogram and two sliders

### Adjusting Levels

1. **Darks Cutoff**: Move slider to the right to replace the darkest percentage of pixels with black
   - Example: Setting to 5% replaces the darkest 5% of pixels with black (0)
   - Effect: Increases contrast in shadows, darkens image

2. **Lights Cutoff**: Move slider to the right to replace the lightest percentage of pixels with white
   - Example: Setting to 10% replaces the lightest 10% of pixels with white (255)
   - Effect: Increases contrast in highlights, brightens image

3. **Combined Effect**: Adjust both sliders simultaneously for maximum contrast
   - Example: Darks 5% + Lights 10% creates a more contrasty image

### Real-time Preview

- As you move sliders, the main image view updates immediately
- The histogram in the tool window updates to reflect the new tonal distribution
- No "Apply" button needed - changes are applied in real-time

### Closing the Tool

- Close the window using standard window controls (X button)
- Adjustments remain applied to the image
- You can reopen the tool to make further adjustments

## Integration Scenarios

### Scenario 1: Basic Levels Adjustment

```python
# User workflow:
# 1. Load image
controller.load_image("path/to/image.jpg")

# 2. Open Levels tool (via menu)
window.show_levels_tool()

# 3. Adjust sliders
# - User moves Darks Cutoff to 5%
# - User moves Lights Cutoff to 10%

# 4. Image updates automatically
# - Controller receives levels_adjusted signal
# - Controller updates ImageModel
# - Main view displays adjusted image

# 5. Close tool window
# - Adjustments remain applied
```

### Scenario 2: Levels After Other Operations

```python
# User workflow with operation chaining:
# 1. Load image
controller.load_image("path/to/image.jpg")

# 2. Apply pixelization
controller.update_pixel_size(8)

# 3. Apply color reduction
controller.update_color_reduction_sensitivity(0.5)

# 4. Open Levels tool
window.show_levels_tool()

# 5. Adjust levels on already-processed image
# - Levels adjustment works on current state (pixelized + color-reduced)
# - Histogram shows distribution of processed image

# 6. All operations chain correctly
# - Undo can revert levels adjustment independently
# - Or revert all operations in sequence
```

### Scenario 3: Multiple Tool Windows

```python
# User can open multiple editing tool windows:
# 1. Open Image Levels tool
window.show_levels_tool()

# 2. (Future) Open another tool (e.g., Curves, Brightness/Contrast)
# window.show_curves_tool()

# 3. Both windows can be open simultaneously
# 4. Each tool operates on the current image state
# 5. Changes from one tool are visible in other tools
```

## Code Examples

### Service Usage

```python
from src.services.levels_adjuster import LevelsAdjuster
from src.models.image_model import ImageModel

# Create service instance
adjuster = LevelsAdjuster()

# Calculate histogram
histogram = adjuster.calculate_histogram(image_model)
# histogram is np.ndarray of shape (256,) with frequency counts

# Apply levels adjustment
# Replace darkest 5% with black, lightest 10% with white
adjusted_image = adjuster.apply_levels(
    image_model,
    darks_cutoff=5.0,
    lights_cutoff=10.0
)
# Returns new ImageModel with adjusted pixel_data
```

### Window Integration

```python
from src.views.levels_window import LevelsWindow
from src.controllers.main_controller import MainController

# Create window (typically done in MainWindow)
levels_window = LevelsWindow(controller)

# Connect signal for image updates
levels_window.levels_adjusted.connect(controller.apply_levels_adjustment)

# Show window
levels_window.show()

# Window handles:
# - Requesting current image from controller
# - Calculating and displaying histogram
# - Applying levels on slider change
# - Emitting signals for controller updates
```

### Controller Integration

```python
# In MainController:

def apply_levels_adjustment(self, adjusted_image: ImageModel) -> None:
    """Apply levels adjustment to current image."""
    if self._image_model is None:
        return
    
    # Update image model
    self._image_model = adjusted_image
    
    # Add to operation history
    self._operation_history.add_operation(
        operation_type="levels_adjustment",
        image_before=self._previous_image_state,
        image_after=adjusted_image,
        parameters={
            "darks_cutoff": darks_value,
            "lights_cutoff": lights_value
        }
    )
    
    # Emit signals
    self.image_updated.emit(adjusted_image)
    self.operation_history_changed.emit()
```

## Testing Examples

### Unit Test: Histogram Calculation

```python
def test_calculate_histogram():
    """Test histogram calculation for test image."""
    adjuster = LevelsAdjuster()
    
    # Create test image (gradient from black to white)
    pixel_data = np.zeros((100, 100, 3), dtype=np.uint8)
    for i in range(100):
        pixel_data[:, i] = [i * 255 // 100] * 3
    
    image = ImageModel(
        width=100, height=100,
        pixel_data=pixel_data,
        original_pixel_data=pixel_data.copy(),
        format="PNG",
        has_alpha=False
    )
    
    histogram = adjuster.calculate_histogram(image)
    
    assert histogram.shape == (256,)
    assert histogram.sum() == 10000  # 100x100 pixels
    assert histogram[0] > 0  # Some black pixels
    assert histogram[255] > 0  # Some white pixels
```

### GUI Test: Slider Adjustment

```python
def test_slider_updates_image(qtbot):
    """Test that slider adjustment updates image."""
    controller = MainController()
    window = LevelsWindow(controller)
    qtbot.addWidget(window)
    
    # Load test image
    # ... setup image ...
    
    # Move darks slider
    qtbot.mouseMove(window.darks_slider, QPoint(50, 10))
    qtbot.mousePress(window.darks_slider, Qt.LeftButton)
    qtbot.mouseMove(window.darks_slider, QPoint(100, 10))  # Move to 50%
    qtbot.mouseRelease(window.darks_slider, Qt.LeftButton)
    
    # Verify signal emitted
    with qtbot.waitSignal(window.levels_adjusted, timeout=1000):
        pass
    
    # Verify image updated
    assert controller.get_current_image() is not None
```

## Common Patterns

### Pattern 1: Histogram Caching

```python
# Cache histogram when image loads or changes
# Recalculate only when:
# - Image changes
# - User explicitly requests refresh
# Don't recalculate on every slider change (use adjusted histogram)
```

### Pattern 2: Real-time Updates

```python
# On slider value change:
# 1. Immediately apply levels adjustment
# 2. Emit signal to controller
# 3. Controller updates image
# 4. Main view updates
# 5. Histogram widget updates (optional - can show adjusted histogram)
```

### Pattern 3: Operation History

```python
# Store levels adjustment in history with:
# - Operation type: "levels_adjustment"
# - Parameters: darks_cutoff, lights_cutoff
# - Image states: before and after
# - Timestamp: for ordering
```

## Troubleshooting

### Issue: Histogram not displaying

**Cause**: Image not loaded or histogram calculation failed  
**Solution**: Check that image is loaded, verify image data is valid

### Issue: Sliders not updating image

**Cause**: Signal/slot connection missing or controller not responding  
**Solution**: Verify `levels_adjusted` signal is connected to controller method

### Issue: Performance lag on slider movement

**Cause**: Recalculating histogram on every slider change  
**Solution**: Cache histogram, only recalculate when image changes

### Issue: Adjustments lost on window close

**Expected**: Adjustments should remain applied  
**Solution**: Verify controller stores adjusted image, window closing doesn't revert changes

## Next Steps

After implementing Image Levels:
- Add more editing tools (Curves, Brightness/Contrast, etc.)
- Consider tool presets (e.g., "High Contrast", "Soft Shadows")
- Add histogram statistics display (mean, median, standard deviation)

