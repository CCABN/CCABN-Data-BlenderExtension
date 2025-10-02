"""
Utility functions and constants for CCABN Dataset Generator
"""

import os
import bpy
from pathlib import Path

# ARKit to Unified Expressions mapping
# Only includes 1:1 mappings that exist in both standards
ARKIT_TO_UNIFIED = {
    # Eye movements
    "eyeLookUpRight": "EyeLookUpRight",
    "eyeLookDownRight": "EyeLookDownRight",
    "eyeLookInRight": "EyeLookInRight",
    "eyeLookOutRight": "EyeLookOutRight",
    "eyeLookUpLeft": "EyeLookUpLeft",
    "eyeLookDownLeft": "EyeLookDownLeft",
    "eyeLookInLeft": "EyeLookInLeft",
    "eyeLookOutLeft": "EyeLookOutLeft",

    # Eye expressions
    "eyeBlinkRight": "EyeClosedRight",
    "eyeBlinkLeft": "EyeClosedLeft",
    "eyeSquintRight": "EyeSquintRight",
    "eyeSquintLeft": "EyeSquintLeft",
    "eyeWideRight": "EyeWideRight",
    "eyeWideLeft": "EyeWideLeft",

    # Brow expressions
    "browDownRight": "BrowDownRight",
    "browDownLeft": "BrowDownLeft",
    "browInnerUp": "BrowInnerUp",
    "browOuterUpRight": "BrowOuterUpRight",
    "browOuterUpLeft": "BrowOuterUpLeft",

    # Nose
    "noseSneerRight": "NoseSneerRight",
    "noseSneerLeft": "NoseSneerLeft",

    # Cheeks
    "cheekSquintRight": "CheekSquintRight",
    "cheekSquintLeft": "CheekSquintLeft",
    "cheekPuff": "CheekPuff",

    # Jaw
    "jawOpen": "JawOpen",
    "mouthClose": "MouthClosed",
    "jawRight": "JawRight",
    "jawLeft": "JawLeft",
    "jawForward": "JawForward",

    # Lips
    "mouthRollUpper": "LipSuckUpper",
    "mouthRollLower": "LipSuckLower",
    "mouthFunnel": "LipFunnel",
    "mouthPucker": "LipPucker",

    # Mouth movements
    "mouthUpperUpRight": "MouthUpperUpRight",
    "mouthUpperUpLeft": "MouthUpperUpLeft",
    "mouthLowerDownRight": "MouthLowerDownRight",
    "mouthLowerDownLeft": "MouthLowerDownLeft",

    # Mouth expressions
    "mouthSmileRight": "MouthSmileRight",
    "mouthSmileLeft": "MouthSmileLeft",
    "mouthFrownRight": "MouthFrownRight",
    "mouthFrownLeft": "MouthFrownLeft",
    "mouthDimpleRight": "MouthDimpleRight",
    "mouthDimpleLeft": "MouthDimpleLeft",
    "mouthStretchRight": "MouthStretchRight",
    "mouthStretchLeft": "MouthStretchLeft",
    "mouthPressRight": "MouthPressRight",
    "mouthPressLeft": "MouthPressLeft",
    "mouthShrugUpper": "MouthUpperRight",  # Approximate mapping
    "mouthShrugLower": "MouthLowerRight",  # Approximate mapping
}

# Reverse mapping for potential future use
UNIFIED_TO_ARKIT = {v: k for k, v in ARKIT_TO_UNIFIED.items()}


def get_image_files(directory):
    """
    Get all image files from a directory

    Args:
        directory: Path to directory containing images

    Returns:
        List of absolute paths to image files
    """
    if not directory or not os.path.exists(directory):
        return []

    valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tga', '.exr', '.hdr'}
    image_files = []

    for file in Path(directory).iterdir():
        if file.is_file() and file.suffix.lower() in valid_extensions:
            image_files.append(str(file.absolute()))

    return image_files


def validate_scene_setup(props):
    """
    Validate that the scene is properly set up for dataset generation

    Args:
        props: CCABN properties from scene

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check camera
    if not props.camera:
        return False, "No camera selected"

    # Check lights
    if len(props.lights) == 0:
        return False, "No lights selected"

    # Check human faces
    if len(props.human_faces) == 0:
        return False, "No human face objects selected"

    # Check gray value ranges are valid
    if props.background_gray_min > props.background_gray_max:
        return False, "Background gray min cannot be greater than max"

    if props.headset_gray_min > props.headset_gray_max:
        return False, "Headset gray min cannot be greater than max"

    # Check selected blendshapes exist on all humans
    selected_shapes = [item.name for item in props.blendshape_list if item.selected]
    if len(selected_shapes) == 0:
        return False, "No blendshapes selected for randomization"

    for item in props.human_faces:
        if not item.obj:
            return False, "One or more human face references are invalid"

        human_obj = item.obj

        if not human_obj.data.shape_keys:
            return False, f"Object '{human_obj.name}' has no shape keys"

        shape_key_names = [sk.name for sk in human_obj.data.shape_keys.key_blocks]
        missing_shapes = [s for s in selected_shapes if s not in shape_key_names]

        if missing_shapes:
            return False, f"Object '{human_obj.name}' is missing blendshapes: {', '.join(missing_shapes)}"

    # Check output path
    if not props.output_path:
        return False, "No output path specified"

    # Expand Blender's relative path notation (//) and other paths
    try:
        # bpy.path.abspath handles Blender's // notation
        output_path = bpy.path.abspath(props.output_path)
        output_path = os.path.expanduser(os.path.expandvars(output_path))
        output_dir = Path(output_path).resolve()
    except Exception as e:
        return False, f"Invalid output path '{props.output_path}': {str(e)}"

    # Check if output directory exists or can be created
    if not output_dir.exists():
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            return False, f"Permission denied: Cannot create directory '{output_dir}'. Try a different location like /tmp/ccabn_output or ~/ccabn_output"
        except Exception as e:
            return False, f"Cannot create output directory '{output_dir}': {str(e)}"

    # Check if writable
    if not os.access(str(output_dir), os.W_OK):
        return False, f"Output directory is not writable: {output_dir}. Check permissions with: ls -la {output_dir.parent}"

    # Check images per human
    if props.images_per_human <= 0:
        return False, "Images per human must be greater than 0"

    return True, ""


def refresh_blendshape_list(context):
    """
    Refresh the blendshape list based on selected human faces

    Args:
        context: Blender context
    """
    props = context.scene.ccabn_props

    # Clear existing list
    props.blendshape_list.clear()

    # If no humans selected, return
    if len(props.human_faces) == 0:
        return

    # Collect all unique shape keys from selected humans
    all_shape_keys = set()
    for item in props.human_faces:
        if not item.obj:
            continue

        human_obj = item.obj

        if human_obj.data.shape_keys:
            for shape_key in human_obj.data.shape_keys.key_blocks:
                # Skip the basis shape
                if shape_key.name != "Basis":
                    all_shape_keys.add(shape_key.name)

    # Add to list
    for shape_name in sorted(all_shape_keys):
        item = props.blendshape_list.add()
        item.name = shape_name
        item.selected = False
        item.min_value = 0.0
        item.max_value = 1.0


def convert_blendshapes_arkit_to_unified(obj):
    """
    Convert ARKit blendshape names to Unified Expressions on a mesh object

    Args:
        obj: Blender mesh object with shape keys

    Returns:
        Tuple of (num_renamed, list_of_renamed_pairs)
    """
    if not obj.data.shape_keys:
        return 0, []

    renamed = []

    for shape_key in obj.data.shape_keys.key_blocks:
        if shape_key.name in ARKIT_TO_UNIFIED:
            old_name = shape_key.name
            new_name = ARKIT_TO_UNIFIED[old_name]
            shape_key.name = new_name
            renamed.append((old_name, new_name))

    return len(renamed), renamed
