import c4d
from pathlib import Path
from pxr import Usd
import maxon

# Be sure to use a unique ID obtained from www.plugincafe.com
PLUGIN_ID = 1062988

OUTPUT: maxon.Id = maxon.Id(
    "com.redshift3d.redshift4c4d.node.output")

STANDARDMATERIAL: maxon.Id = maxon.Id(
    "com.redshift3d.redshift4c4d.nodes.core.standardmaterial")

DISPLACEMENT: maxon.Id = maxon.Id(
    "com.redshift3d.redshift4c4d.nodes.core.displacement")

TEXTURESAMPLER: maxon.Id = maxon.Id(
    "com.redshift3d.redshift4c4d.nodes.core.texturesampler")

BUMPMAP: maxon.Id = maxon.Id(
    "com.redshift3d.redshift4c4d.nodes.core.bumpmap")

BUMPBLENDER: maxon.Id = maxon.Id(
    "com.redshift3d.redshift4c4d.nodes.core.bumpblender")

COLOR: maxon.Id = maxon.Id(
    "net.maxon.asset.utility.color")

VALUE: maxon.Id = maxon.Id(
    "net.maxon.node.type")

MUL: maxon.Id = maxon.Id(
    "com.redshift3d.redshift4c4d.nodes.core.rsmathmul")

VECTORMUL: maxon.Id = maxon.Id(
    "com.redshift3d.redshift4c4d.nodes.core.rsmathmulvector")

ADD: maxon.Id = maxon.Id(
    "com.redshift3d.redshift4c4d.nodes.core.rsmathadd")

RANGE: maxon.Id = maxon.Id(
    "com.redshift3d.redshift4c4d.nodes.core.rsmathrange")

INVERT: maxon.Id = maxon.Id(
    "com.redshift3d.redshift4c4d.nodes.core.rsmathinv")

NODE_DICT = {
    "BaseColor": {
        "type": "color_tex",
        "source": "BaseColor:file",
        "to": ["SurfaceShader:base_color", "SurfaceShader:ms_color", "SurfaceShader:refr_color"]
    },
    "Metalness": {
        "type": "float_tex",
        "source": "Metalness:file",
        "to": ["SurfaceShader:metalness"]
    },
    "SpecularWeight": {
        "type": "float_tex",
        "source": "SpecularWeight:file",
        "to": ["SurfaceShader:refl_weight"]
    },
    "SpecularRoughness": {
        "type": "float_tex",
        "source": "SpecularRoughness:file",
        "to": ["SurfaceShader:refl_roughness"]
    },
    "SpecularColor": {
        "type": "color_tex",
        "source": "SpecularColor:file",
        "to": ["SurfaceShader:refl_color"]
    },
    "SpecularAnisotropy": {
        "type": "float_tex",
        "source": "SpecularAnisotropy:file",
        "to": ["SurfaceShader:refl_aniso"]
    },
    "SpecularRotation": {
        "type": "float_tex",
        "source": "SpecularRotation:file",
        "to": ["SurfaceShader:refl_aniso_rotation"]
    },
    "CoatWeight": {
        "type": "float_tex",
        "source": "CoatWeight:file",
        "to": ["SurfaceShader:coat_weight"]
    },
    "CoatNormal": {
        "type": "normal_tex",
        "source": "CoatNormal:file",
        "to": ["CoatNormalMap:input"]
    },
    "CoatNormalMap": {
        "type": "normal",
        "to": ["SurfaceShader:coat_bump_input"]
    },
    "CoatColor": {
        "type": "color_tex",
        "source": "CoatColor:file",
        "to": ["SurfaceShader:coat_color"]
    },
    "CoatRoughness": {
        "type": "float_tex",
        "source": "CoatRoughness:file",
        "to": ["SurfaceShader:coat_roughness"]
    },
    "SheenWeight": {
        "type": "float_tex",
        "source": "SheenWeight:file",
        "to": ["SurfaceShader:sheen_weight"]
    },
    "SheenColor": {
        "type": "color_tex",
        "source": "SheenColor:file",
        "to": ["SurfaceShader:sheen_color"]
    },
    "SheenRoughness": {
        "type": "float_tex",
        "source": "SheenRoughness:file",
        "to": ["SurfaceShader:sheen_roughness"]
    },
    "SubsurfaceWeight": {
        "type": "float_tex",
        "source": "SubsurfaceWeight:file",
        "to": ["SurfaceShader:ms_amount"]
    },
    "SubsurfaceRadius": {
        "type": "color_tex",
        "source": "SubsurfaceRadius:file",
        "to": ["SubsurfaceSceneScale:input1"]
    },
    "SubsurfaceScale": {
        "type": "float",
        "default": 1.0,
        "source": "SubsurfaceScale:value",
        "to": ["SurfaceShader:ms_radius_scale"]
    },
    "SubsurfaceSceneScale": {
        "type": "vector_multiply",
        "to": ["SurfaceShader:ms_radius", "SurfaceShader:ss_scatter_color"]
    },
    "SubsurfaceAnisotropy": {
        "type": "float_tex",
        "source": "SubsurfaceAnisotropy:file",
        "to": ["SubsurfaceAnisotropyRemap:input"]
    },
    "SubsurfaceAnisotropyRemap": {
        "type": "remap",
        "to": ["SubsurfaceAnisotropyOffset:input1"]
    },
    "SubsurfaceAnisotropyOffset": {
        "type": "add",
        "default": 0.0,
        "source": "SubsurfaceAnisotropyOffset:in2",
        "to": ["SurfaceShader:ms_phase"]
    },
    "EmissionScale": {
        "type": "float",
        "default": 1.0,
        "source": "EmissionScale:value",
        "to": ["SurfaceShader:emission_weight"]
    },
    "EmissionColor": {
        "type": "color_tex",
        "source": "EmissionColor:file",
        "to": ["SurfaceShader:emission_color"]
    },
    "Opacity": {
        "type": "float_tex",
        "source": "Opacity:file",
        "to": ["SurfaceShader:opacity_color"]
    },
    "TransmissionWeight": {
        "type": "float_tex",
        "source": "TransmissionWeight:file",
        "to": ["SurfaceShader:refr_weight"]
    },
    "Normal": {
        "type": "normal_tex",
        "source": "Normal:file",
        "to": ["NormalMap:input"]
    },
    "NormalMap": {
        "type": "normal",
        "to": ["CombinedNormal:baseinput"]
    },
    "Detail": {
        "type": "float_tex",
        "source": "Detail:file",
        "to": ["DetailScale:input1"]
    },
    "DetailScale": {
        "type": "multiply",
        "default": 1.0,
        "source": "DetailScale:in2",
        "to": ["DetailNormal:input", "CombinedDisplacement:input2"]
    },
    "DetailNormal": {
        "type": "bump_normal",
        "to": ["CombinedNormal:bumpinput0"]
    },
    "CombinedNormal": {
        "type": "normal_add",
        "to": ["SurfaceShader:bump_input"]
    },
    "Displacement": {
        "type": "float_tex",
        "source": "Displacement:file",
        "to": ["CombinedDisplacement:input1"]
    },
    "CombinedDisplacement": {
        "type": "add",
        "to": ["DisplacementShader:texmap"]
    },
    "AsNormal": {
        "type": "invert",
        "to": ["NormalMap:scale", "CombinedNormal:bumpweight0"]
    },
    "scene_scale": {
        "type": "float",
        "default": 1.0,
        "source": ":scene_scale",
        "to": ["SubsurfaceSceneScale:input2"]
    },
    "displacement_on": {
        "type": "float",
        "default": 0.0,
        "source": ":displacement_on",
        "to": ["DisplacementShader:scale", "AsNormal:input"]
    }
}

PROP_DICT = {
    "diffuse_roughness": {
        "default": 0,
        "source": "diffuse_roughness"
    },
    "refl_ior": {
        "default": 1.5,
        "source": "specular_IOR"
    },
    "refr_roughness": {
        "default": 0,
        "source": "transmission_roughness"
    },
    "ss_depth": {
        "default": 0,
        "source": "transmission_depth"
    },
    "refr_abbe": {
        "default": 0,
        "source": "transmission_dispersion"
    },
    "thinfilm_ior": {
        "default": 1.5,
        "source": "thin_film_IOR"
    },
    "thinfilm_thickness": {
        "default": 0,
        "source": "thin_film_thickness"
    },
    "coat_ior": {
        "default": 1.5,
        "source": "coat_IOR"
    },
    "refr_thin_walled": {
        "default": 0,
        "source": "thin_walled"
    },
}


def EnhanceMainMenu():
    # Get main menu resource
    mainMenu = c4d.gui.GetMenuResource("M_EDITOR")

    # Create a container to hold a new menu information
    menu = c4d.BaseContainer()
    menu.InsData(c4d.MENURESOURCE_SUBTITLE, "Omoo Asset")
    menu.InsData(c4d.MENURESOURCE_COMMAND, "PLUGIN_CMD_1062988")

    # Insert to menu
    mainMenu.InsData(c4d.MENURESOURCE_STRING, menu)


def PluginMessage(id, data):
    if id == c4d.C4DPL_BUILDMENU:
        EnhanceMainMenu()


def AddNode(graph, asset_id, name=None):
    node: maxon.GraphNode = graph.AddChild(
        maxon.Id(), asset_id)
    if name:
        SetNodeName(node, name)
    return node


def SetNodeName(node: maxon.GraphNode, name: str):
    node.SetValue("net.maxon.node.base.name", maxon.String(name))


def SetNodeProp(node: maxon.GraphNode, prop: str, value):
    if prop.isnumeric():
        prop = node.GetInputs().GetChildren()[int(prop)]
    else:
        props = prop.split(".")
        asset_id = node.GetValue("net.maxon.node.attribute.assetid")[0]
        prop = node.GetInputs().FindChild(f"{asset_id}.{props[0]}")
        if len(props) > 1:
            prop = prop.FindChild(props[1])
    prop.SetDefaultValue(value)


def GetNodeProp(node: maxon.GraphNode, prop: str):
    if prop.isnumeric():
        prop = node.GetInputs().GetChildren()[int(prop)]
    else:
        props = prop.split(".")
        asset_id = node.GetValue("net.maxon.node.attribute.assetid")[0]
        prop = node.GetInputs().FindChild(f"{asset_id}.{props[0]}")
        if len(props) > 1:
            prop = prop.FindChild(props[1])
    return prop.GetValue("effectivevalue")


def LinkNode(node: maxon.GraphNode, target: maxon.GraphNode, target_input: str):
    # Get the color output ports of the two texture nodes and the color blend node.
    node_asset_id = node.GetValue("net.maxon.node.attribute.assetid")[0]
    target_asset_id = target.GetValue("net.maxon.node.attribute.assetid")[0]

    output_port: maxon.GraphNode = node.GetOutputs().GetChildren()[0]
    input_port: maxon.GraphNode = target.GetInputs(
    ).FindChild(f"{target_asset_id}.{target_input}")

    # Wire up the two texture nodes to the blend node and the blend node to the BSDF node.
    output_port.Connect(
        input_port, modes=maxon.WIRE_MODE.NORMAL, reverse=False)


def GetNodeByAssetId(graph, asset_id):
    result: list[maxon.GraphNode] = []
    maxon.GraphModelHelper.FindNodesByAssetId(
        graphModel=graph,
        assetId=asset_id,
        exactId=True,
        callback=result
    )
    if len(result) < 1:
        return None
    node: maxon.GraphNode = result[0]
    return node


def GetNodeByExactName(graph, name):
    result: list[maxon.GraphNode] = []
    maxon.GraphModelHelper.FindNodesByName(
        graphModel=graph,
        nodeName=name,
        kind=maxon.NODE_KIND.NODE,
        direction=maxon.PORT_DIR.INPUT,
        exactName=True,
        callback=result
    )
    if len(result) < 1:
        return None
    node: maxon.GraphNode = result[0]
    return node


def GetChildren(obj):
    children = []
    child = obj.GetDown()
    while child:
        children.append(child)
        child = child.GetNext()
    return children


def ChangeSetting():
    # get usd plugin
    usd_import_plugin = c4d.plugins.FindPlugin(
        c4d.FORMAT_USDIMPORT, c4d.PLUGINTYPE_SCENELOADER)
    if usd_import_plugin is None:
        raise RuntimeError("Failed to retrieve the USD importer.")

    # get import setting object
    data = dict()
    usd_import_plugin.Message(c4d.MSG_RETRIEVEPRIVATEDATA, data)
    import_setting = data.get("imexporter", None)

    # Defines the settings
    import_setting[c4d.USDIMPORTER_KEEPBRIDGEOPEN] = False
    import_setting[c4d.USDIMPORTER_CAMERAS] = False
    import_setting[c4d.USDIMPORTER_LIGHTUNITS] = c4d.USDIMPORTER_LIGHTUNITS_NONE
    import_setting[c4d.USDIMPORTER_GEOMETRY] = True
    import_setting[c4d.USDIMPORTER_NORMALS] = c4d.USDIMPORTER_NORMALS_VERTEX
    import_setting[c4d.USDIMPORTER_UV] = True
    import_setting[c4d.USDIMPORTER_DISPLAYCOLOR] = True
    import_setting[c4d.USDIMPORTER_MATERIALS] = False


def InsertMaterialTag(obj, material):
    material_tag = c4d.BaseTag(5616)  # Initialize a material tag
    # Assign material to the material tag
    material_tag[c4d.TEXTURETAG_MATERIAL] = material
    material_tag[c4d.TEXTURETAG_PROJECTION] = 6  # UVW Mapping
    obj.InsertTag(material_tag)  # Insert tag to the object


class ImportOmooAsset(c4d.plugins.CommandData):

    def Execute(self, doc):

        file_path = c4d.storage.LoadDialog(
            type=c4d.FILESELECTTYPE_SCENES,
            title='Select folder to import',
            flags=c4d.FILESELECT_LOAD,
            force_suffix='usd',  # Currently not used. https://developers.maxon.net/docs/py/2024_3_0/modules/c4d.storage/index.html?highlight=c4d%20storage%20loaddialog#c4d.storage.LoadDialog
            def_path=c4d.storage.GeGetC4DPath(c4d.C4D_PATH_RESOURCE)
        )
        if not file_path:
            return

        file_path: str = Path(file_path).resolve()

        stage = Usd.Stage.Open(str(file_path))
        asset_prim = stage.GetDefaultPrim()
        asset_name = asset_prim.GetName()
        materials_prim = stage.GetPrimAtPath(
            f"{asset_prim.GetPath()}/Materials")

        geometries_prim = stage.GetPrimAtPath(
            f"{asset_prim.GetPath()}/Geometries")

        materials = {}
        for material_prim in materials_prim.GetChildren():
            material_name = material_prim.GetName()

            # check if is omoolab standard surface
            surface_shader_prim = stage.GetPrimAtPath(
                f"{asset_prim.GetPath()}/Materials/{material_name}/SurfaceShader")
            if not surface_shader_prim.IsValid():
                continue

            # https://developers.maxon.net/docs/py/2024_3_0/manuals/manual_graphdescription.html
            # TODO: use new way to create material

            material: c4d.BaseMaterial = c4d.BaseMaterial(c4d.Mmaterial)
            doc.InsertMaterial(material, checknames=True)

            # Get the node material for it and add a graph for the currently active material space to it.
            node_material: c4d.NodeMaterial = material.GetNodeMaterialReference()
            graph: maxon.GraphModelInterface = node_material.CreateDefaultGraph(
                maxon.Id("com.redshift3d.redshift4c4d.class.nodespace")
            )

            surface_shader = GetNodeByAssetId(graph, STANDARDMATERIAL)
            out_shader = GetNodeByAssetId(graph, OUTPUT)

            # Start modifying the graph by opening a transaction. Node graphs follow a database like
            # transaction model where all changes are only finally applied once a transaction is committed.
            with graph.BeginTransaction() as transaction:
                SetNodeName(surface_shader, "SurfaceShader")
                displacement_shader = AddNode(
                    graph, DISPLACEMENT, "DisplacementShader")

                LinkNode(displacement_shader, out_shader, 'displacement')

                # Create node source node dict.
                for node_name in NODE_DICT.keys():
                    # get node value
                    node_value = NODE_DICT[node_name].get("default")
                    if NODE_DICT[node_name].get("source"):
                        source_str = NODE_DICT[node_name]["source"]
                        shader_name = source_str.split(":")[0]
                        shader_parm = source_str.split(":")[1]
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
                                        file_path = Path(
                                            stack[0].layer.realPath)
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
                        tex_default_value = 0.0 \
                            if node_type == "float_tex" else (0.0, 0.0, 0.0, 0.0)
                        if shader_prim.IsValid():
                            shader_default = shader_prim.GetAttribute(
                                "inputs:default")
                            if shader_default.IsValid():
                                tex_default_value = shader_default.Get(0)
                                if node_type != "float_tex":
                                    tex_default_value = (
                                        tex_default_value[0],
                                        tex_default_value[1],
                                        tex_default_value[2],
                                        1.0
                                    )

                        # print(tex_default_value)
                        if node_value:
                            # blender cannot read UNC path with slash
                            node_value = node_value.replace("/", "\\")
                            node = AddNode(
                                graph, TEXTURESAMPLER, node_name)
                            SetNodeProp(node, 'tex0.path', node_value)

                            color_space = 'RS_INPUT_COLORSPACE_SRGB_LINEAR'\
                                if node_type == "color_tex" else 'RS_INPUT_COLORSPACE_RAW'
                            SetNodeProp(node, 'tex0.colorspace', color_space)
                        else:
                            if node_type != "float_tex":
                                node = AddNode(graph, COLOR, node_name)
                                SetNodeProp(node, "0", maxon.ColorA64(
                                    tex_default_value))
                            else:
                                node = AddNode(graph, VALUE, node_name)
                                SetNodeProp(node, "0", tex_default_value)

                    elif node_type == "normal":
                        node = AddNode(graph, BUMPMAP, node_name)
                        SetNodeProp(node, "inputtype", 1)

                    elif node_type == "bump_normal":
                        node = AddNode(graph, BUMPMAP, node_name)
                        SetNodeProp(node, "inputtype", 0)

                    elif node_type == "remap":
                        node = AddNode(graph, RANGE, node_name)
                        SetNodeProp(node, "new_min", -1)
                        SetNodeProp(node, "new_max", 1)

                    elif node_type == "add":
                        node = AddNode(graph, ADD, node_name)
                        if node_value:
                            SetNodeProp(node, "input2", node_value)

                    elif node_type == "multiply":
                        node = AddNode(graph, MUL, node_name)
                        if node_value:
                            SetNodeProp(node, "input2", node_value)

                    elif node_type == "vector_multiply":
                        node = AddNode(graph, VECTORMUL, node_name)
                        if node_value:
                            SetNodeProp(node, "input2", node_value)

                    elif node_type == "invert":
                        node = AddNode(graph, INVERT, node_name)

                    elif node_type == "normal_add":
                        node = AddNode(graph, BUMPBLENDER, node_name)
                        SetNodeProp(node, "bumpweight0", 1)
                        SetNodeProp(node, "additive", True)

                    elif node_type == "float":
                        node = AddNode(graph, VALUE, node_name)
                        SetNodeProp(node, "0", node_value)

                    else:
                        ...

                for node_name in NODE_DICT.keys():
                    node = GetNodeByExactName(graph, node_name)

                    to_list = NODE_DICT[node_name]["to"]
                    for to in to_list:
                        target_name = to.split(":")[0]
                        target_input = to.split(":")[1]
                        target_node = GetNodeByExactName(graph, target_name)

                        # print(node_name, target_name, target_input)
                        LinkNode(node, target_node, target_input)

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

                    SetNodeProp(surface_shader, prop_name, prop_value)

                SetNodeProp(surface_shader, 'ms_include_mode', 0)
                subsurface_scale = GetNodeByExactName(graph, "SubsurfaceScale")
                detail_normal = GetNodeByExactName(graph, "DetailNormal")
                scene_scale = GetNodeByExactName(graph, "scene_scale")

                SetNodeProp(detail_normal, 'scale', 0.5)
                SetNodeProp(scene_scale, '0',
                            float(GetNodeProp(scene_scale, '0'))*100)
                transaction.Commit()

            material.SetName(material_name)  # Set material name
            materials[material_name] = material

        ChangeSetting()
        doc.StartUndo()  # Start recording undos

        # store original scale
        project_scale = doc[c4d.DOCUMENT_DOCUNIT].GetUnitScale()

        # Imports without dialogs
        if not c4d.documents.MergeDocument(
            doc=doc,
            name=str(file_path),
            loadflags=c4d.SCENEFILTER_OBJECTS | c4d.SCENEFILTER_MATERIALS,
            thread=None
        ):
            raise RuntimeError("Fail to load USD")

        # reset scale
        sclData = c4d.UnitScaleData()
        sclData.SetUnitScale(project_scale[0], project_scale[1])
        doc[c4d.DOCUMENT_DOCUNIT] = sclData

        asset_object = doc.SearchObject(asset_name)
        asset_object.SetRelScale(c4d.Vector(100))
        doc.SetActiveObject(asset_object, c4d.SELECTION_NEW)
        rs_object_tag = c4d.BaseTag(c4d.Trsobject)  # Initialize a material tag
        rs_object_tag[c4d.REDSHIFT_OBJECT_GEOMETRY_OVERRIDE] = True
        rs_object_tag[c4d.REDSHIFT_OBJECT_GEOMETRY_SUBDIVISIONENABLED] = True
        rs_object_tag[c4d.REDSHIFT_OBJECT_GEOMETRY_DISPLACEMENTENABLED] = True
        asset_object.InsertTag(rs_object_tag)  # Insert tag to the object
        print(asset_object)

        # Remove Material Prim Path
        materials_prim_object = asset_object.GetDown().GetNext()

        if materials_prim_object:
            materials_prim_object.Remove()

        geometries = GetChildren(asset_object.GetDown())

        for geometry in geometries:
            selection_tag = geometry.GetTag(c4d.Tpolygonselection)
            material = materials.get(selection_tag.GetName())
            if material:
                InsertMaterialTag(geometry, material)

        doc.EndUndo()  # Stop recording undos
        c4d.EventAdd()  # Pushes an update event to Cinema 4D


if __name__ == "__main__":
    # Registers the plugin
    c4d.plugins.RegisterCommandPlugin(
        id=PLUGIN_ID,
        str="Import Omoo Asset (Redshift)",
        info=0,
        help="Import Omoo Asset",
        dat=ImportOmooAsset(),
        icon=None
    )
