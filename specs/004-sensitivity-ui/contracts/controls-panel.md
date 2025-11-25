# Contract: ControlsPanel (Sensitivity Dropdown)

**View**: `src/views/controls_panel.py`  
**Purpose**: UI component for selecting k-means bin count via dropdown

## Interface Changes

### Removed Components

```python
# REMOVED
self._sensitivity_slider: QSlider  # Horizontal slider (0-100)
self._sensitivity_spinbox: QDoubleSpinBox  # Float input (0.0-1.0)
self._on_sensitivity_slider_changed(value: int) -> None
self._on_sensitivity_spinbox_changed(value: float) -> None
```

### New Components

```python
class ControlsPanel(QWidget):
    """Sidebar widget containing editing controls."""
    
    # Signals
    bin_count_changed = Signal(Optional[int])  # None, 4, 8, 16, 32, 64, 128, 256
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize controls panel with dropdown."""
        
    def _setup_ui(self) -> None:
        """Setup UI including bin count dropdown."""
        # ... existing pixel size controls ...
        
        # Bin count dropdown (replaces sensitivity slider/spinbox)
        bin_count_label = QLabel("Color Bins:")
        layout.addWidget(bin_count_label)
        
        self._bin_count_dropdown = QComboBox()
        self._bin_count_dropdown.addItems(["None", "4", "8", "16", "32", "64", "128", "256"])
        self._bin_count_dropdown.setCurrentText("None")  # Default
        self._bin_count_dropdown.currentTextChanged.connect(self._on_bin_count_changed)
        layout.addWidget(self._bin_count_dropdown)
        
    def _on_bin_count_changed(self, value: str) -> None:
        """
        Handle dropdown value change.
        
        Args:
            value: Selected string ("None", "4", "8", "16", "32", "64", "128", "256")
        
        Emits:
            bin_count_changed: With Optional[int] (None for "None", int for others)
        """
        if value == "None":
            bin_count = None
        else:
            bin_count = int(value)
        self.bin_count_changed.emit(bin_count)
    
    def get_bin_count(self) -> Optional[int]:
        """
        Get current bin count selection.
        
        Returns:
            Current bin count (None, 4, 8, 16, 32, 64, 128, 256)
        """
        text = self._bin_count_dropdown.currentText()
        return None if text == "None" else int(text)
    
    def set_bin_count(self, bin_count: Optional[int]) -> None:
        """
        Set dropdown to specified bin count.
        
        Args:
            bin_count: Bin count to select (None, 4, 8, 16, 32, 64, 128, 256)
        """
        if bin_count is None:
            self._bin_count_dropdown.setCurrentText("None")
        else:
            self._bin_count_dropdown.setCurrentText(str(bin_count))
    
    def set_processing_state(self, is_processing: bool) -> None:
        """
        Enable/disable dropdown based on processing state.
        
        Args:
            is_processing: True to disable dropdown, False to enable
        """
        self._bin_count_dropdown.setEnabled(not is_processing)
```

## Responsibilities

1. **Display Dropdown**: Show 8 options (None, 4, 8, 16, 32, 64, 128, 256)
2. **Emit Changes**: Signal `bin_count_changed` when user selects new value
3. **State Management**: Reset to "None" when new image loaded (via controller)
4. **Processing Lock**: Disable dropdown during image processing
5. **Value Conversion**: Convert string selection to Optional[int] for signals

## User Interaction Flow

1. User opens dropdown → Sees 8 options
2. User selects value (e.g., "16") → `_on_bin_count_changed("16")` called
3. Handler converts "16" → `16` → Emits `bin_count_changed.emit(16)`
4. Controller receives signal → Updates settings and processes image
5. During processing → Dropdown disabled (via `set_processing_state(True)`)
6. Processing completes → Dropdown enabled (via `set_processing_state(False)`)
7. New image loaded → Controller calls `set_bin_count(None)` → Resets to "None"

## State Transitions

```
Initial: dropdown = "None", enabled = True
    ↓
User selects "16": dropdown = "16", enabled = True
    ↓
Processing starts: dropdown = "16", enabled = False
    ↓
Processing completes: dropdown = "16", enabled = True
    ↓
New image loaded: dropdown = "None", enabled = True
```

## Error Handling

- Invalid dropdown text: Should never occur (QComboBox only allows valid items)
- Invalid bin_count in `set_bin_count()`: Validate before calling (controller responsibility)
- Processing state mismatch: Controller must manage state correctly

## Accessibility

- Keyboard navigation: QComboBox supports arrow keys and Enter
- Screen readers: QComboBox items are accessible via assistive technologies
- Visual feedback: Disabled state provides clear visual indication

