import csv
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class ColorMatcher:
    """Service for finding closest DMC color match to a given hex color code."""

    def __init__(self, csv_path: Optional[str] = None):
        """
        Initialize ColorMatcher and load DMC colors from CSV.

        Args:
            csv_path: Optional path to DMC colors CSV file.
                     Defaults to data/dmc_colors.csv relative to project root.
        """
        if csv_path is None:
            # Default to data/dmc_colors.csv relative to project root
            project_root = Path(__file__).parent.parent.parent
            csv_path = project_root / "data" / "dmc_colors.csv"

        self.csv_path = Path(csv_path)
        self.colors: List[Dict[str, any]] = []
        self._load_colors()

    def _load_colors(self) -> None:
        """Load and parse DMC colors from CSV file."""
        if not self.csv_path.exists():
            raise FileNotFoundError(f"DMC colors CSV not found: {self.csv_path}")

        self.colors = []
        with open(self.csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Extract hex code from Color column (format: #RRGGBB)
                    hex_code = row["Color"].strip()
                    if not hex_code.startswith("#"):
                        hex_code = "#" + hex_code

                    # Parse RGB values
                    rgb = (
                        int(row["RED"]),
                        int(row["GRN"]),
                        int(row["BLU"]),
                    )

                    self.colors.append(
                        {
                            "dmc": row["DMC"],
                            "name": row["Name"],
                            "hex": hex_code,
                            "rgb": rgb,
                        }
                    )
                except (ValueError, KeyError) as e:
                    # Skip invalid rows
                    continue

        if not self.colors:
            raise ValueError("No valid colors found in CSV file")

    def _parse_hex(self, hex_code: str) -> Tuple[int, int, int]:
        """
        Parse hex color code to RGB tuple.

        Args:
            hex_code: Hex color code in format #RRGGBB, RRGGBB, #RRGGBBAA, or RRGGBBAA

        Returns:
            RGB tuple (r, g, b) with values 0-255. Alpha channel is ignored if present.

        Raises:
            ValueError: If hex code is invalid
        """
        hex_code = hex_code.strip().upper()
        if hex_code.startswith("#"):
            hex_code = hex_code[1:]

        if len(hex_code) not in (6, 8):
            raise ValueError(f"Invalid hex code length: {hex_code} (expected 6 or 8 characters)")

        try:
            r = int(hex_code[0:2], 16)
            g = int(hex_code[2:4], 16)
            b = int(hex_code[4:6], 16)
            # Alpha channel (if present) is ignored
            return (r, g, b)
        except ValueError as e:
            raise ValueError(f"Invalid hex code format: {hex_code}") from e

    def _rgb_to_xyz(self, rgb: Tuple[int, int, int]) -> np.ndarray:
        """
        Convert RGB to XYZ color space (sRGB).

        Args:
            rgb: RGB tuple (0-255 range)

        Returns:
            XYZ array [x, y, z]
        """
        # Normalize to 0-1 range
        r, g, b = [x / 255.0 for x in rgb]

        # Apply gamma correction (sRGB)
        def gamma_correct(c):
            if c <= 0.04045:
                return c / 12.92
            return ((c + 0.055) / 1.055) ** 2.4

        r = gamma_correct(r)
        g = gamma_correct(g)
        b = gamma_correct(b)

        # sRGB to XYZ transformation matrix (D65 white point)
        matrix = np.array(
            [
                [0.4124564, 0.3575761, 0.1804375],
                [0.2126729, 0.7151522, 0.0721750],
                [0.0193339, 0.1191920, 0.9503041],
            ]
        )

        rgb_vec = np.array([r, g, b])
        xyz = matrix @ rgb_vec
        return xyz

    def _xyz_to_lab(self, xyz: np.ndarray) -> np.ndarray:
        """
        Convert XYZ to LAB color space (CIE 1976).

        Args:
            xyz: XYZ array [x, y, z]

        Returns:
            LAB array [l, a, b]
        """
        # D65 white point (sRGB standard)
        x_n, y_n, z_n = 0.95047, 1.00000, 1.08883

        # Normalize by white point
        x = xyz[0] / x_n
        y = xyz[1] / y_n
        z = xyz[2] / z_n

        # Apply f function
        def f(t):
            if t > (6.0 / 29.0) ** 3:
                return t ** (1.0 / 3.0)
            return (1.0 / 3.0) * ((29.0 / 6.0) ** 2) * t + (4.0 / 29.0)

        fx = f(x)
        fy = f(y)
        fz = f(z)

        # Calculate LAB
        l = 116.0 * fy - 16.0
        a = 500.0 * (fx - fy)
        b = 200.0 * (fy - fz)

        return np.array([l, a, b])

    def _rgb_to_lab(self, rgb: Tuple[int, int, int]) -> np.ndarray:
        """
        Convert RGB to LAB color space.

        Args:
            rgb: RGB tuple (0-255 range)

        Returns:
            LAB array [l, a, b]
        """
        xyz = self._rgb_to_xyz(rgb)
        return self._xyz_to_lab(xyz)

    def _delta_e(self, lab1: np.ndarray, lab2: np.ndarray) -> float:
        """
        Calculate Delta E (Euclidean distance) in LAB color space.

        Args:
            lab1: First LAB color
            lab2: Second LAB color

        Returns:
            Delta E distance
        """
        return np.linalg.norm(lab1 - lab2)

    def get_closest_to_hex(self, hex_code: str) -> Dict[str, any]:
        """
        Find the closest DMC color match to the given hex code.

        Args:
            hex_code: Hex color code in format #RRGGBB, RRGGBB, #RRGGBBAA, or RRGGBBAA

        Returns:
            Dictionary with:
                - dmc: DMC code (string)
                - name: Color name
                - hex: Hex code of matched color
                - rgb: RGB tuple
                - distance: Calculated Delta E distance

        Raises:
            ValueError: If hex code is invalid
        """
        # Parse input hex code
        try:
            input_rgb = self._parse_hex(hex_code)
        except ValueError as e:
            raise ValueError(f"Invalid hex code: {hex_code}") from e

        # Convert input to LAB
        input_lab = self._rgb_to_lab(input_rgb)

        # Find closest match
        min_distance = float("inf")
        closest_color = None

        for color in self.colors:
            # Convert DMC color to LAB
            dmc_lab = self._rgb_to_lab(color["rgb"])

            # Calculate distance
            distance = self._delta_e(input_lab, dmc_lab)

            if distance < min_distance:
                min_distance = distance
                closest_color = color

        if closest_color is None:
            raise RuntimeError("No matching color found (should not happen)")

        return {
            "dmc": closest_color["dmc"],
            "name": closest_color["name"],
            "hex": closest_color["hex"],
            "rgb": closest_color["rgb"],
            "distance": float(min_distance),
        }
