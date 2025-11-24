# Pixelizer

Desktop GUI application for pixelizing images and performing image operations.

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Install Dependencies

Install all required dependencies using one of the following methods:

**Using pip with requirements.txt:**
```bash
pip install -r requirements.txt
```

**Using pip with pyproject.toml:**
```bash
pip install -e .
```

**For development (includes test tools):**
```bash
pip install -e ".[dev]"
```

### Key Dependencies

- **PySide6** (>=6.6.0): Qt6 bindings for GUI
- **Pillow** (>=10.0.0): Image processing
- **NumPy** (>=1.24.0): Array operations
- **rembg** (>=2.0.68): AI-powered background removal
- **onnxruntime** (>=1.15.0): Required by rembg for AI model inference
- **openai** (>=1.0.0): OpenAI Python SDK for automatic background removal
- **python-dotenv** (>=1.0.0): Environment variable management

### Background Removal Methods

The application supports two background removal methods:

**1. Interactive Method (rembg with SAM):**
- **u2net** (default): Automatic background removal, fast and accurate
- **sam**: Segment Anything Model - requires point selection, more precise
- **u2netp**: Lightweight version, faster processing
- **u2net_human_seg**: Optimized for human subjects
- **silueta**: Alternative model

To use SAM or other models, see [SAM Setup Checklist](docs/SAM_SETUP_CHECKLIST.md).

**2. Automatic Method (OpenAI API):**
- One-click automatic background removal
- No point selection required
- Uses OpenAI Vision API + rembg for processing
- Requires OpenAI API key (see setup below)

### OpenAI API Setup (Automatic Background Removal)

The automatic background removal method requires an OpenAI API key:

1. **Get an API Key:**
   - Sign up at https://platform.openai.com/
   - Navigate to https://platform.openai.com/api-keys
   - Create a new API key
   - Copy the key (starts with "sk-")

2. **Configure Environment:**
   - Create a `.env` file in the project root (if it doesn't exist)
   - Add your API key:
     ```bash
     OPENAI_API_KEY=sk-your-actual-api-key-here
     ```
   - The `.env` file is gitignored and should never be committed

3. **Verify Setup:**
   - Run the application: `python main.py`
   - The "Remove Background (Automatic)" button will be available if the API key is configured
   - If the API key is missing, the button will not appear (graceful degradation)

**Note:** 
- Each API call incurs costs based on OpenAI pricing
- Subject to OpenAI API rate limits (varies by plan)
- Requires internet connection for API calls
- Check your rate limits at https://platform.openai.com/account/rate-limits

**Example .env file:**
```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-api-key-here

# Optional: rembg model selection
REMBG_MODEL=sam
```

### First-Time Setup

On first use, the `rembg` library will automatically download its AI model (~100MB). This only happens once and requires an internet connection. Subsequent uses work offline.

## Usage

Run the application:
```bash
python main.py
```

For detailed usage instructions, see:
- [Quickstart Guide](specs/002-image-operations/quickstart.md) - User workflow for image operations
- [Specification](specs/002-image-operations/spec.md) - Feature requirements

### Using Image Levels Tool

The Image Levels tool allows you to adjust the tonal distribution of your image by clipping highlights and shadows.

**To access Image Levels:**
1. Load an image using "File > Load Image..." (or Ctrl+O)
2. Select "Photographic Editing Tools > Image Levels" from the menu bar
3. A new window will open displaying a histogram of your image's tonal distribution

**Using the tool:**
- **Histogram**: Shows the distribution of tones in your image
  - Dark tones appear on the left
  - Light tones appear on the right
  - Bar height represents pixel frequency at each tone level
- **Darks Cutoff slider**: Adjusts the percentage of darkest pixels to replace with black (0-100%)
  - Higher values clip more shadows, increasing contrast
  - Example: Setting to 5% replaces the darkest 5% of pixels with black
- **Lights Cutoff slider**: Adjusts the percentage of lightest pixels to replace with white (0-100%)
  - Higher values clip more highlights, increasing contrast
  - Example: Setting to 10% replaces the lightest 10% of pixels with white

**Tips:**
- Adjustments are applied in real-time as you move the sliders
- The histogram updates to reflect changes in the adjusted image
- Both sliders can be used together for maximum contrast control
- Changes are tracked in operation history and can be undone
- Close the window to keep your adjustments applied

## Features

- Image pixelization with adjustable pixel size
- Color reduction with sensitivity control
- Background removal using AI:
  - **Interactive method**: Point-based selection with rembg (SAM model)
  - **Automatic method**: One-click removal using OpenAI API + rembg
- **Photographic editing tools**:
  - **Image Levels**: Adjust tonal distribution with histogram visualization
- Undo operation support (up to 20 operations)
- Save processed images as PNG with transparency support

## Development

### Running Tests

```bash
pytest
```

### Code Quality

- Format code: `black src tests`
- Lint code: `ruff check src tests`
- Type check: `mypy src`

### Test Coverage

Target coverage:
- 80% for business logic (models, services)
- 60% for UI components

Generate coverage report:
```bash
pytest --cov=src --cov-report=html
```

## Project Structure

```
src/
├── models/          # Data models
├── services/        # Business logic services
├── views/           # GUI components
└── controllers/     # Application controllers

tests/
├── unit/            # Unit tests
├── integration/     # Integration tests
└── gui/             # GUI tests (pytest-qt)
```

## License

[Add license information if applicable]

