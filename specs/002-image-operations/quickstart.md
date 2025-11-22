# Quickstart: Image Operations Feature

**Feature**: Image Operations in Controls Panel  
**Date**: 2025-01-27

## Overview

This guide provides a quick introduction to using the new image operation buttons in the Image Pixelizer application. The application now supports removing backgrounds from images and undoing complex operations.

## User Workflow

### 1. Load an Image

Start by loading an image (if not already loaded):
1. Click "File → Load Image" or use Ctrl+O (Cmd+O on Mac)
2. Select an image file
3. Image appears in main content area

**Note**: The "Remove Background" and "Undo" buttons are only available when an image is loaded.

### 2. Remove Background

1. Locate the "Remove Background" button in the controls panel (below the sliders)
2. Click the "Remove Background" button
3. The application processes the image using AI to detect and remove the background
4. Processing may take a few seconds (typically 2-5 seconds for large images)
5. The image updates to show the background removed (transparent)
6. The main subject of the image is preserved

**Tips**:
- First use will download the AI model (~100MB) - this only happens once
- Processing happens in the background - the UI remains responsive
- The result always has a transparent background (PNG format supports this)

### 3. Adjust Effects (Optional)

You can still use the existing sliders after removing the background:
1. Adjust "Pixel Size" slider to pixelize the image with transparent background
2. Adjust "Sensitivity" slider to reduce colors
3. These slider changes are applied to the image with removed background

### 4. Undo Operation

If you want to revert the background removal:
1. Locate the "Undo" button in the controls panel (next to "Remove Background")
2. Click the "Undo" button
3. The image reverts to its state before the last complex operation
4. Any slider adjustments (pixelization/color reduction) that were applied before the background removal are preserved

**Important Notes**:
- Undo only works for complex button-based operations (like "Remove Background")
- Undo does NOT track or revert slider changes (pixelization/color sensitivity)
- You can undo up to 20 operations in sequence
- Undo is disabled when no operations have been applied

### 5. Multiple Operations

You can apply multiple background removal operations:
1. Click "Remove Background" multiple times
2. Each click processes the current state of the image
3. Use "Undo" to revert operations one at a time (most recent first)
4. Each undo restores the image to before that specific operation

### 6. Save Processed Image

After removing the background:
1. Click "Save" button or use Ctrl+S (Cmd+S on Mac)
2. Choose a location and filename
3. The image is saved as PNG with transparent background
4. You can open the saved image in other applications to see the transparency

## Tips

- **Background Removal Quality**: Works best with images that have clear subject/background distinction. Complex or textured backgrounds may require multiple attempts.
- **Undo History**: The undo history is cleared when you load a new image. Make sure to save your work before loading a new image if you want to keep the processed result.
- **Slider Interaction**: Slider changes (pixelization/color reduction) are preserved when you undo. This means you can experiment with effects, remove background, and undo while keeping your slider settings.
- **Processing Time**: Background removal takes longer for larger images. Very large images (approaching 2000x2000px) may take up to 5 seconds.
- **Memory Usage**: The application stores up to 20 operations in memory for undo. Each operation stores a full image snapshot, so memory usage increases with image size.

## Limitations

- **Undo Limit**: Maximum 20 operations can be undone. Older operations are automatically removed when the limit is reached.
- **Operation Types**: Currently only "Remove Background" is supported. More operations may be added in the future.
- **Slider Changes**: Slider-based changes (pixelization/color sensitivity) are NOT tracked in undo history. Only button-based operations are tracked.
- **Persistence**: Undo history is not saved - it's cleared when you close the application or load a new image.

## Troubleshooting

### "Remove Background" button is disabled
- **Cause**: No image is loaded
- **Solution**: Load an image first using "File → Load Image"

### Background removal takes too long
- **Cause**: Large image size or first-time model download
- **Solution**: Wait for processing to complete. First use downloads the AI model (~100MB) which may take time depending on internet speed.

### Background removal failed
- **Cause**: Processing error or invalid image
- **Solution**: Try a different image or ensure the image is in a supported format (JPEG, PNG, GIF, BMP, WebP)

### "Undo" button is disabled
- **Cause**: No operations have been applied yet
- **Solution**: Apply a complex operation (like "Remove Background") first

### Undo doesn't restore slider changes
- **Cause**: This is expected behavior - undo only affects complex operations, not slider changes
- **Solution**: Slider positions remain as you set them. Undo restores the image state but preserves slider settings.

## Keyboard Shortcuts

- **Ctrl+O** (Cmd+O on Mac): Load image
- **Ctrl+S** (Cmd+S on Mac): Save processed image
- **Esc**: Close error dialogs

**Note**: Operation buttons (Remove Background, Undo) are currently mouse-only. Keyboard shortcuts may be added in the future.

## Next Steps

After getting familiar with background removal and undo:
- Experiment with combining background removal and pixelization effects
- Try different images to see how background removal quality varies
- Use undo to experiment with different processing orders
- Save your favorite results as PNG files with transparency

