# Quickstart: Image Pixelizer Application

**Feature**: Image Pixelizer Application  
**Date**: 2025-01-27

## Overview

This guide provides a quick introduction to using the Image Pixelizer application. The application allows users to load images and apply pixelization effects with adjustable pixel size and color reduction sensitivity.

## User Workflow

### 1. Launch Application

Start the application. You'll see:
- Main content area (center) - currently empty
- Sidebar (left) - editing controls with two sliders
- Status bar (bottom) - will show image statistics

### 2. Load an Image

1. Click "Load Image" button or use File → Open menu
2. Select an image file (JPEG, PNG, GIF, or BMP)
3. Image appears in main content area
4. Status bar shows: image dimensions (e.g., "1920 x 1080 pixels") and distinct color count

**Note**: Maximum image size is 2000 x 2000 pixels. Larger images will show an error message.

### 3. Apply Pixelization

1. Locate "Pixel Size" slider in the sidebar
2. Move slider to adjust pixel block size:
   - **Left (minimum)**: No pixelization effect (original image)
   - **Right (maximum)**: Heavy pixelization with large blocks
3. Image updates in real-time as you move the slider
4. Effect is applied immediately (no "Apply" button needed)

### 4. Adjust Color Reduction

1. Locate "Sensitivity" slider in the sidebar
2. Move slider to adjust color reduction:
   - **Left (low sensitivity)**: More colors preserved
   - **Right (high sensitivity)**: Fewer colors (more aggressive merging)
3. Image updates in real-time
4. Status bar updates to show new distinct color count

### 5. View Statistics

The status bar at the bottom continuously displays:
- **Image dimensions**: "Width x Height pixels" (e.g., "1920 x 1080 pixels")
- **Distinct colors**: Number of unique colors in current processed image
- **HEX color**: When you hover your mouse over a pixel, the status bar shows the HEX color code (e.g., "#FF5733")

Statistics update automatically when you adjust sliders. When you move your mouse over the image, the HEX color of the pixel under your cursor is displayed. When you move the mouse away, the status bar reverts to showing dimensions and color count.

## Tips

- **Processing order**: Pixelization is applied first, then color reduction. This produces better visual results.
- **Real-time updates**: Both sliders update the image immediately. No need to click "Apply".
- **Large images**: Processing may take a moment for large images. The UI remains responsive during processing.
- **Reset**: Load a new image to start fresh, or adjust sliders to minimum values.

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png) - including transparency
- GIF (.gif)
- BMP (.bmp)

### 6. Save Processed Image

1. After applying pixelization and color reduction, click "Save" in the menu or use Ctrl+S (Cmd+S on Mac)
2. Choose a location and filename for your saved image
3. The image will be saved as a PNG file
4. You'll receive confirmation when the save completes

**Note**: Images are always saved in PNG format to preserve quality and support transparency.

## Limitations

- Maximum image size: 2000 x 2000 pixels
- Images are saved as PNG files only
- Processing is applied to the displayed image (original is preserved internally for reset)

## Troubleshooting

### "Image size exceeds maximum"
- Your image is larger than 2000 x 2000 pixels
- Resize the image using an external tool, then load again

### "Unsupported image format"
- The file format is not supported
- Convert to JPEG, PNG, GIF, or BMP format

### "File appears corrupted"
- The image file may be damaged
- Try opening the file in another application to verify it's valid
- Try a different image file

### Image doesn't update when moving sliders
- Processing may be in progress (wait a moment)
- If issue persists, try loading the image again

## Keyboard Shortcuts

- **Ctrl+O** (Cmd+O on Mac): Open image file
- **Ctrl+S** (Cmd+S on Mac): Save processed image
- **Esc**: Close error dialogs

## Next Steps

After getting familiar with the basic workflow:
- Experiment with different pixel sizes to find your preferred effect
- Adjust sensitivity to control color palette size
- Try different image types (photos, graphics, etc.) to see how effects vary

