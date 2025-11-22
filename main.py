"""Main entry point for Image Pixelizer application."""

import sys

from PySide6.QtWidgets import QApplication

from src.controllers.main_controller import MainController
from src.models.settings_model import SettingsModel
from src.services.color_reducer import ColorReducer
from src.services.image_loader import ImageLoader
from src.services.image_saver import ImageSaver
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

    # Initialize controller
    controller = MainController(
        settings_model=settings_model,
        image_loader=image_loader,
        pixelizer=pixelizer,
        color_reducer=color_reducer,
        image_saver=image_saver,
    )

    # Initialize and show main window
    window = MainWindow(controller)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

