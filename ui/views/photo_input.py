"""Photo input view for uploading and displaying building images."""

import flet as ft

from ui.app_state import AppState
from ui.components.image_gallery import create_image_gallery


class PhotoInputView(ft.Column):
    """View for uploading and displaying building images."""

    def __init__(self, app_state: AppState, page: ft.Page):
        super().__init__()
        self.app_state = app_state
        self._page_ref = page
        self.gallery_container = ft.Container(expand=True)

        # Set up state change callback
        self.app_state.on_images_changed = self._refresh_gallery

        # Build the view
        self._build()

    def _build(self) -> None:
        """Build the view layout."""
        self.expand = True
        self.spacing = 20
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        # Upload section
        upload_section = self._create_upload_section()

        # Gallery section
        self._refresh_gallery()

        # Action buttons
        action_buttons = self._create_action_buttons()

        self.controls = [
            upload_section,
            self.gallery_container,
            action_buttons,
        ]

    def _create_upload_section(self) -> ft.Container:
        """Create the upload button section with instructions."""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        ft.Icons.CLOUD_UPLOAD,
                        size=48,
                        color=ft.Colors.BLUE_400,
                    ),
                    ft.Text(
                        "Upload Building Photos",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        "Select JPG or PNG images of buildings for analysis",
                        size=14,
                        color=ft.Colors.GREY_600,
                    ),
                    ft.Button(
                        "Select Images",
                        icon=ft.Icons.ADD_PHOTO_ALTERNATE,
                        on_click=self._handle_select_images,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.BLUE_500,
                            color=ft.Colors.WHITE,
                        ),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            bgcolor=ft.Colors.BLUE_50,
            border_radius=ft.border_radius.all(12),
            border=ft.border.all(2, ft.Colors.BLUE_200),
            padding=30,
            alignment=ft.Alignment(0, 0),
        )

    def _create_action_buttons(self) -> ft.Row:
        """Create the action buttons row."""
        return ft.Row(
            controls=[
                ft.Button(
                    "Clear All",
                    icon=ft.Icons.DELETE_SWEEP,
                    on_click=self._handle_clear_all,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.GREY_400,
                        color=ft.Colors.WHITE,
                    ),
                ),
                ft.Button(
                    "Analyze Photos",
                    icon=ft.Icons.ANALYTICS,
                    on_click=self._handle_analyze,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.GREEN_500,
                        color=ft.Colors.WHITE,
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.END,
            spacing=10,
        )

    def _refresh_gallery(self) -> None:
        """Refresh the gallery display."""
        if self.app_state.image_paths:
            self.gallery_container.content = create_image_gallery(
                image_paths=self.app_state.image_paths,
                on_remove=self._handle_remove_image,
            )
        else:
            self.gallery_container.content = ft.Container(
                content=ft.Text(
                    "No images selected",
                    size=16,
                    color=ft.Colors.GREY_500,
                    italic=True,
                ),
                alignment=ft.Alignment(0, 0),
                expand=True,
            )

        if self._page_ref:
            self._page_ref.update()

    async def _handle_select_images(self, e) -> None:
        """Handle the select images button click."""
        if self.app_state.file_picker:
            files = await self.app_state.file_picker.pick_files(
                allow_multiple=True,
                allowed_extensions=["jpg", "jpeg", "png"],
                file_type=ft.FilePickerFileType.CUSTOM,
                dialog_title="Select Building Images",
            )
            if files:
                paths = [f.path for f in files]
                self.app_state.add_images(paths)
                self._refresh_gallery()

    def _handle_remove_image(self, path: str) -> None:
        """Handle removing a single image."""
        self.app_state.remove_image(path)

    def _handle_clear_all(self, e) -> None:
        """Handle the clear all button click."""
        self.app_state.clear_images()

    def _handle_analyze(self, e) -> None:
        """Handle the analyze button click."""
        if not self.app_state.image_paths:
            self._page_ref.snack_bar = ft.SnackBar(
                content=ft.Text("Please select at least one image first."),
                bgcolor=ft.Colors.ORANGE_400,
            )
            self._page_ref.snack_bar.open = True
            self._page_ref.update()
            return

        # Placeholder for analysis functionality
        self._page_ref.snack_bar = ft.SnackBar(
            content=ft.Text(f"Analysis started for {len(self.app_state.image_paths)} image(s)..."),
            bgcolor=ft.Colors.GREEN_400,
        )
        self._page_ref.snack_bar.open = True
        self._page_ref.update()
