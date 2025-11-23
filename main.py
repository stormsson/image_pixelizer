"""Main entry point for Image Pixelizer application."""

import os
import sys
from dotenv import load_dotenv
load_dotenv()

from PySide6.QtWidgets import QApplication

from src.controllers.main_controller import MainController
from src.models.settings_model import SettingsModel
from src.services.background_remover import BackgroundRemover
from src.services.color_reducer import ColorReducer
from src.services.image_loader import ImageLoader
from src.services.image_saver import ImageSaver
from src.services.openai_background_remover import OpenAIBackgroundRemover
from src.services.pixelizer import Pixelizer
from src.views.main_window import MainWindow


def main() -> None:
    """Run the Image Pixelizer application."""
    app = QApplication(sys.argv)

    # Initialize models
    settings_model = SettingsModel()

    # Initialize services
    image_loader = ImageLoader()
    pixelizer = Pixelizer()
    color_reducer = ColorReducer()
    image_saver = ImageSaver()
    background_remover = BackgroundRemover(model=os.getenv('REMBG_MODEL', 'sam'))

    # Initialize OpenAI background remover (optional - only if API key is configured)
    openai_background_remover = None
    try:
        openai_background_remover = OpenAIBackgroundRemover()
    except Exception as e:
        # If OpenAI API key is not configured, continue without automatic background removal
        print(f"Warning: OpenAI background removal not available: {e}")

    # Initialize controller
    controller = MainController(
        settings_model=settings_model,
        image_loader=image_loader,
        pixelizer=pixelizer,
        color_reducer=color_reducer,
        image_saver=image_saver,
        background_remover=background_remover,
        openai_background_remover=openai_background_remover,
    )

    # Initialize and show main window
    window = MainWindow(controller)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

