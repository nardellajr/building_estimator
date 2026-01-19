"""Main entry point for the Building Estimator application."""

import flet as ft

from ui.app_state import AppState
from ui.views.photo_input import PhotoInputView


async def main(page: ft.Page) -> None:
    """Configure and run the Building Estimator application."""
    # Configure page
    page.title = "Building Estimator"
    page.window.width = 1200
    page.window.height = 800
    page.padding = 20

    # Create file picker and add to page services
    file_picker = ft.FilePicker()
    page.services.append(file_picker)

    # Initialize app state
    app_state = AppState(file_picker=file_picker)

    # Create app bar
    app_bar = ft.AppBar(
        title=ft.Text("Building Estimator"),
        center_title=True,
        bgcolor=ft.Colors.BLUE_600,
        color=ft.Colors.WHITE,
    )
    page.appbar = app_bar

    # Create main view
    photo_input_view = PhotoInputView(app_state=app_state, page=page)

    # Add view to page
    page.add(photo_input_view)


if __name__ == "__main__":
    ft.run(main)
