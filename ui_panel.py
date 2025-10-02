"""
UI Panel for CCABN Dataset Generator
"""

import bpy
from bpy.types import Panel, UIList


class CCABN_UL_ObjectList(UIList):
    """UI List for objects (lights and human faces)"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item.obj:
                layout.label(text=item.obj.name, icon='OBJECT_DATA')
            else:
                layout.label(text="<None>", icon='ERROR')
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon='OBJECT_DATA')


class CCABN_UL_BlendshapeList(UIList):
    """UI List for blendshapes with selection and range controls"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)

            # Checkbox for selection
            row.prop(item, "selected", text="")

            # Name
            row.label(text=item.name)

            # Min/Max range
            row.prop(item, "min_value", text="")
            row.label(text="-")
            row.prop(item, "max_value", text="")

        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.prop(item, "selected", text="")


class CCABN_PT_MainPanel(Panel):
    """Main panel for CCABN Dataset Generator"""
    bl_label = "CCABN Dataset Generator"
    bl_idname = "CCABN_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CCABN'

    def draw(self, context):
        layout = self.layout
        props = context.scene.ccabn_props

        # Scene Setup Section
        box = layout.box()
        box.label(text="Scene Setup", icon='SCENE_DATA')

        box.prop_search(props, "camera", context.scene, "objects", text="Camera")

        # Lights list
        box.label(text="Lights:")
        row = box.row()
        row.template_list(
            "CCABN_UL_ObjectList",
            "lights",
            props,
            "lights",
            props,
            "lights_index",
            rows=3
        )
        col = row.column(align=True)
        col.operator("ccabn.add_light", icon='ADD', text="")
        col.operator("ccabn.remove_light", icon='REMOVE', text="")

        box.label(text="Select a light in the scene and click +", icon='INFO')

        # Human faces list
        box.label(text="Human Faces:")
        row = box.row()
        row.template_list(
            "CCABN_UL_ObjectList",
            "human_faces",
            props,
            "human_faces",
            props,
            "human_faces_index",
            rows=3
        )
        col = row.column(align=True)
        col.operator("ccabn.add_human_face", icon='ADD', text="")
        col.operator("ccabn.remove_human_face", icon='REMOVE', text="")

        box.label(text="Select a mesh in the scene and click +", icon='INFO')

        box.prop_search(props, "headset_mesh", context.scene, "objects", text="Headset Mesh (Optional)")

        # Human face conversion
        if len(props.human_faces) > 0:
            row = box.row()
            row.operator("ccabn.convert_blendshapes", icon='FILE_REFRESH')

        # Gray Tone Ranges Section
        box = layout.box()
        box.label(text="Random Gray Tones", icon='COLOR')

        col = box.column(align=True)
        col.label(text="Background Gray Range:")
        row = col.row(align=True)
        row.prop(props, "background_gray_min")
        row.prop(props, "background_gray_max")

        col.separator()
        col.label(text="Headset Gray Range:")
        row = col.row(align=True)
        row.prop(props, "headset_gray_min")
        row.prop(props, "headset_gray_max")

        box.label(text="0.0 = Black, 1.0 = White", icon='INFO')

        # Blendshapes Section
        box = layout.box()
        box.label(text="Blendshapes", icon='SHAPEKEY_DATA')

        row = box.row()
        row.operator("ccabn.refresh_blendshapes", icon='FILE_REFRESH')

        if len(props.blendshape_list) > 0:
            row = box.row()
            row.operator("ccabn.select_all_blendshapes", text="All")
            row.operator("ccabn.deselect_all_blendshapes", text="None")

            box.template_list(
                "CCABN_UL_BlendshapeList",
                "",
                props,
                "blendshape_list",
                props,
                "blendshape_list_index",
                rows=6
            )

            box.label(text="Min/Max: Random range (0.0 - 1.0)", icon='INFO')
        else:
            box.label(text="No blendshapes found", icon='ERROR')
            box.label(text="Select human faces and click Refresh")

        # Camera Variation Section
        box = layout.box()
        box.label(text="Camera Variations", icon='CAMERA_DATA')

        col = box.column(align=True)
        col.label(text="Position (meters):")
        row = col.row(align=True)
        row.prop(props, "camera_pos_x_var")
        row.prop(props, "camera_pos_y_var")
        row.prop(props, "camera_pos_z_var")

        col.separator()
        col.label(text="Rotation (degrees):")
        row = col.row(align=True)
        row.prop(props, "camera_rot_x_var")
        row.prop(props, "camera_rot_y_var")
        row.prop(props, "camera_rot_z_var")

        # Light Variation Section
        box = layout.box()
        box.label(text="Light Variations", icon='LIGHT')

        col = box.column(align=True)
        col.label(text="Position (meters):")
        row = col.row(align=True)
        row.prop(props, "light_pos_x_var")
        row.prop(props, "light_pos_y_var")
        row.prop(props, "light_pos_z_var")

        col.separator()
        col.label(text="Intensity (%):")
        row = col.row(align=True)
        row.prop(props, "light_intensity_min")
        row.prop(props, "light_intensity_max")

        col.separator()
        col.label(text="Color Temperature (K):")
        row = col.row(align=True)
        row.prop(props, "light_temp_min")
        row.prop(props, "light_temp_max")

        # Output Settings Section
        box = layout.box()
        box.label(text="Output Settings", icon='OUTPUT')

        box.prop(props, "output_path", text="")
        box.prop(props, "images_per_human")
        box.prop(props, "render_engine", text="Engine")

        box.label(text="Resolution: 240x240 grayscale", icon='INFO')
        box.label(text="Set camera FOV to 160° for OV2640 simulation", icon='INFO')

        # Generate Button
        layout.separator()

        if props.is_rendering:
            layout.label(text="Rendering in progress...", icon='RENDER_ANIMATION')
        else:
            total_images = len(props.human_faces) * props.images_per_human
            layout.label(text=f"Total images: {total_images}", icon='RENDER_STILL')
            layout.operator("ccabn.generate_dataset", icon='PLAY', text="Generate Dataset")


# Registration
classes = (
    CCABN_UL_ObjectList,
    CCABN_UL_BlendshapeList,
    CCABN_PT_MainPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
