"""Background removal service using rembg AI model."""

from typing import Any, Dict, List, Optional, Union

import numpy as np
from PIL import Image as PILImage

try:
    from rembg import remove, new_session
except ImportError:
    remove = None  # type: ignore
    new_session = None  # type: ignore

from src.models.image_model import ImageModel
from src.services import BackgroundRemovalError


class BackgroundRemover:
    """Service for removing image backgrounds using rembg AI model.

    Supports multiple models including:
    - 'u2net' (default): Automatic background removal, no prompts needed
    - 'sam': Segment Anything Model, requires prompts for best results
    - Other rembg-supported models: 'u2netp', 'u2net_human_seg', 'silueta', etc.
    """

    def __init__(self, model: str = "u2net") -> None:
        """
        Initialize background remover with specified model.

        Args:
            model: Model name to use. Options include:
                - 'u2net' (default): Best for automatic background removal
                - 'sam': Segment Anything Model (requires prompts)
                - 'u2netp': Lightweight version of u2net
                - 'u2net_human_seg': Optimized for human subjects
                - 'silueta': Alternative model
        """
        self._model = model
        self._session: Optional[object] = None

    def remove_background(
        self,
        image: ImageModel,
        prompts: Optional[List[Dict[str, Any]]] = None,
    ) -> ImageModel:
        """
        Remove background from image using rembg AI model.

        Args:
            image: ImageModel to process
            prompts: Optional list of prompts for SAM model. Each prompt is a dict with:
                - 'type': 'rectangle' or 'point'
                - 'data': For rectangle: [x1, y1, x2, y2], For point: [x, y]
                - 'label': 1 for foreground, 0 for background
                Example: [
                    {"type": "rectangle", "data": [100, 100, 300, 400], "label": 1},
                    {"type": "point", "data": [200, 200], "label": 1}
                ]

        Returns:
            New ImageModel with background removed (transparent alpha channel)

        Raises:
            BackgroundRemovalError: If processing fails
            ValueError: If image is invalid
        """


        if image is None:
            raise ValueError("Invalid image. Please load an image first.")

        if remove is None:
            raise BackgroundRemovalError(
                "Background removal requires rembg library. Please install it.",
                user_message="Background removal requires rembg library. Please install it using: pip install rembg",
            )

        try:
            # Convert ImageModel.pixel_data (NumPy array) to PIL Image
            # rembg expects PIL Image input
            if image.has_alpha:
                # RGBA image
                pil_image = PILImage.fromarray(image.pixel_data, "RGBA")
            else:
                # RGB image - convert to RGB mode for PIL
                pil_image = PILImage.fromarray(image.pixel_data, "RGB")

            # Call rembg.remove() with PIL Image
            # Use session for models that require it (like SAM)
            if self._model != "u2net" and new_session is not None:
                # Create session if not already created (for non-default models)
                if self._session is None:
                    try:
                        self._session = new_session(self._model)
                    except Exception as e:
                        raise BackgroundRemovalError(
                            f"Failed to initialize {self._model} model: {str(e)}",
                            user_message=f"Failed to initialize {self._model} model. Please ensure the model is available.",
                        ) from e
                # Pass prompts directly as keyword argument for SAM model
                # rembg.remove() passes **kwargs to session.predict(), which expects sam_prompt
                if prompts and self._model == "sam":
                    result_pil = remove(pil_image, session=self._session, sam_prompt=prompts)
                else:
                    result_pil = remove(pil_image, session=self._session)
            else:
                # Default u2net model - no session needed, prompts ignored
                if prompts:
                    # Warn that prompts are only for SAM
                    pass  # Prompts ignored for non-SAM models
                result_pil = remove(pil_image)

            # Convert result back to NumPy array
            result_array = np.array(result_pil)

            # Ensure result has alpha channel (RGBA format)
            # rembg should always return RGBA, but we'll ensure it
            if result_array.shape[2] == 3:
                # If somehow RGB, add alpha channel
                height, width = result_array.shape[:2]
                alpha = np.full((height, width, 1), 255, dtype=np.uint8)
                result_array = np.concatenate([result_array, alpha], axis=2)

            # Create new ImageModel with processed pixel data
            # Preserve original dimensions and format metadata
            return ImageModel(
                width=image.width,
                height=image.height,
                pixel_data=result_array,
                original_pixel_data=image.original_pixel_data.copy(),
                format=image.format,
                has_alpha=True,  # Always RGBA after background removal
            )

        except Exception as e:
            # Handle rembg processing errors
            error_msg = f"rembg processing failed: {str(e)}"
            raise BackgroundRemovalError(
                error_msg,
                user_message="Failed to remove background. Please try again or use a different image.",
            ) from e

