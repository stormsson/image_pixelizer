# Research: Photographic Editing Tools

**Date**: 2025-01-29  
**Feature**: Photographic Editing Tools - Image Levels

## Research Tasks

### 1. Histogram Calculation for Image Tonal Distribution

**Decision**: Use NumPy for efficient histogram calculation on luminance values.

**Rationale**: 
- NumPy provides `np.histogram()` which is optimized for performance
- For color images, calculate histogram on luminance (grayscale conversion) to show overall tonal distribution
- For grayscale images, use the single channel directly
- Luminance formula: `0.299*R + 0.587*G + 0.114*B` (standard ITU-R BT.601)

**Alternatives considered**:
- Manual pixel iteration: Too slow for large images
- PIL Image.histogram(): Less flexible, returns flattened array
- OpenCV: Adds unnecessary dependency

**Implementation approach**:
- Convert RGB/RGBA to grayscale for histogram calculation
- Use `np.histogram()` with 256 bins (one per tone level 0-255)
- Normalize frequencies for display (max frequency = 100% height)

### 2. Levels Adjustment Algorithm

**Decision**: Implement levels adjustment by mapping pixel values based on cutoff percentages.

**Rationale**:
- Darks cutoff: Replace darkest N% of pixels with black (0)
- Lights cutoff: Replace lightest N% of pixels with white (255)
- Calculate percentile thresholds from histogram data
- Apply mapping to all channels (RGB) while preserving alpha channel

**Alternatives considered**:
- Linear mapping with input/output points: More complex, not required by spec
- Curve-based adjustment: Overkill for simple cutoff operation
- Per-channel independent adjustment: Spec indicates luminance-based operation

**Implementation approach**:
1. Calculate histogram on luminance values
2. Find percentile thresholds (e.g., 5th percentile for darks, 95th percentile for lights)
3. Create mapping: values <= darks_threshold → 0, values >= lights_threshold → 255
4. Apply mapping to RGB channels, preserve alpha

### 3. Real-time Updates and Performance

**Decision**: Use direct pixel manipulation with NumPy vectorized operations, update on slider value change.

**Rationale**:
- NumPy vectorized operations are fast enough for real-time updates
- No need for threading for typical images (2000x2000px max)
- Update both histogram and image view synchronously on slider change
- Cache histogram calculation result, only recalculate when image changes

**Alternatives considered**:
- Background thread for processing: Unnecessary overhead for simple operations
- Debouncing slider updates: Would introduce lag, spec requires real-time
- Preview mode with Apply button: Spec explicitly requires real-time updates

**Implementation approach**:
- Calculate histogram once when window opens or image changes
- On slider change: apply levels adjustment to image, update histogram display
- Use NumPy boolean indexing for efficient pixel replacement
- Emit signal to controller to update main image view

### 4. Window Management and Menu Integration

**Decision**: Use QMainWindow for tool window, add menu item to existing menu bar.

**Rationale**:
- QMainWindow provides standard window behavior (minimize, close, etc.)
- Follows existing pattern (MainWindow is QMainWindow)
- Menu integration follows existing File menu pattern
- Multiple windows can be open simultaneously (QMainWindow instances are independent)

**Alternatives considered**:
- QDialog: Modal behavior not desired, users should be able to interact with main window
- QWidget as floating panel: Less standard window behavior
- Tab-based interface: Not required by spec, separate windows are clearer

**Implementation approach**:
- Create `LevelsWindow(QMainWindow)` class
- Add "Photographic Editing Tools" menu to menu bar with "Image Levels" submenu item
- Store window reference in MainWindow to prevent duplicate windows (optional enhancement)
- Window closes → adjustments remain applied (no Cancel/Apply buttons needed per spec)

### 5. Integration with Operation History

**Decision**: Track levels adjustment as a separate operation in existing operation history.

**Rationale**:
- Follows existing pattern (background removal, etc. are tracked)
- Allows undo/redo of levels adjustments
- Maintains consistency with other image operations

**Implementation approach**:
- Controller method `apply_levels_adjustment()` creates new ImageModel with adjusted pixel data
- Add operation to `OperationHistory` with type "levels_adjustment"
- Store parameters (lights_cutoff, darks_cutoff) for potential reapplication
- Emit `image_updated` signal to update views

### 6. Histogram Visualization

**Decision**: Use QWidget with custom paintEvent to draw histogram bars.

**Rationale**:
- QPainter provides efficient drawing API
- Custom widget allows full control over appearance
- Can update in real-time without flicker
- Follows Qt best practices for custom graphics

**Alternatives considered**:
- QChart/QtCharts: Adds dependency, overkill for simple bar chart
- Matplotlib: Heavy dependency, not suitable for real-time updates
- Third-party histogram widget: Unnecessary dependency

**Implementation approach**:
- Create `HistogramWidget(QWidget)` class
- Override `paintEvent()` to draw bars
- Calculate bar heights from normalized histogram data
- Update widget when histogram data changes (call `update()`)

## Technical Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Histogram calculation | NumPy on luminance | Fast, efficient, no new dependencies |
| Levels algorithm | Percentile-based cutoff | Matches spec requirements, simple and effective |
| Real-time updates | Synchronous NumPy operations | Fast enough, no threading complexity |
| Window type | QMainWindow | Standard window behavior, follows existing patterns |
| Histogram display | Custom QWidget with QPainter | Full control, efficient, no extra dependencies |
| Operation tracking | Existing OperationHistory | Consistency with other operations |

## Dependencies

No new dependencies required. Uses existing:
- PySide6 (QMainWindow, QWidget, QPainter, QSlider, QVBoxLayout, etc.)
- NumPy (histogram calculation, array operations)
- Pillow (already used, but not directly needed for this feature)

## Performance Considerations

- Histogram calculation: O(n) where n = width * height, acceptable for 2000x2000px images
- Levels adjustment: O(n) pixel operations using NumPy vectorization, very fast
- Real-time updates: Slider changes trigger immediate recalculation, should be <100ms for typical images
- Memory: Minimal overhead, histogram is 256 integers, levels adjustment creates new ImageModel

## Open Questions

None - all technical decisions made based on spec requirements and existing codebase patterns.

