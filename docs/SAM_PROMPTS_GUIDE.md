# SAM Prompts Guide

This guide explains how to use prompts with the Segment Anything Model (SAM) for more precise background removal.

## What are Prompts?

Prompts tell SAM which parts of the image to keep (foreground) or remove (background). SAM supports two types of prompts:

1. **Rectangle prompts**: Define a bounding box around the subject
2. **Point prompts**: Mark specific points on the subject or background

## Prompt Format

Prompts are passed as a list of dictionaries, each with the following structure:

```python
prompts = [
    {
        "type": "rectangle",  # or "point"
        "data": [x1, y1, x2, y2],  # For rectangle: top-left and bottom-right corners
        # OR
        "data": [x, y],  # For point: single coordinate
        "label": 1  # 1 = foreground (keep), 0 = background (remove)
    }
]
```

## Examples

### Example 1: Rectangle Prompt (Bounding Box)

Keep everything inside a rectangle:

```python
from src.services.background_remover import BackgroundRemover

remover = BackgroundRemover(model='sam')

# Define rectangle: [x1, y1, x2, y2]
# This keeps everything in a box from (100, 100) to (400, 500)
prompts = [
    {
        "type": "rectangle",
        "data": [100, 100, 400, 500],  # [left, top, right, bottom]
        "label": 1  # Keep this area
    }
]

result = remover.remove_background(image, prompts=prompts)
```

### Example 2: Point Prompts

Mark specific points on the subject:

```python
# Mark a point on the subject to keep
prompts = [
    {
        "type": "point",
        "data": [250, 300],  # Point at (250, 300)
        "label": 1  # This is foreground - keep it
    },
    {
        "type": "point",
        "data": [50, 50],  # Point in background area
        "label": 0  # This is background - remove it
    }
]

result = remover.remove_background(image, prompts=prompts)
```

### Example 3: Multiple Prompts

Combine rectangle and points for better accuracy:

```python
prompts = [
    {
        "type": "rectangle",
        "data": [100, 100, 400, 500],
        "label": 1  # Main subject area
    },
    {
        "type": "point",
        "data": [250, 200],  # Additional point on subject
        "label": 1
    },
    {
        "type": "point",
        "data": [50, 50],  # Background point to remove
        "label": 0
    }
]

result = remover.remove_background(image, prompts=prompts)
```

## How to Use Prompts in Your Code

### Option 1: Modify the Controller

Update `src/controllers/main_controller.py` to pass prompts:

```python
def remove_background(self, prompts: Optional[List[Dict[str, Any]]] = None) -> None:
    # ... existing code ...
    worker = BackgroundRemovalWorker(
        self._background_remover, 
        self._image_model,
        prompts=prompts  # Pass prompts to worker
    )
```

Then update `BackgroundRemovalWorker`:

```python
def __init__(
    self,
    background_remover: "BackgroundRemover",
    image: ImageModel,
    prompts: Optional[List[Dict[str, Any]]] = None,  # Add prompts parameter
    parent: Optional[QObject] = None,
) -> None:
    # ... existing code ...
    self._prompts = prompts

def process(self) -> None:
    processed_image = self._background_remover.remove_background(
        self._image,
        prompts=self._prompts  # Pass prompts
    )
```

### Option 2: Hardcode Prompts for Testing

For quick testing, you can hardcode prompts in the service:

```python
# In src/services/background_remover.py, modify remove_background:
def remove_background(self, image: ImageModel, prompts: Optional[List[Dict]] = None) -> ImageModel:
    # For testing, use default prompts if none provided and model is SAM
    if self._model == "sam" and prompts is None:
        # Example: Use center of image as a point prompt
        width, height = image.width, image.height
        prompts = [
            {
                "type": "point",
                "data": [width // 2, height // 2],  # Center point
                "label": 1  # Keep center area
            }
        ]
    # ... rest of code ...
```

### Option 3: Add UI for Prompt Selection (Advanced)

For a complete solution, you could add UI elements to let users:
1. Draw rectangles on the image
2. Click points on the image
3. Pass those coordinates as prompts

This would require:
- Modifying `ImageView` to capture mouse clicks/draws
- Storing prompt coordinates
- Passing them through the controller to the service

## Coordinate System

- **Origin (0, 0)**: Top-left corner of the image
- **X-axis**: Increases from left to right
- **Y-axis**: Increases from top to bottom
- **Rectangle format**: `[x1, y1, x2, y2]` where:
  - `(x1, y1)` = top-left corner
  - `(x2, y2)` = bottom-right corner
- **Point format**: `[x, y]` = single coordinate

## Tips for Best Results

1. **Rectangle prompts**: Work best when you can draw a box around the entire subject
2. **Point prompts**: Use multiple points on different parts of the subject for better accuracy
3. **Combine both**: Use a rectangle to define the general area, then add points for fine-tuning
4. **Background points**: Use `label: 0` to explicitly mark areas to remove

## Current Limitations

- Prompts are only used when `model='sam'`
- Other models (u2net, etc.) ignore prompts and use automatic detection
- UI for selecting prompts is not yet implemented - you need to provide coordinates programmatically

## Example: Calculate Prompts from Image Dimensions

```python
def create_center_rectangle_prompt(image: ImageModel, margin: int = 50) -> List[Dict]:
    """Create a rectangle prompt in the center of the image."""
    width, height = image.width, image.height
    return [
        {
            "type": "rectangle",
            "data": [
                margin,  # x1
                margin,  # y1
                width - margin,  # x2
                height - margin  # y2
            ],
            "label": 1
        }
    ]

# Usage
remover = BackgroundRemover(model='sam')
prompts = create_center_rectangle_prompt(image_model, margin=100)
result = remover.remove_background(image_model, prompts=prompts)
```

## Troubleshooting

### Prompts not working?

1. **Check model**: Ensure you're using `model='sam'`
2. **Check format**: Prompts must be a list of dicts with correct keys
3. **Check coordinates**: Ensure coordinates are within image bounds
4. **Check label**: Use `1` for foreground (keep), `0` for background (remove)

### Getting errors?

- Ensure `rembg[sam]` is installed
- Verify SAM model is downloaded
- Check that prompt format matches exactly (see examples above)

## Next Steps

To fully integrate prompts into the UI:
1. Add drawing/selection tools to `ImageView`
2. Store selected coordinates
3. Pass them through controller to service
4. Update button to trigger prompt-based removal

