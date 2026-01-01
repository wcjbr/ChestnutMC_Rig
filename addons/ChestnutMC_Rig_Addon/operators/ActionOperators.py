import bpy
import os.path
import glob
import json
import struct
import shutil
import datetime

from ..config import __addon_name__
from ..panels.ImageManager import *
from .Defs import *



#*****************************************************
#*****************************************************
#******************** 自动错帧姿态 ********************
#*****************************************************
#*****************************************************
# 保存起始姿态
class CHESTNUTMC_OT_SaveStartPose(bpy.types.Operator):
    """Auto Offset Animation"""
    bl_idname = "cmc.save_start_pose"
    bl_label = "Save Start Pose"
    bl_description = "Save the start pose of auto offset animation"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != 'POSE':
            return False
        return True

    def execute(self, context: bpy.types.Context):
        if save_selected_bone_pose_for_autooffset(self, context, 'start'):
            self.report({'INFO'}, "Start pose saved successfully!")
            return {'FINISHED'}
        return {'CANCELLED'}


# 保存结束姿态
class CHESTNUTMC_OT_SaveEndPose(bpy.types.Operator):
    """Auto Offset Animation"""
    bl_idname = "cmc.save_end_pose"
    bl_label = "Save End Pose"
    bl_description = "Save the end pose of auto offset animation"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != 'POSE':
            return False
        return True

    def execute(self, context: bpy.types.Context):
        if save_selected_bone_pose_for_autooffset(self, context, 'end'):
            self.report({'INFO'}, "End pose saved successfully!")
            return {'FINISHED'}
        return {'CANCELLED'}


# 保存anticipation姿态
class CHESTNUTMC_OT_SaveAnticipationPose(bpy.types.Operator):
    '''Auto Offset Animation'''
    bl_idname = "cmc.save_anticipation_pose"
    bl_label = "Save Anticipation Pose"
    bl_description = "Save Anticipation Pose if you want to use it"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != 'POSE':
            return False
        if len(context.active_object.cmc_auto_offset_animation_settings) == 0 or context.active_object.cmc_auto_offset_animation_settings[0].use_anticipation_pose is False:
            return False
        return True

    def execute(self, context: bpy.types.Context):
        if save_selected_bone_pose_for_autooffset(self, context, 'anticipation'):
            self.report({'INFO'}, "Anticipation pose saved successfully!")
            return {'FINISHED'}
        return {'CANCELLED'}


# 保存recover姿态
class CHESTNUTMC_OT_SaveRecoverPose(bpy.types.Operator):
    '''Auto Offset Animation'''
    bl_idname = "cmc.save_recover_pose"
    bl_label = "Save Postponement Pose"
    bl_description = "Save Postponement Pose if you want to use it"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != 'POSE':
            return False
        if len(context.active_object.cmc_auto_offset_animation_settings) == 0 or context.active_object.cmc_auto_offset_animation_settings[0].use_recover_pose is False:
            return False
        return True

    def execute(self, context: bpy.types.Context):
        if save_selected_bone_pose_for_autooffset(self, context, 'recover'):
            self.report({'INFO'}, "Postponement pose saved successfully!")
            return {'FINISHED'}
        return {'CANCELLED'}


# 应用起始姿态
class CHESTNUTMC_OT_ApplyStartPose(bpy.types.Operator):
    """Apply start pose"""
    bl_idname = "cmc.apply_start_pose"
    bl_label = "Apply Start Pose"
    bl_description = "Apply start pose"
    bl_options = {'REGISTER', 'UNDO'}

    mode: bpy.props.EnumProperty(
        name="Apply Mode",
        items=[
            ("ALL", "Apply All Bones", "Apply start pose to all bones"),
            ("SELECTED", "Apply Selected Bone", "Only apply start pose to selected bone")
        ],
        default="ALL",
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}
    ) # type: ignore

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != "POSE":
            return False
        if len(context.active_object.cmc_auto_offset_animation_pose) == 0:
            return False
        if not context.active_object.cmc_auto_offset_animation_pose[-1].have_start_pose:
            return False
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        for pose in context.active_object.cmc_auto_offset_animation_pose:
            bone = context.active_object.pose.bones.get(pose.bone_name)
            if pose.have_start_pose:
                if self.mode == 'ALL' or (self.mode == 'SELECTED' and is_bone_selected(self, bone)):
                    # 获取骨骼矩阵
                    matrix = pose.start_pose
                    bone.matrix_basis = matrix
            else:
                self.report({'WARNING'}, f"Bone {pose.bone_name} does not have a start pose saved.")

        self.report({'INFO'}, "Start pose applied successfully!")
        return {'FINISHED'}


# 应用结束姿态
class CHESTNUTMC_OT_ApplyEndPose(bpy.types.Operator):
    '''Apply end pose'''
    bl_idname = "cmc.apply_end_pose"
    bl_label = "Apply End Pose"
    bl_description = "Apply end pose"
    bl_options = {'REGISTER', 'UNDO'}


    mode: bpy.props.EnumProperty(
        name="Apply Mode",
        items=[
            ("ALL", "Apply All Bones", "Apply start pose to all bones"),
            ("SELECTED", "Apply Selected Bone", "Only apply start pose to selected bone")
        ],
        default="ALL",
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}
    ) # type: ignore

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != "POSE":
            return False
        if len(context.active_object.cmc_auto_offset_animation_pose) == 0:
            return False
        if not context.active_object.cmc_auto_offset_animation_pose[-1].have_end_pose:
            return False
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        for pose in context.active_object.cmc_auto_offset_animation_pose:
            bone = context.active_object.pose.bones.get(pose.bone_name)
            if pose.have_end_pose:
                if self.mode == 'ALL' or (self.mode == 'SELECTED' and is_bone_selected(self, bone)):
                    # 获取骨骼矩阵
                    matrix = pose.end_pose
                    bone.matrix_basis = matrix
            else:
                self.report({'WARNING'}, f"Bone {pose.bone_name} does not have a end pose saved.")

        self.report({'INFO'}, "End pose applied successfully!")
        return {'FINISHED'}


# 应用anticipation姿态
class CHESTNUTMC_OT_ApplyAnticipationPose(bpy.types.Operator):
    '''Apply Anticipation Pose'''
    bl_idname = "cmc.apply_anticipation_pose"
    bl_label = "Apply Custom Anticipation Pose"
    bl_description = "Apply custom anticipation pose if had been saved"
    bl_options = {'REGISTER', 'UNDO'}

    mode: bpy.props.EnumProperty(
        name="Apply Mode",
        items=[
            ("ALL", "Apply All Bones", "Apply start pose to all bones"),
            ("SELECTED", "Apply Selected Bone", "Only apply start pose to selected bone")
        ],
        default="ALL",
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}
    ) # type: ignore

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != 'POSE':
            return False
        if len(context.active_object.cmc_auto_offset_animation_pose) == 0:
            return False
        if not context.active_object.cmc_auto_offset_animation_pose[-1].have_anticipation_pose:
            return False
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        for pose in context.active_object.cmc_auto_offset_animation_pose:
            bone = context.active_object.pose.bones.get(pose.bone_name)
            if pose.have_anticipation_pose:
                if self.mode == 'ALL' or (self.mode == 'SELECTED' and is_bone_selected(self, bone)):
                    # 获取骨骼矩阵
                    matrix = pose.anticipation_pose
                    bone.matrix_basis = matrix
            else:
                self.report({'WARNING'}, f"Bone {pose.bone_name} does not have a anticipation pose saved.")

        self.report({'INFO'}, "Anticipation pose applied successfully!")
        return {'FINISHED'}


# 应用recover姿态
class CHESTNUTMC_OT_ApplyRecoverPose(bpy.types.Operator):
    """Apply Postponement Pose."""
    bl_idname = "cmc.apply_recover_pose"
    bl_label = "Apply Custom Postponement Pose"
    bl_description = "Apply custom postponement pose if had been saved"
    bl_options = {'REGISTER', 'UNDO'}

    mode: bpy.props.EnumProperty(
        name="Apply Mode",
        items=[
            ("ALL", "Apply All Bones", "Apply start pose to all bones"),
            ("SELECTED", "Apply Selected Bone", "Only apply start pose to selected bone")
        ],
        default="ALL",
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}
    ) # type: ignore

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != 'POSE':
            return False
        if len(context.active_object.cmc_auto_offset_animation_pose) == 0:
            return False
        if not context.active_object.cmc_auto_offset_animation_pose[-1].have_recover_pose:
            return False
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        for pose in context.active_object.cmc_auto_offset_animation_pose:
            bone = context.active_object.pose.bones.get(pose.bone_name)
            if bone is None:
                self.report({'WARNING'}, f"Bone {pose.bone_name} not found in the armature.")
                continue
            if pose.have_recover_pose:
                if self.mode == 'ALL' or (self.mode == 'SELECTED' and is_bone_selected(self, bone)):
                    # 获取骨骼矩阵
                    matrix = pose.recover_pose
                    bone.matrix_basis = matrix
            else:
                self.report({'WARNING'}, f"Bone {pose.bone_name} does not have a postponement pose saved.")

        self.report({'INFO'}, "Postponement pose applied successfully!")
        return {'FINISHED'}


# 保存中间姿态
class CHESTNUTMC_OT_SaveIntermediatePose(bpy.types.Operator):
    '''Auto Offset Animation'''
    bl_idname = "cmc.save_intermediate_pose"
    bl_label = "Save Intermediate Pose"
    bl_description = "Save Intermediate Pose if you want to use it"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != 'POSE':
            return False
        if len(context.active_object.cmc_auto_offset_animation_pose) == 0:
            return False
        return True

    def execute(self, context: bpy.types.Context):
        armature = context.active_object
        if armature is None or armature.type != 'ARMATURE':
            self.report({'WARNING'}, "Please select an armature object.")
            return {'CANCELLED'}

        # 新键中间姿态数据
        auto_offset_animation_pose = armature.cmc_auto_offset_animation_intermediate_action.add()
        auto_offset_animation_pose.action_name = "Action" + str(len(armature.cmc_auto_offset_animation_intermediate_action) - 1)
        auto_offset_animation_pose.pose_frame = context.scene.frame_current

        # 自动记录动作长度
        armature.cmc_auto_offset_animation_intermediate_action_index = len(armature.cmc_auto_offset_animation_intermediate_action) - 1
        if armature.cmc_auto_offset_animation_intermediate_action_index > 0:
            frame_start = armature.cmc_auto_offset_animation_intermediate_action[armature.cmc_auto_offset_animation_intermediate_action_index - 1].pose_frame
            frame_end = auto_offset_animation_pose.pose_frame
            if frame_start < frame_end:
                armature.cmc_auto_offset_animation_intermediate_action[armature.cmc_auto_offset_animation_intermediate_action_index - 1].frame_length = frame_end - frame_start

        # 保存中间姿态
        if save_selected_bone_pose_for_autooffset(self, context, 'intermediate', auto_offset_animation_pose):
            self.report({'INFO'}, "Intermediate pose saved successfully!")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Fail to save intermediate pose.")
            return {'CANCELLED'}


# 更新中间姿态
class CHESTNUTMC_OT_UpdateIntermediatePose(bpy.types.Operator):
    """Update Intermediate Pose."""
    bl_idname = "cmc.update_intermediate_pose"
    bl_label = "Update Intermediate Pose"
    bl_description = "Update intermediate pose from auto offset animation settings"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.active_object is None or context.active_object.type != 'ARMATURE':
            return False
        if len(context.active_object.cmc_auto_offset_animation_intermediate_action) == 0:
            return False
        return True

    def execute(self, context: bpy.types.Context):
        armature = context.active_object
        index = armature.cmc_auto_offset_animation_intermediate_action_index
        try:
            auto_offset_animation_pose = armature.cmc_auto_offset_animation_intermediate_action[index]
            action_name = auto_offset_animation_pose.action_name
            action = auto_offset_animation_pose.action
            action = action.clear()
            save_selected_bone_pose_for_autooffset(self, context, 'intermediate', auto_offset_animation_pose)
        except IndexError:
            self.report({'ERROR'}, "No intermediate action selected.")
            return {'CANCELLED'}
        self.report({'INFO'}, "Intermediate pose updated successfully!")
        return {'FINISHED'}




# 删除中间姿态
class CHESTNUTMC_OT_DeleteIntermediatePose(bpy.types.Operator):
    """Delete Intermediate Pose."""
    bl_idname = "cmc.delete_intermediate_pose"
    bl_label = "Delete Intermediate Pose"
    bl_description = "Delete intermediate pose from auto offset animation settings"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.active_object is None or context.active_object.type != 'ARMATURE':
            return False
        if len(context.active_object.cmc_auto_offset_animation_intermediate_action) == 0:
            return False
        return True

    def execute(self, context):
        armature = context.active_object
        index = armature.cmc_auto_offset_animation_intermediate_action_index
        try:
            action_name = armature.cmc_auto_offset_animation_intermediate_action[index].action_name
            armature.cmc_auto_offset_animation_intermediate_action.remove(index)
            if index > 0:
                armature.cmc_auto_offset_animation_intermediate_action_index -= 1
            else:
                armature.cmc_auto_offset_animation_intermediate_action_index = 0
        except IndexError:
            armature.cmc_auto_offset_animation_intermediate_action_index = 0
            return{"CANCELLED"}

        self.report({'INFO'}, "Deleted intermediate action: {}".format(action_name))
        return{"FINISHED"}


# 应用中间姿态
class CHESTNUTMC_OT_ApplyIntermediatePose(bpy.types.Operator):
    """Apply Intermediate Pose."""
    bl_idname = "cmc.apply_intermediate_pose"
    bl_label = "Apply Intermediate Pose"
    bl_description = "Apply intermediate pose if had been saved"
    bl_options = {'REGISTER', 'UNDO'}

    mode: bpy.props.EnumProperty(
        name="Apply Mode",
        items=[
            ("ALL", "Apply All Bones", "Apply start pose to all bones"),
            ("SELECTED", "Apply Selected Bone", "Only apply start pose to selected bone")
        ],
        default="ALL",
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}
    ) # type: ignore

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != 'POSE':
            return False
        if len(context.active_object.cmc_auto_offset_animation_intermediate_action) == 0:
            return False
        if context.active_object.cmc_auto_offset_animation_intermediate_action_index >= len(context.active_object.cmc_auto_offset_animation_intermediate_action):
            return False
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        armature = context.active_object
        if armature is None or armature.type != 'ARMATURE':
            self.report({'WARNING'}, "No active armature found.")
            return {'CANCELLED'}

        index = armature.cmc_auto_offset_animation_intermediate_action_index

        for pose in armature.cmc_auto_offset_animation_intermediate_action[index].action:
            bone = armature.pose.bones.get(pose.bone_name)
            if bone is None:
                self.report({'WARNING'}, f"Bone {pose.bone_name} not found in the armature.")
                continue
            else:
                if self.mode == 'ALL' or (self.mode == 'SELECTED' and is_bone_selected(self, bone)):
                    # 获取骨骼矩阵
                    matrix = pose.pose
                    bone.matrix_basis = matrix

        self.report({'INFO'}, "Intermediate pose applied successfully!")
        return {'FINISHED'}


# 在列表中上移中间姿态
class CHESTNUTMC_OT_MovePoseListUp(bpy.types.Operator):
    bl_idname = "cmc.move_pose_list_up"
    bl_label = "Move Up Pose"
    bl_description = "Move up pose in the list"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if len(context.active_object.cmc_auto_offset_animation_intermediate_action) < 2:
            return False
        if context.active_object.cmc_auto_offset_animation_intermediate_action_index == 0:
            return False
        return True

    def execute(self, context):
        armature = context.active_object
        if armature is None or armature.type != "ARMATURE":
            self.report({'ERROR'}, "Please select an armature!")
            return {"CANCELLED"}

        index = armature.cmc_auto_offset_animation_intermediate_action_index

        swap_action_list_item(self, context, index, index-1)
        armature.cmc_auto_offset_animation_intermediate_action_index -= 1
        return {"FINISHED"}


# 在列表中下移中间姿态
class CHESTNUTMC_OT_MovePoseListDown(bpy.types.Operator):
    bl_idname = "cmc.move_pose_list_down"
    bl_label = "Move Pose List Down"
    bl_description = "Move down pose in the list"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if len(context.active_object.cmc_auto_offset_animation_intermediate_action) < 2:
            return False
        if context.active_object.cmc_auto_offset_animation_intermediate_action_index == len(context.active_object.cmc_auto_offset_animation_intermediate_action) - 1:
            return False
        return True

    def execute(self, context):
        armature = context.active_object
        if armature is None or armature.type != "ARMATURE":
            self.report({'ERROR'}, "Please select an armature!")
            return {"CANCELLED"}

        index = armature.cmc_auto_offset_animation_intermediate_action_index

        swap_action_list_item(self, context, index, index+1)
        armature.cmc_auto_offset_animation_intermediate_action_index += 1
        return {"FINISHED"}


# 删除姿态
class CHESTNUTMC_OT_Delete_AO_Pose(bpy.types.Operator):
    bl_idname = "cmc.delete_ao_pose"
    bl_label = "Delete Saved Poses"
    bl_description = "Delete saved pose from auto offset animation settings"
    bl_options = {'REGISTER', 'UNDO'}

    #delete_start_pose: bpy.props.BoolProperty(name="Delete Start Pose", default=True) # type: ignore
    #delete_end_pose: bpy.props.BoolProperty(name="Delete End Pose", default=True) # type: ignore
    delete_anticipation_pose: bpy.props.BoolProperty(name="Delete Anticipation Pose", default=True) # type: ignore
    delete_recover_pose: bpy.props.BoolProperty(name="Delete Postponement Pose", default=True) # type: ignore
    delete_all_action: bpy.props.BoolProperty(name="Delete All Action", default=True) # type: ignore

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != 'POSE':
            return False
        return True

    def invoke(self, context, event):
        # 弹出对话框
        return context.window_manager.invoke_props_dialog(self)


    def execute(self, context):
        armature = context.active_object
        if armature.type != "ARMATURE":
            self.report({"ERROR"}, "Active object must be an armature!")
            return{"CANCELLED"}

        for pose in armature.cmc_auto_offset_animation_pose:
            '''if self.delete_start_pose:
                pose.have_start_pose = False
            if self.delete_end_pose:
                pose.have_end_pose = False'''
            if self.delete_anticipation_pose:
                pose.have_anticipation_pose = False
            if self.delete_recover_pose:
                pose.have_recover_pose = False
            if self.delete_all_action:
                while len(armature.cmc_auto_offset_animation_intermediate_action) > 0:
                    bpy.ops.cmc.delete_intermediate_pose()

        self.report({"INFO"}, "Poses deleted!")
        return{"FINISHED"}



#*********************************************
#*********************************************
#**************** 自动错帧骨骼 ****************
#*********************************************
#*********************************************
# 添加骨骼到列表
class CHESTNUTMC_OT_Add_Bone_To_AutoOffset_List(bpy.types.Operator):
    bl_idname = "cmc.add_bone_to_autooffset_list"
    bl_label = "Add Bone to Auto Offset List"
    bl_description = "Add Bone to Auto Offset List"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.mode != 'POSE':
            return False
        return True

    def execute(self, context):
        armature = context.active_object
        if armature.type != "ARMATURE":
            self.report({"ERROR"}, "Active object must be an armature!")
            return{"CANCELLED"}

        # 获取选中骨骼列表
        selected_bones = get_selected_bone_names(self, armature)

        for bone in armature.cmc_auto_offset_animation_pose:
            if bone.bone_name in selected_bones:
                # 从列表删除
                selected_bones.remove(bone.bone_name)

        if len(selected_bones) > 0:
            for bone_name in selected_bones:
                # 添加到列表
                armature.cmc_auto_offset_animation_pose.add()
                armature.cmc_auto_offset_animation_pose[-1].bone_name = bone_name

        # 添加设置属性
        if len(armature.cmc_auto_offset_animation_settings) == 0:
            armature.cmc_auto_offset_animation_settings.add()

        return {"FINISHED"}


# 从列表中删除骨骼
class CHESTNUTMC_OT_Delete_Bone_From_AutoOffset_List(bpy.types.Operator):
    bl_idname = "cmc.delete_bone_from_autooffset_list"
    bl_label = "Delete Bone from Auto Offset List"
    bl_description = "Delete Bone from Auto Offset List"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.mode != 'POSE':
            return False
        return True

    def execute(self, context):
        armature = context.active_object
        if armature.type != "ARMATURE":
            self.report({"ERROR"}, "Active object must be an armature!")
            return {"CANCELLED"}

        index = armature.cmc_auto_offset_animation_pose_index
        if index >= len(armature.cmc_auto_offset_animation_pose):
            self.report({"ERROR"}, "Index out of range!")
            return {"CANCELLED"}
        # 从列表删除骨骼
        armature.cmc_auto_offset_animation_pose.remove(index)
        if armature.cmc_auto_offset_animation_pose_index > 0:
            armature.cmc_auto_offset_animation_pose_index -= 1
        return {"FINISHED"}


# 选中列表骨骼
class CHESTNUTMC_OT_Select_Bone_inList(bpy.types.Operator):
    bl_idname = "cmc.select_bone_inlist"
    bl_label = "Select Bone List"
    bl_description = "Select Bone in List"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.mode != 'POSE':
            return False
        return True

    def execute(self, context):
        armature = context.active_object
        if armature.type != "ARMATURE":
            self.report({"ERROR"}, "Active object must be an armature!")
            return{"CANCELLED"}

        index = context.object.cmc_auto_offset_animation_pose_index
        armature.data.bones.active = armature.pose.bones[armature.cmc_auto_offset_animation_pose[index].bone_name].bone
        # 刷新界面
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        return{"FINISHED"}


# 选中列表所有骨骼
class CHESTNUTMC_OT_Select_All_Bones_inList(bpy.types.Operator):
    bl_idname = "cmc.select_all_bones_inlist"
    bl_label = "Select All Bones in the List"
    bl_description = "Select All Bones in the List"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.mode != 'POSE':
            return False
        return True

    def execute(self, context):
        armature = context.active_object
        if armature.type != "ARMATURE":
            self.report({"ERROR"}, "Active object must be an armature!")
            return{"CANCELLED"}

        if len(armature.cmc_auto_offset_animation_pose) == 0:
            self.report({"ERROR"}, "No bones in the list!")
            return{"CANCELLED"}

        for pose in armature.cmc_auto_offset_animation_pose:
            bone = armature.pose.bones.get(pose.bone_name)
            if bone:
                # 检查版本
                if bpy.app.version >= (5, 0, 0):
                    bone.select = True
                else:
                    bone.bone.select = True

        return{"FINISHED"}


# 删除列表全部骨骼
class CHESTNUTMC_OT_Delete_All_Bones_inList(bpy.types.Operator):
    bl_idname = "cmc.delete_all_bones_inlist"
    bl_label = "Delete All Bones in the List"
    bl_description = "Delete All Bones in the List"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.mode != 'POSE':
            return False
        return True

    def invoke(self, context, event=None):
        return context.window_manager.invoke_confirm(self, event, title="Are you sure you want to delete all bones in the list?")

    def execute(self, context):
        armature = context.active_object
        if armature.type != "ARMATURE":
            self.report({"ERROR"}, "Active object must be an armature!")
            return{"CANCELLED"}

        armature.cmc_auto_offset_animation_pose.clear()
        armature.cmc_auto_offset_animation_pose_index = 0

        return{"FINISHED"}


# 上移动骨骼列表位置
class CHESTNUTMC_OT_MoveBoneListUp(bpy.types.Operator):
    bl_idname = "cmc.move_bone_list_up"
    bl_label = "Move Bone List Up"
    bl_description = "Move bone up in current list"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.mode != 'POSE':
            return False
        if context.object.cmc_auto_offset_animation_pose_index < 1:
            return False
        return True

    def execute(self, context):
        index = context.object.cmc_auto_offset_animation_pose_index
        swap_bone_list_item(self, context, index, index-1)

        context.object.cmc_auto_offset_animation_pose_index -= 1

        return{"FINISHED"}

# 下移动骨骼列表位置
class CHESTNUTMC_OT_MoveBoneListDown(bpy.types.Operator):
    bl_idname = "cmc.move_bone_list_down"
    bl_label = "Move Bone List Down"
    bl_description = "Move bone down in current list"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.mode != 'POSE':
            return False
        if context.object.cmc_auto_offset_animation_pose_index >= len(context.object.cmc_auto_offset_animation_pose) - 1:
            return False
        return True

    def execute(self, context):
        index = context.object.cmc_auto_offset_animation_pose_index
        swap_bone_list_item(self, context, index, index+1)

        context.object.cmc_auto_offset_animation_pose_index += 1

        return{"FINISHED"}


# 更改起始姿态模式
class CHESTNUTMC_OT_ChangeAnticipationPoseMode(bpy.types.Operator):
    bl_idname = "cmc.change_anticipation_pose_mode"
    bl_label = "Change Anticipation Pose Mode"
    bl_description = "Change bones' anticipation pose mode"
    bl_options = {'REGISTER', 'UNDO'}

    mode: EnumProperty(
        name="Mode",
        items=[
            ("AUTO", "Auto", "Auto generate anticipation pose"),
            ("CUSTOM", "Custom", "Use custom anticipation pose"),
            ("NONE", "None", "No anticipation pose"),
        ],
        default="AUTO"
    ) # type: ignore

    apply_range: EnumProperty(
        name="Apply Range",
        items=[
            ("ALL", "All", "Apply to all"),
            ("SELECTED", "Selected Bones", "Apply to selected bones"),
        ],
        default="ALL"
    ) # type: ignore

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.active_object is None or context.active_object.type != "ARMATURE":
            return False
        if len(context.active_object.cmc_auto_offset_animation_pose) < 1:
            return False
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        armature = context.active_object
        if armature.type != 'ARMATURE':
            self.report({'ERROR'}, "Please select an armature!")
            return {'CANCELLED'}

        bone_list = []
        if self.apply_range == "SELECTED":
            bone_list = [bone.name for bone in armature.pose.bones if is_bone_selected(self, bone)]
        for pose_bone in armature.cmc_auto_offset_animation_pose:
            if self.apply_range == "ALL" or pose_bone.bone_name in bone_list:
                pose_bone.anticipation_pose_mode = self.mode

        return {'FINISHED'}


# 更改结束姿态模式
class CHESTNUTMC_OT_ChangeRecoverPoseMode(bpy.types.Operator):
    bl_idname = "cmc.change_recover_pose_mode"
    bl_label = "Change Postponement Pose Mode"
    bl_description = "Change bones' postponement pose mode"
    bl_options = {'REGISTER', 'UNDO'}

    mode: EnumProperty(
        name="Mode",
        items=[
            ("AUTO", "Auto", "Auto generate anticipation pose"),
            ("CUSTOM", "Custom", "Use custom anticipation pose"),
            ("NONE", "None", "No anticipation pose"),
        ],
        default="AUTO"
    ) # type: ignore

    apply_range: EnumProperty(
        name="Apply Range",
        items=[
            ("ALL", "All", "Apply to all"),
            ("SELECTED", "Selected Bones", "Apply to selected bones"),
        ],
        default="ALL"
    ) # type: ignore

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.active_object is None or context.active_object.type != "ARMATURE":
            return False
        if len(context.active_object.cmc_auto_offset_animation_pose) < 1:
            return False
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        armature = context.active_object
        if armature.type != 'ARMATURE':
            self.report({'ERROR'}, "Please select an armature!")
            return {'CANCELLED'}

        bone_list = []
        if self.apply_range == "SELECTED":
            bone_list = [bone.name for bone in armature.pose.bones if is_bone_selected(self, bone)]
        for pose_bone in armature.cmc_auto_offset_animation_pose:
            if self.apply_range == "ALL" or pose_bone.bone_name in bone_list:
                pose_bone.recover_pose_mode = self.mode

        return {'FINISHED'}


#*****************************************************
#*****************************************************
#******************** 自动错帧 ***********************
#*****************************************************
#*****************************************************
class CHESTNUTMC_OT_CreateAutoOffsetAnimation(bpy.types.Operator):
    bl_description = "Create an auto offset animation based on the bones in list and their poses"
    bl_idname = "cmc.create_auto_offset_animation"
    bl_label = "Create Auto Offset Animation"
    bl_options = {"REGISTER", "UNDO"}

    def insert_selected_bone_keyframe(self, bone, insert_frame, frame_type = 'KEYFRAME'):
        """Helper function to insert keyframe for a bone."""
        # 插入关键帧
        bone.keyframe_insert(data_path="location", frame=insert_frame, group = bone.name, keytype = frame_type)
        # 获取旋转模式
        if bone.rotation_mode == 'QUATERNION':
            bone.keyframe_insert(data_path="rotation_quaternion", frame=insert_frame, group = bone.name, keytype = frame_type)
        elif bone.rotation_mode == 'AXIS_ANGLE':
            bone.keyframe_insert(data_path="rotation_axis_angle", frame=insert_frame, group = bone.name, keytype = frame_type)
        else:
            bone.keyframe_insert(data_path="rotation_euler", frame=insert_frame, group = bone.name, keytype = frame_type)
        bone.keyframe_insert(data_path="scale", frame=insert_frame, group = bone.name, keytype = frame_type)

    '''def create_start_end_keyframe(self, armature: bpy.types.Object, bones_list: dict, current_frame: int, aim_frame: int):
        # 骨骼姿态
        # 在当前帧应用起始和结束姿态
        for bone in armature.pose.bones:
            if bone.name in bones_list.keys():
                index = bones_list[bone.name][0]
                frame_offset = bones_list[bone.name][2] * bones_list[bone.name][1]
                if armature.cmc_auto_offset_animation_pose[index].have_start_pose:
                    # 应用起始姿态
                    matrix = armature.cmc_auto_offset_animation_pose[index].start_pose
                    bone.matrix_basis = matrix
                    # 插入关键帧
                    if frame_offset > 0:
                        self.insert_selected_bone_keyframe(bone, current_frame + frame_offset, "JITTER")
                        bones_list[bone.name][3] = current_frame + frame_offset  # 记录起始关键帧位置
                    else:
                        self.insert_selected_bone_keyframe(bone, current_frame, "KEYFRAME")
                        bones_list[bone.name][3] = current_frame  # 记录起始关键帧位置

                if armature.cmc_auto_offset_animation_pose[index].have_end_pose:
                    # 应用结束姿态
                    matrix = armature.cmc_auto_offset_animation_pose[index].end_pose
                    bone.matrix_basis = matrix
                    # 插入关键帧
                    if frame_offset > 0:
                        self.insert_selected_bone_keyframe(bone, aim_frame + frame_offset, "JITTER")
                        bones_list[bone.name][4] = aim_frame + frame_offset  # 记录结束关键帧位置
                    else:
                        self.insert_selected_bone_keyframe(bone, aim_frame, "KEYFRAME")
                        bones_list[bone.name][4] = aim_frame  # 记录结束关键帧位置'''

    def create_auto_offset_keyframe(self, armature: bpy.types.Object, bones_list: dict, action, frame: int, s_o_e: str = "None"):
        poses = action.action
        offset_weight = action.offset_weight

        for bone in armature.pose.bones:
            if bone.name in bones_list.keys():
                index = bones_list[bone.name][0]
                frame_offset = int(bones_list[bone.name][2] * bones_list[bone.name][1] * offset_weight)
                # 应用姿态
                for pose in poses:
                    if pose.bone_name == bone.name:
                        matrix = pose.pose
                        bone.matrix_basis = matrix
                # 插入关键帧
                if frame_offset > 0:
                    keyframe_type = "JITTER"
                else:
                    keyframe_type = "KEYFRAME"
                self.insert_selected_bone_keyframe(bone, frame + frame_offset, keyframe_type)
                # 记录起始关键帧位置
                if s_o_e == 'start':
                    bones_list[bone.name][3] = frame + frame_offset
                    armature.cmc_auto_offset_animation_pose[index].start_pose = [v for col in bone.matrix_basis.transposed() for v in col]
                elif s_o_e == 'end':
                    bones_list[bone.name][4] = frame + frame_offset
                    armature.cmc_auto_offset_animation_pose[index].end_pose = [v for col in bone.matrix_basis.transposed() for v in col]

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != 'POSE':
            return False
        armature = context.active_object
        if armature is None or armature.type != 'ARMATURE':
            return False
        if len(armature.cmc_auto_offset_animation_pose) == 0:
            return False
        if len(armature.cmc_auto_offset_animation_intermediate_action) < 2:
            return False
        return True

    def execute(self, context: bpy.types.Context):
        armature = context.active_object
        # 获取设置
        frame_length = armature.cmc_auto_offset_animation_settings[0].frame_length    # 帧长度
        average_frame_length = armature.cmc_auto_offset_animation_settings[0].use_average_frame_length  # 平均帧长度
        keyframe_offset = armature.cmc_auto_offset_animation_settings[0].keyframe_offset    # 是否对关键帧进行偏移
        uniform_offset = armature.cmc_auto_offset_animation_settings[0].uniform_offset    # 是否统一对所有骨骼进行关键帧偏移
        uniform_offset_value = armature.cmc_auto_offset_animation_settings[0].uniform_offset_value    # 统一偏移值
        use_anticipation_pose = armature.cmc_auto_offset_animation_settings[0].use_anticipation_pose    # 是否使用预备姿态
        anticipation_pose_offset = armature.cmc_auto_offset_animation_settings[0].anticipation_pose_offset    # 预备姿态偏移
        anticipation_pose_intensity = armature.cmc_auto_offset_animation_settings[0].anticipation_pose_intensity    # 预备姿态强度
        use_recover_pose = armature.cmc_auto_offset_animation_settings[0].use_recover_pose      # 是否使用收尾姿态
        recover_pose_offset = armature.cmc_auto_offset_animation_settings[0].recover_pose_offset    # 收尾姿态偏移
        recover_pose_intensity = armature.cmc_auto_offset_animation_settings[0].recover_pose_intensity    # 收尾姿态强度

        # 验证帧长度设置
        if average_frame_length:
            # 验证评价帧长大于起始和结束姿态帧长
            if frame_length <= (anticipation_pose_offset * use_anticipation_pose):
                self.report({'ERROR'}, "Frame length must be greater than anticipation pose offsets!")
                return {'CANCELLED'}
            if frame_length <= (recover_pose_offset * use_recover_pose):
                self.report({'ERROR'}, "Frame length must be greater than postponement pose offsets!")
                return {'CANCELLED'}
            if frame_length <= uniform_offset_value * uniform_offset:
                self.report({'ERROR'}, "Frame length must be greater than uniform offset value!")
                return {'CANCELLED'}
        else:
            if armature.cmc_auto_offset_animation_intermediate_action[0].frame_length <= (anticipation_pose_offset * use_anticipation_pose) or armature.cmc_auto_offset_animation_intermediate_action[-2].frame_length < (recover_pose_offset * use_recover_pose):
                self.report({'ERROR'}, "Frame length must be greater than anticipation pose offset and postponement pose offset!")
                return {'CANCELLED'}

        # 骨骼列表，并记录优先级、起始和结束关键帧位置
        bones_list = {}
        max_priority = 0
        for i, bone in enumerate(armature.cmc_auto_offset_animation_pose):
            if keyframe_offset and not uniform_offset:
                bones_list[bone.bone_name] = [i, 1, bone.frame_offset, 0, 0]  # [index, priority, frame_offset, start_frame, end_frame]
            elif keyframe_offset and uniform_offset:
                bones_list[bone.bone_name] = [i, bone.priority, uniform_offset_value, 0, 0]
                if bone.priority > max_priority:
                    max_priority = bone.priority
            else:
                bones_list[bone.bone_name] = [i, 0, 0, 0, 0]

        if len(bones_list) == 0:
            self.report({'INFO'}, "No bone selected!")
            return {'CANCELLED'}

        # 获取帧信息
        current_frame = context.scene.frame_current

        # 遍历姿态列表
        for i, action in enumerate(armature.cmc_auto_offset_animation_intermediate_action):

            # 创建动作
            if i == 0:
                self.create_auto_offset_keyframe(armature, bones_list, action, current_frame, "start")
            elif action == armature.cmc_auto_offset_animation_intermediate_action[-1]:
                self.create_auto_offset_keyframe(armature, bones_list, action, current_frame, "end")
            else:
                self.create_auto_offset_keyframe(armature, bones_list, action, current_frame)

            # 更新下一关键帧位置
            if average_frame_length:
                current_frame += frame_length
            else:
                current_frame += action.frame_length

        # 创建预备姿态
        if use_anticipation_pose:
            for bone in armature.pose.bones:
                if bone.name in bones_list.keys():
                    index = bones_list[bone.name][0]
                    if armature.cmc_auto_offset_animation_pose[index].anticipation_pose_mode != 'NONE':
                        if armature.cmc_auto_offset_animation_pose[index].anticipation_pose_mode == 'CUSTOM' and armature.cmc_auto_offset_animation_pose[index].have_anticipation_pose:
                            # 应用自定义预备姿态
                            matrix = armature.cmc_auto_offset_animation_pose[index].anticipation_pose
                            bone.matrix_basis = matrix
                        else:
                            # 应用预备姿态
                            matrix = armature.cmc_auto_offset_animation_pose[index].start_pose
                            bone.matrix_basis = matrix
                        # 插入关键帧
                        self.insert_selected_bone_keyframe(bone, bones_list[bone.name][3] + anticipation_pose_offset, "EXTREME")

        # 创建收尾姿态
        if use_recover_pose:
            for bone in armature.pose.bones:
                if bone.name in bones_list.keys():
                    index = bones_list[bone.name][0]
                    if armature.cmc_auto_offset_animation_pose[index].recover_pose_mode != 'NONE':
                        if armature.cmc_auto_offset_animation_pose[index].recover_pose_mode == 'CUSTOM' and armature.cmc_auto_offset_animation_pose[index].have_recover_pose:
                            # 应用自定义收尾姿态
                            matrix = armature.cmc_auto_offset_animation_pose[index].recover_pose
                            bone.matrix_basis = matrix
                        else:
                            # 应用收尾姿态
                            matrix = armature.cmc_auto_offset_animation_pose[index].end_pose
                            bone.matrix_basis = matrix
                        # 插入关键帧
                        self.insert_selected_bone_keyframe(bone, bones_list[bone.name][4] - recover_pose_offset, "EXTREME")

        # 自动创建预备姿态
        if use_anticipation_pose:
            # 修改预备姿态
            for bone in armature.pose.bones:
                if bone.name in bones_list.keys():
                    index = bones_list[bone.name][0]
                    #if armature.cmc_auto_offset_animation_pose[index].have_start_pose:
                    # 跳转至预备帧
                    context.scene.frame_set(bones_list[bone.name][3] + anticipation_pose_offset)
                    # 清空选中骨骼
                    bpy.ops.pose.select_all(action='DESELECT')
                    # 选中当前骨骼
                    armature.data.bones.active = bone.bone
                    if armature.cmc_auto_offset_animation_pose[index].anticipation_pose_mode == 'AUTO':
                        prev_frame = bones_list[bone.name][3]
                        next_frame = armature.cmc_auto_offset_animation_intermediate_action[0].frame_length + bones_list[bone.name][3]
                        if anticipation_pose_intensity >= 0:
                            # 推移姿态
                            bpy.ops.pose.push(factor = anticipation_pose_intensity/100, prev_frame = prev_frame, next_frame = next_frame)
                        else:
                            # 松弛姿态
                            bpy.ops.pose.relax(factor = -anticipation_pose_intensity/100, prev_frame = prev_frame, next_frame = next_frame)
                        # 插入关键帧
                        self.insert_selected_bone_keyframe(bone, bones_list[bone.name][3] + anticipation_pose_offset, "EXTREME")

        # 自动创建收尾姿态
        if use_recover_pose:
            # 修改首位姿态
            for bone in armature.pose.bones:
                if bone.name in bones_list.keys():
                    index = bones_list[bone.name][0]
                    #if armature.cmc_auto_offset_animation_pose[index].have_end_pose:
                    # 跳转至收尾帧
                    context.scene.frame_set(bones_list[bone.name][4] - recover_pose_offset)
                    # 清空选中骨骼
                    bpy.ops.pose.select_all(action='DESELECT')
                    # 选中当前骨骼
                    armature.data.bones.active = bone.bone
                    if armature.cmc_auto_offset_animation_pose[index].recover_pose_mode == 'AUTO':
                        prev_frame = bones_list[bone.name][4] - armature.cmc_auto_offset_animation_intermediate_action[-2].frame_length
                        next_frame = bones_list[bone.name][4]
                        if recover_pose_intensity >= 0:
                            # 推移姿态
                            bpy.ops.pose.push(factor = recover_pose_intensity/100, prev_frame = prev_frame, next_frame = next_frame)
                        else:
                            # 松弛姿态
                            bpy.ops.pose.relax(factor = -recover_pose_intensity/100, prev_frame = prev_frame, next_frame = next_frame)
                        # 插入关键帧
                        print(bones_list[bone.name][3], anticipation_pose_offset, bones_list[bone.name][4])
                        self.insert_selected_bone_keyframe(bone, bones_list[bone.name][4] - recover_pose_offset, "EXTREME")

        # 跳转至结束帧
        context.scene.frame_set(current_frame)

        if frame_length <= uniform_offset_value * uniform_offset * max_priority:
            self.report({'WARNING'}, "Animation created! But the offset is to long that the animations may not be as expected.")
        else:
            self.report({'INFO'}, "Animation created successfully!")
        return {'FINISHED'}



#*****************************************************
#*****************************************************
#******************** 自动错帧预设 ********************
#*****************************************************
#*****************************************************
# 添加预设
class CHESTNUTMC_OT_Add_AutoOffset_Preset(bpy.types.Operator):
    bl_idname = "cmc.add_auto_offset_preset"
    bl_label = "Add Auto Offset Preset"
    bl_description = "Add a new preset for auto offset animation"
    bl_options = {'REGISTER', 'UNDO'}

    preset_name: bpy.props.StringProperty(name="Preset Name", default="New Preset") # type: ignore

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != 'POSE':
            return False
        return True

    def invoke(self, context, event):
        # 弹出对话框
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context: bpy.types.Context):
        addon_prefs = context.preferences.addons[__addon_name__].preferences
        presets_path = addon_prefs.auto_offset_animation_presets_path
        filepath = os.path.join(presets_path, f"{self.preset_name}.json")

        # 验证路径是否存在
        if not os.path.exists(presets_path):
            os.makedirs(presets_path)
        if os.path.exists(filepath):
            self.report({"ERROR"}, f"Preset '{self.preset_name}' already exists!")
            return {'CANCELLED'}

        preset = {"confirmation": "ChestnutMC_AOA_Preset", "bones": {}, "settings": {}}

        armature = context.active_object
        if armature.type != "ARMATURE":
            self.report({"ERROR"}, "Active object must be an armature!")
            return {'CANCELLED'}

        if len(armature.cmc_auto_offset_animation_pose) > 0:
            for i, bone in enumerate(armature.cmc_auto_offset_animation_pose):
                preset['bones'][i] = get_auto_offset_animation_bone_parameters(armature, '', i)
        else:
            preset['bones'] = {}

        if len(armature.cmc_auto_offset_animation_settings) > 0:
            preset['settings']['frame_length'] = armature.cmc_auto_offset_animation_settings[0].frame_length
            preset["settings"]['use_average_frame_length'] = armature.cmc_auto_offset_animation_settings[0].use_average_frame_length
            preset['settings']['keyframe_offset'] = armature.cmc_auto_offset_animation_settings[0].keyframe_offset
            preset['settings']['uniform_offset'] = armature.cmc_auto_offset_animation_settings[0].uniform_offset
            preset['settings']['uniform_offset_value'] = armature.cmc_auto_offset_animation_settings[0].uniform_offset_value
            preset['settings']['use_anticipation_pose'] = armature.cmc_auto_offset_animation_settings[0].use_anticipation_pose
            preset['settings']['anticipation_pose_offset'] = armature.cmc_auto_offset_animation_settings[0].anticipation_pose_offset
            preset['settings']['anticipation_pose_intensity'] = armature.cmc_auto_offset_animation_settings[0].anticipation_pose_intensity
            preset['settings']['use_recover_pose'] = armature.cmc_auto_offset_animation_settings[0].use_recover_pose
            preset['settings']['recover_pose_offset'] = armature.cmc_auto_offset_animation_settings[0].recover_pose_offset
            preset['settings']['recover_pose_intensity'] = armature.cmc_auto_offset_animation_settings[0].recover_pose_intensity
        else:
            preset['settings'] = {}

        # 创建json文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(preset, f, ensure_ascii=False, indent=4)

        self.report({'INFO'}, f"Preset '{self.preset_name}' added successfully!")
        return {'FINISHED'}


# 删除预设
class CHESTNUTMC_OT_Delete_AutoOffset_Preset(bpy.types.Operator):
    bl_idname = "cmc.delete_auto_offset_preset"
    bl_label = "Delete Auto Offset Animation Preset"
    bl_description = "Delete Auto Offset Animation Preset"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.scene.cmc_auto_offset_animation_presets:
            return True
        return False

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event, title='Delete Auto Offset Animation Preset?')

    def execute(self, context):
        addon_prefs = context.preferences.addons[__addon_name__].preferences
        preset_path = os.path.join(addon_prefs.auto_offset_animation_presets_path, context.scene.cmc_auto_offset_animation_presets)

        if os.path.exists(preset_path):
            os.remove(preset_path)
        else:
            self.report({'ERROR'}, "Preset not found!")
            return {'CANCELED'}

        self.report({'INFO'}, "Preset removed!")
        return {'FINISHED'}


# 重命名预设
class CHESTNUTMC_OT_Rename_AutoOffset_Preset(bpy.types.Operator):
    bl_idname = "cmc.rename_auto_offset_preset"
    bl_label = "Rename Auto Offset Preset"
    bl_description = "Rename Auto Offset Preset"
    bl_options = {'REGISTER', 'UNDO'}

    new_name: StringProperty(name="New Name") # type: ignore

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.scene.cmc_auto_offset_animation_presets:
            return True
        return False

    def invoke(self, context, event):
        # 弹出对话框
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        addon_prefs = context.preferences.addons[__addon_name__].preferences
        origin_preset_path = os.path.join(addon_prefs.auto_offset_animation_presets_path, context.scene.cmc_auto_offset_animation_presets)
        new_preset_path = os.path.join(addon_prefs.auto_offset_animation_presets_path, self.new_name + ".json")

        # 验证重名项
        if os.path.exists(new_preset_path):
            self.report({'ERROR'}, "Preset already exists! Please choose another name!")
            return {'CANCELLED'}

        if os.path.exists(origin_preset_path):
            # 重命名文件
            try:
                os.rename(origin_preset_path, new_preset_path)
                self.report({'INFO'}, "Rename Success")
            except Exception as e:
                self.report({'ERROR'}, str(e))

        self.report({'INFO'}, "Rename Success!")
        return {'FINISHED'}


# 导入预设
class CHESTNUTMC_OT_Import_AutoOffset_Preset(bpy.types.Operator):
    bl_idname = "cmc.import_auto_offset_preset"
    bl_label = "Import Preset"
    bl_description = "Import preset from a file"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH") # type: ignore

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        addon_prefs = context.preferences.addons[__addon_name__].preferences
        presets_path = addon_prefs.auto_offset_animation_presets_path
        file_name = os.path.splitext(os.path.basename(self.filepath))[0]
        destination_path = os.path.join(presets_path, file_name + ".json")
        print(self.filepath)

        # 验证路径是否存在
        if not os.path.exists(self.filepath):
            self.report({'ERROR'}, "Invalid file path: {}".format(self.filepath))
            return {'CANCELLED'}

        # 验证预设合法性
        with open(self.filepath, 'r') as f:
            try:
                preset = json.load(f)
            except Exception as e:
                self.report({'ERROR'}, "Fail to load preset json: {}".format(str(e)))
                return {'CANCELLED'}

            try:
                confirmation = preset['confirmation']
                if confirmation != "ChestnutMC_AOA_Preset":
                    self.report({'ERROR'}, "Invalid preset!")
                    return {'CANCELLED'}
            except:
                self.report({'ERROR'}, "Invalid preset!")
                return {'CANCELLED'}

        # 验证是否有重名项
        rename = 1
        while True:
            if os.path.exists(destination_path):
                new_name = file_name + "_" + str(rename)
                destination_path = os.path.join(presets_path, new_name + ".json")
                rename += 1
            else:
                break

        # 复制文件
        shutil.copy2(self.filepath, destination_path)

        self.report({'INFO'}, "Preset {} import successfully!".format(file_name))
        return {'FINISHED'}


# 加载预设
class CHESTNUTMC_OT_Load_AutoOffset_Preset(bpy.types.Operator):
    bl_idname = "cmc.load_auto_offset_preset"
    bl_label = "Load Auto Offset Preset"
    bl_description = "Load a preset for auto offset animation"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != 'POSE':
            return False
        if context.scene.cmc_auto_offset_animation_presets:
            return True
        return False

    def execute(self, context):
        addon_prefs = context.preferences.addons[__addon_name__].preferences
        preset_name = context.scene.cmc_auto_offset_animation_presets
        preset_path = os.path.join(addon_prefs.auto_offset_animation_presets_path, preset_name)
        armature = context.active_object
        if armature.type != 'ARMATURE':
            self.report({'ERROR'}, "Selected object is not an armature")
            return {'CANCELLED'}

        # 清除原骨骼列表
        armature.cmc_auto_offset_animation_pose.clear()
        armature.cmc_auto_offset_animation_pose_index = 0

        with open(preset_path, 'r') as f:
            try:
                preset = json.load(f)
            except Exception as e:
                self.report({'ERROR'}, "Fail to load preset json: {}".format(str(e)))
                return {'CANCELLED'}

            # 验证预设合法性
            try:
                confirmation = preset['confirmation']
                if confirmation != "ChestnutMC_AOA_Preset":
                    self.report({'ERROR'}, "Invalid preset!")
                    return {'CANCELLED'}
            except:
                self.report({'ERROR'}, "Invalid preset!")
                return {'CANCELLED'}

            for bone_name, bone_parameters in preset['bones'].items():
                bone = armature.data.bones.get(bone_parameters['bone_name'])
                if bone is not None:
                    pose = armature.cmc_auto_offset_animation_pose.add()
                    pose.bone_name = bone_parameters['bone_name']
                    pose.priority = bone_parameters['priority']
                    pose.frame_offset = bone_parameters['frame_offset']
                    pose.anticipation_pose_mode = bone_parameters['anticipation_pose_mode']
                    pose.recover_pose_mode = bone_parameters['recover_pose_mode']
                else:
                    self.report({'WARNING'}, "Bone " + bone_parameters['bone_name'] + " not found, skipping")
                    continue

            if len(armature.cmc_auto_offset_animation_settings) == 0:
                armature.cmc_auto_offset_animation_settings.add()

            armature.cmc_auto_offset_animation_settings[0].frame_length = preset['settings']['frame_length']
            armature.cmc_auto_offset_animation_settings[0].use_average_frame_length = preset['settings']['use_average_frame_length']
            armature.cmc_auto_offset_animation_settings[0].keyframe_offset = preset['settings']['keyframe_offset']
            armature.cmc_auto_offset_animation_settings[0].uniform_offset = preset['settings']['uniform_offset']
            armature.cmc_auto_offset_animation_settings[0].uniform_offset_value = preset['settings']['uniform_offset_value']
            armature.cmc_auto_offset_animation_settings[0].use_anticipation_pose = preset['settings']['use_anticipation_pose']
            armature.cmc_auto_offset_animation_settings[0].anticipation_pose_offset = preset['settings']['anticipation_pose_offset']
            armature.cmc_auto_offset_animation_settings[0].anticipation_pose_intensity = preset['settings']['anticipation_pose_intensity']
            armature.cmc_auto_offset_animation_settings[0].use_recover_pose = preset['settings']['use_recover_pose']
            armature.cmc_auto_offset_animation_settings[0].recover_pose_offset = preset['settings']['recover_pose_offset']
            armature.cmc_auto_offset_animation_settings[0].recover_pose_intensity = preset['settings']['recover_pose_intensity']

        self.report({ 'INFO' }, "Loaded preset: " + preset_name)
        return {'FINISHED'}

