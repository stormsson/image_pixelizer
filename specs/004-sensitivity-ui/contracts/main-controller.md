# Contract: MainController (Bin Count API)

**Controller**: `src/controllers/main_controller.py`  
**Purpose**: Coordinate bin count updates and color reduction processing

## Interface Changes

### Removed Methods

```python
# REMOVED
def update_sensitivity(self, sensitivity: float) -> None:
    """Update sensitivity and apply color reduction."""
```

### New Methods

```python
class MainController(QObject):
    """Coordinates application components following MVC pattern."""
    
    # Signals (existing)
    image_loaded = Signal(ImageModel)
    image_updated = Signal(ImageModel)
    statistics_updated = Signal(ImageStatistics)
    error_occurred = Signal(str)
    processing_started = Signal()  # Emitted when processing begins
    processing_finished = Signal()  # Emitted when processing completes
    
    def update_bin_count(self, bin_count: Optional[int]) -> None:
        """
        Update bin count and apply color reduction.
        
        Color reduction is applied after pixelization if pixelization is enabled.
        The dropdown should be disabled during processing (via processing_started/finished signals).
        
        Args:
            bin_count: Bin count value (None, 4, 8, 16, 32, 64, 128, 256)
                - None: Disables color reduction
                - Integer: Direct k-means cluster count
        
        Emits:
            image_updated: When color reduction is applied
            statistics_updated: When statistics are updated
            error_occurred: If color reduction fails
            processing_started: When processing begins (UI should disable dropdown)
            processing_finished: When processing completes (UI should enable dropdown)
        """
        if self._image_model is None:
            return
        
        if self._color_reducer is None:
            self.error_occurred.emit("Color reducer not initialized")
            return
        
        try:
            # Update settings model
            self._settings_model.color_reduction.bin_count = bin_count
            self._settings_model.color_reduction.is_enabled = bin_count is not None
            
            # Get base image state (after background removal, before pixelization)
            if self._base_image_state is None:
                base_image = ImageModel(
                    width=self._image_model.width,
                    height=self._image_model.height,
                    pixel_data=self._image_model.pixel_data.copy(),
                    original_pixel_data=self._image_model.original_pixel_data.copy(),
                    format=self._image_model.format,
                    has_alpha=self._image_model.has_alpha,
                )
            else:
                base_image = ImageModel(
                    width=self._base_image_state.width,
                    height=self._base_image_state.height,
                    pixel_data=self._base_image_state.pixel_data.copy(),
                    original_pixel_data=self._base_image_state.original_pixel_data.copy(),
                    format=self._base_image_state.format,
                    has_alpha=self._base_image_state.has_alpha,
                )
            
            # Apply pixelization first if enabled
            if (
                self._pixelizer is not None
                and self._settings_model.pixelization.is_enabled
            ):
                pixel_size = self._settings_model.pixelization.pixel_size
                if pixel_size > 1:
                    base_image = self._pixelizer.pixelize(base_image, pixel_size)
            
            # Apply color reduction with bin_count as k parameter
            if bin_count is None:
                # No color reduction - return pixelized (or original) image
                reduced_image = base_image
            else:
                # Use bin_count directly as k parameter, sensitivity=0.0 (ignored when k is provided)
                reduced_image = self._color_reducer.reduce_colors(
                    base_image, sensitivity=0.0, k=bin_count
                )
            
            # Update model
            self._image_model = ImageModel(
                width=reduced_image.width,
                height=reduced_image.height,
                pixel_data=reduced_image.pixel_data,
                original_pixel_data=self._image_model.original_pixel_data.copy(),
                format=reduced_image.format,
                has_alpha=reduced_image.has_alpha,
            )
            
            # Update statistics
            self._update_statistics()
            
            # Emit signals
            self.image_updated.emit(self._image_model)
            self.statistics_updated.emit(self._statistics)
            
        except Exception as e:
            error_msg = f"Color reduction failed: {str(e)}"
            self.error_occurred.emit(error_msg)
    
    def load_image(self, file_path: str) -> None:
        """
        Load image from file path.
        
        After loading, resets color reduction bin_count to None (per FR-005).
        
        Args:
            file_path: Path to image file
            
        Emits:
            image_loaded: When image successfully loaded
            error_occurred: If loading fails
        """
        # ... existing load logic ...
        # After successful load:
        # Reset color reduction to None
        self._settings_model.color_reduction.bin_count = None
        self._settings_model.color_reduction.is_enabled = False
```

## Responsibilities

1. **Update Settings**: Update `ColorReductionSettings.bin_count` from dropdown selection
2. **Coordinate Processing**: Apply pixelization (if enabled) then color reduction with bin_count as k
3. **Signal Processing State**: Emit `processing_started`/`processing_finished` for UI lock
4. **Reset on Load**: Reset bin_count to None when new image loaded (FR-005)
5. **Error Handling**: Catch exceptions and emit error signals with user-friendly messages

## Processing Flow

1. User selects bin count from dropdown → View emits `bin_count_changed` signal
2. Controller receives signal → Calls `update_bin_count(bin_count)`
3. Controller updates `SettingsModel.color_reduction.bin_count`
4. Controller gets base image state (after background removal, before pixelization)
5. If pixelization enabled → Apply pixelization first
6. If bin_count is None → Skip color reduction, use pixelized/original image
7. If bin_count is integer → Call `color_reducer.reduce_colors(image, sensitivity=0.0, k=bin_count)`
8. Controller updates `ImageModel` with result
9. Controller updates statistics
10. Controller emits `image_updated` and `statistics_updated` signals

## Error Handling

- **No image loaded**: Return early, no error signal
- **Color reducer not initialized**: Emit `error_occurred` with message
- **Processing exceptions**: Catch, format user-friendly message, emit `error_occurred`
- **Invalid bin_count**: Should be prevented by dropdown constraints, but if received, handle gracefully

## Migration Notes

- Old `update_sensitivity(sensitivity: float)` method should be removed
- All call sites should be updated to use `update_bin_count(Optional[int])`
- Settings model migration: Existing `sensitivity` values reset to `None` (bin_count) per FR-007

