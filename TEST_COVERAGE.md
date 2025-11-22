# Test Coverage Verification

This document describes how to verify test coverage meets the targets specified in the requirements.

## Coverage Targets

Per requirements (FR-019 through FR-022):
- **Business Logic**: 80% minimum coverage (models, services)
- **UI Components**: 60% minimum coverage (views, GUI components)

## Running Coverage Analysis

### Install Dependencies

```bash
pip install -e ".[dev]"
```

This installs pytest-cov along with other development dependencies.

### Run Coverage Analysis

```bash
# Run tests with coverage for all code
pytest --cov=src --cov-report=html --cov-report=term

# Run coverage for business logic only (models + services)
pytest --cov=src/models --cov=src/services --cov-report=html --cov-report=term

# Run coverage for UI components only (views)
pytest --cov=src/views --cov-report=html --cov-report=term

# Generate detailed HTML report
pytest --cov=src --cov-report=html
# Then open htmlcov/index.html in a browser
```

### Coverage Report Interpretation

The terminal output will show:
```
Name                          Stmts   Miss  Cover
-------------------------------------------------
src/models/image_model.py        87      5    94%
src/services/pixelizer.py        45      2    96%
...
-------------------------------------------------
TOTAL                           450     50    89%
```

The HTML report provides:
- Line-by-line coverage highlighting
- File-by-file coverage percentages
- Missing line indicators

## Coverage Breakdown by Component

### Business Logic (Target: 80%)

**Models** (`src/models/`):
- `image_model.py`: ImageModel, ImageStatistics, rgb_to_hex
- `settings_model.py`: SettingsModel, PixelizationSettings, ColorReductionSettings

**Services** (`src/services/`):
- `image_loader.py`: ImageLoader service
- `image_saver.py`: ImageSaver service
- `pixelizer.py`: Pixelizer service
- `color_reducer.py`: ColorReducer service

**Test Files**:
- `tests/unit/test_image_model.py`
- `tests/unit/test_settings_model.py`
- `tests/unit/test_image_loader.py`
- `tests/unit/test_image_saver.py`
- `tests/unit/test_pixelizer.py`
- `tests/unit/test_color_reducer.py`

### UI Components (Target: 60%)

**Views** (`src/views/`):
- `main_window.py`: MainWindow
- `image_view.py`: ImageView
- `controls_panel.py`: ControlsPanel
- `status_bar.py`: StatusBar

**Test Files**:
- `tests/gui/test_main_window.py`
- `tests/gui/test_image_view.py`
- `tests/gui/test_controls_panel.py`
- `tests/gui/test_status_bar.py`

### Controllers (Part of Business Logic)

**Controllers** (`src/controllers/`):
- `main_controller.py`: MainController

**Test Files**:
- `tests/integration/test_controller.py`

## Integration Tests

Integration tests cover end-to-end workflows:
- `tests/integration/test_image_processing.py`: Full workflows (load, process, save, hover)

## Coverage Exclusions

The following are excluded from coverage (configured in `pyproject.toml`):
- Test files themselves
- `__pycache__` directories
- `__init__.py` files (if they only contain imports)
- TYPE_CHECKING blocks
- Abstract methods and __repr__ methods

## Verifying Coverage Targets

### Check Business Logic Coverage

```bash
pytest --cov=src/models --cov=src/services --cov=src/controllers --cov-report=term-missing
```

Look for the **TOTAL** line and verify it shows **>= 80%**.

### Check UI Components Coverage

```bash
pytest --cov=src/views --cov-report=term-missing
```

Look for the **TOTAL** line and verify it shows **>= 60%**.

### Combined Report

```bash
pytest --cov=src --cov-report=term-missing --cov-report=html
```

This generates both terminal and HTML reports for all components.

## Continuous Integration

For CI/CD pipelines, add coverage verification:

```yaml
# Example GitHub Actions workflow
- name: Run tests with coverage
  run: |
    pytest --cov=src --cov-report=xml --cov-report=term
    # Verify business logic coverage >= 80%
    pytest --cov=src/models --cov=src/services --cov=src/controllers --cov-report=term | grep TOTAL | awk '{if ($3+0 < 80) exit 1}'
    # Verify UI coverage >= 60%
    pytest --cov=src/views --cov-report=term | grep TOTAL | awk '{if ($3+0 < 60) exit 1}'
```

## Notes

- Coverage percentages may vary slightly between runs due to conditional execution paths
- Some code paths (error handlers, edge cases) may have lower coverage but are still important
- Focus on ensuring all public APIs and critical paths are tested
- Integration tests help verify coverage of signal/slot connections and workflows

## Current Test Suite Status

The test suite includes:
- ✅ Unit tests for all models
- ✅ Unit tests for all services
- ✅ GUI tests for all views (pytest-qt)
- ✅ Integration tests for workflows
- ✅ Integration tests for MainController

All meaningful entities and features have test coverage as required by FR-019 through FR-022.

