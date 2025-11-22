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

### Background Removal Models

The application supports multiple background removal models:

- **u2net** (default): Automatic background removal, fast and accurate
- **sam**: Segment Anything Model - more precise but slower
- **u2netp**: Lightweight version, faster processing
- **u2net_human_seg**: Optimized for human subjects
- **silueta**: Alternative model

To use SAM or other models, see [SAM Setup Checklist](docs/SAM_SETUP_CHECKLIST.md).

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
- Background removal using AI (rembg)
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

