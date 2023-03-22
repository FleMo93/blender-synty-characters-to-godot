from . import clean_scene
import re
import os
import bpy

bl_info = {
    # required
    "name": "Synty to Godot",
    "blender": (3, 4, 1),
    "category": "Import-Export",
    # optional
    "version": (1, 0, 0),
    "author": "Florian Hammer",
    "description": "Cleaning up and prepare Synty assets for the godot engine",
    "doc_url": "https://github.com/FleMo93/blender-synty-characters-to-godot",
    "support": "COMMUNITY",
    "location": "Sidebar > Misc"
}


single_fbx_import_filename = ""


def cleanup_current_character():
    print("Cleanup...")

    def get_relevant_armature():
        for i in range(len(bpy.data.armatures)):
            if len(bpy.data.armatures[i].edit_bones) > 0:
                return bpy.data.armatures[i]

    bpy.ops.object.mode_set(mode="POSE")
    bpy.ops.pose.transforms_clear()
    bpy.ops.object.mode_set(mode="EDIT")

    armature = get_relevant_armature()

    def delete_bone(name):
        if name in armature.edit_bones:
            armature.edit_bones.remove(armature.edit_bones[name])

    delete_bone("ik_hand_root")
    delete_bone("ik_hand_gun")
    delete_bone("ik_hand_l")
    delete_bone("ik_hand_r")
    delete_bone("ik_foot_root")
    delete_bone("ik_foot_l")
    delete_bone("ik_foot_r")

    armature.edit_bones["Pelvis"].head.z = armature.edit_bones["Pelvis"].tail.z

    bpy.ops.armature.select_all(action='SELECT')
    bpy.ops.armature.roll_clear(roll=0.0)
    bpy.ops.object.mode_set(mode="OBJECT")


def import_fbx(file, custom_normals):
    print("Import: " + file)
    bpy.ops.import_scene.fbx(
        filepath=file,
        use_custom_normals=custom_normals,
        use_anim=False,
        ignore_leaf_bones=True,
        force_connect_children=True)


def export_gltf(filepath):
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_animations=False
    )


class CLEANUP_PROPS(bpy.types.PropertyGroup):
    source: bpy.props.StringProperty(
        default="")
    target: bpy.props.StringProperty(
        default="")
    custom_normals: bpy.props.BoolProperty(default=True)
    single_fbx_import_filename: bpy.props.StringProperty(default="hi")


class DIRECTORY_PICKER_OPERATOR(bpy.types.Operator):
    bl_idname = "opr.directory_picker_operator"
    bl_label = "Pick directory"

    directory: bpy.props.StringProperty()
    filter_folder: bpy.props.BoolProperty(default=True, options={"HIDDEN"})
    directory_type: bpy.props.StringProperty()

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        print(self.directory)
        bpy.context.scene.CleanupProps[self.directory_type] = self.directory
        return {"FINISHED"}


class BATCH_CLEANUP_OPERATOR(bpy.types.Operator):
    bl_idname = "opr.batch_cleanup_operator"
    bl_label = "Character cleanup directory"

    def execute(self, context):
        directory = bpy.context.scene.CleanupProps.source
        for filename in os.listdir(directory):
            if not filename.endswith(".fbx"):
                continue
            clean_scene.clean_scene()
            source_file = os.path.join(directory, filename)
            import_fbx(
                source_file, bpy.context.scene.CleanupProps.custom_normals)
            target_file = os.path.join(bpy.context.scene.CleanupProps.target, filename)
            target_file = re.sub(r".fbx$", ".glb", target_file)
            cleanup_current_character()
            print("Export: " + target_file)
            export_gltf(target_file)
        return {"FINISHED"}


class SINGLE_CLEAN_SCENE(bpy.types.Operator):
    bl_idname = "opr.single_clean_scene"
    bl_label = "Clean scene"

    def execute(self, context):
        clean_scene.clean_scene()
        return {"FINISHED"}


class SINGLE_FBX_IMPORT_OPERATOR(bpy.types.Operator):
    bl_idname = "opr.single_fbx_import_operator"
    bl_label = "Import single synty character fbx"
    filepath: bpy.props.StringProperty()

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, contect):
        bpy.context.scene.CleanupProps.single_fbx_import_filename = os.path.basename(
            self.filepath)
        import_fbx(self.filepath, bpy.context.scene.CleanupProps.custom_normals)
        return {"FINISHED"}


class SINGLE_CLEANUP_OPERATOR(bpy.types.Operator):
    bl_idname = "opr.cleanup_operator"
    bl_label = "Character cleanup"

    def execute(self, context):
        cleanup_current_character()
        return {"FINISHED"}


class SINGLE_EXPORT_GLTF_OPERATOR(bpy.types.Operator):
    bl_idname = "opr.export_gltf_operator"
    bl_label = "Export character"
    filepath: bpy.props.StringProperty(
        name="File Path",
        description="Filepath used for exporting the file",
        maxlen=1024,
        subtype='FILE_PATH',)
    filename_ext = ".glb"
    filename = bpy.props.StringProperty()

    def invoke(self, context, event):
        self.filepath = re.sub(
            r".fbx$",
            ".glb",
            bpy.context.scene.CleanupProps.single_fbx_import_filename)
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        print("Export: " + self.filepath)
        export_gltf(self.filepath)
        return {"FINISHED"}


class MAINPANEL(bpy.types.Panel):
    bl_idname = "synty_to_godot"
    bl_label = "Synty to Godot"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        col_main = self.layout.column()
        col_main.label(text="Character cleanup")
        col_main.label(text="Settings")
        row = col_main.row()
        row.prop(bpy.context.scene.CleanupProps,
                 property="custom_normals", text="Custom normals")
        col_main.label(text="")

        col_main.label(text="Batch")
        col_batch = col_main.column()
        row = col_batch.row()
        op = row.operator(
            "opr.directory_picker_operator", text="Source dir")
        op.directory_type = "source"
        row.prop(bpy.context.scene.CleanupProps, property="source", text="")

        row = col_batch.row()
        op = row.operator(
            "opr.directory_picker_operator", text="Target dir")
        op.directory_type = "target"
        row.prop(bpy.context.scene.CleanupProps, property="target", text="")

        col_batch.operator("opr.batch_cleanup_operator",
                           text="Batch characters in directory")

        col_main.label(text="")
        col_main.label(text="Single")
        col_single = col_main.column()

        col_single.operator("opr.single_clean_scene",
                            text="Clean scene")
        col_single.operator("opr.single_fbx_import_operator",
                            text="Import fbx")
        col_single.operator("opr.cleanup_operator",
                            text="Cleanup current character")
        col_single.operator("opr.export_gltf_operator",
                            text="Export gLTF")


classes = (
    CLEANUP_PROPS,
    DIRECTORY_PICKER_OPERATOR,
    BATCH_CLEANUP_OPERATOR,
    SINGLE_CLEAN_SCENE,
    SINGLE_FBX_IMPORT_OPERATOR,
    SINGLE_CLEANUP_OPERATOR,
    SINGLE_EXPORT_GLTF_OPERATOR,
    MAINPANEL
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.CleanupProps = bpy.props.PointerProperty(
        type=CLEANUP_PROPS)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del (bpy.types.Scene.CleanupProps)


if __name__ == "__main__":
    register()
