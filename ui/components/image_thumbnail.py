"""Image thumbnail component with remove button."""

from typing import Callable
import flet as ft


def create_image_thumbnail(
    image_path: str,
    on_remove: Callable[[str], None],
    size: int = 150,
) -> ft.Container:
    """
    Create a thumbnail container with an image and remove button overlay.

    Args:
        image_path: Path to the image file
        on_remove: Callback function when remove button is clicked
        size: Size of the thumbnail in pixels

    Returns:
        Container with image and remove button
    """

    def handle_remove(e):
        on_remove(image_path)

    return ft.Container(
        content=ft.Stack(
            controls=[
                # Image
                ft.Image(
                    src=image_path,
                    width=size,
                    height=size,
                    fit=ft.BoxFit.COVER,
                    border_radius=ft.border_radius.all(8),
                ),
                # Remove button overlay
                ft.Container(
                    content=ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_color=ft.Colors.WHITE,
                        icon_size=16,
                        bgcolor=ft.Colors.RED_400,
                        on_click=handle_remove,
                    ),
                    alignment=ft.Alignment(1, -1),
                    padding=4,
                ),
            ],
        ),
        width=size,
        height=size,
        border_radius=ft.border_radius.all(8),
        bgcolor=ft.Colors.GREY_200,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )
