# Research: Image Operations Feature

**Feature**: Image Operations in Controls Panel  
**Date**: 2025-01-27  
**Phase**: 0 - Research & Technology Selection

## Background Removal Technology

### Decision: Use rembg Library

**Rationale**: 
- rembg is a Python library that provides AI-powered background removal using pre-trained deep learning models
- It's well-maintained, actively developed, and has good documentation
- Provides simple API: `remove(input_image)` returns image with transparent background
- Supports both PIL Image and NumPy array inputs, compatible with existing codebase
- Handles model downloading automatically on first use
- Good performance for images up to 2000x2000px (meets spec requirement of <5 seconds)
- Works offline after initial model download

**Alternatives Considered**:
1. **OpenCV-based color segmentation**: 
   - Pros: No external dependencies, fast
   - Cons: Less accurate, requires manual tuning, doesn't work well with complex backgrounds
   - Rejected: Doesn't meet spec requirement of 90% success rate for typical use cases

2. **Manual masking/selection tools**:
   - Pros: User control, precise
   - Cons: More complex UI, requires user interaction
   - Status: Now required - spec updated to require interactive point selection for background removal

3. **Other AI libraries (remove.bg API, backgroundremover)**:
   - Pros: Similar functionality
   - Cons: remove.bg requires API key and internet connection, backgroundremover less mature
   - Rejected: rembg is more suitable for offline desktop application

**Implementation Approach**:
- Install rembg with SAM support: `pip install rembg onnxruntime`
- Use `rembg.new_session('sam')` to create SAM session for interactive point selection
- Use `rembg.remove()` function with PIL Image input and SAM prompts (point coordinates)
- Convert user clicks to SAM prompt format: `[{"type": "point", "data": [x, y], "label": 1}]` for keep, `label: 0` for remove
- Convert result to NumPy array for integration with existing ImageModel
- Handle model download on first use (may require internet connection initially)
- Use QThread for background processing to maintain UI responsiveness
- Capture click coordinates in image pixel space (accounting for view scaling/positioning)

**Performance Considerations**:
- First run: Model download (~100MB) may take time, but only happens once
- Processing time: ~2-4 seconds for 2000x2000px images on typical hardware
- Memory: Model loaded in memory (~100MB), acceptable for desktop application
- Threading: Use QThread to prevent UI blocking during processing

**Error Handling**:
- Handle rembg import errors (dependency not installed)
- Handle model download failures (network issues)
- Handle processing errors (invalid image, memory issues)
- Provide user-friendly error messages

## Operation History Management

### Decision: In-Memory History with Fixed Limit

**Rationale**:
- Spec requires maximum 20 operations in undo history
- In-memory storage is sufficient for desktop application (no persistence needed)
- Fixed limit prevents unbounded memory growth
- Rolling history (oldest removed when limit reached) is simple to implement

**Implementation Approach**:
- Use Python list or deque to store operation history
- Each entry contains: operation type, image state snapshot (ImageModel)
- Maximum 20 entries, remove oldest when adding 21st
- Clear history when new image is loaded
- Only track complex button-based operations (not slider changes)

**Memory Considerations**:
- Each image state snapshot: ~12MB for 2000x2000px RGBA image (worst case)
- 20 operations: ~240MB maximum memory usage
- Acceptable for desktop application
- Can optimize by storing only pixel_data differences if needed (future optimization)

**Data Structure**:
```python
@dataclass
class OperationHistoryEntry:
    operation_type: str  # e.g., "remove_background"
    image_state: ImageModel  # Snapshot before operation
    timestamp: float  # Optional, for debugging

@dataclass
class PointSelection:
    x: int  # X coordinate in image pixel space
    y: int  # Y coordinate in image pixel space
    label: str  # "keep" or "remove"
```

## Integration with Existing Codebase

### Decision: Extend Existing Architecture

**Rationale**:
- Existing MVC architecture is well-established
- New services follow existing patterns (ImageLoader, Pixelizer, ColorReducer)
- Controller already handles signal/slot coordination
- Views already have button management (Save button pattern)

**Integration Points**:
1. **BackgroundRemover Service**: 
   - Similar to existing services (Pixelizer, ColorReducer)
   - Takes ImageModel and point prompts, returns ImageModel
   - Uses SAM model with `new_session('sam')` for point-based removal
   - Converts PointSelection list to SAM prompt format
   - Can be tested independently

2. **OperationHistoryManager**:
   - New service class for managing undo history
   - Controller uses it to track operations
   - Separate from image processing logic

3. **PointSelection Model**:
   - New dataclass for point selection data
   - Stores coordinates and labels (keep/remove)
   - Managed by controller during point selection mode

4. **Controller Extensions**:
   - Add `enter_point_selection_mode()` method
   - Add `add_point(x, y, label)` method
   - Add `clear_points()` method
   - Add `apply_background_removal()` method (processes with selected points)
   - Add `cancel_point_selection()` method
   - Add `undo_operation()` method
   - Emit signals for UI updates (image_updated, operation_history_changed, point_selection_changed)

5. **ControlsPanel Extensions**:
   - Add "Remove Background" button (triggers point selection mode)
   - Add "Apply" button (processes with selected points)
   - Add "Cancel" button (exits point selection mode)
   - Add "Undo" button
   - Button visibility/enabled state management based on point selection mode
   - Signal emissions for button clicks

6. **ImageView Extensions**:
   - Add click event handling (left-click = keep, right-click = remove)
   - Add visual marker rendering (green circles for keep, red circles for remove)
   - Coordinate conversion from view space to image pixel space
   - Point selection mode state management

**Slider Interaction**:
- Slider changes (pixelization/color reduction) are NOT tracked in undo history
- When undo restores image, current slider values are preserved
- Slider changes are applied to the restored image state
- This requires controller to reapply slider-based processing after undo

**Point Selection Interaction**:
- Point selection mode is entered when "Remove Background" is clicked
- Points are collected during point selection mode (not applied until "Apply" is clicked)
- Point selection state is cleared when "Cancel" is clicked or after "Apply" completes
- Point coordinates must be converted from view coordinates (accounting for scaling/positioning) to image pixel coordinates
- Visual markers are rendered on top of the image during point selection mode

## Threading Strategy

### Decision: Use QThread for Background Removal

**Rationale**:
- rembg processing can take 2-4 seconds for large images
- UI must remain responsive (spec requirement)
- QThread is standard Qt pattern for background processing
- Existing codebase may use threading for heavy operations (per plan.md)

**Implementation Approach**:
- Create BackgroundRemovalWorker (QObject) for processing
- Move worker to QThread
- Emit progress/complete signals
- Controller connects signals to update UI
- Handle cancellation if needed (future enhancement)

**Alternative Considered**:
- Synchronous processing with progress indicator
- Rejected: Doesn't meet spec requirement of UI responsiveness

## Error Handling Strategy

### Decision: Service-Level Error Handling with User Messages

**Rationale**:
- Follows existing pattern (ImageLoader, ImageSaver error handling)
- Service layer catches technical errors
- Controller converts to user-friendly messages
- UI displays error dialogs

**Error Scenarios**:
1. rembg not installed: Clear message with installation instructions
2. Model download failure: Network error message, suggest retry
3. Processing failure: Generic error with retry option
4. Memory issues: Clear message about image size limits
5. Invalid image state: Internal error, log for debugging

## Testing Strategy

### Decision: Comprehensive Test Coverage

**Rationale**:
- Follows constitution requirement: 80% business logic, 60% UI
- Existing test patterns established
- New services must be fully testable

**Test Approach**:
1. **Unit Tests**:
   - BackgroundRemover: Test rembg integration with SAM prompts, error handling, prompt format conversion
   - OperationHistoryManager: Test history management, limit enforcement
   - PointSelection: Test coordinate validation, label validation
   - Mock rembg for faster tests

2. **Integration Tests**:
   - End-to-end: Load image → Enter point selection → Click points → Apply → Verify result
   - Point selection workflow: Enter mode → Add points → Cancel → Verify points cleared
   - Undo workflow: Apply operation → Undo → Verify restoration
   - Slider interaction: Apply sliders → Remove background → Undo → Verify sliders preserved
   - Coordinate conversion: Test view coordinates to image pixel coordinates conversion

3. **GUI Tests** (pytest-qt):
   - Button visibility/enabled states (Remove Background, Apply, Cancel, Undo)
   - Button click signals
   - Point selection mode entry/exit
   - Click event handling (left-click vs right-click)
   - Visual marker rendering (green/red markers)
   - UI updates after operations

## Dependencies

### New Dependencies

- **rembg**: AI background removal library with SAM support
  - Version: Latest stable (>=2.0.68)
  - Installation: `pip install rembg`
  - License: MIT (compatible)
  - Size: ~100MB for default model, ~1-2GB for SAM model (model download on first use)
  - SAM model: Required for interactive point selection, automatically downloaded on first use

- **onnxruntime**: Required by rembg for SAM model inference
  - Version: >=1.15.0
  - Installation: `pip install onnxruntime`
  - License: MIT (compatible)

### Existing Dependencies (No Changes)

- PySide6: GUI framework
- Pillow: Image processing
- NumPy: Array operations
- pytest: Testing framework
- pytest-qt: GUI testing

## Performance Targets

Based on research and spec requirements:

- **Point Selection**: Immediate response to clicks (<100ms) ✅
- **Visual Marker Rendering**: Immediate display of markers after click ✅
- **Background Removal**: <5 seconds for 2000x2000px images after "Apply" clicked ✅
- **Undo Operation**: <1 second (in-memory restoration) ✅
- **UI Responsiveness**: No freezing during background removal ✅
- **Memory Usage**: ~240MB maximum for operation history (20 operations × 12MB), ~few KB for point selection ✅

## Open Questions Resolved

1. **Q: Which AI model/library for background removal?**
   - A: rembg with SAM model (user specified for interactive point selection)

2. **Q: How to handle model download?**
   - A: Automatic on first use, handled by rembg library. SAM model (~1-2GB) downloaded when first used.

3. **Q: Threading approach?**
   - A: QThread for background processing to maintain UI responsiveness. Point selection is synchronous (immediate).

4. **Q: Operation history storage?**
   - A: In-memory with fixed 20-operation limit, rolling history

5. **Q: Integration with existing sliders?**
   - A: Undo preserves slider states, reapplies slider processing after restoration

6. **Q: How to handle interactive point selection?**
   - A: Left-click for keep (foreground), right-click for remove (background). Visual markers (green/red) provide feedback. Apply button confirms, Cancel button exits mode.

7. **Q: How to convert view coordinates to image coordinates?**
   - A: ImageView must track scaling/positioning and convert click coordinates from view space to image pixel space before creating PointSelection.

## Next Steps

1. Create data-model.md with OperationHistoryEntry entity
2. Create contracts for BackgroundRemover and OperationHistoryManager services
3. Design quickstart.md workflow for new operations
4. Proceed to task breakdown

