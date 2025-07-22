# ChestnutMC：一个用于制作强大 Blender Minecraft 动画的人模插件

## 😎 概览

**ChestnutMC** 是一个专为 Minecraft 动画设计的 Blender 插件，提供强大且易用的人模系统。该插件已在 **Blender 4.2** 上进行测试，具备以下主要功能：

1. 支持 IK/FK 动画人模系统  
2. 无缝切换 FK 与 IK  
3. 保存并管理人模预设  
4. 便捷的皮肤管理与更换  
5. 自动生成错帧动画  
6. 快速材质管理

---

## 🌲 安装方法

1. 从 [发布页面](https://github.com/chestnuti/ChestnutMC_Rig/releases) 下载插件。
2. 打开 Blender，依次点击：  
   `编辑 > 首选项 > 插件 > 安装`，选择刚下载的文件。  
   _注意：需要 Blender 4.2 或更高版本。_
3. 在插件标签页中，勾选 **ChestnutMC_Rig** 启用插件。

---

## 🔧 使用指南

+ ### 导入和保存人模

1. 点击 **“加载库”（Load Library）** 加载可用的人模资源。  
2. 从列表中选择一个人模。  
3. 点击 **“导入栗籽人模”（Import ChestnutMC Rig）** 将其添加到场景中。
4. 如果你自定义修改了人模，也可以点击 **“保存人模”（Save ChestnutMC Rig）** 保存当前人模。

---

+ ### 更换人模皮肤

1. 选择你要修改的人模模型。  
2. 在 **栗籽人模皮肤替换器** 中选择一个皮肤。  
3. 点击 **“应用皮肤”（Apply Skin）** 以更改人模的外观。  
4. 使用 **“添加”（Add）** 将皮肤保存到库中，或点击 **“移除”（Remove）** 删除皮肤。  
5. 调整完面部设置后，点击 **“保存皮肤脸部设置”（Save Face to Skin）** 以保存设置。带有保存面部设置的皮肤将在名称后出现一个勾选标记。下次应用该皮肤时，会自动附加面部表情设置。  
6. 点击 **“添加皮肤”（Add Skin）** 并选择文件以添加新皮肤；  
   也可通过点击 **“下载ID”（Download from ID）** 从 Mojang 下载皮肤。

> **注意：** 若你重命名或删除了皮肤，在未打包皮肤的项目中，使用了该皮肤的人模可能会丢失贴图。

---

+ ### 无缝 IK ↔ FK 切换

1. 选择人模，并切换至 **姿态模式（Pose Mode）**。  
2. 点击 **“无缝IK→FK”** 或 **“无缝FK→IK”** 按钮切换控制模式。  
3. 若要在切换时插入关键帧，点击 **“插入关键帧”（Insert Keyframe）**。启用 **自动插帧** 后，每次切换时都会自动插入关键帧。  
4. IK/FK 切换的关键帧可能不会显示在时间轴中。若需查看，请打开 **动画工作表（Dope Sheet）** 并启用 **“显示隐藏内容”（Show Hidden）**。

---

+ ### 创建自动错帧动画

> 💡 该功能适用于 **任何骨架**，不仅限于 ChestnutMC 人模。

1. 选择人模并进入 **姿态模式（Pose Mode）**。  
2. 在骨骼列表中选择一个骨骼，点击 **“+”** 按钮。  
   你也可以使用面板下方预设的骨骼组快速选择。  
3. 根据你选择的模式调整每个骨骼的 **优先级** 或 **偏移量**：  
   - 在 **统一偏移模式** 中，设置每个骨骼的 **优先级**；  
   - 在 **自由偏移模式** 中，分别设置每个骨骼的 **偏移量**。

> **说明：** 优先级与偏移量是相对于骨骼层级与目标动作而言的。例如，如果动作从上臂传递到前臂，那么前臂的偏移量可能需要高于上臂。

4. 设置好姿势后，点击 **“保存骨架姿态”（Save Pose）**。  
   至少需保存 **两个** 姿势才可生成动画，当然你也可以根据需要保存更多姿势。  
5. 建议先在时间轴上创建关键姿势。插件会根据关键帧自动计算动画长度；  
   你也可以手动调整，或使用 **“平均动作长度”（Average Action Length）** 使所有姿势持续时间一致。  
6. 若想使动画具有起势与收势感，可启用 **“起始姿势”（Anticipation Pose）** 与 **“延迟姿势”（Postponement Pose）**，系统将自动添加关键帧。  
   > **注意：** 这两个姿势仅影响首尾动作，确保偏移量不超过其动作长度。
7. 完成设置后，点击 **“创建自动错帧动画”（Create Auto Offset Animation）** 以生成动画。  
   效果将更加自然流畅。
8. 你可以将骨骼列表和设置保存为预设，便于今后复用。

---

+ ### 导入和导出资产库

1. 该插件为资源库提供了导出和导入功能。您可以前往：
`编辑 > 偏好设置 > 插件 > ChestnutMC Rig Addon`，然后单击 **”导出资产库“** 或 **”导入资产库“**。
2. 选择要导出或导入的文件。库文件是包含所有资源的 ZIP 文件。导出的库文件可以在任何安装了 ChestnutMC Rig Addon 的计算机上使用。
> **注意：** 我们建议您在更新插件之前导出库文件，以免丢失您的自定义资产。

---

# ChestnutMC: A Rigs with Blender Addon for Creating Powerful Minecraft Animations

## 😎 Overview

**ChestnutMC** is a Blender addon designed to provide powerful and user-friendly rigs for Minecraft animations. It has been tested with **Blender 4.2** and offers a wide range of features, including:

1. IK/FK rigging support for animation.  
2. Seamless switching between FK and IK.  
3. Saving and managing rig presets.  
4. Easy skin management and switching.  
5. Automated creation of offset animations.  
6. Quick material management.

---

## 🌲 Installation

1. Download the addon from the [release page](https://github.com/chestnuti/ChestnutMC_Rig/releases).
2. Open Blender and go to:  
   `Edit > Preferences > Add-ons > Install`, then select the downloaded file.  
   _Note: Blender 4.2 or higher is required._
3. In the Add-ons tab, enable **ChestnutMC_Rig** by checking its box.

---

## 🔧 Usage Guide

+ ### Importing and saving Rigs

1. Click **"Load Library"** to load available rig assets.  
2. Select a rig from the list.  
3. Click **"Import ChestnutMC Rig"** to bring it into your scene.
4. You can click **"Save ChestnutMC Rig"** to save it if you customized the rig.

---

+ ### Changing Rig Skins

1. Select the rig you want to modify.  
2. In the **ChestnutMC Skin Swapper**, choose a skin.  
3. Click **"Apply Skin"** to update the rig's appearance.  
4. Use **"Add"** to save a skin to the library, or **"Remove"** to delete it.  
5. After adjusting the facial settings, click **"Save Face to Skin"** to save those settings. A check mark will appear next to skins with saved face data. Applying the skin later will also apply the saved facial expression.  
6. To add a new skin, click **"Add Skin"** and select a file.  
   You can also download skins directly from Mojang using the **"Download from ID"** option.

> **Note:** If you rename or remove a skin, rigs relying on it may not function properly in projects where the skin isn’t packed.

---

+ ### Seamless IK ↔ FK Switching

1. Select the rig and enter **Pose Mode**.  
2. Use the **"Seamless IK→FK"** or **"Seamless FK→IK"** button to switch control modes.  
3. To add a keyframe during the switch, click **"Insert Keyframe"**. If **Auto Insert Keyframe** is enabled, this happens automatically whenever you switch.  
4. IK/FK switch keyframes might not appear on the timeline. To view them, open the **Dope Sheet** and enable **"Show Hidden"**.

---

+ ### Creating Auto Offset Animations

> 💡 This feature works with **any rig**, not just ChestnutMC rigs.

1. Select the rig and enter **Pose Mode**.  
2. Choose a bone you want to animate and click the **"+"** button in the bone list.  
   You can also use the pre-defined bone groups at the bottom of the panel for quick selection.  
3. Adjust **priority** or **offset** values for each bone depending on your selected mode:  
   - In **Uniform Offset Mode**, set **priority** for each bone.  
   - In **Free Offset Mode**, set individual **offsets**.

> **Note:** Priorities and offsets are relative to the bone hierarchy and the desired motion. For example, if motion flows from the upper arm to the lower arm, the lower arm might need a higher offset/priority.

4. Pose your rig and click **"Save Pose"**.  
   You need to save **at least two** poses to generate offset animation. More poses can be added as needed.  
5. It’s recommended to create key poses on the timeline first.  
   The addon will automatically calculate animation duration based on frame positions.  
   Alternatively, you can manually adjust the action length or use **"Average Action Length"** to make all poses evenly timed.  
6. To add a sense of anticipation or follow-through in your animation, use **"Anticipation Pose"** and **"Postponement Pose"**.  
   These will create extra key poses at the start and end.  
   > **Make sure the offsets don’t exceed the length of the first or last poses.**
7. Once everything is set, click **"Create Auto Offset Animation"** to generate the animation.  
   The result will be more dynamic and visually appealing.  
8. You can save your bone list and settings as a preset for reuse later.

---

+ ### Export and Import Asset Library

1. The addon provides an export and import feature for asset libraries. You can go to:
  `Edit > Preferences > Add-ons > ChestnutMC Rig Addon`, then click **"Export Asset Library"** or **"Import Asset Library"**.
2. Choose the file to export or import. The library file is a ZIP file containing all the assets. The exported library file can be used on any computer with ChestnutMC Rig Addon installed.
> **Note:** We recommended you to export the library file before update the addon to avoid losing your customization.