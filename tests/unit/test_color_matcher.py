"""Unit tests for ColorMatcher service."""

import pytest
from pathlib import Path

from src.services.color_matcher import ColorMatcher


@pytest.fixture
def color_matcher() -> ColorMatcher:
    """Create a ColorMatcher instance for testing."""
    return ColorMatcher()


class TestColorMatcherInitialization:
    """Tests for ColorMatcher initialization."""

    def test_initialization_with_default_path(self) -> None:
        """Test ColorMatcher initializes with default CSV path."""
        matcher = ColorMatcher()
        assert matcher.csv_path.exists()
        assert matcher.csv_path.name == "dmc_colors.csv"
        assert len(matcher.colors) > 0

    def test_initialization_loads_colors(self) -> None:
        """Test ColorMatcher loads colors from CSV."""
        matcher = ColorMatcher()
        assert len(matcher.colors) > 0

        # Check structure of loaded colors
        first_color = matcher.colors[0]
        assert "dmc" in first_color
        assert "name" in first_color
        assert "hex" in first_color
        assert "rgb" in first_color

    def test_initialization_with_custom_path(self, tmp_path: Path) -> None:
        """Test ColorMatcher initializes with custom CSV path."""
        # Create a test CSV file
        csv_file = tmp_path / "test_colors.csv"
        csv_content = """DMC,Name,Color,RED,GRN,BLU
310,Black,#000000,0,0,0
666,Christmas Red,#CC0000,204,0,0"""
        csv_file.write_text(csv_content)

        matcher = ColorMatcher(csv_path=str(csv_file))
        assert len(matcher.colors) == 2
        assert matcher.colors[0]["dmc"] == "310"
        assert matcher.colors[1]["dmc"] == "666"

    def test_initialization_with_missing_file(self, tmp_path: Path) -> None:
        """Test ColorMatcher raises error when CSV file is missing."""
        missing_file = tmp_path / "missing.csv"
        with pytest.raises(FileNotFoundError):
            ColorMatcher(csv_path=str(missing_file))

    def test_initialization_with_invalid_csv(self, tmp_path: Path) -> None:
        """Test ColorMatcher handles invalid CSV gracefully."""
        # Create CSV with invalid data
        csv_file = tmp_path / "invalid.csv"
        csv_file.write_text("Invalid CSV content")

        with pytest.raises(ValueError, match="No valid colors found"):
            ColorMatcher(csv_path=str(csv_file))


class TestParseHex:
    """Tests for _parse_hex method."""

    def test_parse_hex_rgb_with_hash(self, color_matcher: ColorMatcher) -> None:
        """Test _parse_hex parses RGB hex with hash."""
        rgb = color_matcher._parse_hex("#FF5733")
        assert rgb == (255, 87, 51)

    def test_parse_hex_rgb_without_hash(self, color_matcher: ColorMatcher) -> None:
        """Test _parse_hex parses RGB hex without hash."""
        rgb = color_matcher._parse_hex("FF5733")
        assert rgb == (255, 87, 51)

    def test_parse_hex_rgba_with_hash(self, color_matcher: ColorMatcher) -> None:
        """Test _parse_hex parses RGBA hex with hash (ignores alpha)."""
        rgb = color_matcher._parse_hex("#FF5733AA")
        assert rgb == (255, 87, 51)  # Alpha is ignored

    def test_parse_hex_rgba_without_hash(self, color_matcher: ColorMatcher) -> None:
        """Test _parse_hex parses RGBA hex without hash (ignores alpha)."""
        rgb = color_matcher._parse_hex("FF5733AA")
        assert rgb == (255, 87, 51)  # Alpha is ignored

    def test_parse_hex_black(self, color_matcher: ColorMatcher) -> None:
        """Test _parse_hex parses black color."""
        rgb = color_matcher._parse_hex("#000000")
        assert rgb == (0, 0, 0)

    def test_parse_hex_white(self, color_matcher: ColorMatcher) -> None:
        """Test _parse_hex parses white color."""
        rgb = color_matcher._parse_hex("#FFFFFF")
        assert rgb == (255, 255, 255)

    def test_parse_hex_white_rgba(self, color_matcher: ColorMatcher) -> None:
        """Test _parse_hex parses white color with alpha."""
        rgb = color_matcher._parse_hex("#FFFFFF00")
        assert rgb == (255, 255, 255)  # Alpha is ignored

    def test_parse_hex_lowercase(self, color_matcher: ColorMatcher) -> None:
        """Test _parse_hex handles lowercase hex codes."""
        rgb = color_matcher._parse_hex("#ff5733")
        assert rgb == (255, 87, 51)

    def test_parse_hex_with_whitespace(self, color_matcher: ColorMatcher) -> None:
        """Test _parse_hex handles whitespace."""
        rgb = color_matcher._parse_hex("  #FF5733  ")
        assert rgb == (255, 87, 51)

    def test_parse_hex_invalid_length_short(self, color_matcher: ColorMatcher) -> None:
        """Test _parse_hex raises error for too short hex code."""
        with pytest.raises(ValueError, match="Invalid hex code length"):
            color_matcher._parse_hex("#FF57")

    def test_parse_hex_invalid_length_long(self, color_matcher: ColorMatcher) -> None:
        """Test _parse_hex raises error for too long hex code."""
        with pytest.raises(ValueError, match="Invalid hex code length"):
            color_matcher._parse_hex("#FF5733ABCD")

    def test_parse_hex_invalid_characters(self, color_matcher: ColorMatcher) -> None:
        """Test _parse_hex raises error for invalid hex characters."""
        with pytest.raises(ValueError, match="Invalid hex code format"):
            color_matcher._parse_hex("#GGGGGG")

    def test_parse_hex_invalid_rgba_characters(self, color_matcher: ColorMatcher) -> None:
        """Test _parse_hex ignores invalid alpha characters (alpha is not validated)."""
        # Alpha channel is ignored, so invalid alpha characters don't cause errors
        # This is expected behavior - we only parse RGB
        rgb = color_matcher._parse_hex("#FF5733GG")
        assert rgb == (255, 87, 51)  # RGB part is valid, alpha is ignored


class TestGetClosestToHex:
    """Tests for get_closest_to_hex method."""

    def test_get_closest_to_hex_rgb(self, color_matcher: ColorMatcher) -> None:
        """Test get_closest_to_hex with RGB hex code."""
        result = color_matcher.get_closest_to_hex("#000000")
        assert "dmc" in result
        assert "name" in result
        assert "hex" in result
        assert "rgb" in result
        assert "distance" in result
        assert isinstance(result["dmc"], str)
        assert isinstance(result["name"], str)
        assert isinstance(result["rgb"], tuple)
        assert len(result["rgb"]) == 3
        assert isinstance(result["distance"], float)

    def test_get_closest_to_hex_rgba(self, color_matcher: ColorMatcher) -> None:
        """Test get_closest_to_hex with RGBA hex code."""
        result = color_matcher.get_closest_to_hex("#000000FF")
        assert "dmc" in result
        assert "name" in result
        assert "hex" in result
        assert "rgb" in result
        assert "distance" in result

    def test_get_closest_to_hex_without_hash(self, color_matcher: ColorMatcher) -> None:
        """Test get_closest_to_hex works without hash prefix."""
        result = color_matcher.get_closest_to_hex("FF5733")
        assert "dmc" in result
        # Result RGB is the DMC match RGB, not the input RGB
        assert isinstance(result["rgb"], tuple)
        assert len(result["rgb"]) == 3
        assert all(0 <= val <= 255 for val in result["rgb"])

    def test_get_closest_to_hex_black(self, color_matcher: ColorMatcher) -> None:
        """Test get_closest_to_hex finds match for black."""
        result = color_matcher.get_closest_to_hex("#000000")
        # Should find a dark color (likely black DMC 310)
        assert result["dmc"] is not None
        assert result["distance"] >= 0

    def test_get_closest_to_hex_white(self, color_matcher: ColorMatcher) -> None:
        """Test get_closest_to_hex finds match for white."""
        result = color_matcher.get_closest_to_hex("#FFFFFF")
        # Should find a light color
        assert result["dmc"] is not None
        assert result["distance"] >= 0

    def test_get_closest_to_hex_red(self, color_matcher: ColorMatcher) -> None:
        """Test get_closest_to_hex finds match for red."""
        result = color_matcher.get_closest_to_hex("#FF0000")
        assert result["dmc"] is not None
        assert result["distance"] >= 0

    def test_get_closest_to_hex_invalid_hex(self, color_matcher: ColorMatcher) -> None:
        """Test get_closest_to_hex raises error for invalid hex."""
        with pytest.raises(ValueError, match="Invalid hex code"):
            color_matcher.get_closest_to_hex("INVALID")

    def test_get_closest_to_hex_short_hex(self, color_matcher: ColorMatcher) -> None:
        """Test get_closest_to_hex raises error for too short hex."""
        with pytest.raises(ValueError, match="Invalid hex code"):
            color_matcher.get_closest_to_hex("#FF")

    def test_get_closest_to_hex_returns_consistent_results(self, color_matcher: ColorMatcher) -> None:
        """Test get_closest_to_hex returns consistent results for same color."""
        result1 = color_matcher.get_closest_to_hex("#FF5733")
        result2 = color_matcher.get_closest_to_hex("#FF5733")
        assert result1["dmc"] == result2["dmc"]
        assert result1["name"] == result2["name"]
        assert result1["distance"] == result2["distance"]

    def test_get_closest_to_hex_rgb_vs_rgba_same_result(self, color_matcher: ColorMatcher) -> None:
        """Test get_closest_to_hex returns same result for RGB and RGBA of same color."""
        result_rgb = color_matcher.get_closest_to_hex("#FF5733")
        result_rgba = color_matcher.get_closest_to_hex("#FF5733FF")
        # Should find the same DMC match since alpha is ignored
        assert result_rgb["dmc"] == result_rgba["dmc"]
        assert result_rgb["name"] == result_rgba["name"]
        assert result_rgb["distance"] == result_rgba["distance"]

    def test_get_closest_to_hex_distance_is_positive(self, color_matcher: ColorMatcher) -> None:
        """Test get_closest_to_hex returns positive distance."""
        result = color_matcher.get_closest_to_hex("#FF5733")
        assert result["distance"] >= 0

    def test_get_closest_to_hex_returns_valid_rgb(self, color_matcher: ColorMatcher) -> None:
        """Test get_closest_to_hex returns valid RGB tuple."""
        result = color_matcher.get_closest_to_hex("#FF5733")
        rgb = result["rgb"]
        assert isinstance(rgb, tuple)
        assert len(rgb) == 3
        assert all(0 <= val <= 255 for val in rgb)

