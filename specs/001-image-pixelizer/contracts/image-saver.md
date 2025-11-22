# Contract: ImageSaver Service

**Service**: `src/services/image_saver.py`  
**Purpose**: Save processed images to PNG files

## Interface

```python
class ImageSaver:
    """Saves processed images to PNG files."""
    
    def save_image(
        image: Image,
        file_path: str
    ) -> None:
        """
        Save processed image to PNG file.
        
        Args:
            image: Image entity with processed pixel_data
            file_path: Full path where PNG file should be saved
            
        Returns:
            None
            
        Raises:
            ValueError: If image is None or invalid
            IOError: If file cannot be written (permissions, disk full, etc.)
            OSError: If file path is invalid
        """
        
    def save_image_async(
        image: Image,
        file_path: str,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> None:
        """
        Save image asynchronously with progress updates.
        
        Args:
            image: Image entity with processed pixel_data
            file_path: Full path where PNG file should be saved
            progress_callback: Optional callback for progress (0.0 to 1.0)
            
        Returns:
            None
            
        Note: This method should be called from background thread if needed.
        """
```

## File Format

- **Format**: PNG (Portable Network Graphics)
- **Rationale**: Preserves quality, supports transparency (alpha channel), widely supported
- **Quality**: Lossless compression

## Implementation

1. Convert NumPy array (pixel_data) to PIL Image
2. Preserve alpha channel if present (RGBA)
3. Save using PIL's `save()` method with PNG format
4. Handle file path validation and error cases

## Error Messages

- No image loaded: "No image to save. Please load an image first."
- Invalid file path: "Invalid file path. Please choose a valid location."
- Permission denied: "Permission denied. Please choose a different location or check file permissions."
- Disk full: "Disk is full. Please free up space and try again."
- Save failed: "Failed to save image. Please try again."

## Validation

- Image must be loaded (not None)
- Image must have valid pixel_data
- File path must be writable
- File path must have .png extension (or add automatically)

## Return Value

- No return value (void)
- Success indicated by no exception raised
- Failure indicated by exception with user-friendly message

