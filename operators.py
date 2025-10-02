"""
Operators for CCABN Dataset Generator
"""

import bpy
from bpy.types import Operator
from .utils import (
    convert_blendshapes_arkit_to_unified,
    validate_scene_setup,
    refresh_blendshape_list,
)
from .renderer import render_dataset


class CCABN_OT_ConvertBlendshapes(Operator):
    """Convert ARKit blendshape names to Unified Expressions on selected human faces"""
    bl_idname = "ccabn.convert_blendshapes"
    bl_label = "Convert ARKit to Unified Expressions"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.ccabn_props

        if len(props.human_faces) == 0:
            self.report({'ERROR'}, "No human faces selected")
            return {'CANCELLED'}

        total_renamed = 0
        report_lines = []

        for item in props.human_faces:
            if not item.obj:
                continue

            num_renamed, renamed_list = convert_blendshapes_arkit_to_unified(item.obj)
            total_renamed += num_renamed

            if num_renamed > 0:
                report_lines.append(f"{item.obj.name}: {num_renamed} blendshapes renamed")
                print(f"\n=== {item.obj.name} ===")
                for old_name, new_name in renamed_list:
                    print(f"  {old_name} → {new_name}")

        if total_renamed == 0:
            self.report({'WARNING'}, "No ARKit blendshapes found to convert")
        else:
            self.report({'INFO'}, f"Converted {total_renamed} blendshapes across {len(props.human_faces)} objects")
            print(f"\n✓ Total: {total_renamed} blendshapes converted")

            # Refresh blendshape list to show new names
            refresh_blendshape_list(context)

        return {'FINISHED'}


class CCABN_OT_RefreshBlendshapes(Operator):
    """Refresh the blendshape list from selected human faces"""
    bl_idname = "ccabn.refresh_blendshapes"
    bl_label = "Refresh Blendshapes"
    bl_options = {'REGISTER'}

    def execute(self, context):
        refresh_blendshape_list(context)
        props = context.scene.ccabn_props

        num_shapes = len(props.blendshape_list)
        if num_shapes == 0:
            self.report({'WARNING'}, "No blendshapes found on selected human faces")
        else:
            self.report({'INFO'}, f"Found {num_shapes} unique blendshapes")

        return {'FINISHED'}


class CCABN_OT_GenerateDataset(Operator):
    """Generate dataset by rendering randomized facial expressions"""
    bl_idname = "ccabn.generate_dataset"
    bl_label = "Generate Dataset"
    bl_options = {'REGISTER'}

    _timer = None
    _rendering = False

    def modal(self, context, event):
        if event.type == 'TIMER':
            if not self._rendering:
                return {'FINISHED'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        props = context.scene.ccabn_props

        # Validate setup
        is_valid, error_msg = validate_scene_setup(props)
        if not is_valid:
            self.report({'ERROR'}, f"Invalid setup: {error_msg}")
            return {'CANCELLED'}

        # Confirm with user
        total_images = len(props.human_faces) * props.images_per_human
        print(f"\n{'='*60}")
        print(f"CCABN Dataset Generation Starting")
        print(f"{'='*60}")
        print(f"Humans: {len(props.human_faces)}")
        print(f"Images per human: {props.images_per_human}")
        print(f"Total images: {total_images}")
        print(f"Output: {props.output_path}")
        print(f"Render engine: {props.render_engine}")
        print(f"{'='*60}\n")

        # Set rendering flag
        props.is_rendering = True

        # Run rendering
        success, message = render_dataset(context, props)

        # Clear rendering flag
        props.is_rendering = False

        if success:
            self.report({'INFO'}, message)
            print(f"\n{'='*60}")
            print(f"✓ {message}")
            print(f"{'='*60}\n")
        else:
            self.report({'ERROR'}, message)
            print(f"\n{'='*60}")
            print(f"✗ {message}")
            print(f"{'='*60}\n")

        return {'FINISHED'}


class CCABN_OT_SelectAllBlendshapes(Operator):
    """Select all blendshapes in the list"""
    bl_idname = "ccabn.select_all_blendshapes"
    bl_label = "Select All"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.ccabn_props

        for item in props.blendshape_list:
            item.selected = True

        self.report({'INFO'}, f"Selected all {len(props.blendshape_list)} blendshapes")
        return {'FINISHED'}


class CCABN_OT_DeselectAllBlendshapes(Operator):
    """Deselect all blendshapes in the list"""
    bl_idname = "ccabn.deselect_all_blendshapes"
    bl_label = "Deselect All"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.ccabn_props

        for item in props.blendshape_list:
            item.selected = False

        self.report({'INFO'}, "Deselected all blendshapes")
        return {'FINISHED'}


class CCABN_OT_AddLight(Operator):
    """Add selected object as a light to randomize"""
    bl_idname = "ccabn.add_light"
    bl_label = "Add Light"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.ccabn_props

        if not context.active_object:
            self.report({'ERROR'}, "No active object selected")
            return {'CANCELLED'}

        obj = context.active_object

        # Check if it's a light
        if obj.type != 'LIGHT':
            self.report({'ERROR'}, f"'{obj.name}' is not a light object")
            return {'CANCELLED'}

        # Check if already in list
        for item in props.lights:
            if item.obj == obj:
                self.report({'WARNING'}, f"Light '{obj.name}' already in list")
                return {'CANCELLED'}

        # Add to list
        item = props.lights.add()
        item.obj = obj

        self.report({'INFO'}, f"Added light: {obj.name}")
        return {'FINISHED'}


class CCABN_OT_RemoveLight(Operator):
    """Remove light from the list"""
    bl_idname = "ccabn.remove_light"
    bl_label = "Remove Light"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.ccabn_props

        if props.lights_index >= 0 and props.lights_index < len(props.lights):
            obj_name = props.lights[props.lights_index].obj.name if props.lights[props.lights_index].obj else "Unknown"
            props.lights.remove(props.lights_index)
            props.lights_index = max(0, props.lights_index - 1)
            self.report({'INFO'}, f"Removed light: {obj_name}")
        else:
            self.report({'ERROR'}, "No light selected to remove")
            return {'CANCELLED'}

        return {'FINISHED'}


class CCABN_OT_AddHumanFace(Operator):
    """Add selected object as a human face"""
    bl_idname = "ccabn.add_human_face"
    bl_label = "Add Human Face"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.ccabn_props

        if not context.active_object:
            self.report({'ERROR'}, "No active object selected")
            return {'CANCELLED'}

        obj = context.active_object

        # Check if it's a mesh
        if obj.type != 'MESH':
            self.report({'ERROR'}, f"'{obj.name}' is not a mesh object")
            return {'CANCELLED'}

        # Check if already in list
        for item in props.human_faces:
            if item.obj == obj:
                self.report({'WARNING'}, f"Mesh '{obj.name}' already in list")
                return {'CANCELLED'}

        # Add to list
        item = props.human_faces.add()
        item.obj = obj

        self.report({'INFO'}, f"Added human face: {obj.name}")
        return {'FINISHED'}


class CCABN_OT_RemoveHumanFace(Operator):
    """Remove human face from the list"""
    bl_idname = "ccabn.remove_human_face"
    bl_label = "Remove Human Face"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.ccabn_props

        if props.human_faces_index >= 0 and props.human_faces_index < len(props.human_faces):
            obj_name = props.human_faces[props.human_faces_index].obj.name if props.human_faces[props.human_faces_index].obj else "Unknown"
            props.human_faces.remove(props.human_faces_index)
            props.human_faces_index = max(0, props.human_faces_index - 1)
            self.report({'INFO'}, f"Removed human face: {obj_name}")

            # Refresh blendshape list
            refresh_blendshape_list(context)
        else:
            self.report({'ERROR'}, "No human face selected to remove")
            return {'CANCELLED'}

        return {'FINISHED'}


# Registration
classes = (
    CCABN_OT_ConvertBlendshapes,
    CCABN_OT_RefreshBlendshapes,
    CCABN_OT_GenerateDataset,
    CCABN_OT_SelectAllBlendshapes,
    CCABN_OT_DeselectAllBlendshapes,
    CCABN_OT_AddLight,
    CCABN_OT_RemoveLight,
    CCABN_OT_AddHumanFace,
    CCABN_OT_RemoveHumanFace,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
