# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import bpy_extras
from ..common import mlog
from ..cm import M3ImportContentPreset
from .. import m3export
from .. import m3import
from .. import shared


class ExportPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_quickExport"
    bl_label = "M3 Quick Export"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        scene = context.scene
        self.layout.prop(scene.m3_export_options, "path", text="")
        self.layout.operator("m3.quick_export", text="Export As M3")
        ExportPanel.draw_layout(self.layout, scene)

    @classmethod
    def draw_layout(cls, layout: bpy.types.UILayout, scene: bpy.types.Scene):
        layout.prop(scene.m3_export_options, "modlVersion")
        layout.prop(scene.m3_export_options, "animationExportAmount")


class M3_OT_export(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Export a M3 file"""
    bl_idname = "m3.export"
    bl_label = "Export M3 Model"
    bl_options = {"UNDO"}

    filename_ext = ".m3"
    filter_glob: bpy.props.StringProperty(default="*.m3", options={"HIDDEN"})

    filepath: bpy.props.StringProperty(
        name="File Path",
        description="Path of the file that should be created",
        maxlen=1024, default=""
    )

    def execute(self, context):
        scene = context.scene
        scene.m3_export_options.path = self.properties.filepath
        return m3export.export(scene, self, self.properties.filepath)

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def draw(self, context):
        ExportPanel.draw_layout(self.layout, context.scene)


class M3_OT_quickExport(bpy.types.Operator):
    bl_idname = "m3.quick_export"
    bl_label = "Quick Export"
    bl_description = "Exports the model to the specified m3 path without asking further questions"

    def invoke(self, context, event):
        scene = context.scene
        fileName = scene.m3_export_options.path
        return m3export.export(scene, self, fileName)


class ImportPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_quickImport"
    bl_label = "M3 Import"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene.m3_import_options, "path", text="M3 File")
        ImportPanel.draw_layout(layout, scene)
        layout.operator("m3.quick_import", text="Import M3")
        layout.operator("m3.generate_blender_materials", text="Generate Blender Materials")

    @classmethod
    def draw_content_import(cls, layout: bpy.types.UILayout, scene: bpy.types.Scene):
        layout.prop(scene.m3_import_options.content, "mesh")
        layout.prop(scene.m3_import_options.content, "materials")
        layout.prop(scene.m3_import_options.content, "bones")
        layout.prop(scene.m3_import_options.content, "rigging")
        layout.prop(scene.m3_import_options.content, "cameras")
        layout.prop(scene.m3_import_options.content, "fuzzyHitTests")
        layout.prop(scene.m3_import_options.content, "tightHitTest")
        layout.prop(scene.m3_import_options.content, "particleSystems")
        layout.prop(scene.m3_import_options.content, "ribbons")
        layout.prop(scene.m3_import_options.content, "forces")
        layout.prop(scene.m3_import_options.content, "rigidBodies")
        layout.prop(scene.m3_import_options.content, "lights")
        layout.prop(scene.m3_import_options.content, "billboardBehaviors")
        layout.prop(scene.m3_import_options.content, "attachmentPoints")
        layout.prop(scene.m3_import_options.content, "projections")
        layout.prop(scene.m3_import_options.content, "warps")

    @classmethod
    def draw_layout(cls, layout: bpy.types.UILayout, scene: bpy.types.Scene):
        layout.prop(scene.m3_import_options, "contentPreset")
        if scene.m3_import_options.contentPreset == M3ImportContentPreset.Custom:
            ImportPanel.draw_content_import(layout.box().column(heading="Content to import"), scene)
        if scene.m3_import_options.contentPreset not in [M3ImportContentPreset.MeshMaterials, M3ImportContentPreset.MeshMaterialsVG]:
            layout.prop(scene.m3_import_options, "armatureObject")

        layout.prop(scene.m3_import_options, "rootDirectory", text="Root Directory")
        layout.prop(scene.m3_import_options, "generateBlenderMaterials", text="Generate Blender Materials At Import")
        layout.prop(scene.m3_import_options, "applySmoothShading", text="Apply Smooth Shading")
        layout.prop(scene.m3_import_options, "markSharpEdges", text="Mark sharp edges")
        layout.prop(scene.m3_import_options, "teamColor", text="Team Color")


class M3_OT_import(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Load a M3 file"""
    bl_idname = "m3.import"
    bl_label = "Import M3"
    bl_options = {"UNDO"}

    filename_ext = ".m3"
    filter_glob: bpy.props.StringProperty(default="*.m3;*.m3a", options={"HIDDEN"})

    filepath: bpy.props.StringProperty(
        name="File Path",
        description="File path used for importing the simple M3 file",
        maxlen=1024,
        default=""
    )

    files: bpy.props.CollectionProperty(
        type=bpy.types.OperatorFileListElement,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    directory: bpy.props.StringProperty(
        subtype='DIR_PATH',
    )

    def execute(self, context):
        import os
        scene = context.scene
        
        # Determine files to import
        if self.files:
            file_paths = [os.path.join(self.directory, f.name) for f in self.files]
        else:
            file_paths = [self.properties.filepath]

        # Separate M3 and M3A
        m3_files = [f for f in file_paths if f.lower().endswith('.m3')]
        m3a_files = [f for f in file_paths if f.lower().endswith('.m3a')]

        # Sorting: Process M3 first, then M3As
        sorted_files = m3_files + m3a_files
        
        # Performance/Convenience: If only an M3 is selected, try to find matching animations
        if len(m3_files) == 1 and not m3a_files:
            m3_path = m3_files[0]
            m3_dir = os.path.dirname(m3_path)
            
            # Look in these subfolders
            search_dirs = [m3_dir, os.path.join(m3_dir, "animations"), os.path.join(m3_dir, "_requiredanims")]
            for s_dir in search_dirs:
                if os.path.isdir(s_dir):
                    for entry in os.listdir(s_dir):
                        if entry.lower().endswith(".m3a"):
                            anim_path = os.path.join(s_dir, entry)
                            if anim_path not in sorted_files:
                                mlog.info("Auto-discovered animation: %s" % entry)
                                sorted_files.append(anim_path)

        if not sorted_files:
            self.report({'WARNING'}, "No valid .m3 or .m3a files selected.")
            return {'CANCELLED'}

        # If we have an M3 in the list, we probably want to import it into a "fresh" target
        # so we clear any previously selected armature object to avoid accidental merging.
        if m3_files:
            scene.m3_import_options.armatureObject = None

        newly_created_armature = None
        for fpath in sorted_files:
            mlog.debug("Importing %s" % fpath)
            scene.m3_import_options.path = fpath
            
            # If we are importing an M3A and we already imported an M3 in this execution,
            # force the target to be that new one.
            if fpath.lower().endswith('.m3a') and newly_created_armature:
                scene.m3_import_options.armatureObject = newly_created_armature
                
            armature = m3import.importM3BasedOnM3ImportOptions(scene)
            
            if fpath.lower().endswith('.m3'):
                newly_created_armature = armature

        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def draw(self, context):
        ImportPanel.draw_layout(self.layout, context.scene)


class M3_OT_upscale_texture(bpy.types.Operator):
    """Upscale an image from bpy.data.images and optionally replace usages"""
    bl_idname = "m3.upscale_texture"
    bl_label = "Upscale Texture"

    def image_items(self, context):
        items = []
        for img in bpy.data.images:
            items.append((img.name, img.name, ""))
        if not items:
            items = [("", "<no images>", "")]
        return items

    image_name: bpy.props.EnumProperty(items=image_items, name="Image")
    scale: bpy.props.IntProperty(name="Scale", default=2, min=2, max=8)
    method: bpy.props.EnumProperty(
        name="Method",
        items=(
            ("lanczos", "Lanczos", "High-quality resampling (Pillow)",),
            ("bicubic", "Bicubic", "Bicubic resampling (Pillow)",),
            ("blender", "Blender", "Use Blender's built-in scaler (fallback)",),
        ),
        default="lanczos",
    )
    replace: bpy.props.BoolProperty(
        name="Replace usages",
        description="Replace occurrences of the original image in materials with the upscaled one",
        default=False,
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        img = bpy.data.images.get(self.image_name)
        if not img:
            self.report({"ERROR"}, "Image not found: %s" % self.image_name)
            return {"CANCELLED"}

        method = self.method if self.method in ("lanczos", "bicubic") else "blender"
        try:
            new = shared.upscale_image(img, scale=self.scale, method=method, out_name=f"{img.name}_x{self.scale}")
        except Exception as e:
            self.report({"ERROR"}, f"Upscale failed: {e}")
            return {"CANCELLED"}

        if not new:
            self.report({"ERROR"}, "Upscale failed (no result)")
            return {"CANCELLED"}

        # Optionally replace usages in materials
        if self.replace:
            for mat in bpy.data.materials:
                if not getattr(mat, 'node_tree', None):
                    continue
                for node in mat.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and getattr(node, 'image', None) and node.image.name == img.name:
                        node.image = new

        self.report({"INFO"}, f"Created upscaled image: {new.name} ({new.size[0]}x{new.size[1]})")
        return {"FINISHED"}


class UpscalePanel(bpy.types.Panel):
    bl_idname = "SCENE_PT_m3_upscale"
    bl_label = "M3 Texture Upscaler"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Simple Upscaler: choose an image and scale")
        layout.operator("m3.upscale_texture", text="Open Upscaler")


class M3_OT_quickImport(bpy.types.Operator):
    bl_idname = "m3.quick_import"
    bl_label = "Quick Import"
    bl_description = "Imports the model to the specified m3 path without asking further questions"

    def invoke(self, context, event):
        scene = context.scene
        m3import.importM3BasedOnM3ImportOptions(scene)
        return {"FINISHED"}
