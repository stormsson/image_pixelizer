# Research: Image Pixelizer Application

**Date**: 2025-01-27  
**Feature**: Image Pixelizer Application  
**Purpose**: Research technical decisions for PySide6 GUI application with image processing

## Technology Stack Decisions

### GUI Framework: PySide6

**Decision**: Use PySide6 (Qt6 Python bindings) as the GUI framework.

**Rationale**:
- PySide6 is the official Qt6 Python binding, providing native cross-platform GUI capabilities
- Qt6 offers excellent layout management, signal/slot mechanism for MVC architecture
- Strong widget testing support via pytest-qt
- Active development and community support
- Matches constitution requirement for established GUI frameworks
- Better performance and modern features compared to tkinter
- Native look and feel on all platforms

**Alternatives considered**:
- **tkinter**: Built-in Python library, but limited widget set and less modern
- **PyQt6**: Similar to PySide6 but different licensing (GPL vs LGPL)
- **wxPython**: Good cross-platform support but less active development
- **CustomTkinter**: Modern tkinter wrapper, but still limited compared to Qt

**Implementation notes**:
- Use QMainWindow for main window structure
- QHBoxLayout for sidebar + main content layout
- QLabel with QPixmap for image display (scaled appropriately)
- QSlider for pixel size and sensitivity controls
- QStatusBar for bottom status information
- QFileDialog for image file selection
- QThread for background image processing to maintain UI responsiveness

### Image Processing: Pillow (PIL) + NumPy

**Decision**: Use Pillow for image I/O and NumPy for efficient pixel manipulation.

**Rationale**:
- Pillow is the standard Python image library, excellent format support (JPEG, PNG, GIF, BMP)
- NumPy provides efficient array operations for pixel manipulation
- Both libraries are well-maintained, performant, and widely used
- NumPy arrays integrate well with Pillow Image objects
- Enables vectorized operations for fast pixelization and color reduction

**Alternatives considered**:
- **OpenCV**: Powerful but overkill for this use case, larger dependency
- **scikit-image**: Good for advanced image processing, but adds unnecessary complexity
- **Pure Python**: Too slow for real-time image processing

**Implementation notes**:
- Load images with `PIL.Image.open()`
- Convert to NumPy array: `np.array(image)`
- Process pixel data efficiently with NumPy operations
- Convert back to PIL Image: `Image.fromarray()`
- Convert to QPixmap for display: `QPixmap.fromImage()`

### Pixelization Algorithm

**Decision**: Use block averaging algorithm for pixelization.

**Rationale**:
- Simple, fast, and produces clear pixelization effect
- Divides image into blocks of size NxN, averages colors within each block
- Efficiently implementable with NumPy array slicing and mean operations
- Real-time performance achievable for images up to 2000x2000px

**Algorithm**:
1. Divide image into blocks of size `pixel_size x pixel_size`
2. For each block, calculate average RGB values
3. Replace all pixels in block with average color
4. Handle edge cases where image dimensions aren't divisible by block size

**Implementation approach**:
- Use NumPy's `reshape()` and `mean()` for efficient block processing
- Process in chunks to maintain responsiveness for large images
- Cache processed results when possible

### Color Reduction Algorithm

**Decision**: Use color quantization with adjustable sensitivity threshold.

**Rationale**:
- Color quantization reduces distinct colors by grouping similar colors
- Sensitivity parameter controls how "similar" colors must be to merge
- Can use color distance metrics (Euclidean distance in RGB space)
- Efficiently implementable with NumPy operations

**Algorithm options considered**:
1. **Simple threshold-based**: Merge colors within threshold distance
   - Pros: Simple, fast, predictable
   - Cons: May not produce optimal palette
   - **Selected**: Best for real-time performance and user control

2. **K-means clustering**: Find optimal color palette
   - Pros: Produces optimal color distribution
   - Cons: Slower, less predictable for user, requires iteration

3. **Median cut**: Divide color space recursively
   - Pros: Good balance of quality and speed
   - Cons: More complex, less direct user control

**Implementation approach**:
- Calculate color distance between pixels using Euclidean distance in RGB space
- Group pixels with distance < sensitivity threshold
- Replace grouped pixels with average color
- Use NumPy broadcasting for efficient distance calculations
- Process in batches to maintain UI responsiveness

### Threading Strategy

**Decision**: Use QThread for background image processing to maintain UI responsiveness.

**Rationale**:
- Image processing (especially for large images) can block UI thread
- Qt's QThread integrates seamlessly with PySide6 signal/slot mechanism
- Allows progress updates and cancellation
- Maintains responsive UI during processing

**Implementation approach**:
- Create ImageProcessingThread subclass of QThread
- Emit progress signals during processing
- Update UI via signals when processing completes
- Allow cancellation if user changes slider rapidly

### Image Size Constraints

**Decision**: Enforce 2000x2000px maximum image size (per spec edge case).

**Rationale**:
- Prevents memory issues and performance degradation
- Ensures real-time processing performance goals are met
- Clear user feedback on limitations

**Implementation**:
- Validate image dimensions after loading
- Display error message if image exceeds limit
- Suggest resizing to user if needed

## Architecture Patterns

### MVC Architecture

**Decision**: Implement Model-View-Controller pattern as required by constitution.

**Model Layer**:
- `ImageModel`: Holds image data, dimensions, pixel array
- `SettingsModel`: Holds pixel size and sensitivity values

**View Layer**:
- PySide6 widgets (MainWindow, ImageView, ControlsPanel, StatusBar)
- No business logic, only UI presentation

**Controller Layer**:
- `MainController`: Coordinates between models, services, and views
- Connects signals/slots between components
- Handles user actions and updates models/views

**Service Layer** (business logic):
- `ImageLoader`: File loading and validation
- `Pixelizer`: Pixelization algorithm
- `ColorReducer`: Color reduction algorithm

This separation enables:
- Independent testing of each layer
- Easy replacement of UI framework if needed
- Clear boundaries between concerns

## Performance Considerations

### Real-time Processing

**Challenge**: Update image in real-time as sliders move (500ms-1s target).

**Solution**:
- Use efficient NumPy operations (vectorized, not loops)
- Process in background thread to avoid UI blocking
- Debounce slider updates (wait for slider to settle before processing)
- Cache intermediate results when possible
- Scale down preview for very large images, process full resolution on final render

### Memory Management

**Challenge**: Large images consume significant memory.

**Solution**:
- Process images in chunks when possible
- Release intermediate arrays promptly
- Use NumPy's memory-efficient operations
- Enforce size limits (2000x2000px)

## Testing Strategy

### Testing Framework: pytest + pytest-qt

**Decision**: Use pytest for unit and integration tests, pytest-qt for GUI component testing.

**Rationale**:
- pytest is the standard Python testing framework with excellent fixtures and plugin ecosystem
- pytest-qt provides Qt event loop integration for testing PySide6 widgets
- Both frameworks support coverage reporting and CI/CD integration
- Aligns with constitution requirement for testability

**Coverage Targets**:
- Business logic (models, services): 80% minimum coverage
- UI components: 60% minimum coverage
- All tests must pass before merge to main branch

### Unit Tests

**Scope**: Test each meaningful entity and service independently.

- **Models**: ImageModel, SettingsModel, ImageStatistics
  - Test data validation (dimensions, formats, ranges)
  - Test state transitions
  - Test helper functions (rgb_to_hex)
  - Test edge cases (invalid inputs, boundary values)

- **Services**: ImageLoader, Pixelizer, ColorReducer, ImageSaver
  - ImageLoader: file validation, format checking, size limits, error handling
  - Pixelizer: algorithm correctness, edge cases (pixel_size=1, large blocks)
  - ColorReducer: color quantization accuracy, sensitivity ranges, distinct color counting
  - ImageSaver: PNG saving, alpha channel preservation, error handling

**Test Organization**: One test file per entity/service in `tests/unit/`

### Integration Tests

**Scope**: Test interactions between components and end-to-end workflows.

- End-to-end image processing pipeline (load → pixelize → reduce colors → save)
- Model-service integration (ImageModel with ImageLoader, Pixelizer, ColorReducer)
- Controller coordination (signal/slot connections, error propagation)
- Error handling across layers (service errors → controller → view)

**Test Organization**: Workflow tests in `tests/integration/`

### GUI Tests (pytest-qt)

**Scope**: Test PySide6 widgets and user interactions.

- **MainWindow**: Menu actions, file dialogs, error message display
- **ImageView**: Image display, scaling, aspect ratio preservation, mouse hover events
- **StatusBar**: Statistics display, HEX color display, updates on state changes
- **ControlsPanel**: Slider interactions, signal emissions, value ranges

**Test Approach**:
- Use `qtbot` fixture from pytest-qt for widget testing
- Test signal/slot connections
- Test UI updates in response to model changes
- Test user interactions (clicks, slider movements, mouse hover)
- Test error message display

**Test Organization**: One test file per widget in `tests/gui/`

### Test Coverage Tools

**Decision**: Use pytest-cov for coverage reporting.

**Rationale**:
- Integrates seamlessly with pytest
- Provides detailed coverage reports
- Supports coverage thresholds
- Can be integrated into CI/CD pipelines

**Usage**:
```bash
pytest --cov=src --cov-report=html --cov-report=term
```

### Test Execution

- **Local Development**: `pytest` (runs all tests)
- **CI/CD**: `pytest --cov=src --cov-fail-under=80` (fails if coverage below threshold)
- **Specific Categories**: `pytest tests/unit/`, `pytest tests/integration/`, `pytest tests/gui/`

## Dependencies Summary

```python
# requirements.txt or pyproject.toml
PySide6>=6.6.0          # GUI framework
Pillow>=10.0.0          # Image I/O
numpy>=1.24.0           # Efficient pixel manipulation
pytest>=7.4.0           # Testing framework
pytest-qt>=4.2.0        # PySide6 widget testing
ruff>=0.1.0             # Linting
black>=23.0.0           # Code formatting
mypy>=1.5.0             # Type checking
```

### Mouse Hover Tracking

**Decision**: Use Qt's mouse event system (QWidget.mouseMoveEvent) to track mouse position over image.

**Rationale**:
- Qt provides built-in mouse event handling in QWidget
- Efficient event system with minimal overhead
- Easy to extract pixel coordinates relative to image
- Can convert image coordinates to pixel data coordinates

**Implementation approach**:
- Override `mouseMoveEvent()` in ImageView widget
- Calculate pixel coordinates from mouse position (accounting for image scaling)
- Extract RGB values from pixel_data array at calculated coordinates
- Convert RGB to HEX format (e.g., "#FF5733")
- Update ImageStatistics.hover_hex_color
- Emit signal to update status bar
- Override `leaveEvent()` to clear hover color when mouse leaves

### Image Saving

**Decision**: Use Pillow to save processed images as PNG files.

**Rationale**:
- Pillow already used for image I/O
- PNG format preserves quality (lossless)
- PNG supports transparency (alpha channel)
- Widely supported format
- Pillow's `Image.save()` method handles PNG encoding efficiently

**Implementation approach**:
- Convert NumPy array (pixel_data) to PIL Image using `Image.fromarray()`
- Preserve alpha channel if present (RGBA)
- Use `image.save(file_path, 'PNG')` to save
- Handle file path validation and error cases
- Use QFileDialog for user file selection (Qt standard)

**Error handling**:
- Validate image is loaded before save
- Check file path is writable
- Handle permission errors gracefully
- Provide user-friendly error messages

## Open Questions Resolved

1. **Q: Which GUI framework?** → A: PySide6 (specified by user)
2. **Q: How to handle real-time processing?** → A: QThread for background processing
3. **Q: Which pixelization algorithm?** → A: Block averaging (simple, fast, effective)
4. **Q: Which color reduction approach?** → A: Threshold-based color quantization
5. **Q: How to maintain UI responsiveness?** → A: Background threading + efficient NumPy operations
6. **Q: Image size limits?** → A: 2000x2000px maximum (per spec)
7. **Q: How to track mouse hover for HEX color?** → A: Qt mouseMoveEvent in ImageView widget
8. **Q: How to save processed images?** → A: Pillow Image.save() as PNG format

All technical decisions resolved. Ready for Phase 1 design.

