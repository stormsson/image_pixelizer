# Contract: ImageLoader Service

**Service**: `src/services/image_loader.py`  
**Purpose**: Load and validate image files from file system

## Interface

```python
class ImageLoader:
    """Loads and validates image files."""
    
    def load_image(file_path: str) -> Image:
        """
        Load image from file path.
        
        Args:
            file_path: Path to image file
            
        Returns:
            Image entity with loaded pixel data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format not supported
            ValueError: If image dimensions exceed 2000x2000px
            IOError: If file is corrupted or unreadable
        """
        
    def validate_image_format(file_path: str) -> bool:
        """
        Validate that file is a supported image format.
        
        Args:
            file_path: Path to image file
            
        Returns:
            True if format is supported (JPEG, PNG, GIF, BMP)
            
        Raises:
            ValueError: If format not supported
        """
        
    def validate_image_size(image: Image) -> bool:
        """
        Validate image dimensions are within limits.
        
        Args:
            image: Image entity to validate
            
        Returns:
            True if dimensions <= 2000x2000px
            
        Raises:
            ValueError: If dimensions exceed limit
        """
```

## Supported Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)

## Error Messages

- File not found: "The selected file could not be found. Please check the file path."
- Unsupported format: "Unsupported image format. Please use JPEG, PNG, GIF, or BMP."
- Size exceeded: "Image size exceeds maximum of 2000x2000 pixels. Please resize the image."
- Corrupted file: "The image file appears to be corrupted or unreadable. Please try a different file."

## Return Value

Returns `Image` entity with:
- `width`, `height`: Image dimensions
- `pixel_data`: NumPy array of shape (height, width, channels)
- `original_pixel_data`: Same as pixel_data (original unprocessed)
- `format`: Original file format string
- `has_alpha`: Boolean indicating alpha channel presence

