"""Image gallery component displaying a grid of thumbnails."""

from typing import Callable, List
import flet as ft

from ui.components.image_thumbnail import create_image_thumbnail


def create_image_gallery(
    image_paths: List[str],
    on_remove: Callable[[str], None],
    max_extent: int = 160,
    thumbnail_size: int = 150,
) -> ft.GridView:
    """
    Create a responsive grid of image thumbnails.

    Args:
        image_paths: List of image file paths
        on_remove: Callback function when remove button is clicked
        max_extent: Maximum width of each grid cell
        thumbnail_size: Size of each thumbnail

    Returns:
        GridView containing all thumbnails
    """
    thumbnails = [
        create_image_thumbnail(path, on_remove, size=thumbnail_size)
        for path in image_paths
    ]

    return ft.GridView(
        controls=thumbnails,
        runs_count=5,
        max_extent=max_extent,
        child_aspect_ratio=1.0,
        spacing=10,
        run_spacing=10,
        expand=True,
        padding=10,
    )
