# Contract: MainController

**Controller**: `src/controllers/main_controller.py`  
**Purpose**: Coordinate between models, services, and views

## Interface

```python
class MainController(QObject):
    """Coordinates application components."""
    
    # Signals
    image_loaded = Signal(Image)
    image_updated = Signal(Image)
    statistics_updated = Signal(ImageStatistics)
    hover_color_changed = Signal(str)  # HEX color code or None
    error_occurred = Signal(str)  # error message
    save_completed = Signal(str)  # file path
    
    def __init__(
        self,
        image_model: ImageModel,
        settings_model: SettingsModel,
        image_loader: ImageLoader,
        image_saver: ImageSaver,
        pixelizer: Pixelizer,
        color_reducer: ColorReducer
    ):
        """Initialize controller with dependencies."""
        
    def load_image(self, file_path: str) -> None:
        """
        Load image from file path.
        
        Emits:
            image_loaded: When image successfully loaded
            error_occurred: If loading fails
        """
        
    def update_pixel_size(self, pixel_size: int) -> None:
        """
        Update pixelization settings and reprocess image.
        
        Emits:
            image_updated: When processing completes
            statistics_updated: When statistics recomputed
            error_occurred: If processing fails
        """
        
    def update_sensitivity(self, sensitivity: float) -> None:
        """
        Update color reduction settings and reprocess image.
        
        Emits:
            image_updated: When processing completes
            statistics_updated: When statistics recomputed
            error_occurred: If processing fails
        """
        
    def get_statistics(self) -> ImageStatistics:
        """
        Get current image statistics.
        
        Returns:
            Current ImageStatistics instance
        """
        
    def update_hover_color(self, x: int, y: int) -> None:
        """
        Update hover color based on mouse position over image.
        
        Args:
            x: Mouse X coordinate relative to image
            y: Mouse Y coordinate relative to image
            
        Emits:
            hover_color_changed: When HEX color is extracted and updated
        """
        
    def clear_hover_color(self) -> None:
        """
        Clear hover color when mouse leaves image area.
        
        Emits:
            hover_color_changed: With None or empty string to revert status bar
        """
        
    def save_image(self, file_path: str) -> None:
        """
        Save current processed image to PNG file.
        
        Args:
            file_path: Path where PNG file should be saved
            
        Emits:
            save_completed: When save succeeds (with file path)
            error_occurred: If save fails
        """
```

## Responsibilities

1. **Coordinate Loading**: Use ImageLoader to load files, update ImageModel
2. **Coordinate Processing**: Use Pixelizer/ColorReducer, update ImageModel
3. **Coordinate Saving**: Use ImageSaver to save processed images as PNG
4. **Update Statistics**: Recompute ImageStatistics after image changes
5. **Handle Mouse Hover**: Extract pixel color at mouse position, update ImageStatistics
6. **Error Handling**: Catch exceptions, emit error signals with user-friendly messages
7. **Threading**: Manage background threads for image processing and saving
8. **Signal/Slot Connections**: Connect UI signals to model updates

## Processing Flow

1. User action (slider change, file load) → View emits signal
2. Controller receives signal → Updates SettingsModel
3. Controller calls service (Pixelizer/ColorReducer) → Processes ImageModel.pixel_data
4. Controller updates ImageModel → Emits image_updated signal
5. Controller recomputes statistics → Emits statistics_updated signal
6. View receives signals → Updates UI display

Mouse Hover Flow:
1. Mouse moves over image → ImageView emits mouse position
2. Controller receives position → Extracts pixel color from ImageModel.pixel_data
3. Controller converts RGB to HEX → Updates ImageStatistics.hover_hex_color
4. Controller emits hover_color_changed signal → Status bar displays HEX color

Save Flow:
1. User selects Save → View emits save signal with file path
2. Controller receives signal → Validates image is loaded
3. Controller calls ImageSaver → Saves ImageModel.pixel_data as PNG
4. Controller emits save_completed signal → User receives confirmation

## Error Handling

- Catch all exceptions from services
- Convert technical errors to user-friendly messages
- Emit error_occurred signal with message
- Maintain last valid state (don't corrupt models on error)

## Threading

- Use QThread for background image processing
- Emit progress signals during processing
- Update UI only from main thread (via signals)
- Handle cancellation if user changes settings rapidly

