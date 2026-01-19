"""Calculation utilities for building estimation."""

import math
from typing import Tuple


def calculate_floor_area(length: float, width: float) -> float:
    """Calculate floor area in square feet.

    Args:
        length: Building length in feet.
        width: Building width in feet.

    Returns:
        Floor area in square feet.
    """
    return length * width


def calculate_total_living_area(length: float, width: float, stories: int) -> float:
    """Calculate total living area for all floors.

    Args:
        length: Building length in feet.
        width: Building width in feet.
        stories: Number of stories.

    Returns:
        Total living area in square feet.
    """
    return calculate_floor_area(length, width) * stories


def calculate_perimeter(length: float, width: float) -> float:
    """Calculate building perimeter in feet.

    Args:
        length: Building length in feet.
        width: Building width in feet.

    Returns:
        Perimeter in feet.
    """
    return 2 * (length + width)


def calculate_exterior_wall_area(
    length: float,
    width: float,
    wall_height: float,
    stories: int
) -> float:
    """Calculate total exterior wall area.

    Args:
        length: Building length in feet.
        width: Building width in feet.
        wall_height: Height per story in feet.
        stories: Number of stories.

    Returns:
        Total exterior wall area in square feet.
    """
    perimeter = calculate_perimeter(length, width)
    return perimeter * wall_height * stories


def calculate_roof_area(
    length: float,
    width: float,
    roof_style: str,
    roof_pitch: float = 6.0
) -> float:
    """Calculate roof area based on style and pitch.

    Args:
        length: Building length in feet.
        width: Building width in feet.
        roof_style: Type of roof (Gable, Hip, Flat, etc.).
        roof_pitch: Roof pitch as rise over 12" run (e.g., 6 = 6:12 pitch).

    Returns:
        Roof area in square feet.
    """
    footprint = length * width

    if roof_style.lower() == "flat":
        # Flat roof - add 10% for drainage slope and edges
        return footprint * 1.10

    # Calculate pitch multiplier
    # For pitched roofs, area = footprint * sqrt(1 + (pitch/12)^2) * roof_factor
    pitch_multiplier = math.sqrt(1 + (roof_pitch / 12) ** 2)

    if roof_style.lower() == "gable":
        # Gable roof - two rectangular planes
        return footprint * pitch_multiplier

    elif roof_style.lower() == "hip":
        # Hip roof - typically 10-15% more material than gable
        return footprint * pitch_multiplier * 1.12

    elif roof_style.lower() in ("mansard", "gambrel"):
        # Complex roofs - significantly more area
        return footprint * pitch_multiplier * 1.3

    elif roof_style.lower() == "shed":
        # Single slope
        return footprint * pitch_multiplier * 0.95

    else:
        # Default to gable calculation
        return footprint * pitch_multiplier


def calculate_foundation_concrete(
    length: float,
    width: float,
    foundation_type: str = "slab",
    footer_width: float = 2.0,
    footer_depth: float = 1.0,
    slab_thickness: float = 0.33  # 4 inches
) -> Tuple[float, float]:
    """Calculate concrete needed for foundation.

    Args:
        length: Building length in feet.
        width: Building width in feet.
        foundation_type: Type of foundation (slab, crawl, basement).
        footer_width: Footer width in feet.
        footer_depth: Footer depth in feet.
        slab_thickness: Slab thickness in feet.

    Returns:
        Tuple of (cubic yards of concrete, linear feet of footer).
    """
    perimeter = calculate_perimeter(length, width)

    # Footer concrete
    footer_volume = perimeter * footer_width * footer_depth

    if foundation_type.lower() == "slab":
        # Slab on grade
        slab_area = length * width
        slab_volume = slab_area * slab_thickness
        total_cubic_feet = footer_volume + slab_volume

    elif foundation_type.lower() == "crawl":
        # Crawl space - just footers and stem wall
        stem_wall_height = 2.0  # feet
        stem_wall_thickness = 0.67  # 8 inches
        stem_wall_volume = perimeter * stem_wall_height * stem_wall_thickness
        total_cubic_feet = footer_volume + stem_wall_volume

    elif foundation_type.lower() == "basement":
        # Full basement
        wall_height = 8.0  # feet
        wall_thickness = 0.83  # 10 inches
        wall_volume = perimeter * wall_height * wall_thickness
        floor_area = length * width
        floor_volume = floor_area * slab_thickness
        total_cubic_feet = footer_volume + wall_volume + floor_volume

    else:
        total_cubic_feet = footer_volume

    # Convert to cubic yards (27 cubic feet per cubic yard)
    cubic_yards = total_cubic_feet / 27

    return cubic_yards, perimeter


def calculate_framing_lumber(
    length: float,
    width: float,
    stories: int,
    wall_height: float = 9.0,
    stud_spacing: float = 16.0  # inches on center
) -> dict:
    """Calculate framing lumber quantities.

    Args:
        length: Building length in feet.
        width: Building width in feet.
        stories: Number of stories.
        wall_height: Height per story in feet.
        stud_spacing: Stud spacing in inches on center.

    Returns:
        Dictionary with lumber quantities by type.
    """
    perimeter = calculate_perimeter(length, width)
    floor_area = calculate_floor_area(length, width)

    # Interior wall linear feet estimate (rough rule of thumb)
    interior_wall_lf = floor_area * 0.8

    total_wall_lf = (perimeter + interior_wall_lf) * stories

    # Calculate studs (add 10% for waste and blocking)
    stud_spacing_feet = stud_spacing / 12
    studs_per_lf = 1 / stud_spacing_feet
    total_studs = int(total_wall_lf * studs_per_lf * 1.10)

    # Plates - bottom and double top plate
    plate_lf = total_wall_lf * 3

    # Headers over openings - estimate
    header_lf = total_wall_lf * 0.15

    # Floor joists
    joist_spacing_feet = 16 / 12  # 16" OC
    if width <= 12:
        joist_size = "2x8"
    elif width <= 16:
        joist_size = "2x10"
    else:
        joist_size = "2x12"

    joists_per_floor = int(length / joist_spacing_feet) + 1
    total_joists = joists_per_floor * stories

    # Rim/band joists
    rim_joist_lf = perimeter * stories

    # Roof rafters (simplified)
    rafter_count = int(length / joist_spacing_feet) + 1

    # Sheathing (wall and roof)
    wall_sheathing_sqft = calculate_exterior_wall_area(length, width, wall_height, stories)
    roof_sheathing_sqft = calculate_roof_area(length, width, "gable")
    floor_sheathing_sqft = floor_area * stories

    # Convert to sheets (4x8 = 32 sqft, minus 10% for waste)
    sheet_coverage = 32 * 0.90
    wall_sheets = math.ceil(wall_sheathing_sqft / sheet_coverage)
    roof_sheets = math.ceil(roof_sheathing_sqft / sheet_coverage)
    floor_sheets = math.ceil(floor_sheathing_sqft / sheet_coverage)

    return {
        "studs_2x4": total_studs if wall_height <= 9 else 0,
        "studs_2x6": total_studs if wall_height > 9 else 0,
        "plates_2x4_lf": int(plate_lf),
        "headers_2x12_lf": int(header_lf),
        "floor_joists": total_joists,
        "floor_joist_size": joist_size,
        "rim_joist_lf": int(rim_joist_lf),
        "rafters": rafter_count * 2,  # Both sides of roof
        "wall_sheathing_sheets": wall_sheets,
        "roof_sheathing_sheets": roof_sheets,
        "floor_sheathing_sheets": floor_sheets
    }


def calculate_insulation(
    length: float,
    width: float,
    wall_height: float,
    stories: int,
    climate_zone: int,
    ceiling_r_value: float = None,
    wall_r_value: float = None
) -> dict:
    """Calculate insulation quantities.

    Args:
        length: Building length in feet.
        width: Building width in feet.
        wall_height: Height per story in feet.
        stories: Number of stories.
        climate_zone: IRC climate zone (1-8).
        ceiling_r_value: Override ceiling R-value.
        wall_r_value: Override wall R-value.

    Returns:
        Dictionary with insulation quantities.
    """
    # Default R-values by climate zone (IRC 2021)
    ceiling_r_defaults = {1: 30, 2: 38, 3: 38, 4: 49, 5: 49, 6: 49, 7: 49, 8: 49}
    wall_r_defaults = {1: 13, 2: 13, 3: 20, 4: 20, 5: 20, 6: 20, 7: 20, 8: 20}

    ceiling_r = ceiling_r_value or ceiling_r_defaults.get(climate_zone, 38)
    wall_r = wall_r_value or wall_r_defaults.get(climate_zone, 20)

    # Calculate areas
    ceiling_area = calculate_floor_area(length, width)
    wall_area = calculate_exterior_wall_area(length, width, wall_height, stories)

    # Reduce wall area by 15% for windows/doors
    net_wall_area = wall_area * 0.85

    return {
        "ceiling_sqft": ceiling_area,
        "ceiling_r_value": ceiling_r,
        "wall_sqft": net_wall_area,
        "wall_r_value": wall_r,
        "ceiling_batts": math.ceil(ceiling_area / 40),  # ~40 sqft per bag
        "wall_batts": math.ceil(net_wall_area / 88)  # ~88 sqft per bag (R-15)
    }


def calculate_drywall(
    length: float,
    width: float,
    wall_height: float,
    stories: int
) -> dict:
    """Calculate drywall quantities.

    Args:
        length: Building length in feet.
        width: Building width in feet.
        wall_height: Height per story in feet.
        stories: Number of stories.

    Returns:
        Dictionary with drywall quantities.
    """
    floor_area = calculate_floor_area(length, width)
    perimeter = calculate_perimeter(length, width)

    # Ceiling drywall
    ceiling_sqft = floor_area * stories

    # Wall drywall - exterior walls
    exterior_wall_sqft = perimeter * wall_height * stories

    # Interior walls - estimate based on floor area
    interior_wall_lf = floor_area * 0.8 * stories
    interior_wall_sqft = interior_wall_lf * wall_height * 2  # Both sides

    total_wall_sqft = exterior_wall_sqft + interior_wall_sqft

    # Reduce for openings (doors, windows) - approximately 10%
    net_wall_sqft = total_wall_sqft * 0.90

    total_sqft = ceiling_sqft + net_wall_sqft

    # Convert to sheets (4x8 = 32 sqft, add 10% for waste)
    sheets_needed = math.ceil(total_sqft / 32 * 1.10)

    return {
        "ceiling_sqft": ceiling_sqft,
        "wall_sqft": net_wall_sqft,
        "total_sqft": total_sqft,
        "sheets_4x8": sheets_needed,
        "joint_compound_buckets": math.ceil(sheets_needed / 30),  # ~30 sheets per 5-gal
        "tape_rolls": math.ceil(sheets_needed / 20)  # ~20 sheets per 500ft roll
    }


def calculate_electrical(floor_area: float, stories: int) -> dict:
    """Estimate electrical quantities based on floor area.

    Args:
        floor_area: Floor area per story in square feet.
        stories: Number of stories.

    Returns:
        Dictionary with electrical quantities.
    """
    total_area = floor_area * stories

    # Rough estimates based on typical residential
    outlets = max(10, int(total_area / 60))  # ~1 outlet per 60 sqft
    switches = max(5, int(total_area / 150))  # ~1 switch per 150 sqft
    light_fixtures = max(8, int(total_area / 100))  # ~1 fixture per 100 sqft

    # Wire runs estimate
    wire_14_2_lf = total_area * 2  # General circuits
    wire_12_2_lf = total_area * 0.5  # 20A circuits

    # Breakers
    breakers_15a = max(6, int(total_area / 500))
    breakers_20a = max(4, int(total_area / 600))

    return {
        "outlets": outlets,
        "switches": switches,
        "light_fixtures": light_fixtures,
        "wire_14_2_lf": int(wire_14_2_lf),
        "wire_12_2_lf": int(wire_12_2_lf),
        "breakers_15a": breakers_15a,
        "breakers_20a": breakers_20a,
        "panel_size_amps": 200 if total_area > 2000 else 100
    }


def calculate_plumbing(bathrooms: int, kitchens: int = 1) -> dict:
    """Estimate plumbing quantities.

    Args:
        bathrooms: Number of bathrooms.
        kitchens: Number of kitchens.

    Returns:
        Dictionary with plumbing quantities.
    """
    # Fixtures
    toilets = bathrooms
    sinks = bathrooms + kitchens
    showers_tubs = bathrooms
    kitchen_sink = kitchens

    # Rough-in counts
    drain_rough_ins = toilets + sinks + showers_tubs + kitchen_sink
    water_rough_ins = drain_rough_ins * 2  # Hot and cold for most

    # Pipe estimates (very rough)
    drain_pipe_lf = drain_rough_ins * 15
    supply_pipe_lf = water_rough_ins * 20

    return {
        "toilets": toilets,
        "sinks": sinks,
        "showers_tubs": showers_tubs,
        "drain_rough_ins": drain_rough_ins,
        "water_rough_ins": water_rough_ins,
        "drain_pipe_lf": drain_pipe_lf,
        "supply_pipe_lf": supply_pipe_lf,
        "water_heater": 1
    }


def calculate_hvac(total_sqft: float, climate_zone: int) -> dict:
    """Estimate HVAC requirements.

    Args:
        total_sqft: Total conditioned square footage.
        climate_zone: IRC climate zone (1-8).

    Returns:
        Dictionary with HVAC specifications.
    """
    # BTU per sqft varies by climate
    btu_per_sqft = {
        1: 25, 2: 25, 3: 22,
        4: 20, 5: 35, 6: 40,
        7: 45, 8: 50
    }

    btu_needed = total_sqft * btu_per_sqft.get(climate_zone, 30)
    tons_ac = btu_needed / 12000

    # Round up to standard sizes
    if tons_ac <= 1.5:
        system_size = 1.5
    elif tons_ac <= 2:
        system_size = 2
    elif tons_ac <= 2.5:
        system_size = 2.5
    elif tons_ac <= 3:
        system_size = 3
    elif tons_ac <= 3.5:
        system_size = 3.5
    elif tons_ac <= 4:
        system_size = 4
    else:
        system_size = 5

    # Ductwork estimate
    duct_lf = total_sqft * 0.5
    registers = max(6, int(total_sqft / 200))

    return {
        "btu_required": int(btu_needed),
        "tonnage": system_size,
        "duct_lf": int(duct_lf),
        "supply_registers": registers,
        "return_registers": max(2, registers // 3)
    }


def calculate_exterior_materials(
    length: float,
    width: float,
    wall_height: float,
    stories: int,
    exterior_type: str,
    window_count: int,
    door_count: int
) -> dict:
    """Calculate exterior finish materials.

    Args:
        length: Building length in feet.
        width: Building width in feet.
        wall_height: Height per story in feet.
        stories: Number of stories.
        exterior_type: Type of exterior material.
        window_count: Number of windows.
        door_count: Number of doors.

    Returns:
        Dictionary with exterior material quantities.
    """
    wall_area = calculate_exterior_wall_area(length, width, wall_height, stories)

    # Deduct for openings
    window_area = window_count * 15  # ~15 sqft per window average
    door_area = door_count * 20  # ~20 sqft per door average
    net_wall_area = wall_area - window_area - door_area

    # Material-specific calculations
    if exterior_type.lower() in ("vinyl siding", "wood siding", "fiber cement"):
        # Siding - sold by square (100 sqft)
        squares = math.ceil(net_wall_area / 100 * 1.10)  # 10% waste
        return {
            "siding_squares": squares,
            "net_wall_sqft": net_wall_area,
            "trim_lf": calculate_perimeter(length, width) * stories * 4,
            "corners": 4 * stories
        }

    elif exterior_type.lower() == "brick":
        # Brick - ~7 bricks per sqft
        bricks = int(net_wall_area * 7 * 1.05)
        return {
            "bricks": bricks,
            "mortar_bags": math.ceil(bricks / 500),
            "net_wall_sqft": net_wall_area,
            "wall_ties": int(net_wall_area * 1.5)
        }

    elif exterior_type.lower() in ("stone", "stucco", "eifs"):
        return {
            "coverage_sqft": net_wall_area,
            "net_wall_sqft": net_wall_area
        }

    else:
        return {
            "net_wall_sqft": net_wall_area
        }


def calculate_roofing(
    length: float,
    width: float,
    roof_style: str,
    roof_pitch: float = 6.0
) -> dict:
    """Calculate roofing materials.

    Args:
        length: Building length in feet.
        width: Building width in feet.
        roof_style: Type of roof.
        roof_pitch: Roof pitch.

    Returns:
        Dictionary with roofing material quantities.
    """
    roof_area = calculate_roof_area(length, width, roof_style, roof_pitch)

    # Roofing is sold by "square" (100 sqft)
    squares = math.ceil(roof_area / 100 * 1.10)  # 10% waste

    # Underlayment
    underlayment_rolls = math.ceil(roof_area / 400)  # ~4 squares per roll

    # Ridge and hip length estimate
    if roof_style.lower() == "gable":
        ridge_lf = length
        hip_lf = 0
    elif roof_style.lower() == "hip":
        ridge_lf = length * 0.5
        hip_lf = math.sqrt(2) * width * 2  # Approximate hip length
    else:
        ridge_lf = length
        hip_lf = 0

    # Drip edge and flashing
    perimeter = calculate_perimeter(length, width)

    return {
        "roof_sqft": roof_area,
        "shingle_squares": squares,
        "underlayment_rolls": underlayment_rolls,
        "ridge_cap_lf": int(ridge_lf),
        "hip_cap_lf": int(hip_lf),
        "drip_edge_lf": int(perimeter),
        "starter_strip_lf": int(perimeter),
        "nails_lbs": squares * 2  # ~2 lbs nails per square
    }
