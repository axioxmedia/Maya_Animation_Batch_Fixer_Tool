# ALPHA 批量动画工具

**适用于 Autodesk Maya 2024 的生产级批量动画扫描、验证、修正、重定向与 FBX 导出工具包。**

专为游戏动画管线（Unreal Engine 5 就绪）设计。专注于从 SMPL-H / 动捕风格源骨架到 MetaHuman 风格或自定义骨架的高保真重定向，尤其在手臂、手掌、手指及双手交互的自然度上进行了大量优化。

由 **香港安溯媒体技术有限公司 (Axiox Media Technology Limited)** 内部开发，用于《凯普勒 186F》等项目。

---

## ✨ 核心功能

- **批量扫描与质量检测**：15+ 自动验证规则（缺失骨骼、空动画、动画长度、缩放异常、旋转/位移突变、肩部/颈部/手臂异常姿势、根运动、手部翻转等）
- **智能自动修正**：可选修复旋转/位移突变、缩放异常、肩部抬起、颈部姿态、手臂扭转、手部翻转（支持保守模式）
- **高级重定向引擎**：
  - 核心方法：Maya HumanIK + 大量自定义后处理
  - 源引导手臂 IK（极向量控制、伸展限制、同侧锁定）
  - 智能手掌帧分类与自动求解（搭腿 / 双手交叠 / 胸前接触姿势）
  - 参考与用户自定义交叠/手指弯曲模板
  - 双手收敛求解，实现自然的双手交互
  - 时间稳定、手腕解剖限制、大腿避让等
  - 丰富的混合强度参数可精细调节
- **NPZ 支持**：可导入 SMPL/AMASS 风格的 `.npz` 动作数据（支持自定义结构描述）
- **双语界面**：完整英文 + 简体中文支持
- **生产工作流**：试运行、跳过 BAD 文件、自动分类 Good/Bad 文件夹、详细 JSON/CSV/TXT 报告
- **开箱即用预设**：包含完整的 SMPL-H → FemaleStd（MetaHuman 兼容）映射与安全配置

---

## 📋 系统要求

- **Autodesk Maya 2024**（Python 3.9 环境），其他较新版本可能需少量调整
- **HumanIK** 插件（Maya 标准组件）
- **FBX** 支持（`fbxmaya` 插件，工具会自动加载）
- 可选：安装 `numpy` 以完整支持 NPZ 文件
- 推荐 Windows 系统（路径处理与 Maya 稳定性最佳）
- 推荐配置：32GB+ 内存、现代多核 CPU

---

## 📁 推荐项目结构

```
ALPHAMayaBatchAnimTool/
├── ALPHABatchAnimationTool.py              # 完整批量工具（扫描 + 重定向 + 修正 + 导出）
├── ALPHAOption1CalibrationTest.py          # 简洁的重定向专用界面（日常使用推荐）
├── ALPHA_UI_zh_CN.json                     # 中文界面翻译
├── Folders/
│   ├── Input/                              # ← 将源动画 FBX 放在这里
│   ├── Output_Retargeted/                  # ← 重定向后的 FBX 输出目录
│   ├── BadOrNeedsFix/                      # 自动复制的问题文件
│   ├── Good/                               # 自动复制的正常文件
│   └── ReportFolder/                       # 详细报告（JSON + CSV + TXT）
├── Presets/
│   └── SMPLH_FemaleStd/
│       ├── smplh_Tpose.fbx                 # 源休息姿势（必需）
│       ├── FemaleStd_CombinedSkelMesh1.FBX # 示例目标骨架
│       ├── smplh_to_femalestd_body_mapping.json
│       ├── ALPHA_SMPLH_to_FemaleStd_safe_config.json  # 推荐的安全配置
│       └── smplh_npz_schema_template.json
└── README.zh-CN.md
```

> **提示**：保持此结构，工具会自动规范化所有路径。

---

## 🚀 快速开始（SMPL-H → FemaleStd 重定向）

使用内置预设即可快速获得高质量结果。

### 1. 准备数据
- 将你的 SMPL-H 骨架动画 `.fbx` 文件复制到 `Folders/Input/` 文件夹

### 2. 启动重定向界面（推荐）

```python
# 在 Maya 脚本编辑器（Python 标签）或 Shelf 按钮中执行：
import sys
sys.path.append(r"D:/path/to/ALPHAMayaBatchAnimTool")   # ← 修改为你的实际路径
import ALPHAOption1CalibrationTest as retarget
retarget.show()
```

### 3. 在界面中配置路径

| 字段                     | 推荐值                                                      |
|--------------------------|-------------------------------------------------------------|
| Input Folder             | `Folders/Input`                                             |
| Output Folder            | `Folders/Output_Retargeted`                                 |
| Report Folder            | `Folders/ReportFolder_Retargeting`                          |
| Source Rest Skeleton     | `Presets/SMPLH_FemaleStd/smplh_Tpose.fbx`                   |
| Target Skeleton          | `Presets/SMPLH_FemaleStd/FemaleStd_CombinedSkelMesh1.FBX`（或你自己的目标骨架） |
| Joint Mapping JSON       | `Presets/SMPLH_FemaleStd/smplh_to_femalestd_body_mapping.json` |
| Max Files                | 先设为 `1` 测试，验证后再增大                               |

### 4. 运行并检查结果
- 点击 **Run Retargeting**（开始重定向）
- 在日志窗口观察进度
- 完成后检查：
  - `Output_Retargeted/` 中的 FBX 文件
  - Report 文件夹中的 `.txt` / `.json` 报告（重点关注 `WARNING` 和 `ERROR`）

---

## ⚙️ 配置与自定义

### 加载安全生产配置（强烈推荐）
1. 启动完整工具界面（`ALPHABatchAnimationTool.py` → `show()`）
2. 点击 **Load Settings**（加载设置）
3. 选择 `Presets/SMPLH_FemaleStd/ALPHA_SMPLH_to_FemaleStd_safe_config.json`
4. 此配置已针对生产环境调优（许多实验性手掌/手指功能已优化或关闭以保证稳定性）

### 适配自己的骨架
1. 导出源骨架的干净 **T-pose** FBX
2. 导出目标骨架的干净 T-pose / A-pose FBX
3. 编辑或新建 `mapping.json`，格式示例：
   ```json
   {
     "joints": {
       "pelvis": "你的骨盆关节名称",
       "upperarm_l": "你的左上臂关节名称",
       ...
     }
   }
   ```
4. 先用 **Max Files = 1** 测试，观察输出效果，再调整以下参数：
   - `retarget_translation_scale`（骨盆位移缩放）
   - `matrix_delta_order`（`rest_inv_current` 或 `current_rest_inv`）
   - HumanIK 后处理对齐强度、臂 IK 各项参数
   - 手掌与手指模板混合值

> **常见问题修复**：若目标角色保持 A-pose，尝试切换 `matrix_delta_order`，或检查关节名称是否完全一致（区分大小写，无多余命名空间）。

---

## 📊 报告与文件管理

每次批处理会自动生成带时间戳的报告：
- `ALPHABatchAnimationReport_YYYYMMDD_HHMMSS.json` — 完整机器可读结果 + 配置快照
- `.csv` — 可直接用 Excel 打开（状态、问题数量、错误代码）
- `.txt` — 人类可读摘要，突出显示问题文件

可开启自动将 **Good**（正常）和 **Bad/Needs Fix**（需修正）文件分类复制/移动到独立文件夹，并保留或扁平化原有目录结构。

---

## 🛠️ 完整工具 vs 重定向专用界面

| 工具                              | 适用场景                     | 主要特点                                      |
|-----------------------------------|------------------------------|-----------------------------------------------|
| `ALPHAOption1CalibrationTest.py`  | 日常重定向工作               | 界面简洁、默认安全、专注重定向                |
| `ALPHABatchAnimationTool.py`      | 完整管线 / 动画库质检        | 支持仅扫描模式、修正流程、100+ 高级参数、配置保存/加载 |

启动完整工具：
```python
import ALPHABatchAnimationTool as alpha
alpha.show()
```

---

## ❓ 常见问题排查

**重定向后目标角色保持 T-pose / A-pose**
- 检查关节映射名称是否完全匹配
- 尝试更换 `matrix_delta_order`
- 确认已正确加载 Source Rest Skeleton（T-pose）

**导出后目标骨架没有动画**
- 源 FBX 可能只包含网格动画而非关节关键帧
- 开启 `fail_if_no_target_animation` 进行严格检查

**手部姿态不自然或互相穿插**
- 启用 `alpha_v3_enable_auto_palm_frame_solver` 及相关手掌求解选项（参考 safe_config）
- 微调 `humanik_source_guided_arm_ik_*` 手掌/手指参数
- 对特定交互姿势使用参考交叠模板

**长动画处理缓慢**
- 提高 `sample_every_n_frames`（仅影响验证阶段）
- 分批处理（设置较小的 `max_files`）

**FBX 导出失败或文件极小**
- 检查 Output 文件夹写入权限
- 确认 `fbxmaya` 插件已加载
- 避免使用过长的文件路径

---

## 📌 最佳实践

1. **始终先用 1 个文件测试**，确认效果后再批量处理。
2. 实验新参数时开启 **Dry Run**（试运行）模式。
3. 最终清洁运行时建议开启「重定向前跳过 BAD 文件」。
4. 输出给 UE5 时，建议开启「包含目标网格」+「强制给目标关节打 Key」。
5. 将最终调优后的参数保存为项目专用的 JSON 配置文件。

---

## 📞 联系与支持

**香港安溯媒体技术有限公司 (Axiox Media Technology Limited)**  
邮箱：**official@axiox.net**

如有问题、需要自定义骨架映射帮助、管线集成建议或功能建议，欢迎邮件联系。我们也欢迎社区反馈与贡献！

---

## 📄 许可证

本项目采用 **MIT License** 许可证。

完整许可证文本请查看仓库中的 [LICENSE](LICENSE) 文件。

Copyright (c) 2026 Axiox Media Technology Limited

---

*本工具凝聚了在真实游戏动画生产管线中多年迭代的经验。先进的手臂 IK、手掌求解器与手指匹配系统，专门用于解决动捕转游戏时「手部总是变形」这一顽疾。*

**祝重定向工作顺利！** 🎮
