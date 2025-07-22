import requests
import os
import bpy

from ..config import __addon_name__

def get_uuid(username):
    """通过 Mojang API 获取 UUID"""
    url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("id")
    else:
        print(f"无法找到用户 {username}")
        return None

def download_skin(username, save_dir="skins"):
    """下载玩家皮肤"""
    uuid = get_uuid(username)
    if not uuid:
        return

    skin_url = f"https://crafatar.com/skins/{uuid}"
    response = requests.get(skin_url)

    if response.status_code == 200:
        os.makedirs(save_dir, exist_ok=True)
        filepath = os.path.join(save_dir, f"{username}.png")
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"Skin downloaded successfully to {filepath}")
        return True
    else:
        return False

class CHESTNUTMC_OT_Download_Skin(bpy.types.Operator):
    bl_idname = "cmc.download_skin"
    bl_label = "Download Skin"
    bl_description = "Download skin from Mojang"
    bl_options = {"REGISTER", "UNDO"}

    username: bpy.props.StringProperty(name="Username") # type: ignore

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        addon_prefs = context.preferences.addons[__addon_name__].preferences
        skin_path = addon_prefs.skin_path
        filepath = os.path.join(skin_path, f"{self.username}.png")
        # 检查文件是否已经存在
        if os.path.exists(filepath):
            self.report({"INFO"}, "Skin already exists")
            return {"CANCELLED"}

        if download_skin(self.username, skin_path):
            self.report({"INFO"}, "Download skin successfully")
            bpy.ops.cmc.load_library()
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, "Failed to download skin")
            return {"CANCELLED"}