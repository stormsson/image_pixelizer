# SAM (Segment Anything Model) Setup Checklist

This checklist guides you through setting up and using the Segment Anything Model (SAM) for background removal in the Pixelizer application.

## Prerequisites

- [ ] Python 3.11 or higher installed
- [ ] `rembg` library installed (`pip install rembg`)
- [ ] `onnxruntime` installed (`pip install onnxruntime`)
- [ ] Sufficient disk space (~1-2GB for SAM model files)

## Step 1: Install SAM Model Dependencies

The SAM model requires additional dependencies. Install them:

```bash
pip install rembg[sam]
```

Or install individually:
```bash
pip install rembg
pip install onnxruntime
```

## Step 2: Download SAM Model (Automatic)

The SAM model will be automatically downloaded on first use. However, you can pre-download it:

```bash
python -c "from rembg import new_session; new_session('sam')"
```

This will download the SAM model checkpoint to `~/.u2net/` (or similar location depending on your OS).

**Note**: First download may take several minutes and requires internet connection. The model is ~1-2GB in size.

## Step 3: Update Application Code to Use SAM

### Option A: Change Default Model in `main.py`

Edit `main.py` and change the BackgroundRemover initialization:

```python
# Change from:
background_remover = BackgroundRemover()

# To:
background_remover = BackgroundRemover(model='sam')
```

### Option B: Make Model Configurable

You can make the model configurable via environment variable or config file:

```python
import os
model = os.getenv('REMBG_MODEL', 'u2net')  # Default to u2net
background_remover = BackgroundRemover(model=model)
```

Then set environment variable:
```bash
export REMBG_MODEL=sam
python main.py
```

## Step 4: Verify SAM is Working

1. [ ] Run the application: `python main.py`
2. [ ] Load an image
3. [ ] Click "Remove Background"
4. [ ] Verify background removal works (may take longer than u2net)
5. [ ] Check console for any error messages

## Available Models

The following models are supported by rembg:

| Model | Description | Best For | Speed |
|-------|-------------|----------|-------|
| `u2net` | Default model | General purpose, automatic | Fast |
| `sam` | Segment Anything Model | Precise segmentation with prompts | Slower |
| `u2netp` | Lightweight u2net | Faster processing, lower accuracy | Very Fast |
| `u2net_human_seg` | Human-optimized | People/portraits | Fast |
| `silueta` | Alternative model | General purpose | Medium |

## Troubleshooting

### Issue: "Failed to initialize sam model"

**Solution**: 
- Ensure `rembg[sam]` is installed
- Check internet connection for first-time model download
- Verify sufficient disk space (~2GB free)

### Issue: SAM is slower than expected

**Solution**: 
- SAM is inherently slower than u2net
- Consider using `u2net` for automatic removal
- SAM is best when you need precise control with prompts

### Issue: Model download fails

**Solution**:
- Check internet connection
- Try manual download: `python -c "from rembg import new_session; new_session('sam')"`
- Check firewall/proxy settings
- Verify disk space

### Issue: "ModuleNotFoundError: No module named 'onnxruntime'"

**Solution**:
```bash
pip install onnxruntime
```

## Performance Notes

- **u2net (default)**: ~2-4 seconds for 2000x2000px images
- **SAM**: ~5-10 seconds for 2000x2000px images (first run may be slower)
- **Memory**: SAM uses more memory (~500MB-1GB) compared to u2net (~200MB)

## Advanced: Using SAM with Prompts

Currently, the implementation uses automatic background removal. To use SAM with prompts (for more precise control), you would need to:

1. Modify `BackgroundRemover.remove_background()` to accept prompt parameters
2. Pass prompts to `rembg.remove()` via the `extra` parameter
3. Update the UI to allow users to specify prompts (bounding boxes, points, etc.)

Example prompt format:
```python
extra = {
    "sam_prompt": [
        {"type": "rectangle", "data": [x1, y1, x2, y2], "label": 1}
    ]
}
result_pil = remove(pil_image, session=session, extra=extra)
```

## Model Storage Locations

Models are typically stored in:
- **Linux/Mac**: `~/.u2net/` or `~/.cache/rembg/`
- **Windows**: `%USERPROFILE%\.u2net\` or `%APPDATA%\rembg\`

## Next Steps

After setting up SAM:
- [ ] Test with various image types
- [ ] Compare results with default u2net model
- [ ] Consider adding model selection UI (future enhancement)
- [ ] Document any model-specific issues or preferences

## References

- [rembg GitHub](https://github.com/danielgatis/rembg)
- [SAM Paper](https://arxiv.org/abs/2304.02643)
- [rembg Documentation](https://github.com/danielgatis/rembg#models)

