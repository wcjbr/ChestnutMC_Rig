import bpy
import os
from ..config import __addon_name__

from .ImageManager import skin_previews, Load_skin_previews


# 皮肤列表绘制
class CMC_UL_Skin_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # 获取当前的皮肤列表
        skin_collection = getattr(data, "cmc_skin_list", [])

        if index >= len(skin_collection):
            return

        skin = skin_collection[index]

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            # 验证skin是否有预览图
            if skin.name in skin_previews:
                row.prop(skin, "name", text="", emboss=False, icon_value=skin_previews[skin_collection[index].name].icon_id)  # 加载名称和图标
            else:
                Load_skin_previews()
            if skin.have_preset:
                row.label(icon='CHECKMARK')

        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=skin.preview)


# 自动错帧骨骼绘制
class CMC_UL_AutoOffsetList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # 获取当前的骨骼列表
        bone_collection = getattr(data, "cmc_auto_offset_animation_pose", [])

        if index >= len(bone_collection):
            return

        bone = bone_collection[index]

        try:
            priority_active = context.object.cmc_auto_offset_animation_settings[0].keyframe_offset and context.object.cmc_auto_offset_animation_settings[0].uniform_offset
            frame_offset_active = context.object.cmc_auto_offset_animation_settings[0].keyframe_offset and (not context.object.cmc_auto_offset_animation_settings[0].uniform_offset)
        except Exception as e:
            priority_active = False
            frame_offset_active = False
            print(e)

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            bcolumn = layout.column(align=True)
            row = bcolumn.row(align=True)
            if context.object.cmc_auto_offset_animation_pose[context.object.cmc_auto_offset_animation_pose_index].bone_name == bone.bone_name:
                row.operator("cmc.select_bone_inlist", text=bone.bone_name, icon="RESTRICT_SELECT_OFF", depress=True)
            else:
                row.label(text=bone.bone_name, icon="BONE_DATA")
            column = row.column(align=True)
            column.active = priority_active
            column.prop(bone, "priority", text="priority")
            column = row.column(align=True)
            column.active = frame_offset_active
            column.prop(bone, "frame_offset", text="frame offset")
            # 高级面板
            if bone.meum_expand:
                nrow = bcolumn.row()
                nrow.alignment = 'RIGHT'
                ncolumn = nrow.column()
                ncolumn.scale_x=1.5

                nrow = ncolumn.row()
                nrow.alignment = 'RIGHT'
                nrow.label(text="Anticipation Pose:")
                nrow.prop(bone, "anticipation_pose_mode", text="")

                nrow = ncolumn.row()
                nrow.alignment = 'RIGHT'
                nrow.label(text="Recover Pose:")
                nrow.prop(bone, "recover_pose_mode", text="")
            # 面板展开与收起
            row.prop(bone, "meum_expand",
                    icon="DISCLOSURE_TRI_DOWN" if bone.meum_expand else "DISCLOSURE_TRI_RIGHT",
                    text="",
                    emboss=True)

        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'


# 自动错帧骨骼列表菜单
class CMC_MT_AutoOffsetListMenu(bpy.types.Menu):
    bl_label = "Auto Offset Animation Pose List Menu"
    bl_idname = "CMC_MT_auto_offset_list_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("cmc.delete_all_bones_inlist", icon="TRASH")
        layout.operator("cmc.select_all_bones_inlist", icon="RESTRICT_SELECT_OFF")
        layout.separator()
        layout.operator("cmc.change_anticipation_pose_mode")
        layout.operator("cmc.change_recover_pose_mode")


# 自动错帧中间动作存储列表绘制
class CMC_UL_AutoOffset_IntermediateActionList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # 获取当前的骨骼列表
        action_collection = getattr(data, "cmc_auto_offset_animation_intermediate_action", [])

        if index >= len(action_collection):
            return

        action = action_collection[index]

        length_active = True
        try:
            if context.object.cmc_auto_offset_animation_settings[0].use_average_frame_length:
                length_active = False
        except:
            pass


        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            bcolumn = layout.column(align=True)
            row = bcolumn.row(align=True)
            if len(context.object.cmc_auto_offset_animation_intermediate_action[index].action) != len(context.object.cmc_auto_offset_animation_pose):
                row.label(text="", icon='ERROR')
            column = row.column(align=True)
            column.scale_x = 1.2
            column.prop(action, "action_name", text=f"Action: {index}", emboss=False)
            column = row.column(align=True)
            column.active = length_active
            column.prop(action, "frame_length", text="Action Length")
            # 高级面板
            if action.meum_expand:
                nrow = bcolumn.row()
                nrow.alignment = 'RIGHT'
                ncolumn = nrow.column()
                ncolumn.scale_x=1.5

                nrow = ncolumn.row()
                nrow.alignment = 'RIGHT'
                nrow.label(text="Offset Weight")
                nrow.prop(action, "offset_weight", text="")
            # 面板展开与收起
            row.prop(action, "meum_expand",
                    icon="DISCLOSURE_TRI_DOWN" if action.meum_expand else "DISCLOSURE_TRI_RIGHT",
                    text="",
                    emboss=True)

        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
