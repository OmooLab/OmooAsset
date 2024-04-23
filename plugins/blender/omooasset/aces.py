import bpy
from pathlib import Path


COLOR_TEXTURES = (
    'diffuse', 'diffusion', 'basecolor', 'base', 'albedo',
    'sss', 'subsurface',
    'emission', 'emissive',
)

RAW_TEXTURES = (
    'displacement', 'displace', 'disp', 'dsp', 'heightmap', 'height',
    'glossiness', 'glossy', 'gloss',
    'normal', 'norm', 'nor', 'nrml', 'nrm',
    'normalbump', 'bump', 'bmp',
    'specularity', 'specular', 'spec', 'spc',
    'roughness', 'rough', 'rgh',
    'metalness', 'metallic', 'metal', 'mtl',
    'ao', 'ambient', 'occlusion',
    'transparency', 'opacity', 'alpha',
    'transmission', 'thickness',
    'curvature', 'curv'
)


def matched_names(text: str, name_list: list[str]):
    """
    Returns the strings that match the given text from a string list in order of match degrees.
    """
    for name in name_list:
        if name in text.lower():
            return True

    return False


class FixColorSpaceBase:
    bl_options = {'REGISTER', 'UNDO'}

    @property
    def linear_colorspace(self):
        if bpy.context.scene.display_settings.display_device == 'ACES':
            return 'Utility - Linear - Rec.709'
        elif 'Display' in bpy.context.scene.display_settings.display_device:
            return 'Linear Rec.709 (sRGB)'
        else:
            return 'Linear Rec.709'

    @property
    def srgb_colorspace(self):
        if bpy.context.scene.display_settings.display_device == 'ACES':
            return 'Utility - sRGB - Texture'
        elif 'Display' in bpy.context.scene.display_settings.display_device:
            return 'sRGB - Texture'
        else:
            return 'sRGB'

    @property
    def raw_colorspace(self):
        if bpy.context.scene.display_settings.display_device == 'ACES':
            return 'Utility - Raw'
        elif 'Display' in bpy.context.scene.display_settings.display_device:
            return 'Raw'
        else:
            return 'Non-Color'

    def set_color_space(self, node_tree: bpy.types.ShaderNodeTree):
        for node in node_tree.nodes:
            if node.type == 'TEX_IMAGE' and node.image:
                if matched_names(node.label, COLOR_TEXTURES) \
                        or matched_names(node.image.name, COLOR_TEXTURES):

                    ext = Path(node.image.filepath).suffix
                    if ext == ".exr":
                        node.image.colorspace_settings.name = self.linear_colorspace
                    else:
                        node.image.colorspace_settings.name = self.srgb_colorspace

                if matched_names(node.label, RAW_TEXTURES) \
                        or matched_names(node.image.name, RAW_TEXTURES):
                    node.image.colorspace_settings.name = self.raw_colorspace

            elif node.type == 'GROUP':
                self.set_color_space(node.node_tree)

    @property
    def materials(self):
        return [material for material in bpy.data.materials if material.node_tree]

    def execute(self, _context):
        for material in self.materials:
            if material.node_tree:
                self.set_color_space(material.node_tree)

        return {'FINISHED'}


class FixColorSpaceAll(FixColorSpaceBase, bpy.types.Operator):
    bl_idname = "scene.fix_colorspace_all"
    bl_label = "Filmic"


class FixColorSpaceSelected(FixColorSpaceBase, bpy.types.Operator):
    bl_idname = "scene.fix_colorspace_selected"
    bl_label = "Filmic"

    @property
    def materials(self):
        selected = [obj for obj in bpy.context.selected_objects]
        materials = []
        for obj in selected:
            for material_slot in obj.material_slots:
                materials.append(material_slot.material)
        return materials


class FixColorSpace_PT_Panel(bpy.types.Panel):
    bl_idname = "FIXCOLORSPACE_PT_Panel"
    bl_label = "Fix Color Space"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"  # change Tool to any custom name if you want a new tab
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        layout.operator("scene.fix_colorspace_all",
                        text="Fix ColorSpace (All)")
        layout.operator("scene.fix_colorspace_selected",
                        text="Fix ColorSpace (Selected)")
