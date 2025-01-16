import c4d
from c4d import plugins, gui
import os
import maxon
import re


def import_alembic_with_scale(doc, filePath, scale_value):
    """导入 Alembic 文件到当前文档"""
    # 获取Alembic导入插件的ID
    abcImportId = c4d.FORMAT_ABCIMPORT
    plug = c4d.plugins.FindPlugin(abcImportId, c4d.PLUGINTYPE_SCENELOADER)
    if plug is None:
        raise RuntimeError("Failed to retrieve the Alembic importer.")

    # 初始化一个字典以存储插件数据
    data = dict()
    # 向Alembic导入插件发送MSG_RETRIEVEPRIVATEDATA消息
    if not plug.Message(c4d.MSG_RETRIEVEPRIVATEDATA, data):
        raise RuntimeError("Failed to retrieve private data.")

    # 获取导入设置容器
    abcImport = data.get("imexporter", None)
    if abcImport is None:
        raise RuntimeError("Failed to retrieve BaseContainer private data.")

    # 设置Alembic导入单位为米
    scaleData = c4d.UnitScaleData()  # 创建一个UnitScaleData对象
    scaleData.SetUnitScale(scale_value, c4d.DOCUMENT_UNIT_M)  # 设置单位为从厘米到米
    abcImport[c4d.ABCIMPORT_SCALE] = scaleData  # 将单位设置为米

    # 合并文件到当前文档
    if not c4d.documents.MergeDocument(doc, filePath, c4d.SCENEFILTER_OBJECTS | c4d.SCENEFILTER_MATERIALS):
        raise RuntimeError("Failed to import the Alembic file.")

    c4d.EventAdd()
    print(f"Document successfully imported from: {filePath} with scale {scale_value}.")
def search_usda_for_material_and_scales(file_path, scale_value):
    if not os.path.isfile(file_path):
        print(f"文件 {file_path} 不存在")
        return

    with open(file_path, 'r') as file:
        lines = file.readlines()

    # 匹配模式
    material_pattern = re.compile(r'def Material \"([^\"]+)\"')  # 匹配材质名
    scene_scale_pattern = re.compile(r'inputs:scene_scale\s*=\s*([0-9.]+)')  # 匹配场景缩放值
    raw_scene_scale_pattern = re.compile(r'inputs:raw_scene_scale\s*=\s*([0-9.]+)')  # 匹配原始缩放值
    detail_scale_pattern = re.compile(r'float inputs:in2\s*=\s*([0-9.]+)')  # 匹配细节缩放值
    subsurface_scale_pattern =  re.compile(r'float inputs:value\s*=\s*([0-9.]+)')  # 匹配SubsurfaceScale
    point_color_weight_pattern = re.compile(r'float inputs:value\s*=\s*([0-9.]+)')
    
    materials = {}  # 存储材质名和其相关的字典
    current_material = None  # 用于跟踪当前的材质名
    in_subsurface_shader = False  # 标记当前是否在 SubsurfaceScale Shader 中
    in_point_color_weight_shader = False

    for line in lines:
        # 检查是否是材质定义行
        material_match = material_pattern.search(line)
        if material_match:
            current_material = material_match.group(1)
            materials[current_material] = {
                'scene_scale': 1.0,          # 默认场景缩放值
                'raw_scene_scale': 1.0,     # 默认原始缩放值
                'DetailScale': 1.0,         # 默认细节缩放值
                'SubsurfaceScale': 1.0,    # 默认 SubsurfaceScale 值
                'PointColorWeight': 0.0    # 默认 PointColorWeight 值
            }
            print(f"找到材质: {current_material}")
            continue

        # 如果找到场景缩放值且当前材质存在，将场景缩放值存入该材质的字典
        if current_material:
            scene_scale_match = scene_scale_pattern.search(line)
            if scene_scale_match:
                scene_scale_value = scene_scale_match.group(1)
                print(f"找到场景缩放行: {line.strip()}")
                print(f"场景缩放值: {scene_scale_value}")
                materials[current_material]['scene_scale'] = float(scene_scale_value)*float(scale_value)

                # 如果找到原始缩放值且当前材质存在，将原始缩放值存入该材质的字典
                raw_scene_scale_match = raw_scene_scale_pattern.search(line)
                if raw_scene_scale_match:
                    raw_scene_scale_value = raw_scene_scale_match.group(1)
                    print(f"找到原始缩放行: {line.strip()}")
                    print(f"原始缩放值: {raw_scene_scale_value}")
                    materials[current_material]['raw_scene_scale'] = float(raw_scene_scale_value)*float(scale_value)
                    continue
                else:
                    materials[current_material]['raw_scene_scale'] = float(scene_scale_value)*float(scale_value)

                continue
            
            # 如果找到细节缩放值且当前材质存在，将细节缩放值存入该材质的字典
            detail_scale_match = detail_scale_pattern.search(line)
            if detail_scale_match:
                detail_scale_value = detail_scale_match.group(1)
                print(f"找到细节缩放行: {line.strip()}")
                print(f"细节缩放值: {detail_scale_value}")
                materials[current_material]['DetailScale'] = detail_scale_value
                continue
                
            # 检查是否进入了 SubsurfaceScale 的 Shader 定义
            if 'def Shader "PointColorWeight"' in line:
                in_point_color_weight_shader = True
                print(f"进入 PointColorWeight Shader 定义: {line.strip()}")
                continue

            # 检查是否匹配 PointColorWeight Shader，提取 value 值
            if in_point_color_weight_shader:
                point_color_weight_match = point_color_weight_pattern.search(line)
                if point_color_weight_match:
                    point_color_weight_value = point_color_weight_match.group(1)
                    print(f"找到 PointColorWeight 的 value 值: {point_color_weight_value}")
                    materials[current_material]['PointColorWeight'] = point_color_weight_value
                    in_point_color_weight_shader  = False
                    continue

            # 检查是否进入了 SubsurfaceScale 的 Shader 定义
            if 'def Shader "SubsurfaceScale"' in line:
                in_subsurface_shader = True
                print(f"进入 SubsurfaceScale Shader 定义: {line.strip()}")
                continue

            # 如果在 SubsurfaceScale Shader 中，寻找 SubsurfaceScale 值
            if in_subsurface_shader:
                subsurface_scale_match = subsurface_scale_pattern.search(line)
                if subsurface_scale_match:
                    subsurface_scale_value = subsurface_scale_match.group(1)
                    print(f"找到SubsurfaceScale值: {subsurface_scale_value}")
                    materials[current_material]['SubsurfaceScale'] = subsurface_scale_value
                    in_subsurface_shader = False  # 离开 SubsurfaceScale 定义
                    continue

    return materials

def load_material_template(doc, templatePath, material_name):
    """从模板文件加载材质并重命名"""
    # 加载材质模板
    loadedDoc = c4d.documents.LoadDocument(templatePath, c4d.SCENEFILTER_MATERIALS)
    if loadedDoc is None:
        raise RuntimeError("Could not load the material template document.")
    
    # 查找目标材质
    mat = loadedDoc.GetFirstMaterial()
    while mat:
        if mat.GetName() == "RSBaseMaterialNode":  # 这里根据原始材质名称进行查找
            clone = mat.GetClone()
            clone.SetName(material_name)  # 重命名材质
            doc.InsertMaterial(clone)  # 插入到当前文档
            c4d.EventAdd()
            return clone
        mat = mat.GetNext()

    raise RuntimeError(f"Material 'RSBaseMaterialNode' not found in template '{templatePath}'.")

def FindNodeByName(graphModel, nodeName):
    """使用节点名称查找指定的节点。"""
    foundNodes = maxon.GraphModelHelper.FindNodesByName(
        graphModel,
        nodeName,  # 要查找的节点名称
        maxon.NODE_KIND.NODE,  # 节点类型
        maxon.PORT_DIR.INPUT,  # 查找输入端口方向的节点
        True,  # 精确匹配节点名称
        None  # 不使用回调，返回节点列表
    )
    

    if foundNodes:
        print("找到节点：",nodeName)
        return foundNodes  # 假设只找到一个节点
    else:
        return None

def set_scene_attribute(material, materials_attributes_from_usda):
    """设置材质的scene_scale值或其他属性"""
    node_material = material.GetNodeMaterialReference()
    if not node_material:
        return

    redshiftNodeSpaceId = maxon.Id("com.redshift3d.redshift4c4d.class.nodespace")
    graph = node_material.GetGraph(redshiftNodeSpaceId)
    if graph is None:
        print(f"材质 {material.GetName()} 的节点图为空或无效.")
        return
    
    # 设置 raw_scene_scale 值
    raw_scene_scale_value = materials_attributes_from_usda['raw_scene_scale']
    if raw_scene_scale_value:
        raw_scene_scale_node = FindNodeByName(graph, "raw_scene_scale")[0]
        
        if raw_scene_scale_node:
            raw_scene_scalePort = raw_scene_scale_node.GetInputs().FindChild("in")
            print("raw_scene_scalePort",raw_scene_scalePort)
            if raw_scene_scalePort:
                with graph.BeginTransaction() as transaction:
                    # Define the value of the Color's port.
                        raw_scene_scalePort.SetPortValue(maxon.Float(float(raw_scene_scale_value)))
                        print(f"已为材质 {material.GetName()} 设置 raw_scene_scale 值为 {raw_scene_scale_value}.")
                        transaction.Commit()

    # 设置 scene_scale 值
    scene_scale_value = materials_attributes_from_usda['scene_scale']
    if scene_scale_value:
        
        # 查找所有名为 'scene_scale' 的节点
        scene_scale_nodes = FindNodeByName(graph, "scene_scale")  # 假设 FindNodesByName 返回多个节点
        if scene_scale_nodes:
            # 遍历所有找到的 'scene_scale' 节点并设置它们的值
            for scene_scale_node in scene_scale_nodes:
                scalePort = scene_scale_node.GetInputs().FindChild("in")
                if scalePort:
                    # 创建并使用一个GraphModelInterface事务
                    transaction = graph.BeginTransaction()
                    try:
                        # 设置每个 scalePort 的值
                        scalePort.SetPortValue(maxon.Float(float(scene_scale_value)))
                        print(f"已为材质 {material.GetName()} 设置 scene_scale 值为 {scene_scale_value}.")
                        transaction.Commit()  # 提交事务
                    except Exception as e:
                        transaction.Rollback()  # 回滚事务
                        print(f"设置 scene_scale 值时出现错误: {e}")
        else:
            print(f"没有找到 'scene_scale' 节点。")

    # 设置 DetailScale 值
    detail_scale_value = materials_attributes_from_usda['DetailScale']
    if detail_scale_value:
        detail_scale_node = FindNodeByName(graph, "DetailScale")[0]
        
        if detail_scale_node:
            detail_scalePort = detail_scale_node.GetInputs().FindChild("in")
            print("detail_scalePort",detail_scalePort)
            if detail_scalePort:
                with graph.BeginTransaction() as transaction:
                    # Define the value of the Color's port.
                        detail_scalePort.SetPortValue(maxon.Float(float(detail_scale_value)))
                        print(f"已为材质 {material.GetName()} 设置 DetailScale 值为 {detail_scale_value}.")
                        transaction.Commit()
    
    # 设置 DetailScale 值
    subsurface_scale_value = materials_attributes_from_usda['SubsurfaceScale']
    if subsurface_scale_value:
        subsurface_scale_node = FindNodeByName(graph, "SubsurfaceScale")[0]
        
        if subsurface_scale_node:
            subsurface_scalePort = subsurface_scale_node.GetInputs().FindChild("in")
            print("subsurface_scalePort",subsurface_scalePort)
            if subsurface_scalePort:
                with graph.BeginTransaction() as transaction:
                    # Define the value of the Color's port.
                        subsurface_scalePort.SetPortValue(maxon.Float(float(subsurface_scale_value)))
                        print(f"已为材质 {material.GetName()} 设置 SubsurfaceScale 值为 {subsurface_scale_value}.")
                        transaction.Commit()

    # 设置 PointColorWeight 值
    point_color_weight_value = materials_attributes_from_usda.get('PointColorWeight')
    if point_color_weight_value:
        point_color_weight_nodes = FindNodeByName(graph, "PointColorWeight")
        if point_color_weight_nodes:
            point_color_weight_node = point_color_weight_nodes[0]
            point_color_weight_port = point_color_weight_node.GetInputs().FindChild("in")
            print("point_color_weight_port", point_color_weight_port)
            if point_color_weight_port:
                with graph.BeginTransaction() as transaction:
                    point_color_weight_port.SetPortValue(maxon.Float(float(point_color_weight_value)))
                    print(f"已为材质 {material.GetName()} 设置 PointColorWeight 值为 {point_color_weight_value}.")
                    transaction.Commit()

def apply_material_to_object(material, obj, selection_tag_name, materials_attributes_from_usda):
    """为网格对象添加材质标签"""

    print(f"Applying material to object: {obj.GetName()}")  # 调试信息：显示应用材质的对象名称
    texture_tag = c4d.TextureTag()
    texture_tag[c4d.TEXTURETAG_MATERIAL] = material
    obj.InsertTag(texture_tag)
    print(f"Material '{material.GetName()}' applied to '{obj.GetName()}'")  # 调试信息：显示材质应用情况
    texture_tag[c4d.TEXTURETAG_RESTRICTION] = selection_tag_name

    # Redshift Object Tag的插件ID
    REDSHIFT_OBJECT_TAG_ID = 1036222

    # 检查对象是否已有Redshift Object Tag
    tag = obj.GetTag(REDSHIFT_OBJECT_TAG_ID)
    if tag:
        print(f"对象 {obj.GetName()} 已有Redshift Object Tag，跳过。")  # 调试信息
    else:
        print(f"对象 {obj.GetName()} 没有Redshift Object Tag，添加标签。")  # 调试信息
        tag = obj.MakeTag(REDSHIFT_OBJECT_TAG_ID)
        if tag is None:
            c4d.gui.MessageDialog(f"无法为对象 {obj.GetName()} 添加Redshift Object Tag。")
            print(f"无法为对象 {obj.GetName()} 添加Redshift Object Tag。")  # 调试信息
        else:
            print(f"成功为对象 {obj.GetName()} 添加了Redshift Object Tag。")  # 调试信息
        
        # 启用几何覆盖和置换选项
        tag[c4d.REDSHIFT_OBJECT_GEOMETRY_OVERRIDE] = True
        tag[c4d.REDSHIFT_OBJECT_GEOMETRY_DISPLACEMENTENABLED] = True
        print(f"已启用对象 {obj.GetName()} 的几何覆盖和置换选项。")  # 调试信息

        # 启用曲面细分，设置最大细分为1
        # tag[c4d.REDSHIFT_OBJECT_GEOMETRY_SUBDIVISIONENABLED] = True
        # tag[c4d.REDSHIFT_OBJECT_GEOMETRY_MAXTESSELLATIONSUBDIVS] = 1
        # print(f"已启用对象 {obj.GetName()} 的曲面细分，最大细分设置为1。")  # 调试信息
        
        # 关闭自动凹凸映射，设置最大置换为10
        tag[c4d.REDSHIFT_OBJECT_GEOMETRY_AUTOBUMPENABLED] = False
        tag[c4d.REDSHIFT_OBJECT_GEOMETRY_MAXDISPLACEMENT] = 10

        # 填入点速度
        tag[c4d.REDSHIFT_OBJECT_MOTIONBLUR_MOTIONVECTOR_X] = '.velocities[0]'
        tag[c4d.REDSHIFT_OBJECT_MOTIONBLUR_MOTIONVECTOR_Y] = '.velocities[1]'
        tag[c4d.REDSHIFT_OBJECT_MOTIONBLUR_MOTIONVECTOR_Z] = '.velocities[2]'

        print(f"已关闭对象 {obj.GetName()} 的自动凹凸映射，最大置换设置为10。")
    # 应用 scene_scale 值
    set_scene_attribute(material,materials_attributes_from_usda)

def set_texture_paths(material, texture_folder, material_name, texture_list):
    """设置材质节点的贴图路径，并删除无效的贴图采样器节点"""
    node_material = material.GetNodeMaterialReference()
    if not node_material:
        return

    redshiftNodeSpaceId = maxon.Id("com.redshift3d.redshift4c4d.class.nodespace")
    graph = node_material.GetGraph(redshiftNodeSpaceId)
    if graph is None:
        print(f"材质 {material.GetName()} 的节点图为空或无效.")
        return

    print(f"处理材质 {material.GetName()}...")

    # 文件大小阈值
    size_threshold = 400 * 1024  # 400KB

    # 正则表达式，用于匹配 <前缀>.<UDIM>.exr 文件名模式
    filename_pattern = re.compile(r'^.*\.\d{4}\.exr$', re.IGNORECASE)

    with graph.BeginTransaction() as transaction:
        nodes = graph.GetRoot().GetInnerNodes(maxon.NODE_KIND.NODE, includeThis=False)

        for node in nodes:
            nodeName = node.GetValue(maxon.NODE.BASE.NAME)
            nodeId = node.GetId().ToString().split("@")[0]

            if nodeId == "texturesampler":
                pathPort = node.GetInputs().FindChild("com.redshift3d.redshift4c4d.nodes.core.texturesampler.tex0").FindChild("path")
                
                if pathPort:
                    pathValue = pathPort.GetPortValue()
                    pathValueStr = str(pathValue)
                    print(f"检查节点 {nodeId} 的路径: {pathValueStr}")

                    if pathValueStr:
                        # 获取文件夹路径和文件名模式
                        folder_path = os.path.dirname(pathValueStr)
                        file_name_pattern = os.path.basename(pathValueStr).replace('<UDIM>', r'\d{4}').replace('.exr', r'\.exr')
                        
                        if os.path.isdir(folder_path):
                            # 收集所有匹配的文件
                            matching_files = [
                                os.path.join(folder_path, filename)
                                for filename in os.listdir(folder_path)
                                if os.path.isfile(os.path.join(folder_path, filename)) and re.match(file_name_pattern, filename)
                            ]

                            # 如果没有匹配的文件，删除节点
                            if not matching_files:
                                print(f"没有匹配的文件，节点 {nodeId} 将被删除。")
                                node.Remove()
                                continue

                            # 检查所有匹配文件的大小
                            all_files_invalid = True
                            for file_path in matching_files:
                                file_size = os.path.getsize(file_path)
                                print(f"文件 {os.path.basename(file_path)} 大小: {file_size} 字节")
                                
                                if file_size > size_threshold:
                                    print(f"文件 {os.path.basename(file_path)} 大于阈值 {size_threshold} 字节，节点保留。")
                                    all_files_invalid = False
                                    break

                            # 如果所有文件大小都小于阈值，删除节点
                            if all_files_invalid:
                                print(f"所有匹配文件大小均小于阈值，节点 {nodeId} 将被删除。")
                                node.Remove()
                                continue
                            else:
                                print(f"至少一个文件大小符合要求，节点 {nodeId} 将保留。")
                        else:
                            print(f"文件夹路径 {folder_path} 无效或不存在，节点将被删除。")
                            node.Remove()
                            continue

                # 如果贴图路径有效且没有删除，更新其路径
                texture_path = os.path.join(texture_folder, f"{material_name}_{nodeName}.<UDIM>.exr")
                pathPort.SetPortValue(texture_path)
                print(f"材质 '{material_name}' 的节点 '{nodeName}' 的路径已设置为: {texture_path}")

                # 设置 UV 通道
                uvPort = node.GetInputs().FindChild("com.redshift3d.redshift4c4d.nodes.core.texturesampler.tspace_id")
                if uvPort:
                    uvPort.SetPortValue("uv")  # 设置 UV 通道为 'uv'
                    print(f"材质 '{material_name}' 的节点 '{nodeName}' 的 UV 通道已设置为 'uv'。")

        transaction.Commit()
        print(f"已更新材质 {material.GetName()} 的所有贴图路径并删除无效节点。")

def delete_Invalid_texture(material):
    """删除无效的贴图采样器节点（纹理节点）"""
    # 正则表达式，用于匹配 <前缀>.<UDIM>.exr 文件名模式
    filename_pattern = re.compile(r'^.*\.\d{4}\.exr$', re.IGNORECASE)
    # 文件大小阈值
    size_threshold = 400 * 1024  # 400KB

    # 确保材质是一个节点材质
    nodeMaterial = material.GetNodeMaterialReference()
    if nodeMaterial is None:
        print(f"材质 {material.GetName()} 不是一个节点材质.")
        return
    
    # 获取材质的节点图，检查节点空间为 Redshift
    redshiftNodeSpaceId = maxon.Id("com.redshift3d.redshift4c4d.class.nodespace")
    graph = nodeMaterial.GetGraph(redshiftNodeSpaceId)
    if graph is None:
        print(f"材质 {material.GetName()} 的节点图为空或无效.")
        return
    
    print(f"处理材质 {material.GetName()} 以删除无效的贴图...")

    # 使用事务来确保操作的原子性
    with graph.BeginTransaction() as transaction:
        # 获取材质图的所有内部节点
        nodes = graph.GetRoot().GetInnerNodes(maxon.NODE_KIND.NODE, includeThis=False)
        
        # 遍历找到的节点并删除符合条件的纹理节点
        for node in nodes:
            # 获取节点 ID 并检查它是否为 "texturesampler"
            nodeId = node.GetId().ToString().split("@")[0]
            if nodeId == "texturesampler":
                # 查找 'path' 端口
                pathPort = node.GetInputs().FindChild("com.redshift3d.redshift4c4d.nodes.core.texturesampler.tex0").FindChild("path")
                
                # 如果找到端口，且路径值是字符串，且路径有效，则检查文件
                if pathPort:
                    pathValue = pathPort.GetPortValue()
                    pathValueStr = str(pathValue)
                    print(f"检查节点 {nodeId} 的路径: {pathValueStr}")
                    
                    if pathValueStr:
                        # 获取文件夹路径和文件名
                        folder_path = os.path.dirname(pathValueStr)
                        file_name_pattern = os.path.basename(pathValueStr).replace('<UDIM>', r'\d{4}').replace('.exr', r'\.exr')
                        # 确保文件夹路径存在
                        if os.path.isdir(folder_path):
                            # 收集所有匹配的文件
                            matching_files = [
                                os.path.join(folder_path, filename)
                                for filename in os.listdir(folder_path)
                                if os.path.isfile(os.path.join(folder_path, filename)) and re.match(file_name_pattern, filename)
                            ]

                            # 如果没有匹配的文件，删除节点
                            if not matching_files:
                                print(f"没有匹配的文件，节点 {nodeId} 将被删除。")
                                node.Remove()
                                continue

                            # 检查所有匹配文件的大小
                            all_files_invalid = True
                            for file_path in matching_files:
                                file_size = os.path.getsize(file_path)
                                print(f"文件 {os.path.basename(file_path)} 大小: {file_size} 字节")
                                
                                if file_size > size_threshold:
                                    print(f"文件 {os.path.basename(file_path)} 大于阈值 {size_threshold} 字节，节点保留。")
                                    all_files_invalid = False
                                    break

                            # 如果所有文件大小都小于阈值，删除节点
                            if all_files_invalid:
                                print(f"所有匹配文件大小均小于阈值，节点 {nodeId} 将被删除。")
                                node.Remove()
                            else:
                                print(f"至少一个文件大小符合要求，节点 {nodeId} 将保留。")
                        else:
                            print(f"文件夹路径 {folder_path} 无效或不存在，节点将被删除。")
                            node.Remove()
                            continue
    
        # 提交事务
        transaction.Commit()

def process_objects(doc, parent, material_template_path, filePath, usda_file_path, scale_value):
    """处理所有对象及其子对象，应用材质并从 USDA 中读取 scene_scale"""
    document_folder = os.path.dirname(filePath)
    texture_folder = os.path.join(document_folder, "Textures")
    # print("texture_folder:", texture_folder)
    
    if not os.path.isdir(texture_folder):
        print("Texture folder does not exist.")
        texture_folder = document_folder
    
    # 获取贴图列表
    texture_list = [f for f in os.listdir(texture_folder) if os.path.isfile(os.path.join(texture_folder, f))]
    # 从 USDA 文件中读取材质与 scene_scale 对应关系
    materials_attributes_from_usda = search_usda_for_material_and_scales(usda_file_path, scale_value)
    print("材质属性列表",materials_attributes_from_usda)
    def process_child(obj):
        if obj is None:
            return

        print("Object Name:", obj.GetName())

        # 如果是网格模型
        if obj.GetType() == c4d.Oalembicgenerator:
            print("这是一个 Alembic 生成器")
            tags = obj.GetTags()
            for tag in tags:
                tag_name = tag.GetName()
                if tag_name.startswith("material_"):
                    material_name = tag_name[len("material_"):]
                    print("Tag Name:", tag_name)
                    if material_name:
                        # 从模板文件中导入材质
                        material = load_material_template(doc, material_template_path, material_name)
                        
                        material_attributes = materials_attributes_from_usda[material_name]
                        
                        # 应用材质并设置属性（例如 scene_scale 和 DetailScale）
                        apply_material_to_object(material, obj, tag_name, material_attributes)
                        
                        # 设置材质的贴图路径
                        set_texture_paths(material, texture_folder, material_name, texture_list)
                        
                        # 设置贴图路径后，删除无效的纹理节点
                        delete_Invalid_texture(material)

        # 递归处理子对象
        for child in obj.GetChildren():
            process_child(child)

    process_child(parent)

class AlembicImportDialog(gui.GeDialog):
    ID_SCALE_INPUT = 1000
    ID_BUTTON_OK = 1001
    
    def __init__(self):
        super().__init__()
        self.scale_value = 1.0  # 默认缩放值

    def CreateLayout(self):
        # 设置窗口标题
        self.SetTitle("Alembic Import Settings")

        # 添加文本标签
        self.AddStaticText(0, c4d.BFH_LEFT, name="Set Scale Value:")

        # 添加一个输入框来输入缩放值
        self.AddEditNumberArrows(self.ID_SCALE_INPUT, c4d.BFH_LEFT, initw=200, inith=10)
        self.SetFloat(self.ID_SCALE_INPUT, self.scale_value)  # 设置默认值

        # 添加OK按钮
        self.AddButton(self.ID_BUTTON_OK, c4d.BFH_CENTER, name="OK")
        
        return True

    def Command(self, id, msg):
        # 当点击OK按钮时
        if id == self.ID_BUTTON_OK:
            # 获取用户输入的缩放值
            self.scale_value = self.GetFloat(self.ID_SCALE_INPUT)
            self.Close()  # 关闭对话框
            return True
        return False
    
def main(doc):
    # 弹出文件选择器，选择 Alembic 文件
    filePath = c4d.storage.LoadDialog(c4d.FILESELECTTYPE_ANYTHING, "Select Alembic File", c4d.FILESELECT_LOAD, "abc")
    if not filePath:
        return

    # 创建并显示自定义对话框
    dialog = AlembicImportDialog()
    dialog.Open(c4d.DLG_TYPE_MODAL)  # 以模态方式显示对话框，等待用户输入

    # 获取用户选择的缩放值
    scale_value = dialog.scale_value

    # 调用导入 Alembic 文件的函数，应用用户输入的缩放值
    import_alembic_with_scale(doc, filePath, scale_value)

    # 获取Alembic文件的文件夹路径
    document_folder = os.path.dirname(filePath)

    # 设置usda文件路径
    usda_file_path = os.path.join(document_folder, "temp.usda")

    # 获取当前脚本的绝对路径
    script_path = os.path.abspath(__file__)
    # 获取当前脚本所在文件夹的路径
    script_dir = os.path.dirname(script_path)

    # 设置材质模板路径
    material_template_path = os.path.join(script_dir, "RSBaseMaterialNode.c4d")

    # 处理所有对象及其子对象
    root = doc.GetFirstObject()
    process_objects(doc, root, material_template_path, filePath, usda_file_path, scale_value)


class AlembicImportDialog(gui.GeDialog):
    ID_SCALE_INPUT = 1000
    ID_BUTTON_OK = 1001
    
    def __init__(self):
        super().__init__()
        self.scale_value = 1.0  # 默认缩放值

    def CreateLayout(self):
        # 设置窗口标题
        self.SetTitle("Alembic Import Settings")

        # 添加文本标签
        self.AddStaticText(0, c4d.BFH_LEFT, name="Set Scale Value:")

        # 添加一个输入框来输入缩放值
        self.AddEditNumberArrows(self.ID_SCALE_INPUT, c4d.BFH_LEFT, initw=200, inith=10)
        self.SetFloat(self.ID_SCALE_INPUT, self.scale_value)  # 设置默认值

        # 添加OK按钮
        self.AddButton(self.ID_BUTTON_OK, c4d.BFH_CENTER, name="OK")
        
        return True

    def Command(self, id, msg):
        # 当点击OK按钮时
        if id == self.ID_BUTTON_OK:
            # 获取用户输入的缩放值
            self.scale_value = self.GetFloat(self.ID_SCALE_INPUT)
            self.Close()  # 关闭对话框
            return True
        return False
    
def main(doc):
    # 弹出文件选择器，选择 Alembic 文件
    filePath = c4d.storage.LoadDialog(c4d.FILESELECTTYPE_ANYTHING, "Select Alembic File", c4d.FILESELECT_LOAD, "abc")
    if not filePath:
        return

    # 创建并显示自定义对话框
    dialog = AlembicImportDialog()
    dialog.Open(c4d.DLG_TYPE_MODAL)  # 以模态方式显示对话框，等待用户输入

    # 获取用户选择的缩放值
    scale_value = dialog.scale_value

    # 调用导入 Alembic 文件的函数，应用用户输入的缩放值
    import_alembic_with_scale(doc, filePath, scale_value)

    # 获取Alembic文件的文件夹路径
    document_folder = os.path.dirname(filePath)

    # 设置usda文件路径
    usda_file_path = os.path.join(document_folder, "temp.usda")

    # 获取当前脚本的绝对路径
    script_path = os.path.abspath(__file__)
    # 获取当前脚本所在文件夹的路径
    script_dir = os.path.dirname(script_path)

    # 设置材质模板路径
    material_template_path = os.path.join(script_dir, "RSBaseMaterialNode.c4d")

    # 处理所有对象及其子对象
    root = doc.GetFirstObject()
    process_objects(doc, root, material_template_path, filePath, usda_file_path, scale_value)


class OmooAssetsMenu(plugins.CommandData):
    def Execute(self, doc):
        # 调用 OmooAssetsAlembic.py 中的 main 函数
        main(doc)
        return True

    def GetState(self, doc):
        return c4d.CMD_ENABLED

if __name__ == "__main__":
    PLUGIN_ID = 1064257
    # 注册插件
    if not plugins.RegisterCommandPlugin(
        PLUGIN_ID, "Import .abc (OmooAsset)", 0, None, "Import Alembic File", OmooAssetsMenu()):
        raise Exception("Failed to register plugin")