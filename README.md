# ALPHA Batch Animation Tool

**Production-grade batch animation scanning, validation, correction, retargeting & FBX export toolkit for Autodesk Maya 2024.**

Designed for game animation pipelines (Unreal Engine 5 ready). Specializes in high-fidelity retargeting from SMPL-H / mocap-style sources to MetaHuman-style or custom skeletons, with industry-leading attention to natural arm, palm, finger, and two-hand interaction quality.

Developed by **Axiox Media Technology Limited** (Hong Kong) for internal use on titles like *Kepler 186F*.

---

## ✨ Key Features

- **Batch Scanning & QC**: 15+ automatic validation rules (missing bones, empty clips, animation length, scale extremes, rotation/translation spikes, abnormal shoulder/neck/arm poses, root motion, hand flips, etc.)
- **Smart Auto-Correction**: Optional fixes for spikes, scale, shoulder raise, neck pose, arm twist, hand orientation (conservative mode available)
- **Advanced Retargeting Engine**:
  - Primary method: Maya HumanIK + extensive custom post-processing
  - Source-guided arm IK with pole control, reach limits, same-side locking
  - Intelligent palm frame classification & auto-solving (lap / clasp / chest contact poses)
  - Reference & user-defined clasp/finger curl templates
  - Paired-hand convergence for natural two-hand interactions
  - Temporal stabilization, wrist anatomy guard, thigh clearance
  - Many fine-tune blend/strength parameters
- **NPZ Support**: Import SMPL/AMASS-style `.npz` motion (with configurable schema)
- **Bilingual UI**: Full English + Simplified Chinese interface
- **Production Workflow**: Dry-run, skip-bad-before-retarget, auto file sorting (Good / BadOrNeedsFix folders), detailed JSON/CSV/TXT reports per batch
- **Ready Presets**: Complete SMPL-H → FemaleStd (MetaHuman-compatible) mapping + safe configuration included

---

## 📋 Requirements

- **Autodesk Maya 2024** (Python 3.9 environment). Other recent versions may work with minor adjustments.
- **HumanIK** plugin (included with Maya)
- **FBX** support (`fbxmaya` plugin — automatically loaded by the tool)
- Optional: `numpy` for full NPZ import support
- Windows recommended (best path & Maya stability)
- Recommended hardware: 32 GB+ RAM, modern multi-core CPU

---

## 📁 Recommended Project Structure

```
ALPHAMayaBatchAnimTool/
├── ALPHABatchAnimationTool.py              # Full-featured batch tool (scan + retarget + correct + export)
├── ALPHAOption1CalibrationTest.py          # Simpler dedicated Retargeting UI (recommended for daily use)
├── ALPHA_UI_zh_CN.json                     # Chinese UI translations
├── Folders/
│   ├── Input/                              # ← Put your source animation FBX files here
│   ├── Output_Retargeted/                  # ← Retargeted FBX output goes here
│   ├── BadOrNeedsFix/                      # Auto-copied problematic files
│   ├── Good/                               # Auto-copied clean files
│   └── ReportFolder/                       # Detailed reports (JSON + CSV + TXT)
├── Presets/
│   └── SMPLH_FemaleStd/
│       ├── smplh_Tpose.fbx                 # Source rest/T-pose (required)
│       ├── FemaleStd_CombinedSkelMesh1.FBX # Example target skeleton
│       ├── smplh_to_femalestd_body_mapping.json
│       ├── ALPHA_SMPLH_to_FemaleStd_safe_config.json  # Recommended starting config
│       └── smplh_npz_schema_template.json
└── README.md
```

> **Tip**: Keep this exact structure. The tool normalizes all paths automatically.

---

## 🚀 Quick Start (Retarget SMPL-H → FemaleStd)

This is the fastest way to get high-quality results using the included preset.

### 1. Prepare Data
- Copy your SMPL-H rigged animation `.fbx` files into `Folders/Input/`

### 2. Launch the Retargeting UI (Recommended)

```python
# In Maya Script Editor (Python tab) or shelf button:
import sys
sys.path.append(r"D:/path/to/ALPHAMayaBatchAnimTool")   # ← change to your folder
import ALPHAOption1CalibrationTest as retarget
retarget.show()
```

### 3. Configure Paths in UI
| Field                    | Recommended Value                                      |
|--------------------------|--------------------------------------------------------|
| Input Folder             | `Folders/Input`                                        |
| Output Folder            | `Folders/Output_Retargeted`                            |
| Report Folder            | `Folders/ReportFolder_Retargeting`                     |
| Source Rest Skeleton     | `Presets/SMPLH_FemaleStd/smplh_Tpose.fbx`              |
| Target Skeleton          | `Presets/SMPLH_FemaleStd/FemaleStd_CombinedSkelMesh1.FBX` (or your own) |
| Joint Mapping JSON       | `Presets/SMPLH_FemaleStd/smplh_to_femalestd_body_mapping.json` |
| Max Files                | `1` (for first test) → increase after verification     |

### 4. Run & Review
- Click **Run Retargeting**
- Monitor progress in the log window
- After completion, inspect:
  - Output FBX files in `Output_Retargeted/`
  - Report `.txt` / `.json` in Report Folder (look for `WARNING` / `ERROR`)

---

## ⚙️ Configuration & Customization

### Load Safe Production Config (Strongly Recommended)
1. In the full UI (`ALPHABatchAnimationTool.py` → `show()`), click **Load Settings**
2. Select `Presets/SMPLH_FemaleStd/ALPHA_SMPLH_to_FemaleStd_safe_config.json`
3. This loads battle-tested values (many experimental palm/finger features tuned or disabled for stability).

### For Your Own Skeletons
1. Export clean **T-pose** FBX of your **source** skeleton.
2. Export clean T-pose/A-pose of your **target** skeleton.
3. Edit or create a new `mapping.json`:
   ```json
   {
     "joints": {
       "pelvis": "YourSourcePelvisName",
       "upperarm_l": "YourSourceLeftUpperArm",
       ...
     }
   }
   ```
4. Test with **Max Files = 1**, review output, then adjust:
   - `retarget_translation_scale`
   - `matrix_delta_order` (`rest_inv_current` vs `current_rest_inv`)
   - HumanIK post-align / arm IK strengths
   - Palm & finger template blends

> Common fix for "target stays in A-pose": Switch `matrix_delta_order` or verify joint names match exactly (case-sensitive, no extra namespaces).

---

## 📊 Reports & File Management

Every batch automatically generates:
- `ALPHABatchAnimationReport_YYYYMMDD_HHMMSS.json` — Complete machine-readable results + full config snapshot
- `.csv` — Easy to open in Excel (status, issue counts, codes)
- `.txt` — Human-readable summary highlighting problem files

You can enable automatic copying/moving of **Good** and **Bad/Needs Fix** files into separate folders while preserving (or flattening) folder structure.

---

## 🛠️ Full Batch Tool vs Retarget UI

| Tool                              | Best For                              | Features                                      |
|-----------------------------------|---------------------------------------|-----------------------------------------------|
| `ALPHAOption1CalibrationTest.py`  | Daily retarget work                   | Clean focused UI, safe defaults               |
| `ALPHABatchAnimationTool.py`      | Full pipeline / library QC            | Scanning only mode, correction passes, 100+ advanced toggles, config load/save |

Launch full tool with:
```python
import ALPHABatchAnimationTool as alpha
alpha.show()
```

---

## ❓ Troubleshooting

**Target character stays in T-pose / A-pose after retarget**
- Check joint mapping names (exact match required)
- Try changing `matrix_delta_order`
- Confirm Source Rest Skeleton is loaded and valid

**No animation exported on target**
- Source FBX may contain only mesh animation — ensure joints are keyed
- Enable `fail_if_no_target_animation` for strict mode

**Hands look unnatural or intersecting**
- Enable `alpha_v3_enable_auto_palm_frame_solver` + related palm options (use safe_config as reference)
- Tune `humanik_source_guided_arm_ik_*` palm/finger parameters
- Use reference clasp templates for specific interaction poses

**Slow performance on long animations**
- Increase `sample_every_n_frames` (validation only)
- Process in smaller batches (`max_files`)

**FBX export fails or produces tiny files**
- Check write permissions on Output folder
- Verify `fbxmaya` plugin is loaded
- Avoid extremely long file paths

---

## 📌 Best Practices

1. **Always test with 1 file first** before large batches.
2. Use **Dry Run** mode when experimenting with new settings.
3. Keep `Skip Bad Files Before Retarget` **OFF** during initial validation, **ON** for final clean runs.
4. For UE5: Enable "Include Target Meshes" + "Force Key Target Joints".
5. Save your final tuned settings as a project-specific JSON config.

---

## 📞 Contact & Support

**Axiox Media Technology Limited**  
Hong Kong  
Email: **official@axiox.net**

For questions, custom skeleton mapping help, pipeline integration advice, or feature suggestions, feel free to reach out. Contributions and feedback are welcome!

---

## 📄 License

This project is licensed under the **MIT License**.

See the [LICENSE](LICENSE) file for the full license text.

Copyright (c) 2026 Axiox Media Technology Limited

---

*This tool represents years of iteration on real production animation retargeting challenges. The advanced arm IK, palm solvers, and finger matching systems were specifically developed to solve the "hands always look broken" problem common in mocap-to-game pipelines.*

**Happy retargeting!** 🎮
