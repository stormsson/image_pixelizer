# Architecture Documentation

**Last Updated**: 2025-01-29  
**Project**: Image Pixelizer

## Overview

Image Pixelizer is a desktop GUI application built with PySide6 (Qt6) following the Model-View-Controller (MVC) architecture pattern. The application provides image processing capabilities including pixelization, color reduction, background removal, and photographic editing tools.

## Architecture Pattern

The application follows a strict MVC separation:

- **Models** (`src/models/`): Data structures and business entities
- **Views** (`src/views/`): GUI components and user interface
- **Controllers** (`src/controllers/`): Coordinate between models and views
- **Services** (`src/services/`): Business logic and algorithms (stateless)

## Component Overview

### Models

- **ImageModel**: Represents image data with pixel arrays, dimensions, format, and transparency
- **ImageStatistics**: Computed statistics (color count, dimensions, hover color)
- **SettingsModel**: Application settings (pixelization, color reduction)
- **PointSelectionCollection**: Manages point selections for background removal

### Services

Services are stateless classes that perform specific operations:

- **ImageLoader**: Loads and validates image files
- **ImageSaver**: Saves processed images to disk
- **Pixelizer**: Applies pixelization algorithm
- **ColorReducer**: Reduces color palette using quantization and clustering
- **BackgroundRemover**: Interactive background removal using rembg
- **OpenAIBackgroundRemover**: Automatic background removal using OpenAI API
- **LevelsAdjuster**: Calculates histograms and applies levels adjustments
- **OperationHistoryManager**: Manages undo/redo operation history

### Views

GUI components built with PySide6:

- **MainWindow**: Main application window with menu bar
- **ImageView**: Displays images with scaling and mouse tracking
- **ControlsPanel**: Sidebar with sliders and buttons
- **StatusBar**: Displays statistics and color information
- **LevelsWindow**: Separate window for Image Levels tool with histogram

### Controllers

- **MainController**: Central coordinator following MVC pattern
  - Manages image state
  - Coordinates services
  - Emits signals for view updates
  - Handles operation history

## Signal/Slot Communication

The application uses Qt's signal/slot mechanism for loose coupling:

**Controller → View Signals:**
- `image_loaded(ImageModel)`: Emitted when image is loaded
- `image_updated(ImageModel)`: Emitted when image is modified
- `statistics_updated(ImageStatistics)`: Emitted when statistics change
- `error_occurred(str)`: Emitted when errors occur
- `operation_history_changed()`: Emitted when undo state changes

**View → Controller Signals:**
- Slider value changes (pixel size, sensitivity)
- Button clicks (save, undo, background removal)
- Menu actions

## Image Levels Tool Workflow

The Image Levels tool demonstrates the MVC pattern and service integration:

### 1. User Action
- User selects "Photographic Editing Tools > Image Levels" from menu
- MainWindow creates LevelsWindow instance

### 2. Window Initialization
- LevelsWindow requests current image from MainController
- LevelsWindow creates LevelsAdjuster service instance
- Histogram is calculated and cached

### 3. User Interaction
- User adjusts sliders (Darks Cutoff, Lights Cutoff)
- LevelsWindow applies adjustment using LevelsAdjuster
- Adjusted image histogram is calculated and displayed
- LevelsWindow emits `levels_adjusted(ImageModel)` signal

### 4. Controller Integration
- MainWindow connects `levels_adjusted` signal to `MainController.apply_levels_adjustment()`
- Controller saves current state to operation history
- Controller updates image model
- Controller emits `image_updated` signal

### 5. View Updates
- MainWindow receives `image_updated` signal
- ImageView displays updated image
- StatusBar updates statistics
- LevelsWindow receives `image_updated` signal and recalculates histogram

### Data Flow Diagram

```
User Action (Menu)
    ↓
MainWindow._on_levels_menu_triggered()
    ↓
LevelsWindow.__init__(controller)
    ↓
LevelsWindow._update_histogram()
    ↓
MainController.get_current_image()
    ↓
LevelsAdjuster.calculate_histogram(image)
    ↓
HistogramWidget.set_histogram_data()
    ↓
[User adjusts sliders]
    ↓
LevelsWindow._apply_levels_adjustment()
    ↓
LevelsAdjuster.apply_levels(image, darks, lights)
    ↓
LevelsWindow.levels_adjusted.emit(adjusted_image)
    ↓
MainController.apply_levels_adjustment(adjusted_image)
    ↓
OperationHistoryManager.add_operation("levels_adjustment", ...)
    ↓
MainController.image_updated.emit(updated_image)
    ↓
MainWindow._on_image_updated(image)
    ↓
ImageView.display_image(...)
```

## Service Design Principles

1. **Stateless**: Services have no instance variables (except configuration)
2. **Pure Functions**: Methods return new data rather than modifying inputs
3. **Testable**: Services can be tested without GUI dependencies
4. **Reusable**: Services can be used independently or in combination

## Error Handling

- **Service Level**: Services raise `ValueError` with descriptive messages
- **Controller Level**: Catches exceptions and emits `error_occurred` signal
- **View Level**: Displays user-friendly error messages via QMessageBox

## Operation History

The application maintains a rolling history of up to 20 operations:

- Each operation stores a snapshot of the image state before the operation
- Operations are tracked by type (e.g., "levels_adjustment", "remove_background")
- Undo restores the previous image state
- History is cleared when a new image is loaded

## Performance Considerations

- **Histogram Caching**: LevelsWindow caches histogram when image loads, only recalculates on image change
- **Vectorized Operations**: NumPy operations use vectorization for efficiency
- **Memory Management**: Services create new ImageModel instances rather than modifying originals
- **Background Processing**: Long-running operations (background removal) use QThread workers

## Testing Strategy

- **Unit Tests**: Test services independently (80% coverage target)
- **GUI Tests**: Test UI components with pytest-qt (60% coverage target)
- **Integration Tests**: Test end-to-end workflows

## Dependencies

- **PySide6**: GUI framework
- **NumPy**: Array operations and image processing
- **Pillow**: Image I/O
- **rembg**: AI-powered background removal
- **OpenAI**: Automatic background removal API
- **pytest/pytest-qt**: Testing framework

## Future Extensibility

The architecture supports adding new editing tools:

1. Create new service class (e.g., `BrightnessAdjuster`)
2. Create new window class (e.g., `BrightnessWindow`)
3. Add menu item in MainWindow
4. Connect signals in MainController
5. Follow same MVC pattern

