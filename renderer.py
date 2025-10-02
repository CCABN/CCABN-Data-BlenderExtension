"""
Core rendering logic for CCABN Dataset Generator
"""

import bpy
import os
import random
import math
import json
from pathlib import Path
from mathutils import Vector, Euler


def kelvin_to_rgb(kelvin):
    """
    Convert color temperature in Kelvin to RGB values
    Based on Tanner Helland's algorithm

    Args:
        kelvin: Temperature in Kelvin (1000-40000)

    Returns:
        Tuple of (r, g, b) values in range 0-1
    """
    temp = kelvin / 100.0

    # Red
    if temp <= 66:
        red = 255
    else:
        red = temp - 60
        red = 329.698727446 * (red ** -0.1332047592)
        red = max(0, min(255, red))

    # Green
    if temp <= 66:
        green = temp
        green = 99.4708025861 * math.log(green) - 161.1195681661
    else:
        green = temp - 60
        green = 288.1221695283 * (green ** -0.0755148492)
    green = max(0, min(255, green))

    # Blue
    if temp >= 66:
        blue = 255
    elif temp <= 19:
        blue = 0
    else:
        blue = temp - 10
        blue = 138.5177312231 * math.log(blue) - 305.0447927307
        blue = max(0, min(255, blue))

    return (red / 255.0, green / 255.0, blue / 255.0)


def setup_render_settings(context, props):
    """
    Configure render settings for dataset generation

    Args:
        context: Blender context
        props: CCABN properties
    """
    scene = context.scene

    # Set render engine
    scene.render.engine = props.render_engine

    # Configure Cycles if selected
    if props.render_engine == 'CYCLES':
        scene.cycles.device = 'GPU'
        # Use GPU devices
        prefs = context.preferences
        cprefs = prefs.addons['cycles'].preferences
        cprefs.compute_device_type = 'CUDA'  # or 'OPTIX' or 'HIP' depending on GPU

        # Enable all GPU devices
        for device in cprefs.devices:
            device.use = True

    # Set resolution
    scene.render.resolution_x = 240
    scene.render.resolution_y = 240
    scene.render.resolution_percentage = 100

    # Set output to grayscale
    scene.render.image_settings.color_mode = 'BW'
    scene.render.image_settings.file_format = 'PNG'

    # Note: Camera FOV is controlled manually by the user
    # For OV2640 simulation, set camera FOV to 160° in the scene


def set_world_background_gray(scene, min_gray, max_gray):
    """
    Set a random gray color to the world background

    Args:
        scene: Blender scene
        min_gray: Minimum gray value (0.0 to 1.0)
        max_gray: Maximum gray value (0.0 to 1.0)

    Returns:
        The gray value that was set
    """
    # Generate random gray value
    gray_value = random.uniform(min_gray, max_gray)

    # Ensure world exists
    if not scene.world:
        scene.world = bpy.data.worlds.new("World")

    world = scene.world

    # Enable nodes
    world.use_nodes = True

    # Find or create Background node
    bg_node = None
    for node in world.node_tree.nodes:
        if node.type == 'BACKGROUND':
            bg_node = node
            break

    if not bg_node:
        # Create Background node if it doesn't exist
        bg_node = world.node_tree.nodes.new('ShaderNodeBackground')
        output = None
        for node in world.node_tree.nodes:
            if node.type == 'OUTPUT_WORLD':
                output = node
                break
        if not output:
            output = world.node_tree.nodes.new('ShaderNodeOutputWorld')
        world.node_tree.links.new(bg_node.outputs['Background'], output.inputs['Surface'])

    # Set the background color to the random gray
    bg_node.inputs['Color'].default_value = (gray_value, gray_value, gray_value, 1.0)
    bg_node.inputs['Strength'].default_value = 1.0

    return gray_value


def set_random_gray_material(obj, min_gray, max_gray):
    """
    Set a random gray color to an object's material

    Args:
        obj: Object with material
        min_gray: Minimum gray value (0.0 to 1.0)
        max_gray: Maximum gray value (0.0 to 1.0)

    Returns:
        The gray value that was set
    """
    if not obj or not obj.data.materials:
        # Create a material if it doesn't exist
        if obj:
            mat = bpy.data.materials.new(name=f"{obj.name}_Material")
            mat.use_nodes = True
            if len(obj.data.materials) == 0:
                obj.data.materials.append(mat)
            else:
                obj.data.materials[0] = mat
        else:
            return None

    mat = obj.data.materials[0]

    # Ensure material uses nodes
    if not mat.use_nodes:
        mat.use_nodes = True

    # Generate random gray value
    gray_value = random.uniform(min_gray, max_gray)

    # Find or create Principled BSDF node
    principled = None
    for node in mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            principled = node
            break

    if not principled:
        # Create Principled BSDF if it doesn't exist
        principled = mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
        output = None
        for node in mat.node_tree.nodes:
            if node.type == 'OUTPUT_MATERIAL':
                output = node
                break
        if not output:
            output = mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
        mat.node_tree.links.new(principled.outputs['BSDF'], output.inputs['Surface'])

    # Set the base color to the random gray
    principled.inputs['Base Color'].default_value = (gray_value, gray_value, gray_value, 1.0)

    return gray_value


def randomize_blendshapes(obj, blendshape_configs):
    """
    Randomize shape key values on an object

    Args:
        obj: Mesh object with shape keys
        blendshape_configs: List of (name, min, max) tuples

    Returns:
        Dictionary of {blendshape_name: value}
    """
    if not obj.data.shape_keys:
        return {}

    randomized = {}

    for shape_name, min_val, max_val in blendshape_configs:
        # Find the shape key
        shape_key = obj.data.shape_keys.key_blocks.get(shape_name)
        if shape_key:
            value = random.uniform(min_val, max_val)
            shape_key.value = value
            randomized[shape_name] = value

    return randomized


def randomize_camera(camera, props, base_location, base_rotation):
    """
    Randomize camera position and rotation

    Args:
        camera: Camera object
        props: CCABN properties
        base_location: Original camera location (Vector)
        base_rotation: Original camera rotation (Euler)
    """
    # Randomize position
    new_location = Vector((
        base_location.x + random.uniform(-props.camera_pos_x_var, props.camera_pos_x_var),
        base_location.y + random.uniform(-props.camera_pos_y_var, props.camera_pos_y_var),
        base_location.z + random.uniform(-props.camera_pos_z_var, props.camera_pos_z_var),
    ))
    camera.location = new_location

    # Randomize rotation (convert degrees to radians)
    new_rotation = Euler((
        base_rotation.x + math.radians(random.uniform(-props.camera_rot_x_var, props.camera_rot_x_var)),
        base_rotation.y + math.radians(random.uniform(-props.camera_rot_y_var, props.camera_rot_y_var)),
        base_rotation.z + math.radians(random.uniform(-props.camera_rot_z_var, props.camera_rot_z_var)),
    ), base_rotation.order)
    camera.rotation_euler = new_rotation


def randomize_light(light, props, base_location, base_energy):
    """
    Randomize light position, intensity, and color temperature

    Args:
        light: Light object
        props: CCABN properties
        base_location: Original light location (Vector)
        base_energy: Original light energy/intensity
    """
    # Randomize position
    new_location = Vector((
        base_location.x + random.uniform(-props.light_pos_x_var, props.light_pos_x_var),
        base_location.y + random.uniform(-props.light_pos_y_var, props.light_pos_y_var),
        base_location.z + random.uniform(-props.light_pos_z_var, props.light_pos_z_var),
    ))
    light.location = new_location

    # Randomize intensity (percentage of base energy)
    intensity_mult = random.uniform(props.light_intensity_min, props.light_intensity_max) / 100.0
    light.data.energy = base_energy * intensity_mult

    # Randomize color temperature
    temp = random.uniform(props.light_temp_min, props.light_temp_max)
    rgb = kelvin_to_rgb(temp)
    light.data.color = rgb


def hide_all_humans_except(human_faces, active_human):
    """
    Hide all human face objects except the active one

    Args:
        human_faces: Collection of ObjectItem instances
        active_human: The object to keep visible
    """
    for item in human_faces:
        if not item.obj:
            continue
        item.obj.hide_render = (item.obj != active_human)
        item.obj.hide_viewport = (item.obj != active_human)


def render_dataset(context, props):
    """
    Main rendering loop for dataset generation

    Args:
        context: Blender context
        props: CCABN properties

    Returns:
        Tuple of (success, message)
    """
    scene = context.scene

    # Setup render settings
    setup_render_settings(context, props)

    # Expand output path (handles Blender's // notation and ~ expansion)
    output_path = bpy.path.abspath(props.output_path)
    output_path = os.path.expanduser(os.path.expandvars(output_path))
    output_dir = Path(output_path).resolve()

    # Get selected blendshapes with ranges
    blendshape_configs = [
        (item.name, item.min_value, item.max_value)
        for item in props.blendshape_list
        if item.selected
    ]

    if not blendshape_configs:
        return False, "No blendshapes selected"

    # Store original states
    camera_base_loc = props.camera.location.copy()
    camera_base_rot = props.camera.rotation_euler.copy()

    light_base_states = []
    for item in props.lights:
        if not item.obj:
            continue
        light_base_states.append({
            'obj': item.obj,
            'location': item.obj.location.copy(),
            'energy': item.obj.data.energy,
        })

    # Counter for output files
    file_counter = 1

    total_images = len(props.human_faces) * props.images_per_human
    current_image = 0

    try:
        # Iterate through each human
        for human_idx, item in enumerate(props.human_faces):
            if not item.obj:
                continue

            human = item.obj
            print(f"\n=== Processing human {human_idx + 1}/{len(props.human_faces)}: {human.name} ===")

            # Hide all other humans
            hide_all_humans_except(props.human_faces, human)

            # Generate images for this human
            for img_idx in range(props.images_per_human):
                current_image += 1
                progress = (current_image / total_images) * 100

                print(f"[{progress:.1f}%] Rendering image {file_counter} (human {human_idx + 1}, image {img_idx + 1}/{props.images_per_human})")

                # Randomize blendshapes
                blendshape_values = randomize_blendshapes(human, blendshape_configs)

                # Set random gray background (world)
                bg_gray = set_world_background_gray(
                    scene,
                    props.background_gray_min,
                    props.background_gray_max
                )

                # Set random gray headset (if specified)
                headset_gray = None
                if props.headset_mesh:
                    headset_gray = set_random_gray_material(
                        props.headset_mesh,
                        props.headset_gray_min,
                        props.headset_gray_max
                    )

                # Randomize camera
                randomize_camera(props.camera, props, camera_base_loc, camera_base_rot)

                # Randomize lights
                for light_state in light_base_states:
                    randomize_light(
                        light_state['obj'],
                        props,
                        light_state['location'],
                        light_state['energy']
                    )

                # Update scene
                context.view_layer.update()

                # Render
                output_filename = f"{file_counter}.png"
                render_path = output_dir / output_filename
                scene.render.filepath = str(render_path)

                bpy.ops.render.render(write_still=True)

                # Save metadata
                metadata = {
                    "image": output_filename,
                    "human_object": human.name,
                    "blendshapes": blendshape_values,
                    "background_gray": bg_gray,
                }

                # Add headset gray if it was used
                if headset_gray is not None:
                    metadata["headset_gray"] = headset_gray

                metadata_path = output_dir / f"{file_counter}.json"
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)

                file_counter += 1

        # Restore original states
        props.camera.location = camera_base_loc
        props.camera.rotation_euler = camera_base_rot

        for light_state in light_base_states:
            light_state['obj'].location = light_state['location']
            light_state['obj'].data.energy = light_state['energy']

        # Show all humans again
        for item in props.human_faces:
            if item.obj:
                item.obj.hide_render = False
                item.obj.hide_viewport = False

        context.view_layer.update()

        return True, f"Successfully generated {total_images} images"

    except Exception as e:
        # On error, still restore states
        props.camera.location = camera_base_loc
        props.camera.rotation_euler = camera_base_rot

        for light_state in light_base_states:
            light_state['obj'].location = light_state['location']
            light_state['obj'].data.energy = light_state['energy']

        for item in props.human_faces:
            if item.obj:
                item.obj.hide_render = False
                item.obj.hide_viewport = False

        context.view_layer.update()

        return False, f"Error during rendering: {str(e)}. Saved {file_counter - 1} images before failure."
