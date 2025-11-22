"""Business logic services for image processing."""

from typing import Optional


class ImageProcessingError(Exception):
    """Base exception for image processing errors.

    This exception provides both a technical message for logging/debugging
    and a user-friendly message for display in the UI.

    Attributes:
        user_message: User-friendly error message suitable for display in dialogs.
    """

    def __init__(self, message: str, user_message: Optional[str] = None) -> None:
        """Initialize image processing error.

        Args:
            message: Technical error message for logging/debugging.
            user_message: Optional user-friendly message. If not provided,
                uses the technical message.
        """
        super().__init__(message)
        self.user_message = user_message or message


class ImageLoadError(ImageProcessingError):
    """Exception raised when image loading fails.

    This exception is raised when an image file cannot be loaded due to:
    - File not found
    - Corrupted or unreadable file
    - Unsupported format
    - Other I/O errors
    """

    pass


class ImageValidationError(ImageProcessingError):
    """Exception raised when image validation fails.

    This exception is raised when an image fails validation checks such as:
    - Unsupported file format
    - Image dimensions exceed maximum allowed size (2000x2000px)
    - Invalid image data structure
    """

    pass


class ImageSaveError(ImageProcessingError):
    """Exception raised when image saving fails.

    This exception is raised when an image cannot be saved due to:
    - Permission denied
    - Disk full
    - Invalid file path
    - Other I/O errors
    """

    pass
