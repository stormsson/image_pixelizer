# Contract: Pixelizer Service

**Service**: `src/services/pixelizer.py`  
**Purpose**: Apply pixelization effect to images

## Interface

```python
class Pixelizer:
    """Applies pixelization effect to images."""
    
    def pixelize(
        image: np.ndarray,
        pixel_size: int
    ) -> np.ndarray:
        """
        Apply pixelization effect to image.
        
        Args:
            image: NumPy array of shape (height, width, channels)
            pixel_size: Size of each pixel block (1 = no effect)
            
        Returns:
            Processed NumPy array with same shape as input
            
        Raises:
            ValueError: If pixel_size < 1
            ValueError: If image array is invalid
        """
        
    def pixelize_async(
        image: np.ndarray,
        pixel_size: int,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> np.ndarray:
        """
        Apply pixelization asynchronously with progress updates.
        
        Args:
            image: NumPy array of shape (height, width, channels)
            pixel_size: Size of each pixel block
            progress_callback: Optional callback for progress (0.0 to 1.0)
            
        Returns:
            Processed NumPy array
            
        Note: This method should be called from background thread.
        """
```

## Algorithm

1. Divide image into blocks of size `pixel_size x pixel_size`
2. For each block, calculate mean RGB/RGBA values
3. Replace all pixels in block with mean color
4. Handle edge blocks where dimensions aren't divisible by pixel_size

## Edge Cases

- `pixel_size = 1`: Return original image unchanged (no pixelization)
- `pixel_size >= min(width, height)`: Entire image becomes single color
- Image dimensions not divisible by pixel_size: Handle edge blocks appropriately

## Performance

- Target: Process 2000x2000px image in < 500ms
- Use NumPy vectorized operations (no Python loops)
- Process in chunks for very large images if needed

## Input/Output

- **Input**: NumPy array shape (H, W, 3) or (H, W, 4) for RGB/RGBA
- **Output**: NumPy array with same shape and dtype
- Preserves alpha channel if present

