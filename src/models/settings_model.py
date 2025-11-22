"""Settings models for pixelization and color reduction."""

from dataclasses import dataclass


@dataclass
class PixelizationSettings:
    """Configuration for pixelization effect.

    Attributes:
        pixel_size: Size of each pixel block (1-50). Value of 1 means no
            pixelization effect.
        is_enabled: Whether pixelization is currently enabled. Automatically
            set to True when pixel_size > 1.
    """

    pixel_size: int = 1
    is_enabled: bool = False

    def __post_init__(self) -> None:
        """Validate pixelization settings after initialization.

        Raises:
            ValueError: If pixel_size is outside valid range (1-50).
        """
        if self.pixel_size < 1:
            raise ValueError("pixel_size must be >= 1")
        if self.pixel_size > 50:
            raise ValueError("pixel_size should not exceed 50 for reasonable effects")


@dataclass
class ColorReductionSettings:
    """Configuration for color reduction effect.

    Attributes:
        sensitivity: Color similarity threshold (0.0-1.0). Higher values
            result in more aggressive color merging and fewer distinct colors.
            Value of 0.0 means no color reduction.
        is_enabled: Whether color reduction is currently enabled. Automatically
            set to True when sensitivity > 0.0.
    """

    sensitivity: float = 0.0
    is_enabled: bool = False

    def __post_init__(self) -> None:
        """Validate color reduction settings after initialization.

        Raises:
            ValueError: If sensitivity is outside valid range (0.0-1.0).
        """
        if not 0.0 <= self.sensitivity <= 1.0:
            raise ValueError("sensitivity must be between 0.0 and 1.0")


@dataclass
class SettingsModel:
    """Container for all application settings.

    This model holds configuration for all image processing operations,
    including pixelization and color reduction settings.

    Attributes:
        pixelization: Pixelization effect configuration.
        color_reduction: Color reduction effect configuration.
    """

    pixelization: PixelizationSettings
    color_reduction: ColorReductionSettings

    def __init__(self) -> None:
        """Initialize settings model with default values.

        Creates new instances of PixelizationSettings and ColorReductionSettings
        with default values (no effects enabled).
        """
        self.pixelization = PixelizationSettings()
        self.color_reduction = ColorReductionSettings()

