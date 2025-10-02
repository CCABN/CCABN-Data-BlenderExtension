"""
Property definitions for CCABN Dataset Generator
"""

import bpy
from bpy.props import (
    PointerProperty,
    CollectionProperty,
    StringProperty,
    IntProperty,
    FloatProperty,
    BoolProperty,
    EnumProperty,
)
from bpy.types import PropertyGroup


class ObjectItem(PropertyGroup):
    """Reference to a scene object"""
    obj: PointerProperty(
        type=bpy.types.Object,
        name="Object",
        description="Reference to a scene object"
    )


class BlendshapeItem(PropertyGroup):
    """Individual blendshape with selection and range"""
    name: StringProperty(
        name="Blendshape Name",
        default=""
    )
    selected: BoolProperty(
        name="Selected",
        default=False,
        description="Include this blendshape in randomization"
    )
    min_value: FloatProperty(
        name="Min",
        default=0.0,
        min=0.0,
        max=1.0,
        description="Minimum random value for this blendshape"
    )
    max_value: FloatProperty(
        name="Max",
        default=1.0,
        min=0.0,
        max=1.0,
        description="Maximum random value for this blendshape"
    )


class CCABNProperties(PropertyGroup):
    """Main properties for CCABN Dataset Generator"""

    # Scene objects
    camera: PointerProperty(
        type=bpy.types.Object,
        name="Camera",
        description="Camera to render from (will be set to 160° FOV)"
    )

    lights: CollectionProperty(
        type=ObjectItem,
        name="Lights",
        description="Lights to randomize"
    )

    lights_index: IntProperty(
        name="Lights Index",
        default=0
    )

    headset_mesh: PointerProperty(
        type=bpy.types.Object,
        name="Headset Mesh",
        description="Mesh object representing VR headset (will have random gray material)"
    )

    human_faces: CollectionProperty(
        type=ObjectItem,
        name="Human Faces",
        description="Mesh objects containing human faces with blendshapes"
    )

    human_faces_index: IntProperty(
        name="Human Faces Index",
        default=0
    )

    # Background gray tone range
    background_gray_min: FloatProperty(
        name="Min",
        default=0.2,
        min=0.0,
        max=1.0,
        description="Minimum gray value for background (0=black, 1=white)"
    )

    background_gray_max: FloatProperty(
        name="Max",
        default=0.8,
        min=0.0,
        max=1.0,
        description="Maximum gray value for background (0=black, 1=white)"
    )

    # Headset gray tone range
    headset_gray_min: FloatProperty(
        name="Min",
        default=0.1,
        min=0.0,
        max=1.0,
        description="Minimum gray value for headset (0=black, 1=white)"
    )

    headset_gray_max: FloatProperty(
        name="Max",
        default=0.4,
        min=0.0,
        max=1.0,
        description="Maximum gray value for headset (0=black, 1=white)"
    )

    # Blendshapes
    blendshape_list: CollectionProperty(
        type=BlendshapeItem,
        name="Blendshapes",
        description="Available blendshapes for randomization"
    )

    blendshape_list_index: IntProperty(
        name="Blendshape Index",
        default=0
    )

    # Camera variations
    camera_pos_x_var: FloatProperty(
        name="±X",
        default=0.0,
        min=0.0,
        description="Camera position variation in X axis (meters)"
    )

    camera_pos_y_var: FloatProperty(
        name="±Y",
        default=0.0,
        min=0.0,
        description="Camera position variation in Y axis (meters)"
    )

    camera_pos_z_var: FloatProperty(
        name="±Z",
        default=0.0,
        min=0.0,
        description="Camera position variation in Z axis (meters)"
    )

    camera_rot_x_var: FloatProperty(
        name="±X",
        default=0.0,
        min=0.0,
        description="Camera rotation variation in X axis (degrees)"
    )

    camera_rot_y_var: FloatProperty(
        name="±Y",
        default=0.0,
        min=0.0,
        description="Camera rotation variation in Y axis (degrees)"
    )

    camera_rot_z_var: FloatProperty(
        name="±Z",
        default=0.0,
        min=0.0,
        description="Camera rotation variation in Z axis (degrees)"
    )

    # Light variations
    light_pos_x_var: FloatProperty(
        name="±X",
        default=0.0,
        min=0.0,
        description="Light position variation in X axis (meters)"
    )

    light_pos_y_var: FloatProperty(
        name="±Y",
        default=0.0,
        min=0.0,
        description="Light position variation in Y axis (meters)"
    )

    light_pos_z_var: FloatProperty(
        name="±Z",
        default=0.0,
        min=0.0,
        description="Light position variation in Z axis (meters)"
    )

    light_intensity_min: FloatProperty(
        name="Min",
        default=50.0,
        min=0.0,
        max=100.0,
        subtype='PERCENTAGE',
        description="Minimum light intensity percentage"
    )

    light_intensity_max: FloatProperty(
        name="Max",
        default=150.0,
        min=0.0,
        max=1000.0,
        subtype='PERCENTAGE',
        description="Maximum light intensity percentage"
    )

    light_temp_min: FloatProperty(
        name="Min",
        default=3000.0,
        min=1000.0,
        max=12000.0,
        description="Minimum color temperature in Kelvin"
    )

    light_temp_max: FloatProperty(
        name="Max",
        default=6500.0,
        min=1000.0,
        max=12000.0,
        description="Maximum color temperature in Kelvin"
    )

    # Output settings
    output_path: StringProperty(
        name="Output Folder",
        description="Folder to save rendered images and metadata",
        subtype='DIR_PATH',
        default=""
    )

    images_per_human: IntProperty(
        name="Images per Human",
        default=100,
        min=1,
        description="Number of images to render per human face"
    )

    render_engine: EnumProperty(
        name="Render Engine",
        items=[
            ('CYCLES', "Cycles GPU", "Use Cycles render engine with GPU acceleration"),
            ('BLENDER_EEVEE', "Eevee", "Use Eevee render engine (faster but less realistic)"),
        ],
        default='CYCLES',
        description="Render engine to use for image generation"
    )

    # Runtime state
    is_rendering: BoolProperty(
        name="Is Rendering",
        default=False,
        description="Whether dataset generation is currently running"
    )


# Registration
classes = (
    ObjectItem,
    BlendshapeItem,
    CCABNProperties,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.ccabn_props = PointerProperty(type=CCABNProperties)


def unregister():
    del bpy.types.Scene.ccabn_props

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
