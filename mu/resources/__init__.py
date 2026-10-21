from pathlib import Path

from PyQt5.QtGui import QPixmap, QIcon, QMovie
from PyQt5.QtCore import QDir

import os


BASE_DIR = Path(__file__).parent

IMAGES_DIR = BASE_DIR / "images"
CSS_DIR = BASE_DIR / "css"
FONTS_DIR = BASE_DIR / "fonts"

QDir.addSearchPath("images", str(IMAGES_DIR))
QDir.addSearchPath("css", str(CSS_DIR))


def path(name, resource_dir="images/", ext=""):
    """Return the filename for the referenced resource."""
    return str(BASE_DIR / resource_dir / f"{name}{ext}")


def load_icon(name):
    """Load an icon from the resources directory."""
    svg_path = path(name, ext=".svg")
    if os.path.exists(svg_path):
        svg_icon = QIcon(svg_path)
        if svg_icon:
            return svg_icon
    return QIcon(path(name))


def load_pixmap(name, size=None):
    """Load a pixmap from the resources directory."""
    if size is not None:
        icon = load_icon(name)
        return icon.pixmap(size)
    return QPixmap(path(name))


def load_movie(name):
    """Load an animated GIF from the resources directory."""
    return QMovie(path(name))


def load_stylesheet(name):
    """Load a CSS stylesheet from the resources directory."""
    css_file = CSS_DIR / name
    return css_file.read_text(encoding="utf-8")


def load_font_data(name):
    """Load font bytes."""
    font_file = FONTS_DIR / name
    return font_file.read_bytes()