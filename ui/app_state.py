"""Centralized application state management."""

from dataclasses import dataclass, field
from typing import Callable, List, Optional
import flet as ft


@dataclass
class AppState:
    """Centralized state for the Building Estimator application."""

    image_paths: List[str] = field(default_factory=list)
    file_picker: Optional[ft.FilePicker] = None
    on_images_changed: Optional[Callable[[], None]] = None

    def add_image(self, path: str) -> None:
        """Add an image path to the collection."""
        if path not in self.image_paths:
            self.image_paths.append(path)
            self._notify_change()

    def add_images(self, paths: List[str]) -> None:
        """Add multiple image paths to the collection."""
        for path in paths:
            if path not in self.image_paths:
                self.image_paths.append(path)
        self._notify_change()

    def remove_image(self, path: str) -> None:
        """Remove an image path from the collection."""
        if path in self.image_paths:
            self.image_paths.remove(path)
            self._notify_change()

    def clear_images(self) -> None:
        """Clear all image paths."""
        self.image_paths.clear()
        self._notify_change()

    def _notify_change(self) -> None:
        """Notify listeners of state change."""
        if self.on_images_changed:
            self.on_images_changed()
