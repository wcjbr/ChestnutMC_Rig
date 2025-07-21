import bpy

from ..config import __addon_name__
from ..operators.AddonOperators import *
from ..operators.ActionOperators import *
from ....common.i18n.i18n import i18n
from ....common.types.framework import reg_order
from .UI import *
from .RigParameters import *


class BasePanel(object):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ChestnutMC"

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return True


# 导入面板
@reg_order(0)
class ImportPanel(BasePanel, bpy.types.Panel):
    bl_label = "ChestnutMC Import panel"
    bl_idname = "CHESTNUTMC_PT_ImportPanel"

    def draw(self, context: bpy.types.Context):
        addon_prefs = context.preferences.addons[__addon_name__].preferences

        layout = self.layout
        scene = context.scene

        row = layout.row()
        if CHESTNUTMC_OT_RigImportOperator.poll(context):
            row.label(text="Libraries loaded")
            row.operator(CHESTNUTMC_OT_LoadLibraryOperator.bl_idname, text="Reload Libraries", icon="FILE_REFRESH")
        else:
            row.label(icon="INFO", text="Please load libraries first")
            row.operator(CHESTNUTMC_OT_LoadLibraryOperator.bl_idname, text="Load Libraries")
        layout.separator()

        layout.prop(addon_prefs, "using_mode", text="Mode")
        # layout.props_enum(addon_prefs, "rig_preset")
        # layout.template_list("UI_UL_list","",addon_prefs,"Rig_assets_List",addon_prefs,"Rig_assets_List_index",rows=1,)

        # 预览面板
        row = layout.row()
        row.template_icon_view(scene, "cmc_rig_previews")
        row = layout.row()
        row.prop(scene, "cmc_rig_previews", text='Select Rig')

        # 操作按钮行
        layout.operator(CHESTNUTMC_OT_RigImportOperator.bl_idname, icon="IMPORT")
        row = layout.row()
        colum = row.column()
        colum.operator(CHESTNUTMC_OT_RigSave.bl_idname, icon="FILE_NEW")
        colum.operator(CHESTNUTMC_OT_RigDelete.bl_idname, icon="TRASH")
        colum = row.column()
        colum.operator(CHESTNUTMC_OT_UpdateRigPreview.bl_idname, icon="FILE_REFRESH")
        colum.operator(CMC_OT_RigRename.bl_idname, icon="FILE_TICK")
        layout.separator()

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != "OBJECT":
            return False
        return True

# 皮肤面板
@reg_order(1)
class SkinSwapperPanel(BasePanel, bpy.types.Panel):
    bl_label = "ChestnutMC Skin Swapper"
    bl_idname = "CHESTNUTMC_PT_SkinSwapperPanel"

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        addon_prefs = context.preferences.addons[__addon_name__].preferences

        scene = context.scene

        # 列表模板
        layout.label(text="Select Skin")
        row = layout.row()
        row.template_list(
            "CMC_UL_Skin_List",  # 列表类型
            "cmc_skin_list",    # 唯一标识符
            scene,         # 数据源
            "cmc_skin_list",    # 集合属性
            scene,
            "cmc_skin_list_index"   # 活动项索引
        )

        column = row.column(align=True,)
        column.scale_x  = 0.7
        column.operator(CHESTNUTMC_OT_SkinAdd.bl_idname, text="Add", icon='ADD')
        column.operator(CHESTNUTMC_OT_SkinRemove.bl_idname, text="Remove", icon='REMOVE')
        column.separator()
        column.operator(CHESTNUTMC_OT_SkinRename.bl_idname, text="Rename", icon='FILE_TICK')
        if not scene.cmc_skin_list_index >= len(scene.cmc_skin_list):
            column.template_icon(icon_value=skin_previews[scene.cmc_skin_list[scene.cmc_skin_list_index].name].icon_id, scale=4.0)
        layout.operator(CHESTNUTMC_OT_SkinApply.bl_idname, text="Apply Skin", icon='CHECKMARK')
        row = layout.row()
        row.operator(CHESTNUTMC_OT_SaveFace2Skin.bl_idname, text="Save Face to Skin", icon='FILE_NEW')
        row.operator(CHESTNUTMC_OT_DeleteFace2Skin.bl_idname, text="Delete Face from Skin", icon='TRASH')

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != "OBJECT":
            return False
        return True


# 参数面板
@reg_order(2)
class RigPropertiesPanel(BasePanel, bpy.types.Panel):
    bl_label = "ChestnutMC Rig Properties Panel"
    bl_idname = "CHESTNUTMC_PT_RigPropertiesPanel"

    def draw(self, context: bpy.types.Context):
        layout = self.layout

        # 骨骼参数绘制面板
        # 验证活动物体为骨骼
        armature = None
        if context.active_object and context.active_object.type != "ARMATURE":
            if context.active_object.parent is not None and context.active_object.parent.type == "ARMATURE":
                for child in context.active_object.parent.children:
                    if child.name.startswith("preview"):
                        armature = context.active_object.parent
        elif context.active_object and context.active_object.type == "ARMATURE":
            if context.active_object.children:
                for child in context.active_object.children:
                    if child.name.startswith("preview"):
                        armature = context.active_object
        if armature is not None:
            box  = layout.box()
            get_rig_parameters(box, context, "meum.body.setting")
            box  = layout.box()
            get_rig_parameters(box, context, "meum.face.mouth.setting")
            box  = layout.box()
            row = box.row()
            Lbox = row.box()
            get_rig_parameters(Lbox, context, "meum.arm.setting.R")
            Rbox  = row.box()
            get_rig_parameters(Rbox, context, "meum.arm.setting.L")
            row = box.row()
            Lbox = row.box()
            get_rig_parameters(Lbox, context, "meum.leg.setting.R")
            Rbox  = row.box()
            get_rig_parameters(Rbox, context, "meum.leg.setting.L")

            # 材质参数绘制面板
            box = layout.box()
            get_face_parameters(box, context, "Mouth")
            box = layout.box()
            get_face_parameters(box, context, "Face")
            box = layout.box()
            get_face_parameters(box, context, "Skin")
            box = layout.box()
            get_face_parameters(box, context, "EdgeLight")

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != "OBJECT" and context.mode != 'POSE':
            return False
        return True


# 动作管理面板
@reg_order(4)
class ActionManagerPanel(BasePanel, bpy.types.Panel):
    bl_label = "ChestnutMC Action Manager Panel"
    bl_idname = "CHESTNUTMC_PT_ActionManagerPanel"

    def draw(self, context: bpy.types.Context):
        Object = context.object
        layout = self.layout
        # 面板展开与收起
        box = layout.box()
        row = box.row()
        row.prop(context.scene, "cmc_auto_offset_animation_expand",
                    icon="TRIA_DOWN" if context.scene.cmc_auto_offset_animation_expand else "TRIA_RIGHT",
                    text="",
                    emboss=True)
        row.label(text="Auto Offset Animation Setting", icon="ANIM")
        # 面板展开与收起
        if context.scene.cmc_auto_offset_animation_expand:

            # 预设部分
            nbox = box.box()
            row = nbox.row()
            row.operator("cmc.add_auto_offset_preset", text="Add Preset", icon='ADD')
            row.operator("cmc.delete_auto_offset_preset", text="Delete Preset", icon='X')
            row.operator("cmc.rename_auto_offset_preset", text="Rename Preset", icon='FILE_TICK')
            row.operator("cmc.import_auto_offset_preset", text="Import Preset", icon='IMPORT')
            row = nbox.row()
            row.prop(context.scene, "cmc_auto_offset_animation_presets", text="Preset")
            row.operator("cmc.load_auto_offset_preset", text="Load Preset", icon='CHECKMARK')
            box.separator()

            # 骨骼列表绘制
            box = box.box()
            box.label(text="Bone List", icon="BONE_DATA")
            row = box.row()
            row.template_list(
                "CMC_UL_AutoOffsetList",  # 列表类型
                "cmc_auto_offset_animation_pose",    # 唯一标识符
                Object,         # 数据源
                "cmc_auto_offset_animation_pose",    # 集合属性
                Object,
                "cmc_auto_offset_animation_pose_index",   # 活动项索引
                rows=6
            )
            column = row.column()
            column.operator("cmc.add_bone_to_autooffset_list", text="", icon="ADD")
            column.operator("cmc.delete_bone_from_autooffset_list", text="", icon="REMOVE")
            column.separator()
            column.menu("CMC_MT_auto_offset_list_menu", text="", icon="DOWNARROW_HLT")
            column.separator()
            column.operator("cmc.move_bone_list_up", text="", icon="TRIA_UP")
            column.operator("cmc.move_bone_list_down", text="", icon="TRIA_DOWN")
            box.separator()

            '''# 起始动作部分
            row = box.row()
            column = row.column()
            column.operator(CHESTNUTMC_OT_SaveStartPose.bl_idname,
                        text="Save Start Pose",
                        icon='FILE_TICK',
                        depress=True if len(context.active_object.cmc_auto_offset_animation_pose) > 0 and context.active_object.cmc_auto_offset_animation_pose[-1].have_start_pose else False)
            column.operator(CHESTNUTMC_OT_ApplyStartPose.bl_idname, text="Apply Start Pose", icon='POSE_HLT')
            # 结束动作部分
            column = row.column()
            column.operator(CHESTNUTMC_OT_SaveEndPose.bl_idname,
                        text="Save End Pose",
                        icon='FILE_TICK',
                        depress=True if len(context.active_object.cmc_auto_offset_animation_pose) > 0 and context.active_object.cmc_auto_offset_animation_pose[-1].have_end_pose else False)
            column.operator(CHESTNUTMC_OT_ApplyEndPose.bl_idname, text="Apply End Pose", icon='POSE_HLT')'''
            # 中间动作部分
            box.label(text="Action List", icon="POSE_HLT")
            row = box.row()
            row.template_list(
                "CMC_UL_AutoOffset_IntermediateActionList",
                "cmc_auto_offset_animation_intermediate_action",
                Object,
                "cmc_auto_offset_animation_intermediate_action",
                Object,
                "cmc_auto_offset_animation_intermediate_action_index",
                rows=8
            )
            column = row.column()
            column.operator("cmc.save_intermediate_pose", text="Save Pose", icon="FILE_TICK")
            column.operator("cmc.update_intermediate_pose", text="Update Pose", icon = "FILE_REFRESH")
            column.operator("cmc.delete_intermediate_pose", text="Delete Pose", icon="TRASH")
            column.separator()
            column.operator("cmc.move_pose_list_up", text="Move Up", icon="TRIA_UP")
            column.operator("cmc.move_pose_list_down", text="Move Down", icon="TRIA_DOWN")
            column.separator()
            column.operator("cmc.apply_intermediate_pose", text="Apply Pose", icon='POSE_HLT')
            column.operator(CHESTNUTMC_OT_Delete_AO_Pose.bl_idname, text="Delete Saved Poses", icon='TRASH')

            # 设置部分
            setting = getattr(Object, "cmc_auto_offset_animation_settings", [])
            if len(setting) > 0:
                box.label(text="Auto Offset Animation Settings", icon="SETTINGS")
                # 基本设置
                nbox = box.box()
                row = nbox.row()
                row.prop(setting[0], "use_average_frame_length", text="Average Action Length")
                column = row.column()
                column.prop(setting[0], "frame_length", text="")
                column.enabled = True if setting[0].use_average_frame_length else False
                row = nbox.row()
                row.prop(setting[0], "keyframe_offset", text="Keyframe Offset")
                column = row.column()
                column.active = True if setting[0].keyframe_offset else False
                column.prop(setting[0], "uniform_offset", text="Uniform Offset")
                column.prop(setting[0], "uniform_offset_value", text="Offset")

                # 预备式设置
                nbox = box.box()
                row = nbox.row()
                row.prop(setting[0], "use_anticipation_pose", text="Anticipation Pose")
                column = row.column()
                column.active = True if setting[0].use_anticipation_pose else False
                nrow = column.row()
                nrow.prop(setting[0], "anticipation_pose_offset", text="Offset")
                nrow.prop(setting[0], "anticipation_pose_intensity", text="intensity")
                column.separator()
                # 面板展开与收起
                row.prop(context.active_object.cmc_auto_offset_animation_settings[0], "anticipation_advance_expand",
                            icon="DISCLOSURE_TRI_DOWN" if context.active_object.cmc_auto_offset_animation_settings[0].anticipation_advance_expand else "DISCLOSURE_TRI_RIGHT",
                            text="",
                            emboss=True)
                if context.active_object.cmc_auto_offset_animation_settings[0].anticipation_advance_expand:
                    column.operator("cmc.save_anticipation_pose",
                                    text="Save Custom Anticipation Pose",
                                    icon='FILE_TICK',
                                depress=True if len(context.active_object.cmc_auto_offset_animation_pose) > 0 and context.active_object.cmc_auto_offset_animation_pose[-1].have_anticipation_pose else False)
                    column.operator("cmc.apply_anticipation_pose", text="Apply Custom Anticipation Pose", icon='POSE_HLT')

                # 收尾式设置
                nbox = box.box()
                row = nbox.row()
                row.prop(setting[0], "use_recover_pose", text="Recover Pose")
                column = row.column()
                column.active = True if setting[0].use_recover_pose else False
                nrow = column.row()
                nrow.prop(setting[0], "recover_pose_offset", text="Offset")
                nrow.prop(setting[0], "recover_pose_intensity", text="intensity")
                column.separator()
                # 面板展开与收起
                row.prop(context.active_object.cmc_auto_offset_animation_settings[0], "recover_advance_expand",
                            icon="DISCLOSURE_TRI_DOWN" if context.active_object.cmc_auto_offset_animation_settings[0].recover_advance_expand else "DISCLOSURE_TRI_RIGHT",
                            text="",
                            emboss=True)
                if context.active_object.cmc_auto_offset_animation_settings[0].recover_advance_expand:
                    column.operator("cmc.save_recover_pose",
                                    text="Save Custom Recover Pose",
                                    icon='FILE_TICK',
                                depress=True if len(context.active_object.cmc_auto_offset_animation_pose) > 0 and context.active_object.cmc_auto_offset_animation_pose[-1].have_recover_pose else False)
                    column.operator("cmc.apply_recover_pose", text="Apply Custom Recover Pose", icon='POSE_HLT')

                # 错帧动画创建
                box.separator()
                row = box.row()
                row.operator("cmc.create_auto_offset_animation", text="Create Auto Offset Animation", icon='TRIA_RIGHT', depress=bpy.ops.cmc.create_auto_offset_animation.poll())



        #* 变换面板
        layout = self.layout
        layout.use_property_split = True
        layout.separator()

        ob = context.object
        bone = context.active_bone

        layout.label(text="Transform", icon='TRANSFORM_ORIGINS')

        col = layout.column()

        if bone and ob:
            pchan = ob.pose.bones[bone.name]
            col.active = not (bone.parent and bone.use_connect)

            row = col.row(align=True)
            row.prop(pchan, "location")
            row.use_property_decorate = False
            row.prop(pchan, "lock_location", text="", emboss=False, icon='DECORATE_UNLOCKED')

            rotation_mode = pchan.rotation_mode
            if rotation_mode == 'QUATERNION':
                col = layout.column()
                row = col.row(align=True)
                row.prop(pchan, "rotation_quaternion", text="Rotation")
                sub = row.column(align=True)
                sub.use_property_decorate = False
                sub.prop(pchan, "lock_rotation_w", text="", emboss=False, icon='DECORATE_UNLOCKED')
                sub.prop(pchan, "lock_rotation", text="", emboss=False, icon='DECORATE_UNLOCKED')
            elif rotation_mode == 'AXIS_ANGLE':
                col = layout.column()
                row = col.row(align=True)
                row.prop(pchan, "rotation_axis_angle", text="Rotation")

                sub = row.column(align=True)
                sub.use_property_decorate = False
                sub.prop(pchan, "lock_rotation_w", text="", emboss=False, icon='DECORATE_UNLOCKED')
                sub.prop(pchan, "lock_rotation", text="", emboss=False, icon='DECORATE_UNLOCKED')
            else:
                col = layout.column()
                row = col.row(align=True)
                row.prop(pchan, "rotation_euler", text="Rotation")
                row.use_property_decorate = False
                row.prop(pchan, "lock_rotation", text="", emboss=False, icon='DECORATE_UNLOCKED')
            row = layout.row(align=True)
            row.prop(pchan, "rotation_mode", text="Mode")
            row.label(text="", icon='BLANK1')

            col = layout.column()
            row = col.row(align=True)
            row.prop(pchan, "scale")
            row.use_property_decorate = False
            row.prop(pchan, "lock_scale", text="", emboss=False, icon='DECORATE_UNLOCKED')

        elif context.edit_bone:
            bone = context.edit_bone
            col = layout.column()
            col.prop(bone, "head")
            col.prop(bone, "tail")

            col = layout.column()
            col.prop(bone, "roll")
            col.prop(bone, "length")
            col.prop(bone, "lock")


        #* 选择集面板
        layout = self.layout
        layout.separator()

        arm = context.object
        layout.label(text="Selection Sets", icon='GROUP_BONE')

        row = layout.row()
        row.enabled = (context.mode == 'POSE')

        # UI list
        rows = 4 if len(arm.selection_sets) > 0 else 1
        row.template_list(
            "POSE_UL_selection_set", "",  # type and unique id
            arm, "selection_sets",  # pointer to the CollectionProperty
            arm, "active_selection_set",  # pointer to the active identifier
            rows=rows
        )

        # add/remove/specials UI list Menu
        col = row.column(align=True)
        col.operator("pose.selection_set_add", icon='ADD', text="")
        col.operator("pose.selection_set_remove", icon='REMOVE', text="")
        col.menu("POSE_MT_selection_sets_context_menu", icon='DOWNARROW_HLT', text="")

        # move up/down arrows
        if len(arm.selection_sets) > 0:
            col.separator()
            col.operator("pose.selection_set_move", icon='TRIA_UP', text="").direction = 'UP'
            col.operator("pose.selection_set_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

        # buttons
        row = layout.row()

        sub = row.row(align=True)
        sub.operator("pose.selection_set_assign", text="Assign")
        sub.operator("pose.selection_set_unassign", text="Remove")

        sub = row.row(align=True)
        sub.operator("pose.selection_set_select", text="Select")
        sub.operator("pose.selection_set_deselect", text="Deselect")

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != 'POSE':
            return False
        return True
