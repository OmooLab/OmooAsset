import bpy
from bpy.props import (
    StringProperty,
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
)
from bpy_extras.io_utils import (
    ImportHelper
)
from bpy.types import (
    Operator
)
from pathlib import Path
from pxr import Usd


NODE_DICT = {
    "BaseColor": {
        "type": "color_tex",
        "source": "BaseColor:file",
        "to": ["SurfaceShader:Base Color"]
    },
    "Metalness": {
        "type": "float_tex",
        "source": "Metalness:file",
        "to": ["SurfaceShader:Metallic"]
    },
    "SpecularRoughness": {
        "type": "float_tex",
        "source": "SpecularRoughness:file",
        "to": ["SurfaceShader:Roughness"]
    },
    "SpecularColor": {
        "type": "color_tex",
        "source": "SpecularColor:file",
        "to": ["SurfaceShader:Specular Tint"]
    },
    "SpecularAnisotropy": {
        "type": "float_tex",
        "source": "SpecularAnisotropy:file",
        "to": ["SurfaceShader:Anisotropic"]
    },
    "SpecularRotation": {
        "type": "float_tex",
        "source": "SpecularRotation:file",
        "to": ["SurfaceShader:Anisotropic Rotation"]
    },
    "CoatWeight": {
        "type": "float_tex",
        "source": "CoatWeight:file",
        "to": ["SurfaceShader:Coat Weight"]
    },
    "CoatNormal": {
        "type": "normal_tex",
        "source": "CoatNormal:file",
        "to": ["CoatNormalMap:Color"]
    },
    "CoatNormalMap": {
        "type": "normal",
        "to": ["SurfaceShader:Coat Normal"]
    },
    "CoatColor": {
        "type": "color_tex",
        "source": "CoatColor:file",
        "to": ["SurfaceShader:Coat Tint"]
    },
    "CoatRoughness": {
        "type": "float_tex",
        "source": "CoatRoughness:file",
        "to": ["SurfaceShader:Coat Roughness"]
    },
    "SheenWeight": {
        "type": "float_tex",
        "source": "SheenWeight:file",
        "to": ["SurfaceShader:Sheen Weight"]
    },
    "SheenColor": {
        "type": "color_tex",
        "source": "SheenColor:file",
        "to": ["SurfaceShader:Sheen Tint"]
    },
    "SheenRoughness": {
        "type": "float_tex",
        "source": "SheenRoughness:file",
        "to": ["SurfaceShader:Sheen Roughness"]
    },
    "SubsurfaceWeight": {
        "type": "float_tex",
        "source": "SubsurfaceWeight:file",
        "to": ["SurfaceShader:Subsurface Weight"]
    },
    "SubsurfaceRadius": {
        "type": "color_tex",
        "source": "SubsurfaceRadius:file",
        "to": ["SurfaceShader:Subsurface Radius"]
    },
    "SubsurfaceScale": {
        "type": "float",
        "default": 1.0,
        "source": "SubsurfaceScale:value",
        "to": ["SubsurfaceSceneScale:0"]
    },
    "SubsurfaceSceneScale": {
        "type": "multiply",
        "to": ["SurfaceShader:Subsurface Scale"]
    },
    "SubsurfaceAnisotropy": {
        "type": "float_tex",
        "source": "SubsurfaceAnisotropy:file",
        "to": ["SubsurfaceAnisotropyRemap:Value"]
    },
    "SubsurfaceAnisotropyRemap": {
        "type": "remap",
        "to": ["SubsurfaceAnisotropyOffset:0"]
    },
    "SubsurfaceAnisotropyOffset": {
        "type": "add",
        "default": 0.0,
        "source": "SubsurfaceAnisotropyOffset:in2",
        "to": ["SurfaceShader:Subsurface Anisotropy"]
    },
    "EmissionScale": {
        "type": "float",
        "default": 1.0,
        "source": "EmissionScale:value",
        "to": ["SurfaceShader:Emission Strength"]
    },
    "EmissionColor": {
        "type": "color_tex",
        "source": "EmissionColor:file",
        "to": ["SurfaceShader:Emission Color"]
    },
    "Opacity": {
        "type": "float_tex",
        "source": "Opacity:file",
        "to": ["SurfaceShader:Alpha"]
    },
    "TransmissionWeight": {
        "type": "float_tex",
        "source": "TransmissionWeight:file",
        "to": ["SurfaceShader:Transmission Weight"]
    },
    "Normal": {
        "type": "normal_tex",
        "source": "Normal:file",
        "to": ["NormalMap:Color"]
    },
    "NormalMap": {
        "type": "normal",
        "to": ["CombinedNormal:Normal"]
    },
    "Detail": {
        "type": "float_tex",
        "source": "Detail:file",
        "to": ["DetailScale:0"]
    },
    "DetailScale": {
        "type": "multiply",
        "default": 1.0,
        "source": "DetailScale:in2",
        "to": ["CombinedNormal:Height", "CombinedDisplacement:1"]
    },
    "CombinedNormal": {
        "type": "normal_add",
        "to": ["SurfaceShader:Normal"]
    },
    "Displacement": {
        "type": "float_tex",
        "source": "Displacement:file",
        "to": ["CombinedDisplacement:0"]
    },
    "CombinedDisplacement": {
        "type": "add",
        "to": ["DisplacementShader:Height"]
    },
    "scene_scale": {
        "type": "float",
        "default": 1.0,
        "source": ":scene_scale",
        "to": ["SubsurfaceSceneScale:1"]
    },
    "displacement_on": {
        "type": "float",
        "default": 0.0,
        "source": ":displacement_on",
        "to": ["DisplacementShader:Scale"]
    }
}

PROP_DICT = {
    "IOR": {
        "default": 1.5,
        "source": "specular_IOR"
    },
    "Coat IOR": {
        "default": 1.5,
        "source": "coat_IOR"
    },
}


def get_object_prim_path(obj):
    tree = [obj]
    while obj.parent:
        obj = obj.parent
        tree.append(obj)

    return "/"+"/".join(map(lambda x: x.name.split(".")[0], tree[::-1]))


def get_object_root(obj):
    while obj.parent:
        obj = obj.parent
    return obj


class ImportOmooAsset(Operator, ImportHelper):
    bl_idname = "omoo_asset.import"
    bl_label = "Omoo Asset (.usd)"
    bl_description = "Load STL triangle mesh data"
    bl_options = {'UNDO'}

    filepath: StringProperty(
        subtype="FILE_PATH"
    )  # type: ignore

    filter_glob: StringProperty(
        default='*.usd',
        options={'HIDDEN'}
    )  # type: ignore

    global_scale: FloatProperty(
        name="Scale",
        soft_min=0.001, soft_max=1000.0,
        min=1e-6, max=1e6,
        default=1.0,
    )  # type: ignore
    
    def execute(self, context):
        file_path: str = Path(self.filepath).resolve().as_posix()

        stage = Usd.Stage.Open(file_path)
        asset_prim = stage.GetDefaultPrim()
        asset_name = asset_prim.GetName()
        materials_prim = stage.GetPrimAtPath(
            f"{asset_prim.GetPath()}/Materials")

        geometries_prim = stage.GetPrimAtPath(
            f"{asset_prim.GetPath()}/Geometries")
        geometry_paths = []
        for geometry_prim in geometries_prim.GetChildren():
            geometry_paths.append(geometry_prim.GetPath())

        # import usd
        bpy.ops.wm.usd_import(filepath=self.filepath, relative_path=True)

        # edit materials
        materials = set()
        root_active = get_object_root(bpy.context.active_object)
        for obj in bpy.data.objects:
            root_obj = get_object_root(obj)
            obj_path = get_object_prim_path(obj)
            if obj_path in geometry_paths and root_active == root_obj:
                for slot in obj.material_slots:
                    materials.add(slot.material)

        print(list(materials))

        for material in materials:
            material_name = material.name.split(".")[0]

            # check if is omoolab standard surface
            surface_shader_prim = stage.GetPrimAtPath(
                f"{asset_prim.GetPath()}/Materials/{material_name}/SurfaceShader")
            if not surface_shader_prim.IsValid():
                continue

            nodes = material.node_tree.nodes
            links = material.node_tree.links

            # Modify/Create "Surface Shader" and "Displacement Shader"
            surface_node = nodes.get("Principled BSDF")
            surface_node.name = "SurfaceShader"
            surface_node.label = "SurfaceShader"

            displacement_node = nodes.new('ShaderNodeDisplacement')
            displacement_node.name = "DisplacementShader"
            displacement_node.label = "DisplacementShader"
            displacement_node.inputs[1].default_value = 0

            out_node = nodes.get("Material Output")

            links.new(
                displacement_node.outputs[0],
                out_node.inputs['Displacement']
            )

            # Clean bleneder created shaders.
            for node in nodes:
                if node not in [surface_node, displacement_node, out_node]:
                    try:
                        bpy.data.images.remove(node.image)
                    except:
                        ...
                    nodes.remove(node)

            # Create node source node dict.
            for node_name in NODE_DICT.keys():
                # get node value
                node_value = NODE_DICT[node_name].get("default")
                if NODE_DICT[node_name].get("source"):
                    shader_name = NODE_DICT[node_name]["source"].split(":")[0]
                    shader_parm = NODE_DICT[node_name]["source"].split(":")[1]
                    shader_prim_path = f"{asset_prim.GetPath()}/Materials/{material_name}/{shader_name}"\
                        if shader_name != "" else f"{asset_prim.GetPath()}/Materials/{material_name}"
                    shader_prim = stage.GetPrimAtPath(shader_prim_path)

                    if shader_prim.IsValid():
                        shader_attribute = shader_prim.GetAttribute(
                            f"inputs:{shader_parm}")
                        if shader_attribute.IsValid():
                            if shader_parm == "file":
                                node_value = shader_attribute.Get(0).path
                                if node_value.startswith("./"):
                                    stack = shader_attribute.GetPropertyStack(
                                        1)
                                    file_path = Path(stack[0].layer.realPath)
                                    node_value = Path(
                                        file_path.parent, node_value).as_posix()

                            else:
                                if shader_attribute.Get(0):
                                    node_value = shader_attribute.Get(0)

                # create node
                node_type = NODE_DICT[node_name]["type"]
                # print(node_name, node_type, node_value)
                if node_type in ["color_tex", "float_tex", "normal_tex"]:
                    # get texture default value
                    tex_default_value = 0.0 if node_type == "float_tex" else (
                        0.0, 0.0, 0.0, 0.0)
                    if shader_prim.IsValid():
                        shader_default = shader_prim.GetAttribute(
                            "inputs:default")
                        if shader_default.IsValid():
                            tex_default_value = shader_default.Get(0)
                            if node_type != "float_tex":
                                tex_default_value = (
                                    tex_default_value[0], tex_default_value[1], tex_default_value[2], 1.0)
                    # print(tex_default_value)
                    if node_value:
                        # blender cannot read UNC path with slash
                        node_value = node_value.replace("/", "\\")
                        node = nodes.new('ShaderNodeTexImage')
                        node.image = bpy.data.images.load(node_value)
                        node.image.source = 'TILED'
                        node.image.colorspace_settings.name = 'Linear Rec.709 (sRGB)'\
                            if node_type == "color_tex" else 'Raw'
                    else:
                        # if not get any texture use constant value node
                        node = nodes.new('ShaderNodeRGB') \
                            if node_type != "float_tex" else nodes.new('ShaderNodeValue')
                        node.outputs[0].default_value = tex_default_value

                elif node_type == "normal":
                    node = nodes.new('ShaderNodeNormalMap')

                elif node_type == "remap":
                    node = nodes.new('ShaderNodeMapRange')
                    node.inputs[3].default_value = -1
                    node.inputs[4].default_value = 1

                elif node_type == "add":
                    node = nodes.new('ShaderNodeMath')
                    node.operation = 'ADD'
                    if node_value:
                        node.inputs[1].default_value = node_value

                elif node_type == "multiply":
                    node = nodes.new('ShaderNodeMath')
                    node.operation = 'MULTIPLY'
                    if node_value:
                        node.inputs[1].default_value = node_value

                elif node_type == "invert":
                    node = nodes.new('ShaderNodeMath')
                    node.operation = 'SUBTRACT'
                    node.inputs[0].default_value = 1

                elif node_type == "normal_add":
                    node = nodes.new('ShaderNodeBump')
                    
                elif node_type == "float":
                    node = nodes.new('ShaderNodeValue')
                    node.outputs[0].default_value = node_value
                    
                else:
                    ...

                node.name = node_name
                node.label = node_name

            # link the nodes
            for node_name in NODE_DICT.keys():
                node = nodes.get(node_name)
                to_list = NODE_DICT[node_name]["to"]

                for to in to_list:
                    # print(node_name, to)
                    target_node = nodes.get(to.split(":")[0])
                    target_input = to.split(":")[1]
                    links.new(
                        node.outputs[0],
                        target_node.inputs[
                            int(target_input)
                            if target_input.isnumeric() else target_input
                        ]
                    )

            for prop_name in PROP_DICT.keys():
                prop_value = PROP_DICT[prop_name].get("default")
                shader_parm = PROP_DICT[prop_name]['source']
                shader_prim = stage.GetPrimAtPath(
                    f"{asset_prim.GetPath()}/Materials/{material_name}/SurfaceShader")
                if shader_prim.IsValid():
                    shader_attribute = shader_prim.GetAttribute(
                        f"inputs:{shader_parm}")
                    if shader_attribute.IsValid():
                        if shader_attribute.Get(0):
                            prop_value = shader_attribute.Get(0)

                surface_node.inputs[prop_name].default_value = prop_value

            surface_node.subsurface_method = 'BURLEY'
            nodes["SubsurfaceScale"].outputs[0].default_value *= 10
            nodes["CombinedNormal"].inputs[0].default_value = 0.5

            material['scene_scale'] = nodes["scene_scale"].outputs[0].default_value
            material['displacement_on'] = nodes["displacement_on"].outputs[0].default_value == 1.0
            material.cycles.displacement_method = 'DISPLACEMENT'

            def add_driver(prop_name):
                driver = nodes[prop_name].outputs[0].driver_add(
                    "default_value")
                var1 = driver.driver.variables.new()
                var1.name = prop_name
                var1.targets[0].id_type = 'MATERIAL'
                var1.targets[0].id = material
                var1.targets[0].data_path = f'["{prop_name}"]'
                driver.driver.expression = var1.name

            add_driver('scene_scale')
            add_driver('displacement_on')

        return {'FINISHED'}


def menu_import(self, context):
    layout = self.layout
    layout.operator(ImportOmooAsset.bl_idname)


class OmooAssetMenu():
    def register():
        bpy.types.TOPBAR_MT_file_import.prepend(menu_import)  # Render menu

    def unregister():
        bpy.types.TOPBAR_MT_file_import.remove(menu_import)  # Render menu
