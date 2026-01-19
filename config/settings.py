"""Application configuration and settings."""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = BASE_DIR / "database"

# OpenAI API configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Database settings
DATABASE_PATH = DATABASE_DIR / "building_estimator.db"

# Default values
DEFAULT_CONTINGENCY_PERCENT = 10.0
DEFAULT_PERMIT_PERCENT = 2.0

# Climate zones (IRC)
CLIMATE_ZONES = {
    1: "Very Hot - Humid",
    2: "Hot - Humid",
    3: "Warm - Humid/Marine",
    4: "Mixed - Humid/Marine",
    5: "Cool - Humid",
    6: "Cold - Humid",
    7: "Very Cold",
    8: "Subarctic"
}

# Building types
BUILDING_TYPES = [
    "Single Family Residential",
    "Multi-Family Residential",
    "Commercial",
    "Industrial",
    "Mixed Use"
]

# Roof styles
ROOF_STYLES = [
    "Gable",
    "Hip",
    "Flat",
    "Mansard",
    "Gambrel",
    "Shed",
    "Butterfly"
]

# Exterior materials
EXTERIOR_MATERIALS = [
    "Vinyl Siding",
    "Wood Siding",
    "Fiber Cement",
    "Brick",
    "Stone",
    "Stucco",
    "Metal",
    "EIFS"
]

# App settings
APP_TITLE = "Building Estimator"
APP_WIDTH = 1200
APP_HEIGHT = 800
