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

## Features

- Image pixelization with adjustable pixel size
- Color reduction with sensitivity control
- Background removal using AI:
  - **Interactive method**: Point-based selection with rembg (SAM model)
  - **Automatic method**: One-click removal using OpenAI API + rembg
- Undo operation support (up to 20 operations)
- Save processed images as PNG with transparency support

## Libraries

### External Libraries

**GUI Framework:**
- **PySide6** (>=6.6.0): Qt6 Python bindings for the desktop GUI interface, providing widgets, signals/slots, and event handling

**Image Processing:**
- **Pillow** (>=10.0.0): Core image manipulation library for loading, saving, and converting image formats (PNG, JPEG, etc.)
- **NumPy** (>=1.24.0): High-performance array operations for pixel data manipulation and mathematical operations on image arrays

**AI/ML:**
- **rembg** (>=2.0.68): AI-powered background removal library supporting multiple models (u2net, SAM, u2netp, etc.)
- **onnxruntime** (>=1.15.0): Runtime for executing ONNX models used by rembg for AI inference

**API Integration:**
- **openai** (>=1.0.0): OpenAI Python SDK for Vision API integration in automatic background removal

**Utilities:**
- **python-dotenv** (>=1.0.0): Environment variable management for loading API keys from `.env` files

**Development Tools:**
- **pytest** (>=7.4.0): Testing framework
- **pytest-qt** (>=4.2.0): Qt-specific testing utilities for GUI component testing
- **ruff** (>=0.1.0): Fast Python linter
- **black** (>=23.0.0): Code formatter
- **mypy** (>=1.5.0): Static type checker

### Internal Modules

**Models** (`src/models/`):
- `image_model.py`: Core image data model with pixel array management and statistics
- `point_selection.py`: Point selection collection for interactive background removal
- `settings_model.py`: Application settings and configuration management

**Services** (`src/services/`):
- `pixelizer.py`: Pixelization algorithm using block averaging
- `color_reducer.py`: Color reduction using K-Means clustering
- `background_remover.py`: Interactive background removal service using rembg
- `openai_background_remover.py`: Automatic background removal via OpenAI API
- `image_loader.py`: Image loading and format conversion
- `image_saver.py`: Image saving with PNG transparency support
- `operation_history.py`: Undo/redo operation history management

**Views** (`src/views/`):
- `main_window.py`: Main application window and layout
- `image_view.py`: Image display widget with zoom and pan capabilities
- `controls_panel.py`: UI controls for pixelization, color reduction, and background removal
- `status_bar.py`: Status bar for displaying image statistics and messages

**Controllers** (`src/controllers/`):
- `main_controller.py`: Main application controller coordinating models, services, and views following MVC pattern

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

