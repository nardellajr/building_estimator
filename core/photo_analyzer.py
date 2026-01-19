"""Photo analysis using OpenAI Vision API."""

import base64
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from openai import OpenAI

from config.settings import OPENAI_API_KEY


@dataclass
class PhotoAnalysisResult:
    """Results from photo analysis."""
    building_type: str = "Single Family Residential"
    roof_style: str = "Gable"
    exterior_material: str = "Vinyl Siding"
    stories: int = 1
    window_count: int = 0
    door_count: int = 0
    estimated_window_size: str = "3x4 ft"
    estimated_door_size: str = "3x7 ft"
    has_garage: bool = False
    garage_doors: int = 0
    has_porch: bool = False
    has_deck: bool = False
    has_dormers: bool = False
    dormer_count: int = 0
    special_features: list = field(default_factory=list)
    photo_quality: str = "medium"  # low, medium, high
    confidence: float = 0.5
    raw_response: str = ""
    error: Optional[str] = None


class PhotoAnalyzer:
    """Analyzes building photos using OpenAI Vision API."""

    ANALYSIS_PROMPT = """Analyze this building photo and extract the following information.
Respond ONLY with a valid JSON object (no markdown, no explanation), using this exact structure:

{
    "building_type": "Single Family Residential|Multi-Family Residential|Commercial|Industrial|Mixed Use",
    "roof_style": "Gable|Hip|Flat|Mansard|Gambrel|Shed|Butterfly",
    "exterior_material": "Vinyl Siding|Wood Siding|Fiber Cement|Brick|Stone|Stucco|Metal|EIFS",
    "stories": <number>,
    "window_count": <number of visible windows>,
    "door_count": <number of visible doors, not including garage>,
    "estimated_window_size": "<width>x<height> ft",
    "estimated_door_size": "<width>x<height> ft",
    "has_garage": true|false,
    "garage_doors": <number>,
    "has_porch": true|false,
    "has_deck": true|false,
    "has_dormers": true|false,
    "dormer_count": <number>,
    "special_features": ["list", "of", "notable", "features"],
    "photo_quality": "low|medium|high",
    "confidence": <0.0 to 1.0 based on how clearly features are visible>
}

Be conservative in your estimates. If something is not clearly visible, indicate lower confidence.
Count only what you can see - don't assume features on non-visible sides."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the photo analyzer.

        Args:
            api_key: OpenAI API key. If not provided, uses environment variable.
        """
        self.api_key = api_key or OPENAI_API_KEY
        self.client = None
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 for API submission."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def _get_image_media_type(self, image_path: str) -> str:
        """Determine the media type based on file extension."""
        ext = Path(image_path).suffix.lower()
        media_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp"
        }
        return media_types.get(ext, "image/jpeg")

    def analyze(self, image_path: str) -> PhotoAnalysisResult:
        """Analyze a building photo.

        Args:
            image_path: Path to the image file.

        Returns:
            PhotoAnalysisResult with extracted building features.
        """
        result = PhotoAnalysisResult()

        if not self.client:
            result.error = "OpenAI API key not configured. Set OPENAI_API_KEY environment variable."
            return result

        if not Path(image_path).exists():
            result.error = f"Image file not found: {image_path}"
            return result

        try:
            base64_image = self._encode_image(image_path)
            media_type = self._get_image_media_type(image_path)

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": self.ANALYSIS_PROMPT},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{media_type};base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )

            raw_response = response.choices[0].message.content
            result.raw_response = raw_response

            # Parse JSON response
            try:
                data = json.loads(raw_response)
                result.building_type = data.get("building_type", result.building_type)
                result.roof_style = data.get("roof_style", result.roof_style)
                result.exterior_material = data.get("exterior_material", result.exterior_material)
                result.stories = data.get("stories", result.stories)
                result.window_count = data.get("window_count", result.window_count)
                result.door_count = data.get("door_count", result.door_count)
                result.estimated_window_size = data.get("estimated_window_size", result.estimated_window_size)
                result.estimated_door_size = data.get("estimated_door_size", result.estimated_door_size)
                result.has_garage = data.get("has_garage", result.has_garage)
                result.garage_doors = data.get("garage_doors", result.garage_doors)
                result.has_porch = data.get("has_porch", result.has_porch)
                result.has_deck = data.get("has_deck", result.has_deck)
                result.has_dormers = data.get("has_dormers", result.has_dormers)
                result.dormer_count = data.get("dormer_count", result.dormer_count)
                result.special_features = data.get("special_features", result.special_features)
                result.photo_quality = data.get("photo_quality", result.photo_quality)
                result.confidence = data.get("confidence", result.confidence)
            except json.JSONDecodeError as e:
                result.error = f"Failed to parse API response: {e}"

        except Exception as e:
            result.error = f"API error: {str(e)}"

        return result

    def analyze_multiple(self, image_paths: list[str]) -> PhotoAnalysisResult:
        """Analyze multiple photos and combine results.

        Args:
            image_paths: List of paths to image files.

        Returns:
            Combined PhotoAnalysisResult from all images.
        """
        if not image_paths:
            result = PhotoAnalysisResult()
            result.error = "No images provided"
            return result

        results = [self.analyze(path) for path in image_paths]

        # Filter out failed results
        valid_results = [r for r in results if r.error is None]

        if not valid_results:
            # Return first error if all failed
            return results[0]

        # Combine results - use highest confidence values
        combined = PhotoAnalysisResult()
        best = max(valid_results, key=lambda r: r.confidence)

        # Copy most fields from best result
        combined.building_type = best.building_type
        combined.roof_style = best.roof_style
        combined.exterior_material = best.exterior_material
        combined.stories = max(r.stories for r in valid_results)
        combined.estimated_window_size = best.estimated_window_size
        combined.estimated_door_size = best.estimated_door_size
        combined.has_garage = any(r.has_garage for r in valid_results)
        combined.has_porch = any(r.has_porch for r in valid_results)
        combined.has_deck = any(r.has_deck for r in valid_results)
        combined.has_dormers = any(r.has_dormers for r in valid_results)

        # Sum counts across images (rough estimate for full building)
        combined.window_count = sum(r.window_count for r in valid_results)
        combined.door_count = sum(r.door_count for r in valid_results)
        combined.garage_doors = max(r.garage_doors for r in valid_results)
        combined.dormer_count = sum(r.dormer_count for r in valid_results)

        # Combine special features
        all_features = set()
        for r in valid_results:
            all_features.update(r.special_features)
        combined.special_features = list(all_features)

        # Average confidence, boost for multiple photos
        avg_confidence = sum(r.confidence for r in valid_results) / len(valid_results)
        combined.confidence = min(1.0, avg_confidence * (1 + 0.1 * (len(valid_results) - 1)))

        # Photo quality is best of all
        quality_order = {"high": 3, "medium": 2, "low": 1}
        combined.photo_quality = max(
            (r.photo_quality for r in valid_results),
            key=lambda q: quality_order.get(q, 0)
        )

        return combined
