# Contract: ColorReducer Service

**Service**: `src/services/color_reducer.py`  
**Purpose**: Reduce number of distinct colors in images

## Interface

```python
class ColorReducer:
    """Reduces number of distinct colors in images."""
    
    def reduce_colors(
        image: np.ndarray,
        sensitivity: float
    ) -> np.ndarray:
        """
        Reduce number of distinct colors by merging similar colors.
        
        Args:
            image: NumPy array of shape (height, width, channels)
            sensitivity: Color similarity threshold (0.0 to 1.0)
                        Higher = more aggressive merging = fewer colors
            
        Returns:
            Processed NumPy array with same shape as input
            
        Raises:
            ValueError: If sensitivity not in valid range
            ValueError: If image array is invalid
        """
        
    def reduce_colors_async(
        image: np.ndarray,
        sensitivity: float,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> np.ndarray:
        """
        Reduce colors asynchronously with progress updates.
        
        Args:
            image: NumPy array of shape (height, width, channels)
            sensitivity: Color similarity threshold
            progress_callback: Optional callback for progress (0.0 to 1.0)
            
        Returns:
            Processed NumPy array
            
        Note: This method should be called from background thread.
        """
        
    def count_distinct_colors(image: np.ndarray) -> int:
        """
        Count number of distinct colors in image.
        
        Args:
            image: NumPy array of shape (height, width, channels)
            
        Returns:
            Number of unique RGB/RGBA color values
        """
```

## Algorithm

1. Calculate color distance between pixels using Euclidean distance in RGB space
2. Group pixels with distance < sensitivity threshold
3. Replace grouped pixels with average color of group
4. Iterate until no more merges possible (or use single-pass approximation)

## Sensitivity Range

- **0.0**: No color reduction (preserve all colors)
- **0.5**: Moderate color reduction
- **1.0**: Maximum color reduction (most aggressive merging)

## Edge Cases

- `sensitivity = 0.0`: Return original image unchanged
- Monochrome/grayscale images: Algorithm still functions correctly
- Images with transparency: Preserve alpha channel, reduce RGB only

## Performance

- Target: Process 2000x2000px image in < 1 second
- Use NumPy broadcasting for efficient distance calculations
- Consider approximation algorithms for real-time performance

## Input/Output

- **Input**: NumPy array shape (H, W, 3) or (H, W, 4) for RGB/RGBA
- **Output**: NumPy array with same shape and dtype
- Preserves alpha channel if present
- Reduces distinct color count based on sensitivity

