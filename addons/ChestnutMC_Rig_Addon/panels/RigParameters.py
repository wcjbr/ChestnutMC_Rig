import bpy
from ..operators import Defs

Rig_Parameters_bones = {
    "meum.body.setting": "General Setting",
    "meum.face.mouth.setting": "Face Setting",
    "meum.arm.setting.R": "Right Arm Setting",
    "meum.arm.setting.L": "Left Arm Setting",
    "meum.leg.setting.R": "Right Leg Setting",
    "meum.leg.setting.L": "Left Leg Setting"
}

Face_Parameters_nodes = {
    "Skin": ["Adjuster", "Emotion", "ChestnutMC_PBR_Shader"],
    "Face": ["ChestnutMC_EyeShader", "SkinSorter"],
    "Mouth": ["ChestnutMC_Mouth"],
    "EdgeLight": ["ChestnutMC_EdgeLight"]
}



# 骨骼参数绘制方法
def get_rig_parameters(box, context: bpy.types.Context, bone_name: str):
    # 获取cmcrig
    armature = Defs.get_cmc_rig(context.active_object)

    # 验证骨骼是否存在
    try:
        bone = armature.pose.bones[bone_name]
    except:
        return None

    # 面板展开与收起
    row = box.row()
    row.prop(bone, "cmc_bone_expand",
                icon="TRIA_DOWN" if bone.cmc_bone_expand else "TRIA_RIGHT",
                text="",
                emboss=True)
    row.label(text=Rig_Parameters_bones[bone_name], icon="POSE_HLT")
    # 面板展开与收起
    if bone.cmc_bone_expand is False:
        return None

    # 获取自定义属性
    custom_props = bone.keys()
    # 绘制参数
    for prop_name in custom_props:
        # 验证属性值是否为数字
        if type(bone[prop_name]) not in [bool, int, float]:
            continue
        if prop_name == "cmc_bone_expand":
            continue
        row = box.row()
        # 更改文本
        text_c = prop_name
        if text_c == "FK/IK":
            if bone["FK/IK"] == 0:
                text_c = "FK"
                row.alert = True
            else:
                text_c = "IK"
                row.alert = False
        if text_c == "男/女":
            if bone["男/女"] == 0:
                text_c = "粗手臂"
                row.alert = True
            else:
                text_c = "细手臂"
                row.alert = False
        #row.label(text=prop_name)
        row.prop(bone, '["%s"]' % prop_name, text=text_c, emboss=True, icon="CHECKMARK" if bone[prop_name] else "DOT", slider=True)
    # 无缝切换FK/IK
    if bone.name == "meum.arm.setting.L":
        row = box.row()
        if bone["FK/IK"] == 0:
            row.operator("cmc.switch_l_arm_fkik", text="Seamless FK->IK", icon="MODIFIER")
        else:
            row.operator("cmc.switch_l_arm_fkik", text="Seamless IK->FK", icon="MODIFIER")
        row = box.row()
        op = row.operator("cmc.insert_seamless_switch_keyframe", text="Insert Keyframe", icon="DECORATE_KEYFRAME")
        op.bone_list_select = 1
    elif bone.name == "meum.arm.setting.R":
        row = box.row()
        if bone["FK/IK"] == 0:
            row.operator("cmc.switch_r_arm_fkik", text="Seamless FK->IK", icon="MODIFIER")
        else:
            row.operator("cmc.switch_r_arm_fkik", text="Seamless IK->FK", icon="MODIFIER")
        row = box.row()
        op = row.operator("cmc.insert_seamless_switch_keyframe", text="Insert Keyframe", icon="DECORATE_KEYFRAME")
        op.bone_list_select = 2
    elif bone.name == "meum.leg.setting.L":
        row = box.row()
        if bone["FK/IK"] == 0:
            row.operator("cmc.switch_l_leg_fkik", text="Seamless FK->IK", icon="MODIFIER")
        else:
            row.operator("cmc.switch_l_leg_fkik", text="Seamless IK->FK", icon="MODIFIER")
        row = box.row()
        op = row.operator("cmc.insert_seamless_switch_keyframe", text="Insert Keyframe", icon="DECORATE_KEYFRAME")
        op.bone_list_select = 3
    elif bone.name == "meum.leg.setting.R":
        row = box.row()
        if bone["FK/IK"] == 0:
            row.operator("cmc.switch_r_leg_fkik", text="Seamless FK->IK", icon="MODIFIER")
        else:
            row.operator("cmc.switch_r_leg_fkik", text="Seamless IK->FK", icon="MODIFIER")
        row = box.row()
        op = row.operator("cmc.insert_seamless_switch_keyframe", text="Insert Keyframe", icon="DECORATE_KEYFRAME")
        op.bone_list_select = 4


# 材质参数绘制方法
_count = 0
def get_face_parameters(box, context: bpy.types.Context, material_name: str):
    global _count
    material = None

    armature = Defs.get_cmc_rig(context.active_object)
    for child in armature.children:
        if child.type == 'MESH' and child.name.startswith("preview"):
            for material in child.material_slots:
                if material.material.name.startswith(material_name):
                    material = material.material
                    break

    if material is None:
        return None

    # 在材质节点树中找到对应节点
    try:
        for node in material.node_tree.nodes:
            if node.name in Face_Parameters_nodes[material_name] or node.label in Face_Parameters_nodes[material_name]:
                #if (node.name.startswith("Adjuster") or node.name.startswith("ChestnutMC_EdgeLight")) and bpy.context.scene.render.engine != 'BLENDER_EEVEE_NEXT':
                #    continue
                if node.name.startswith("ChestnutMC_PBR_Shader") and bpy.context.scene.render.engine != 'CYCLES':
                    continue
                row = box.row()
                # 面板展开与收起
                row.prop(node, "cmc_node_expand",
                    icon="TRIA_DOWN" if node.cmc_node_expand else "TRIA_RIGHT",
                    text="",
                    emboss=True)
                row.label(text=node.name)
                if node.cmc_node_expand is False:
                    continue

                newbox = box.box()
                # 如果为PBR节点
                # 旧版实现方法(v1.0.6及之前)
                if node.name.startswith("ChestnutMC_PBR_Shader") or node.label.startswith("ChestnutMC_PBR_Shader"):
                    node_tree = bpy.data.node_groups.get(node.node_tree.name)
                    for node in node_tree.nodes:
                        if node.name.startswith("ChestnutMC_PBR_Shader") or node.label.startswith("ChestnutMC_PBR_Shader"):
                            for inp in node.inputs:
                                # 如果节点被连接
                                if inp.is_linked:
                                    continue
                                else:
                                    newbox.template_node_view(node_tree, node, inp)
                # 如果节点有输入(非图像节点)，则展示未连接节点
                if len(node.inputs) > 1:
                    for inp in node.inputs:
                        # 如果节点被连接
                        if inp.is_linked:
                            continue
                        else:
                            newbox.template_node_view(material.node_tree, node, inp)
                # 若为图像节点，则展示节点
                elif node.type == 'TEX_IMAGE':
                    newbox.template_image(node, "image", node.image_user)
                # 如果节点无输入则进入节点组(Adjuster)
                else:
                    node_tree = bpy.data.node_groups.get(node.node_tree.name)
                    # EEVEE材质切换
                    EC_Switch = None
                    EC_Switch_Node = None
                    PBR_Shader = None
                    for EC_node in node_tree.nodes:
                        if EC_node.name.startswith("E/C_Switch"):
                            EC_Switch = bpy.data.node_groups.get(EC_node.node_tree.name)
                        if EC_node.name.startswith("ChestnutMC_PBR_Shader"):
                            PBR_Shader = bpy.data.node_groups.get(EC_node.node_tree.name)
                    if EC_Switch is not None:
                        for EC_node in EC_Switch.nodes:
                            if EC_node.name.startswith("E/C_Switch_Node"):
                                EC_Switch_Node = EC_node
                                # 绘制E/C_Switch节点
                                #row = newbox.row()
                                #row.template_node_view(EC_Switch, EC_Switch_Node, EC_Switch_Node.inputs[0])
                                #if bpy.context.scene.render.engine == 'CYCLES':
                                #    row.enabled = False
                                #newbox.separator()
                    if (EC_Switch_Node is None or EC_Switch_Node.inputs[0].default_value != 1) and bpy.context.scene.render.engine != 'CYCLES':
                        # 材质切换按钮
                        row = newbox.row()
                        row.operator("cmc.switch_npr_pbr", text="NPR Shader", icon="NODE_MATERIAL")
                        newbox.separator()
                        for out in node_tree.nodes['组输出'].inputs:
                            # 如果节点有输入
                            if out.is_linked:
                                row = newbox.row()
                                row.alignment = 'RIGHT'
                                row.label(text=out.name)
                                row.label(text="Custom Used", icon= "SETTINGS")
                            else:
                                newbox.template_node_view(node_tree, node, out)
                    else:
                        # 材质切换按钮
                        if bpy.context.scene.render.engine != 'CYCLES':
                            row = newbox.row()
                            row.operator("cmc.switch_npr_pbr", text="PBR Shader", icon="NODE_MATERIAL")
                            newbox.separator()
                        if PBR_Shader is not None:
                            for node in PBR_Shader.nodes:
                                if node.name.startswith("ChestnutMC_PBR_Shader") or node.label.startswith("ChestnutMC_PBR_Shader"):
                                    for inp in node.inputs:
                                        # 如果节点被连接
                                        if inp.is_linked:
                                            continue
                                        else:
                                            newbox.template_node_view(PBR_Shader, node, inp)
    except Exception as e:
        print(e)
        pass