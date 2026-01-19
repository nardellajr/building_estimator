"""Photo analysis using OpenAI Vision API."""

import base64
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from openai import OpenAI

from config.settings import OPENAI_API_KEY


SYSTEM_MESSAGE = """You are an expert construction estimator and building inspector
with 20+ years of experience. You analyze building photos to identify materials,
features, and construction details for cost estimation purposes. Be precise and
conservative - only report what you can clearly identify."""


@dataclass
class PhotoAnalysisResult:
    """Results from photo analysis."""
    # Building basics
    building_type: str = "Unknown"
    architectural_style: str = "Unknown"
    estimated_age: str = "Unknown"
    condition: str = "Unknown"
    stories: int = 1

    # Roof details
    roof_style: str = "Unknown"
    roof_material: str = "Unknown"
    roof_condition: str = "Unknown"
    has_gutters: bool = False
    has_chimney: bool = False

    # Exterior
    primary_exterior: str = "Unknown"
    secondary_exterior: str = "None"
    exterior_color: str = "Unknown"

    # Windows & Doors
    window_count: int = 0
    window_style: str = "Unknown"
    window_material: str = "Unknown"
    estimated_window_size: str = "3x4 ft"
    door_count: int = 0
    entry_door_material: str = "Unknown"
    has_storm_door: bool = False
    estimated_door_size: str = "3x7 ft"

    # Garage
    has_garage: bool = False
    garage_type: str = "None"
    garage_doors: int = 0
    garage_door_width: str = "Unknown"

    # Features
    has_porch: bool = False
    porch_type: str = "None"
    has_deck: bool = False
    deck_material: str = "None"
    has_dormers: bool = False
    dormer_count: int = 0
    special_features: list = field(default_factory=list)

    # Confidence scores
    field_confidence: dict = field(default_factory=dict)
    overall_confidence: float = 0.5
    analysis_notes: str = ""

    # Metadata
    photo_quality: str = "medium"
    raw_response: str = ""
    error: Optional[str] = None


class PhotoAnalyzer:
    """Analyzes building photos using OpenAI Vision API."""

    ANALYSIS_PROMPT = """Analyze this building photo for construction estimation.

## INSTRUCTIONS
1. Only report features you can CLEARLY see
2. Use "Unknown" if uncertain (don't guess)
3. Provide confidence (0.0-1.0) for each category
4. Note any obstructions or limitations in analysis_notes

## REQUIRED OUTPUT (JSON)
{
  "building": {
    "type": "Single Family|Multi-Family|Commercial|Industrial|Unknown",
    "architectural_style": "Colonial|Ranch|Cape Cod|Modern|Craftsman|Victorian|Contemporary|Split-Level|Other|Unknown",
    "estimated_decade": "Pre-1950|1950s|1960s|1970s|1980s|1990s|2000s|2010s|2020s|Unknown",
    "condition": "Excellent|Good|Fair|Poor|Unknown",
    "stories": 1
  },
  "roof": {
    "style": "Gable|Hip|Flat|Mansard|Gambrel|Shed|Complex|Unknown",
    "material": "Asphalt Shingles|Metal Standing Seam|Metal Ribbed|Clay Tile|Concrete Tile|Slate|Wood Shake|Flat Membrane|Unknown",
    "condition": "Excellent|Good|Fair|Poor|Unknown",
    "has_gutters": false,
    "has_chimney": false
  },
  "exterior": {
    "primary_material": "Vinyl Siding|Wood Siding|Fiber Cement|Brick|Stone|Stucco|Metal|EIFS|Log|Unknown",
    "secondary_material": "None|Wood Trim|Vinyl Trim|Stone Accent|Brick Accent|Other",
    "primary_color": "Unknown"
  },
  "windows": {
    "count": 0,
    "style": "Double-Hung|Casement|Slider|Picture|Bay|Awning|Mixed|Unknown",
    "frame_material": "Vinyl|Wood|Aluminum|Fiberglass|Unknown",
    "estimated_size": "3x4 ft"
  },
  "doors": {
    "entry_count": 0,
    "entry_material": "Steel|Fiberglass|Wood|Unknown",
    "has_storm_door": false,
    "estimated_size": "3x7 ft"
  },
  "garage": {
    "present": false,
    "type": "Attached|Detached|Carport|None",
    "door_count": 0,
    "door_width": "Single|Double|Unknown"
  },
  "features": {
    "has_porch": false,
    "porch_type": "Covered|Screened|Open|Wrap-Around|None",
    "has_deck": false,
    "deck_material": "Wood|Composite|Unknown|None",
    "has_dormers": false,
    "dormer_count": 0,
    "other_features": []
  },
  "confidence": {
    "building": 0.5,
    "roof": 0.5,
    "exterior": 0.5,
    "windows": 0.5,
    "doors": 0.5,
    "garage": 0.5,
    "features": 0.5,
    "overall": 0.5
  },
  "photo_quality": "medium",
  "analysis_notes": "Any observations about photo quality, obstructions, or uncertainty"
}

Be conservative in your estimates. Count only what you can see - don't assume features on non-visible sides."""

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

    def _parse_structured_response(self, data: dict) -> PhotoAnalysisResult:
        """Convert nested API response to flat PhotoAnalysisResult.

        Args:
            data: Nested JSON response from the API.

        Returns:
            Populated PhotoAnalysisResult dataclass.
        """
        result = PhotoAnalysisResult()

        # Building basics
        building = data.get("building", {})
        result.building_type = building.get("type", "Unknown")
        result.architectural_style = building.get("architectural_style", "Unknown")
        result.estimated_age = building.get("estimated_decade", "Unknown")
        result.condition = building.get("condition", "Unknown")
        result.stories = building.get("stories", 1)

        # Roof details
        roof = data.get("roof", {})
        result.roof_style = roof.get("style", "Unknown")
        result.roof_material = roof.get("material", "Unknown")
        result.roof_condition = roof.get("condition", "Unknown")
        result.has_gutters = roof.get("has_gutters", False)
        result.has_chimney = roof.get("has_chimney", False)

        # Exterior
        exterior = data.get("exterior", {})
        result.primary_exterior = exterior.get("primary_material", "Unknown")
        result.secondary_exterior = exterior.get("secondary_material", "None")
        result.exterior_color = exterior.get("primary_color", "Unknown")

        # Windows
        windows = data.get("windows", {})
        result.window_count = windows.get("count", 0)
        result.window_style = windows.get("style", "Unknown")
        result.window_material = windows.get("frame_material", "Unknown")
        result.estimated_window_size = windows.get("estimated_size", "3x4 ft")

        # Doors
        doors = data.get("doors", {})
        result.door_count = doors.get("entry_count", 0)
        result.entry_door_material = doors.get("entry_material", "Unknown")
        result.has_storm_door = doors.get("has_storm_door", False)
        result.estimated_door_size = doors.get("estimated_size", "3x7 ft")

        # Garage
        garage = data.get("garage", {})
        result.has_garage = garage.get("present", False)
        result.garage_type = garage.get("type", "None")
        result.garage_doors = garage.get("door_count", 0)
        result.garage_door_width = garage.get("door_width", "Unknown")

        # Features
        features = data.get("features", {})
        result.has_porch = features.get("has_porch", False)
        result.porch_type = features.get("porch_type", "None")
        result.has_deck = features.get("has_deck", False)
        result.deck_material = features.get("deck_material", "None")
        result.has_dormers = features.get("has_dormers", False)
        result.dormer_count = features.get("dormer_count", 0)
        result.special_features = features.get("other_features", [])

        # Confidence scores
        confidence = data.get("confidence", {})
        result.field_confidence = {
            "building": confidence.get("building", 0.5),
            "roof": confidence.get("roof", 0.5),
            "exterior": confidence.get("exterior", 0.5),
            "windows": confidence.get("windows", 0.5),
            "doors": confidence.get("doors", 0.5),
            "garage": confidence.get("garage", 0.5),
            "features": confidence.get("features", 0.5),
        }
        result.overall_confidence = confidence.get("overall", 0.5)

        # Metadata
        result.photo_quality = data.get("photo_quality", "medium")
        result.analysis_notes = data.get("analysis_notes", "")

        return result

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
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_MESSAGE
                    },
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
                max_tokens=1500
            )

            raw_response = response.choices[0].message.content
            result.raw_response = raw_response

            # Parse JSON response using helper method
            try:
                data = json.loads(raw_response)
                result = self._parse_structured_response(data)
                result.raw_response = raw_response
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

        # Combine results - use highest overall confidence as the primary source
        combined = PhotoAnalysisResult()
        best = max(valid_results, key=lambda r: r.overall_confidence)

        # Building basics - use best result
        combined.building_type = best.building_type
        combined.architectural_style = best.architectural_style
        combined.estimated_age = best.estimated_age
        combined.condition = best.condition
        combined.stories = max(r.stories for r in valid_results)

        # Roof details - use best result
        combined.roof_style = best.roof_style
        combined.roof_material = best.roof_material
        combined.roof_condition = best.roof_condition
        combined.has_gutters = any(r.has_gutters for r in valid_results)
        combined.has_chimney = any(r.has_chimney for r in valid_results)

        # Exterior - use best result
        combined.primary_exterior = best.primary_exterior
        combined.secondary_exterior = best.secondary_exterior
        combined.exterior_color = best.exterior_color

        # Windows - sum counts, use best for other fields
        combined.window_count = sum(r.window_count for r in valid_results)
        combined.window_style = best.window_style
        combined.window_material = best.window_material
        combined.estimated_window_size = best.estimated_window_size

        # Doors - sum counts, use best for other fields
        combined.door_count = sum(r.door_count for r in valid_results)
        combined.entry_door_material = best.entry_door_material
        combined.has_storm_door = any(r.has_storm_door for r in valid_results)
        combined.estimated_door_size = best.estimated_door_size

        # Garage - use best but take max doors
        combined.has_garage = any(r.has_garage for r in valid_results)
        combined.garage_type = best.garage_type if best.has_garage else next(
            (r.garage_type for r in valid_results if r.has_garage), "None"
        )
        combined.garage_doors = max(r.garage_doors for r in valid_results)
        combined.garage_door_width = best.garage_door_width

        # Features
        combined.has_porch = any(r.has_porch for r in valid_results)
        combined.porch_type = best.porch_type if best.has_porch else next(
            (r.porch_type for r in valid_results if r.has_porch), "None"
        )
        combined.has_deck = any(r.has_deck for r in valid_results)
        combined.deck_material = best.deck_material if best.has_deck else next(
            (r.deck_material for r in valid_results if r.has_deck), "None"
        )
        combined.has_dormers = any(r.has_dormers for r in valid_results)
        combined.dormer_count = sum(r.dormer_count for r in valid_results)

        # Combine special features
        all_features = set()
        for r in valid_results:
            all_features.update(r.special_features)
        combined.special_features = list(all_features)

        # Combine field confidence - average across all results
        combined_confidence = {}
        confidence_fields = ["building", "roof", "exterior", "windows", "doors", "garage", "features"]
        for field in confidence_fields:
            values = [r.field_confidence.get(field, 0.5) for r in valid_results]
            combined_confidence[field] = sum(values) / len(values)
        combined.field_confidence = combined_confidence

        # Average overall confidence, boost for multiple photos
        avg_confidence = sum(r.overall_confidence for r in valid_results) / len(valid_results)
        combined.overall_confidence = min(1.0, avg_confidence * (1 + 0.1 * (len(valid_results) - 1)))

        # Combine analysis notes
        notes = [r.analysis_notes for r in valid_results if r.analysis_notes]
        combined.analysis_notes = " | ".join(notes) if notes else ""

        # Photo quality is best of all
        quality_order = {"high": 3, "medium": 2, "low": 1}
        combined.photo_quality = max(
            (r.photo_quality for r in valid_results),
            key=lambda q: quality_order.get(q, 0)
        )

        return combined
