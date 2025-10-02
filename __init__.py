"""
CCABN Dataset Generator - Blender Extension
Generate synthetic facial expression datasets for neural network training

Main entry point for the extension
"""

bl_info = {
    "name": "CCABN Dataset Generator",
    "author": "CCABN Team",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > CCABN",
    "description": "Generate synthetic facial expression datasets for neural network training",
    "category": "Render",
}

import bpy

# Import modules
from . import properties
from . import operators
from . import ui_panel
from . import utils
from . import renderer


# Registration
def register():
    """Register all classes and properties"""
    properties.register()
    operators.register()
    ui_panel.register()

    print("CCABN Dataset Generator registered")


def unregister():
    """Unregister all classes and properties"""
    ui_panel.unregister()
    operators.unregister()
    properties.unregister()

    print("CCABN Dataset Generator unregistered")


if __name__ == "__main__":
    register()
