"""Unit tests for OpenAI background remover service."""

import base64
import io
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest
from PIL import Image as PILImage

from src.models.image_model import ImageModel
from src.services import OpenAIBackgroundRemovalError
from src.services.openai_background_remover import OpenAIBackgroundRemover


class TestOpenAIBackgroundRemovalError:
    """Tests for OpenAIBackgroundRemovalError exception."""

    def test_exception_creation_with_user_message(self) -> None:
        """Test exception creation with both technical and user messages."""
        error = OpenAIBackgroundRemovalError(
            technical_message="Technical error",
            user_message="User-friendly error",
        )
        assert str(error) == "Technical error"
        assert error.technical_message == "Technical error"
        assert error.user_message == "User-friendly error"

    def test_exception_creation_without_user_message(self) -> None:
        """Test exception creation with only technical message."""
        error = OpenAIBackgroundRemovalError(technical_message="Technical error")
        assert str(error) == "Technical error"
        assert error.technical_message == "Technical error"
        assert error.user_message == "Technical error"  # Falls back to technical message

    def test_exception_has_technical_message_attribute(self) -> None:
        """Test that exception has technical_message attribute."""
        error = OpenAIBackgroundRemovalError(
            technical_message="Technical error",
            user_message="User error",
        )
        assert hasattr(error, "technical_message")
        assert error.technical_message == "Technical error"


class TestAPICeyLoading:
    """Tests for API key loading and validation."""

    @patch.dict(os.environ, {}, clear=True)
    def test_load_from_env_var(self) -> None:
        """Test loading API key from environment variable."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test123"}):
            remover = OpenAIBackgroundRemover()
            assert remover._api_key == "sk-test123"

    def test_load_from_parameter(self) -> None:
        """Test loading API key from constructor parameter."""
        remover = OpenAIBackgroundRemover(api_key="sk-param123")
        assert remover._api_key == "sk-param123"

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_key_error(self) -> None:
        """Test error when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(OpenAIBackgroundRemovalError) as exc_info:
                OpenAIBackgroundRemover()
            assert "OpenAI API key not found" in exc_info.value.user_message
            assert "OPENAI_API_KEY" in exc_info.value.user_message

    @patch.dict(os.environ, {}, clear=True)
    def test_invalid_key_format_error(self) -> None:
        """Test error when API key format is invalid."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "invalid-key"}):
            with pytest.raises(OpenAIBackgroundRemovalError) as exc_info:
                OpenAIBackgroundRemover()
            assert "Invalid OpenAI API key" in exc_info.value.user_message

    @patch.dict(os.environ, {}, clear=True)
    def test_empty_key_error(self) -> None:
        """Test error when API key is empty string."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            with pytest.raises(OpenAIBackgroundRemovalError) as exc_info:
                OpenAIBackgroundRemover()
            assert "OpenAI API key not found" in exc_info.value.user_message


class TestImageInputFormatConversion:
    """Tests for image input format conversion (T052)."""

    @pytest.fixture
    def remover(self) -> OpenAIBackgroundRemover:
        """Create OpenAIBackgroundRemover instance for testing."""
        return OpenAIBackgroundRemover(api_key="sk-test123")

    def test_convert_file_path_to_pil(self, remover: OpenAIBackgroundRemover, sample_image_path: Path) -> None:
        """Test converting file path to PIL Image."""
        pil_image = remover._convert_input_to_pil(str(sample_image_path))
        assert isinstance(pil_image, PILImage.Image)
        assert pil_image.size == (100, 100)
        assert pil_image.mode in ("RGB", "RGBA")

    def test_convert_path_object_to_pil(self, remover: OpenAIBackgroundRemover, sample_image_path: Path) -> None:
        """Test converting Path object to PIL Image."""
        pil_image = remover._convert_input_to_pil(sample_image_path)
        assert isinstance(pil_image, PILImage.Image)
        assert pil_image.size == (100, 100)

    def test_convert_bytes_to_pil(self, remover: OpenAIBackgroundRemover) -> None:
        """Test converting bytes to PIL Image."""
        # Create image bytes
        image = PILImage.new("RGB", (50, 50), color=(255, 0, 0))
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()

        pil_image = remover._convert_input_to_pil(image_bytes)
        assert isinstance(pil_image, PILImage.Image)
        assert pil_image.size == (50, 50)

    def test_convert_pil_image_to_pil(self, remover: OpenAIBackgroundRemover) -> None:
        """Test converting PIL Image to PIL Image (no-op)."""
        original_image = PILImage.new("RGB", (75, 75), color=(0, 255, 0))
        pil_image = remover._convert_input_to_pil(original_image)
        assert pil_image is original_image or isinstance(pil_image, PILImage.Image)
        assert pil_image.size == (75, 75)

    def test_convert_numpy_array_to_pil(self, remover: OpenAIBackgroundRemover) -> None:
        """Test converting NumPy array to PIL Image."""
        array = np.zeros((60, 60, 3), dtype=np.uint8)
        array[:, :] = [128, 64, 192]
        pil_image = remover._convert_input_to_pil(array)
        assert isinstance(pil_image, PILImage.Image)
        assert pil_image.size == (60, 60)

    def test_convert_numpy_array_rgba_to_pil(self, remover: OpenAIBackgroundRemover) -> None:
        """Test converting RGBA NumPy array to PIL Image."""
        array = np.zeros((40, 40, 4), dtype=np.uint8)
        array[:, :] = [128, 64, 192, 255]
        pil_image = remover._convert_input_to_pil(array)
        assert isinstance(pil_image, PILImage.Image)
        assert pil_image.size == (40, 40)

    def test_convert_image_model_to_pil(self, remover: OpenAIBackgroundRemover, sample_image_model: ImageModel) -> None:
        """Test converting ImageModel to PIL Image."""
        pil_image = remover._convert_input_to_pil(sample_image_model)
        assert isinstance(pil_image, PILImage.Image)
        assert pil_image.size == (100, 100)

    def test_invalid_file_path_error(self, remover: OpenAIBackgroundRemover) -> None:
        """Test error with invalid file path."""
        with pytest.raises(ValueError) as exc_info:
            remover._convert_input_to_pil("/nonexistent/path/image.png")
        assert "Failed to load image from path" in str(exc_info.value)

    def test_invalid_bytes_error(self, remover: OpenAIBackgroundRemover) -> None:
        """Test error with invalid bytes."""
        with pytest.raises(ValueError) as exc_info:
            remover._convert_input_to_pil(b"invalid image data")
        assert "Failed to load image from bytes" in str(exc_info.value)

    def test_invalid_numpy_array_shape_error(self, remover: OpenAIBackgroundRemover) -> None:
        """Test error with invalid NumPy array shape."""
        invalid_array = np.zeros((50, 50), dtype=np.uint8)  # 2D instead of 3D
        with pytest.raises(ValueError) as exc_info:
            remover._convert_input_to_pil(invalid_array)
        assert "NumPy array must have shape" in str(exc_info.value)

    def test_invalid_numpy_array_channels_error(self, remover: OpenAIBackgroundRemover) -> None:
        """Test error with invalid NumPy array channels."""
        invalid_array = np.zeros((50, 50, 5), dtype=np.uint8)  # 5 channels
        with pytest.raises(ValueError) as exc_info:
            remover._convert_input_to_pil(invalid_array)
        assert "NumPy array must have shape" in str(exc_info.value)

    def test_unsupported_type_error(self, remover: OpenAIBackgroundRemover) -> None:
        """Test error with unsupported input type."""
        with pytest.raises(ValueError) as exc_info:
            remover._convert_input_to_pil(12345)  # int is not supported
        assert "Unsupported input type" in str(exc_info.value)


class TestImageValidation:
    """Tests for image validation (T053)."""

    @pytest.fixture
    def remover(self) -> OpenAIBackgroundRemover:
        """Create OpenAIBackgroundRemover instance for testing."""
        return OpenAIBackgroundRemover(api_key="sk-test123")

    def test_validate_valid_image(self, remover: OpenAIBackgroundRemover) -> None:
        """Test validation of valid image."""
        image = PILImage.new("RGB", (100, 100), color=(255, 0, 0))
        # Should not raise
        remover._validate_image(image)

    def test_validate_max_size_image(self, remover: OpenAIBackgroundRemover) -> None:
        """Test validation of image at maximum size (2000x2000)."""
        image = PILImage.new("RGB", (2000, 2000), color=(255, 0, 0))
        # Should not raise
        remover._validate_image(image)

    def test_validate_exceeds_width_limit(self, remover: OpenAIBackgroundRemover) -> None:
        """Test validation error when width exceeds 2000px."""
        image = PILImage.new("RGB", (2001, 100), color=(255, 0, 0))
        with pytest.raises(ValueError) as exc_info:
            remover._validate_image(image)
        assert "2000x2000px limit" in str(exc_info.value)

    def test_validate_exceeds_height_limit(self, remover: OpenAIBackgroundRemover) -> None:
        """Test validation error when height exceeds 2000px."""
        image = PILImage.new("RGB", (100, 2001), color=(255, 0, 0))
        with pytest.raises(ValueError) as exc_info:
            remover._validate_image(image)
        assert "2000x2000px limit" in str(exc_info.value)

    def test_validate_zero_width_error(self, remover: OpenAIBackgroundRemover) -> None:
        """Test validation error when width is zero."""
        image = PILImage.new("RGB", (0, 100), color=(255, 0, 0))
        with pytest.raises(ValueError) as exc_info:
            remover._validate_image(image)
        assert "must be greater than 0" in str(exc_info.value)

    def test_validate_zero_height_error(self, remover: OpenAIBackgroundRemover) -> None:
        """Test validation error when height is zero."""
        image = PILImage.new("RGB", (100, 0), color=(255, 0, 0))
        with pytest.raises(ValueError) as exc_info:
            remover._validate_image(image)
        assert "must be greater than 0" in str(exc_info.value)


class TestBase64Encoding:
    """Tests for base64 image encoding (T054)."""

    @pytest.fixture
    def remover(self) -> OpenAIBackgroundRemover:
        """Create OpenAIBackgroundRemover instance for testing."""
        return OpenAIBackgroundRemover(api_key="sk-test123")

    def test_encode_rgb_image_to_base64(self, remover: OpenAIBackgroundRemover) -> None:
        """Test encoding RGB PIL Image to base64."""
        image = PILImage.new("RGB", (50, 50), color=(255, 128, 64))
        base64_str = remover._encode_image_to_base64(image)
        assert base64_str.startswith("data:image/png;base64,")
        # Verify it's valid base64
        base64_data = base64_str.replace("data:image/png;base64,", "")
        decoded = base64.b64decode(base64_data)
        assert len(decoded) > 0

    def test_encode_rgba_image_to_base64(self, remover: OpenAIBackgroundRemover) -> None:
        """Test encoding RGBA PIL Image to base64."""
        image = PILImage.new("RGBA", (50, 50), color=(255, 128, 64, 200))
        base64_str = remover._encode_image_to_base64(image)
        assert base64_str.startswith("data:image/png;base64,")
        # Verify format preservation
        base64_data = base64_str.replace("data:image/png;base64,", "")
        decoded = base64.b64decode(base64_data)
        decoded_image = PILImage.open(io.BytesIO(decoded))
        assert decoded_image.mode == "RGBA"

    def test_base64_format_preservation(self, remover: OpenAIBackgroundRemover) -> None:
        """Test that base64 encoding preserves image format."""
        image = PILImage.new("RGB", (30, 30), color=(100, 200, 50))
        base64_str = remover._encode_image_to_base64(image)
        # Decode and verify
        base64_data = base64_str.replace("data:image/png;base64,", "")
        decoded = base64.b64decode(base64_data)
        decoded_image = PILImage.open(io.BytesIO(decoded))
        assert decoded_image.size == (30, 30)
        assert decoded_image.mode in ("RGB", "RGBA")


class TestAPIRequestConstruction:
    """Tests for API request construction (T055)."""

    @pytest.fixture
    def remover(self) -> OpenAIBackgroundRemover:
        """Create OpenAIBackgroundRemover instance for testing."""
        return OpenAIBackgroundRemover(api_key="sk-test123")

    @patch("src.services.openai_background_remover.OpenAI")
    def test_api_request_contains_prompt(self, mock_openai_class: Mock, remover: OpenAIBackgroundRemover) -> None:
        """Test that API request contains correct prompt text."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response

        image = PILImage.new("RGB", (50, 50), color=(255, 0, 0))
        base64_image = remover._encode_image_to_base64(image)
        import io
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()
        remover._call_openai_api(base64_image, image_bytes)

        # Verify API was called
        assert mock_client.chat.completions.create.called
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert len(messages[0]["content"]) == 2
        assert messages[0]["content"][0]["type"] == "text"
        assert "remove the background from the attached file" in messages[0]["content"][0]["text"]

    @patch("src.services.openai_background_remover.OpenAI")
    def test_api_request_contains_image(self, mock_openai_class: Mock, remover: OpenAIBackgroundRemover) -> None:
        """Test that API request contains base64-encoded image."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response

        image = PILImage.new("RGB", (50, 50), color=(255, 0, 0))
        base64_image = remover._encode_image_to_base64(image)
        import io
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()
        remover._call_openai_api(base64_image, image_bytes)

        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        assert messages[0]["content"][1]["type"] == "image_url"
        assert "data:image/png;base64," in messages[0]["content"][1]["image_url"]["url"]

    @patch("src.services.openai_background_remover.OpenAI")
    def test_api_request_model_selection(self, mock_openai_class: Mock, remover: OpenAIBackgroundRemover) -> None:
        """Test that API request uses correct model (gpt-5.1)."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response

        image = PILImage.new("RGB", (50, 50), color=(255, 0, 0))
        base64_image = remover._encode_image_to_base64(image)
        import io
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()
        remover._call_openai_api(base64_image, image_bytes)

        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "gpt-5.1"


class TestAPIResponseParsing:
    """Tests for API response parsing (T056)."""

    @pytest.fixture
    def remover(self) -> OpenAIBackgroundRemover:
        """Create OpenAIBackgroundRemover instance for testing."""
        return OpenAIBackgroundRemover(api_key="sk-test123")

    @patch("src.services.openai_background_remover.OpenAI")
    def test_parse_text_response(self, mock_openai_class: Mock, remover: OpenAIBackgroundRemover) -> None:
        """Test parsing text response from API."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "The image contains a person with a blue background"
        mock_client.chat.completions.create.return_value = mock_response

        image = PILImage.new("RGB", (50, 50), color=(255, 0, 0))
        base64_image = remover._encode_image_to_base64(image)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()
        response, _ = remover._call_openai_api(base64_image, image_bytes)

        assert response == "The image contains a person with a blue background"

    @patch("src.services.openai_background_remover.OpenAI")
    def test_parse_empty_response(self, mock_openai_class: Mock, remover: OpenAIBackgroundRemover) -> None:
        """Test parsing empty response from API."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = None
        mock_client.chat.completions.create.return_value = mock_response

        image = PILImage.new("RGB", (50, 50), color=(255, 0, 0))
        base64_image = remover._encode_image_to_base64(image)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()
        response, _ = remover._call_openai_api(base64_image, image_bytes)

        assert response == ""


class TestErrorHandling:
    """Tests for error handling (T057)."""

    @pytest.fixture
    def remover(self) -> OpenAIBackgroundRemover:
        """Create OpenAIBackgroundRemover instance for testing."""
        return OpenAIBackgroundRemover(api_key="sk-test123")

    @patch("src.services.openai_background_remover.OpenAI")
    def test_network_error_handling(self, mock_openai_class: Mock, remover: OpenAIBackgroundRemover) -> None:
        """Test handling of network errors."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = ConnectionError("Network connection failed")

        image = PILImage.new("RGB", (50, 50), color=(255, 0, 0))
        base64_image = remover._encode_image_to_base64(image)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()

        with pytest.raises(OpenAIBackgroundRemovalError) as exc_info:
            remover._call_openai_api(base64_image, image_bytes)
        assert "Network error" in exc_info.value.user_message or "connection" in exc_info.value.user_message.lower()

    @patch("src.services.openai_background_remover.OpenAI")
    def test_rate_limit_error_handling(self, mock_openai_class: Mock, remover: OpenAIBackgroundRemover) -> None:
        """Test handling of rate limit errors."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        # Simulate rate limit error (429 status or rate_limit in message)
        error = Exception("Rate limit exceeded: 429")
        error.response = MagicMock()
        error.response.status_code = 429
        mock_client.chat.completions.create.side_effect = error

        image = PILImage.new("RGB", (50, 50), color=(255, 0, 0))
        base64_image = remover._encode_image_to_base64(image)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()

        with pytest.raises(OpenAIBackgroundRemovalError) as exc_info:
            remover._call_openai_api(base64_image, image_bytes)
        # Check that error message contains rate limit info (handled in _call_openai_api)
        assert "rate limit" in exc_info.value.user_message.lower() or "429" in str(exc_info.value)

    @patch("src.services.openai_background_remover.OpenAI")
    def test_api_error_handling(self, mock_openai_class: Mock, remover: OpenAIBackgroundRemover) -> None:
        """Test handling of general API errors."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API error: Invalid request")

        image = PILImage.new("RGB", (50, 50), color=(255, 0, 0))
        base64_image = remover._encode_image_to_base64(image)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()

        with pytest.raises(OpenAIBackgroundRemovalError) as exc_info:
            remover._call_openai_api(base64_image, image_bytes)
        assert "Failed to process image" in exc_info.value.user_message or "API" in exc_info.value.user_message


class TestOptionalFileSaving:
    """Tests for optional file saving (T058)."""

    @pytest.fixture
    def remover(self) -> OpenAIBackgroundRemover:
        """Create OpenAIBackgroundRemover instance for testing."""
        return OpenAIBackgroundRemover(api_key="sk-test123")

    @patch("rembg.remove")
    @patch("src.services.openai_background_remover.OpenAI")
    def test_save_path_provided_saves_file(
        self, mock_openai_class: Mock, mock_rembg_remove: Mock, remover: OpenAIBackgroundRemover, tmp_path: Path
    ) -> None:
        """Test that save_path provided saves file and returns ImageModel."""
        # Mock OpenAI API
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response

        # Mock rembg
        mock_output = PILImage.new("RGBA", (100, 100), color=(255, 87, 51, 255))
        mock_rembg_remove.return_value = mock_output

        image = PILImage.new("RGB", (100, 100), color=(255, 0, 0))
        save_path = tmp_path / "output.png"

        result = remover.remove_background(image, save_path=str(save_path))

        assert save_path.exists()
        assert isinstance(result, ImageModel)
        assert result.has_alpha is True

    @patch("rembg.remove")
    @patch("src.services.openai_background_remover.OpenAI")
    def test_no_save_path_returns_image_data(
        self, mock_openai_class: Mock, mock_rembg_remove: Mock, remover: OpenAIBackgroundRemover
    ) -> None:
        """Test that no save_path returns image data without saving."""
        # Mock OpenAI API
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response

        # Mock rembg
        mock_output = PILImage.new("RGBA", (100, 100), color=(255, 87, 51, 255))
        mock_rembg_remove.return_value = mock_output

        image = PILImage.new("RGB", (100, 100), color=(255, 0, 0))

        result = remover.remove_background(image)

        assert isinstance(result, PILImage.Image)
        assert result.mode == "RGBA"


class TestOutputFormatHandling:
    """Tests for output format handling (T059)."""

    @pytest.fixture
    def remover(self) -> OpenAIBackgroundRemover:
        """Create OpenAIBackgroundRemover instance for testing."""
        return OpenAIBackgroundRemover(api_key="sk-test123")

    @patch("rembg.remove")
    @patch("src.services.openai_background_remover.OpenAI")
    def test_imagemodel_return_for_app_integration(
        self, mock_openai_class: Mock, mock_rembg_remove: Mock, remover: OpenAIBackgroundRemover, sample_image_model: ImageModel
    ) -> None:
        """Test that ImageModel input returns ImageModel for app integration."""
        # Mock OpenAI API
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response

        # Mock rembg
        mock_output = PILImage.new("RGBA", (100, 100), color=(255, 87, 51, 255))
        mock_rembg_remove.return_value = mock_output

        result = remover.remove_background(sample_image_model)

        assert isinstance(result, ImageModel)
        assert result.width == sample_image_model.width
        assert result.height == sample_image_model.height
        assert result.has_alpha is True

    @patch("rembg.remove")
    @patch("src.services.openai_background_remover.OpenAI")
    def test_pil_image_return_for_autonomous_use(
        self, mock_openai_class: Mock, mock_rembg_remove: Mock, remover: OpenAIBackgroundRemover
    ) -> None:
        """Test that PIL Image input returns PIL Image for autonomous use."""
        # Mock OpenAI API
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response

        # Mock rembg
        mock_output = PILImage.new("RGBA", (100, 100), color=(255, 87, 51, 255))
        mock_rembg_remove.return_value = mock_output

        image = PILImage.new("RGB", (100, 100), color=(255, 0, 0))
        result = remover.remove_background(image)

        assert isinstance(result, PILImage.Image)
        assert result.mode == "RGBA"

    @patch("rembg.remove")
    @patch("src.services.openai_background_remover.OpenAI")
    def test_numpy_array_return_for_autonomous_use(
        self, mock_openai_class: Mock, mock_rembg_remove: Mock, remover: OpenAIBackgroundRemover
    ) -> None:
        """Test that NumPy array input returns NumPy array for autonomous use."""
        # Mock OpenAI API
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response

        # Mock rembg
        mock_output = PILImage.new("RGBA", (100, 100), color=(255, 87, 51, 255))
        mock_rembg_remove.return_value = mock_output

        array = np.zeros((100, 100, 3), dtype=np.uint8)
        result = remover.remove_background(array)

        assert isinstance(result, np.ndarray)
        assert result.shape == (100, 100, 4)  # RGBA

