"""Pixelization service for applying pixelization effects to images."""

import numpy as np

from src.models.image_model import ImageModel


class Pixelizer:
    """Service for pixelizing images using block averaging algorithm."""

    def pixelize(self, image: ImageModel, pixel_size: int) -> ImageModel:
        """
        Apply pixelization effect to image.

        Args:
            image: ImageModel to pixelize
            pixel_size: Size of each pixel block (1-50)

        Returns:
            New ImageModel with pixelized pixel data

        Raises:
            ValueError: If pixel_size is invalid
        """
        if pixel_size < 1:
            raise ValueError("pixel_size must be >= 1")
        if pixel_size > 50:
            raise ValueError("pixel_size should not exceed 50")

        # If pixel_size is 1, no pixelization needed
        if pixel_size == 1:
            return ImageModel(
                width=image.width,
                height=image.height,
                pixel_data=image.pixel_data.copy(),
                original_pixel_data=image.original_pixel_data.copy(),
                format=image.format,
                has_alpha=image.has_alpha,
            )

        pixel_data = image.pixel_data.copy()
        height, width, channels = pixel_data.shape

        # Process image in blocks
        result = pixel_data.copy()

        # Calculate number of complete blocks
        blocks_h = height // pixel_size
        blocks_w = width // pixel_size

        # Process complete blocks
        for i in range(blocks_h):
            for j in range(blocks_w):
                # Extract block
                y_start = i * pixel_size
                y_end = y_start + pixel_size
                x_start = j * pixel_size
                x_end = x_start + pixel_size

                block = pixel_data[y_start:y_end, x_start:x_end, :]

                # Calculate average color for this block
                avg_color = np.mean(block, axis=(0, 1), dtype=np.float32).astype(
                    np.uint8
                )

                # Fill block with average color
                result[y_start:y_end, x_start:x_end, :] = avg_color

        # Handle edge cases (remaining pixels that don't form complete blocks)
        # Right edge
        if width % pixel_size != 0:
            x_start = blocks_w * pixel_size
            for i in range(blocks_h):
                y_start = i * pixel_size
                y_end = y_start + pixel_size
                block = pixel_data[y_start:y_end, x_start:, :]
                avg_color = np.mean(block, axis=(0, 1), dtype=np.float32).astype(
                    np.uint8
                )
                result[y_start:y_end, x_start:, :] = avg_color

        # Bottom edge
        if height % pixel_size != 0:
            y_start = blocks_h * pixel_size
            for j in range(blocks_w):
                x_start = j * pixel_size
                x_end = x_start + pixel_size
                block = pixel_data[y_start:, x_start:x_end, :]
                avg_color = np.mean(block, axis=(0, 1), dtype=np.float32).astype(
                    np.uint8
                )
                result[y_start:, x_start:x_end, :] = avg_color

        # Bottom-right corner (if both edges exist)
        if height % pixel_size != 0 and width % pixel_size != 0:
            y_start = blocks_h * pixel_size
            x_start = blocks_w * pixel_size
            block = pixel_data[y_start:, x_start:, :]
            avg_color = np.mean(block, axis=(0, 1), dtype=np.float32).astype(
                np.uint8
            )
            result[y_start:, x_start:, :] = avg_color

        return ImageModel(
            width=image.width,
            height=image.height,
            pixel_data=result,
            original_pixel_data=image.original_pixel_data.copy(),
            format=image.format,
            has_alpha=image.has_alpha,
        )

