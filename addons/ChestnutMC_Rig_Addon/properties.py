import os

import bpy
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty, PointerProperty, CollectionProperty, FloatVectorProperty, FloatProperty
from .panels.UI import *


#******************** 人模导入属性 ********************
class CMC_RigListItem(bpy.types.PropertyGroup):
    name: StringProperty(name="Name") # type: ignore
    path: StringProperty(name="Rig Asset", subtype="FILE_PATH") # type: ignore
    preview: StringProperty(name="Preview", subtype="FILE_PATH") # type: ignore
    collection: StringProperty(name="Collection", default="") # type: ignore

class CMC_RigPresetItem(bpy.types.PropertyGroup):
    name: StringProperty(name="Name") # type: ignore
    enabled: BoolProperty(name="Enabled", default=False) # type: ignore


#******************** 预设属性 ********************
class CMC_SkinListItem(bpy.types.PropertyGroup):
    name: StringProperty(name="Name") # type: ignore
    path: StringProperty(name="Path") # type: ignore
    have_preset: BoolProperty(name="Have Preset", default=False) # type: ignore


#******************** 自动错帧属性 ********************
# 中间姿态存储单元
class CMC_AutoOffsetAnimation_IntermediateActionItem(bpy.types.PropertyGroup):
    bone_name: StringProperty(name="Name") # type: ignore
    pose: FloatVectorProperty(name="Pose", subtype="MATRIX", size=16, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore

# 自动错帧骨骼数据
class CMC_AutoOffsetAnimationItem(bpy.types.PropertyGroup):
    bone_name: StringProperty(name="Name", options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    priority: IntProperty(name="Priority", default=0, min=0, max=16, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    frame_offset: IntProperty(name="Frame Offset", default=0, soft_min=0, soft_max=20, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    start_pose: FloatVectorProperty(name="Start Matrix", subtype="MATRIX", size=16, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    have_start_pose: BoolProperty(name="Have Start Pose", default=False, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    end_pose: FloatVectorProperty(name="End Matrix", subtype="MATRIX", size=16, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    have_end_pose: BoolProperty(name="Have End Pose", default=False, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    intermediate_pose: FloatVectorProperty(name="Intermediate Matrix", subtype="MATRIX", size=16, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    meum_expand: BoolProperty(name="Meum Expand", default=False, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    anticipation_pose: FloatVectorProperty(name="Anticipation Matrix", subtype="MATRIX", size=16, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    anticipation_pose_mode: EnumProperty(
        name="Anticipation Pose Mode",
        items=[
            ("AUTO", "Auto", "Auto generate anticipation pose"),
            ("CUSTOM", "Custom", "Use custom anticipation pose"),
            ("NONE", "None", "No anticipation pose"),
        ],
        default="AUTO",
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}
    ) # type: ignore
    have_anticipation_pose: BoolProperty(name="Have Anticipation Pose", default=False, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    recover_pose: FloatVectorProperty(name="Recover Matrix", subtype="MATRIX", size=16, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    recover_pose_mode: EnumProperty(
        name="Postponement Pose Mode",
        items=[
            ("AUTO", "Auto", "Auto generate recover pose"),
            ("CUSTOM", "Custom", "Use custom recover pose"),
            ("NONE", "None", "No recover pose")
        ],
        default="AUTO",
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}
        )   # type: ignore
    have_recover_pose: BoolProperty(name="Have Postponement Pose", default=False, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore

# 中间姿态
class CMC_AutoOffsetAnimation_IntermediateAction(bpy.types.PropertyGroup):
    action_name: StringProperty(name="Name", options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    action: CollectionProperty(type=CMC_AutoOffsetAnimation_IntermediateActionItem, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    pose_frame: IntProperty(name="Pose Frame", default=0, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    frame_length: IntProperty(name="Action Length", default=1, min=1, soft_max=20, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    offset_weight: FloatProperty(name="Offset Weight", default=1, soft_min=-2, soft_max=2, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    meum_expand: BoolProperty(name="Meum Expand", default=False, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore

# 自动错帧设置
class CMC_AutoOffsetAnimationSettings(bpy.types.PropertyGroup):
    frame_length: IntProperty(name="Frame Length", default=10, min=1, soft_max=100, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    use_average_frame_length: BoolProperty(name="Use Average Frame Length", default=False, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    keyframe_offset: BoolProperty(name="Keyframe Offset", default=False, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    uniform_offset: BoolProperty(name="Uniform Offset", default=False, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    uniform_offset_value: IntProperty(name="Uniform Offset Value", default=1, soft_min=-10, soft_max=10, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    use_anticipation_pose: BoolProperty(name="Anticipation Pose", default=False, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    anticipation_pose_offset: IntProperty(name="Anticipation Pose Offset", default=4, soft_min=-10, soft_max=10, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    anticipation_pose_intensity: IntProperty(name="Anticipation Pose Intension", default=50, min=-100, max=100, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    use_recover_pose: BoolProperty(name="Postponement Pose", default=False, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    recover_pose_offset: IntProperty(name="Postponement Pose Offset", default=4, soft_min=-10, soft_max=10, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    recover_pose_intensity: IntProperty(name="Postponement Pose Intension", default=50, min=-100, max=100, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    anticipation_advance_expand: BoolProperty(name="Anticipation Advance", default=False, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    recover_advance_expand: BoolProperty(name="Recover Advance", default=False, options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'}) # type: ignore

# 自动错帧预设
class CMC_AutoOffsetAnimationPresetItem(bpy.types.PropertyGroup):
    name: StringProperty(name="Name") # type: ignore
    path: StringProperty(name="Path", subtype="FILE_PATH") # type: ignore