import bpy
import json

from ..config import __addon_name__
from ..panels.ImageManager import *



#*****************************************************
#*****************************************************
#********************* 读取方法 ***********************
#*****************************************************
#*****************************************************

def read_skin_json(self):
    '''读取skin预设的json文件，并返回字典'''
    addon_prefs = bpy.context.preferences.addons[__addon_name__].preferences

    # 验证资产库路径
    try:
        with open(addon_prefs.skin_preset_json, 'r') as f:
            library = json.load(f)
            #print(library)
            return library
    except Exception as e:
        self.report({'ERROR'}, "Fail to load skin json: {}".format(str(e)))
        return None

def read_rig_json(self):
    '''读取rig预设的json文件，并返回字典'''
    addon_prefs = bpy.context.preferences.addons[__addon_name__].preferences

    # 验证资产库路径
    try:
        with open(addon_prefs.rig_preset_json, 'r') as f:
            library = json.load(f)
            #print(library)
            return library
    except Exception as e:
        self.report({'ERROR'}, "Fail to load rig json: {}".format(str(e)))
        return None

def search_skin_preset(json, skin_name):
    '''搜索皮肤预设，并返回皮肤预设字典'''
    if json is None:
        return None
    for list, skin_preset in json.items():
        if skin_preset['skin_name'] == skin_name:
            return skin_preset
    return None

def check_cmc_rig(selected_object: bpy.types.Object):
    '''检查选中项是否属于栗籽人模'''
    # 如果当前活动物体是Mesh
    if selected_object.type == 'MESH':
        # 验证名称前缀是否为"preview"
        if selected_object.name.startswith("preview"):
            return True
        else:
            # 获取父级骨骼
            parent_armature = None
            if selected_object.parent is not None:
                parent_armature = selected_object.parent
                if parent_armature and parent_armature.type == 'ARMATURE':
                    # 获取父级骨骼中名为"preview"的子物体
                    for child in parent_armature.children:
                        if child.type == 'MESH' and child.name.startswith("preview"):
                            return True
            else:
                return False
    # 如果当前活动物体是Armature
    elif selected_object.type == 'ARMATURE':
        # 选择子集中前缀为preview的mesh
        for child in selected_object.children:
            if child.type == 'MESH' and child.name.startswith("preview"):
                return True

    return False

def get_cmc_rig(selected_object: bpy.types.Object):
    '''检查选中项是否属于栗籽人模，并返回人模骨架'''
    if check_cmc_rig(selected_object):
        if selected_object.type == 'ARMATURE':
            for child in selected_object.children:
                if child.type == 'MESH' and child.name.startswith("preview"):
                    return selected_object
        elif selected_object.type == 'MESH':
            if selected_object.parent.type == 'ARMATURE':
                for chile in selected_object.parent.children:
                    if chile.type == 'MESH' and chile.name.startswith("preview"):
                        return selected_object.parent
    return None



#*****************************************************
#*****************************************************
#******************** 骨骼相关操作 ********************
#*****************************************************
#*****************************************************
# 复制骨骼变换
def copy_transform(self, context: bpy.types.Context, bone_name: str, aim_bone_name: str):
    '''为骨骼添加复制变换约束，目标为aim_bone，并应用约束'''
    armature = context.active_object
    # 复制变换
    bone = context.active_object.pose.bones[bone_name]
    aim_bone = context.active_object.pose.bones[aim_bone_name]
    # 为骨骼添加复制变换约束
    constraint = bone.constraints.new("COPY_TRANSFORMS")
    constraint.target = context.active_object
    constraint.subtarget = aim_bone_name
    # 应用约束
    armature.data.bones.active = bone.bone
    bpy.ops.constraint.apply(constraint=constraint.name, owner='BONE')

# 插入无缝IKFK关键帧
def insert_seamless_ikfk_keyframe(self, context: bpy.types.Context, bone_list, properity_bone_name: str, frame: int):
    armature = context.active_object
    if check_cmc_rig(armature) is False:
        self.report({'ERROR'}, "Not a ChestnutMC Rig")
        return False

    try:
        properity_bone = armature.pose.bones[properity_bone_name]
    except:
        self.report({'ERROR'}, "Bone not found: {}".format(properity_bone_name))
        return False

    for bone_name in bone_list:
        try:
            bone = armature.pose.bones[bone_name]
        except:
            self.report({'ERROR'}, "Bone not found: {}".format(bone_name))
            continue
        # 插入关键帧
        bone.keyframe_insert(data_path="location", frame=frame, group = bone.name)
        # 检查骨骼旋转模式
        if bone.rotation_mode == 'QUATERNION':
            bone.keyframe_insert(data_path="rotation_quaternion", frame=frame, group = bone.name)
        elif bone.rotation_mode == 'AXIS_ANGLE':
            bone.keyframe_insert(data_path="rotation_axis_angle", frame=frame, group = bone.name)
        else:
            bone.keyframe_insert(data_path="rotation_euler", frame=frame, group = bone.name)
        bone.keyframe_insert(data_path="scale", frame=frame, group = bone.name)

    for prop in properity_bone.keys():
        if prop.startswith("FK/IK") or prop.startswith("IK极向独立控制"):
            # 注意：这里使用 properity_bone，而且 data_path 要加 ['prop']
            path = f'["{prop}"]'
            properity_bone.keyframe_insert(data_path=path, frame=frame, group=properity_bone.name)

    return True




#*************************************************
#*************************************************
#******************** 自动错帧 ********************
#*************************************************
#*************************************************
# 保存骨骼姿态
def save_selected_bone_pose_for_autooffset(self, context: bpy.types.Context, mode: str, auto_offset_animation_pose = None):
    '''保存骨骼姿态到Armature的cmc_auto_offset_animation_pose属性'''
    armature = context.active_object
    if armature.type != 'ARMATURE':
        self.report({'ERROR'}, "Must be an armature!")
        return False
    if mode != 'start' and mode != 'end' and mode != 'anticipation' and mode != 'recover' and mode != 'intermediate':
        print("Invalid mode!")
        return False

    # 获取选中骨骼集合
    selected_bones = [bone.bone_name for bone in armature.cmc_auto_offset_animation_pose]
    if len(selected_bones) == 0:
            self.report({'INFO'}, "No bone in list!")
            return False

    # 保存姿态
    for bone_name in selected_bones:
        try:
            bone = armature.pose.bones[bone_name]
        except:
            self.report({'ERROR'}, "Bone not found: {}".format(bone_name))
            continue

        # 检查是否已经有该属性
        if mode != 'intermediate':
            if len(armature.cmc_auto_offset_animation_pose) > 0:
                for i, pose in enumerate(armature.cmc_auto_offset_animation_pose):
                    if pose.bone_name == bone_name:
                        auto_offset_animation_pose = armature.cmc_auto_offset_animation_pose[i]
                        break

        if mode == 'start':
            matrix = bone.matrix_basis.copy()
            auto_offset_animation_pose.start_pose = [v for col in matrix.transposed() for v in col]
            auto_offset_animation_pose.have_start_pose = True
        elif mode == 'end':
            matrix = bone.matrix_basis.copy()
            auto_offset_animation_pose.end_pose = [v for col in matrix.transposed() for v in col]
            auto_offset_animation_pose.have_end_pose = True
        elif mode == 'anticipation':
            matrix = bone.matrix_basis.copy()
            auto_offset_animation_pose.anticipation_pose = [v for col in matrix.transposed() for v in col]
            auto_offset_animation_pose.have_anticipation_pose = True
        elif mode == 'recover':
            matrix = bone.matrix_basis.copy()
            auto_offset_animation_pose.recover_pose = [v for col in matrix.transposed() for v in col]
            auto_offset_animation_pose.have_recover_pose = True
        elif mode == 'intermediate':
            matrix = bone.matrix_basis.copy()
            bone = auto_offset_animation_pose.action.add()
            bone.bone_name = bone_name
            bone.pose = [v for col in matrix.transposed() for v in col]
        else:
            pass

    # 添加设置属性
    if len(armature.cmc_auto_offset_animation_settings) == 0:
        armature.cmc_auto_offset_animation_settings.add()

    return True

# 删除骨骼姿态
def delete_bone_pose_from_autooffset(self, context: bpy.types.Context, mode: str):
    '''删除Armature中的选中的cmc_auto_offset_animation_pose骨骼姿态'''
    armature = context.active_object
    if armature.type != 'ARMATURE':
        self.report({'ERROR'}, "Must be an armature!")
        return False
    if mode != 'start' and mode != 'end':
        print("Invalid mode!")
        return False

    if len(armature.cmc_auto_offset_animation_pose) > 0:
        for pose in armature.cmc_auto_offset_animation_pose:
            setattr(pose, mode, False)

    return True

# 调换骨骼在列表中位置
def swap_bone_list_item(self, context, index: int, direction: int):
    armature = context.active_object
    if armature.type != "ARMATURE":
        self.report({"ERROR"}, "Active object must be an armature!")
        return{"CANCELLED"}

    origin_pose = get_auto_offset_animation_bone_parameters(armature, '', index)
    temp = get_auto_offset_animation_bone_parameters(armature, '', direction)

    exchange_pose = armature.cmc_auto_offset_animation_pose[direction]

    pose = armature.cmc_auto_offset_animation_pose

    exchange_pose.bone_name = origin_pose['bone_name']
    exchange_pose.priority = origin_pose['priority']
    exchange_pose.frame_offset = origin_pose['frame_offset']
    exchange_pose.start_pose = origin_pose['start_pose']
    exchange_pose.end_pose = origin_pose['end_pose']
    exchange_pose.have_start_pose = origin_pose['have_start_pose']
    exchange_pose.have_end_pose = origin_pose['have_end_pose']
    exchange_pose.meum_expand = origin_pose['meum_expand']
    exchange_pose.anticipation_pose = origin_pose['anticipation_pose']
    exchange_pose.anticipation_pose_mode = origin_pose['anticipation_pose_mode']
    exchange_pose.have_anticipation_pose = origin_pose['have_anticipation_pose']
    exchange_pose.recover_pose = origin_pose['recover_pose']
    exchange_pose.recover_pose_mode = origin_pose['recover_pose_mode']
    exchange_pose.have_recover_pose = origin_pose['have_recover_pose']

    pose[index].bone_name = temp['bone_name']
    pose[index].priority = temp['priority']
    pose[index].frame_offset = temp['frame_offset']
    pose[index].start_pose = temp['start_pose']
    pose[index].end_pose = temp['end_pose']
    pose[index].have_start_pose = temp['have_start_pose']
    pose[index].have_end_pose = temp['have_end_pose']
    pose[index].meum_expand = temp['meum_expand']
    pose[index].anticipation_pose = temp['anticipation_pose']
    pose[index].anticipation_pose_mode = temp['anticipation_pose_mode']
    pose[index].have_anticipation_pose = temp['have_anticipation_pose']
    pose[index].recover_pose = temp['recover_pose']
    pose[index].recover_pose_mode = temp['recover_pose_mode']
    pose[index].have_recover_pose = temp['have_recover_pose']


# 调换动作在列表中的顺序
def swap_action_list_item(self, context, index: int, direction: int):
    armature = context.active_object
    if armature.type != "ARMATURE":
        self.report({"ERROR"}, "Active object must be an armature!")
        return{"CANCELLED"}

    original_poses = get_auto_offset_animation_action_poses(armature, '', index)
    temp_poses = get_auto_offset_animation_action_poses(armature, '', direction)

    exchange_action = armature.cmc_auto_offset_animation_intermediate_action[direction]
    action = armature.cmc_auto_offset_animation_intermediate_action[index]

    # 保存目标位置参数
    exchange_action_name = armature.cmc_auto_offset_animation_intermediate_action[direction].action_name
    exchange_action_pose_frame = armature.cmc_auto_offset_animation_intermediate_action[direction].pose_frame
    exchange_action_frame_length = armature.cmc_auto_offset_animation_intermediate_action[direction].frame_length

    exchange_action.action_name = armature.cmc_auto_offset_animation_intermediate_action[index].action_name
    exchange_action.pose_frame = armature.cmc_auto_offset_animation_intermediate_action[index].pose_frame
    exchange_action.frame_length =armature.cmc_auto_offset_animation_intermediate_action[index].frame_length
    # 存入姿态数据
    exchange_action.action.clear()
    for key, value in original_poses.items():
        new_action = exchange_action.action.add()
        new_action.bone_name = key
        new_action.pose = value


    action.action_name = exchange_action_name
    action.pose_frame = exchange_action_pose_frame
    action.frame_length = exchange_action_frame_length
    # 存入动作数据
    action.action.clear()
    for key, value in temp_poses.items():
        new_action = action.action.add()
        new_action.bone_name = key
        new_action.pose = value


# 获取自动错帧骨骼参数
def get_auto_offset_animation_bone_parameters(armature: bpy.types.Object, bone_name: str, index: int = -1):
    '''获取自动错帧骨骼参数'''
    if armature.type != 'ARMATURE':
        return None

    # 找到骨骼列表
    if index < 0:
        for i, bone in enumerate(armature.cmc_auto_offset_animation_pose):
            if bone.bone_name == bone_name:
                index = i
                break

    if index < 0 or index >= len(armature.cmc_auto_offset_animation_pose):
        return None

    bone = armature.cmc_auto_offset_animation_pose[index]

    # 骨骼参数
    parameters = {
        "bone_name":     bone.bone_name,
        "priority":      bone.priority,
        "frame_offset":  bone.frame_offset,
        "have_start_pose":    bone.have_start_pose,
        "have_end_pose":      bone.have_end_pose,
        "start_pose":    [v for row in bone.start_pose.transposed() for v in row],
        "end_pose":      [v for row in bone.end_pose.transposed() for v in row],
        "meum_expand":   bone.meum_expand,
        "anticipation_pose": [v for row in bone.anticipation_pose.transposed() for v in row],
        "anticipation_pose_mode": bone.anticipation_pose_mode,
        "have_anticipation_pose": bone.have_anticipation_pose,
        "recover_pose": [v for row in bone.recover_pose.transposed() for v in row],
        "recover_pose_mode": bone.recover_pose_mode,
        "have_recover_pose": bone.have_recover_pose,
    }

    return parameters


# 获取自动错帧动作中各个骨骼的姿态
def get_auto_offset_animation_action_poses(armature: bpy.types.Object, action: str, index: int = -1):
    '''获取自动错帧动作参数'''
    if armature.type != 'ARMATURE':
        return None

    # 找到对应姿态
    if index < 0:
        for i, _action in enumerate(armature.cmc_auto_offset_animation_intermediate_action):
            if _action.name == action:
                index = i
                break

    if index < 0 or index >= len(armature.cmc_auto_offset_animation_intermediate_action):
        return None

    poses = armature.cmc_auto_offset_animation_intermediate_action[index].action

    parameters = {}
    for pose in poses:
        parameters[pose.bone_name] = [v for row in pose.pose.transposed() for v in row]

    return parameters


# 加载自动错帧预设列表
_CMC_AUTOOFFSET_PERSETS = []
def load_auto_offset_animation_preset_list(self, context: bpy.types.Context):
    '''加载自动错帧预设列表'''
    addon_prefs = context.preferences.addons[__addon_name__].preferences
    presets_path = addon_prefs.auto_offset_animation_presets_path
    global _CMC_AUTOOFFSET_PERSETS

    if not os.path.isdir(presets_path):
        os.makedirs(presets_path)

    # 读取目录中所有json文件
    preset_files = []
    try:
        for file in os.listdir(presets_path):
            if file.endswith(".json"):
                file_name = os.path.splitext(file)[0]
                preset_files.append((file, file_name, ''))
    except Exception as e:
        print(e)
        return False

    _CMC_AUTOOFFSET_PERSETS = preset_files

    return _CMC_AUTOOFFSET_PERSETS