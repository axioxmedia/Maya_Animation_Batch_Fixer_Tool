from __future__ import annotations

import os

import sys

import json

import time

import traceback

from typing import Dict, Any



try:

    import maya.cmds as cmds

except Exception:

    cmds = None



WINDOW_NAME = "ALPHARetargetingWindow"

LANGUAGE_ENGLISH = "en"

LANGUAGE_CHINESE_SIMPLIFIED = "zh_CN"





def maya_required():

    if cmds is None:

        raise RuntimeError("This tool must be run inside Maya Python.")





def norm_path(path: str) -> str:

    return os.path.normpath(str(path or "")).replace("\\", "/")





def script_dir() -> str:

    try:

        return norm_path(os.path.dirname(os.path.abspath(__file__)))

    except Exception:

        return norm_path(os.getcwd())





def ensure_dir(path: str) -> str:

    path = norm_path(path)

    if path and not os.path.isdir(path):

        os.makedirs(path)

    return path





def settings_path() -> str:

    return norm_path(os.path.join(script_dir(), "ALPHA_Retarget_Settings.json"))





def load_settings() -> Dict[str, Any]:

    path = settings_path()

    if os.path.isfile(path):

        try:

            with open(path, "r", encoding="utf-8") as f:

                data = json.load(f)

            if isinstance(data, dict):

                return data

        except Exception:

            pass

    return {}





def save_settings(data: Dict[str, Any]) -> None:

    with open(settings_path(), "w", encoding="utf-8") as f:

        json.dump(data, f, ensure_ascii=False, indent=2)





def load_alpha():

    d = script_dir()

    if d not in sys.path:

        sys.path.append(d)

    import importlib

    import ALPHABatchAnimationTool as alpha

    importlib.reload(alpha)

    return alpha





class ALPHARetargetingUI:

    def __init__(self):

        maya_required()

        self.alpha = load_alpha()

        data = load_settings()

        d = script_dir()

        self.controls = {}

        self.log_ctrl = None

        self.input_folder = norm_path(data.get("input_folder") or os.path.join(d, "Folders", "Input"))

        self.output_folder = norm_path(data.get("output_folder") or os.path.join(d, "Folders", "Output_Retargeted"))

        self.report_folder = norm_path(data.get("report_folder") or os.path.join(d, "Folders", "ReportFolder_Retargeting"))

        self.source_rest = norm_path(data.get("source_rest") or os.path.join(d, "Presets", "SMPLH_FemaleStd", "smplh_Tpose.fbx"))

        self.target_file = norm_path(data.get("target_file") or os.path.join(d, "Presets", "SMPLH_FemaleStd", "FemaleStd_CombinedSkelMesh1.FBX"))

        self.mapping_json = norm_path(data.get("mapping_json") or os.path.join(d, "Presets", "SMPLH_FemaleStd", "smplh_to_femalestd_body_mapping.json"))

        self.max_files = int(data.get("max_files") if data.get("max_files") is not None else 0)

        self.language = self.load_language()

        self.translations_zh_cn = self.alpha.load_chinese_translations()



    def load_language(self) -> str:

        try:

            path = self.alpha.config_default_path()

            if os.path.isfile(path):

                data = self.alpha.load_json_file(path)

                value = data.get("ui_language", LANGUAGE_ENGLISH)

                if value in (LANGUAGE_ENGLISH, LANGUAGE_CHINESE_SIMPLIFIED):

                    return value

        except Exception:

            pass

        return LANGUAGE_ENGLISH



    def save_language(self) -> None:

        try:

            cfg = self.alpha.ToolConfig()

            path = self.alpha.config_default_path()

            if os.path.isfile(path):

                try:

                    cfg = self.alpha.ToolConfig.from_dict(self.alpha.load_json_file(path))

                except Exception:

                    pass

            cfg.ui_language = self.language

            self.alpha.save_json_file(path, cfg.to_dict())

        except Exception:

            pass



    def tr(self, key: str, fallback: str) -> str:

        if self.language == LANGUAGE_CHINESE_SIMPLIFIED:

            return self.translations_zh_cn.get(key, fallback)

        return fallback



    def change_language(self, language: str) -> None:

        if language not in (LANGUAGE_ENGLISH, LANGUAGE_CHINESE_SIMPLIFIED):

            language = LANGUAGE_ENGLISH

        self.read()

        self.language = language

        self.save_language()

        self.show()



    def show(self) -> None:

        self.controls = {}

        self.translations_zh_cn = self.alpha.load_chinese_translations()

        if cmds.window(WINDOW_NAME, exists=True):

            cmds.deleteUI(WINDOW_NAME)

        window = cmds.window(WINDOW_NAME, title=self.tr("retarget.window_title", "ALPHA Retargeting"), sizeable=True, widthHeight=(720, 620))

        cmds.columnLayout(adjustableColumn=True, rowSpacing=6)

        cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnWidth2=(220, 220))

        cmds.button(label=u"切换到中文", command=lambda *_: self.change_language(LANGUAGE_CHINESE_SIMPLIFIED), height=28)

        cmds.button(label="Change Language to English", command=lambda *_: self.change_language(LANGUAGE_ENGLISH), height=28)

        cmds.setParent("..")

        cmds.separator(height=8, style="in")

        cmds.frameLayout(label=self.tr("section.paths", "Paths"), collapsable=False, marginWidth=8, marginHeight=8)

        cmds.columnLayout(adjustableColumn=True, rowSpacing=4)

        self.path_row("input_folder", "Input Folder", True)

        self.path_row("output_folder", "Output Folder", True)

        self.path_row("report_folder", "Report Folder", True)

        self.path_row("source_rest", "Source Rest Skeleton", False, "FBX Files (*.fbx *.FBX)")

        self.path_row("target_file", "Target Skeleton", False, "FBX Files (*.fbx *.FBX)")

        self.path_row("mapping_json", "Joint Mapping JSON", False, "JSON Files (*.json)")

        cmds.setParent("..")

        cmds.setParent("..")

        cmds.frameLayout(label=self.tr("section.batch", "Batch Options"), collapsable=False, marginWidth=8, marginHeight=8)

        cmds.columnLayout(adjustableColumn=True, rowSpacing=4)

        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=(220, 140))

        cmds.text(label=self.tr("label.max_files", "Max Files (0 = all)"), align="right")

        self.controls["max_files"] = cmds.intField(value=int(self.max_files), minValue=0)

        cmds.setParent("..")

        cmds.setParent("..")

        cmds.setParent("..")

        cmds.frameLayout(label=self.tr("section.actions", "Actions"), collapsable=False, marginWidth=8, marginHeight=8)

        cmds.columnLayout(adjustableColumn=True, rowSpacing=6)

        cmds.rowLayout(numberOfColumns=3, adjustableColumn=1, columnWidth3=(220, 180, 180))

        cmds.button(label=self.tr("button.run_retargeting", "Run Retargeting"), height=38, command=lambda *_: self.run_retargeting())

        cmds.button(label=self.tr("button.save_config", "Save Settings"), height=38, command=lambda *_: self.save_current_settings())

        cmds.button(label=self.tr("button.open_output_folder", "Open Output Folder"), height=38, command=lambda *_: self.open_output_folder())

        cmds.setParent("..")

        cmds.setParent("..")

        cmds.setParent("..")

        self.log_ctrl = cmds.scrollField(editable=False, wordWrap=False, height=210)

        cmds.showWindow(window)

        self.log(self.tr("log.retarget_loaded", "Retargeting is ready."))



    def path_row(self, key: str, label: str, folder: bool, file_filter: str = "All Files (*.*)") -> None:

        cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnWidth3=(180, 430, 80))

        cmds.text(label=self.tr("label." + key, label), align="right")

        self.controls[key] = cmds.textField(text=getattr(self, key))

        cmds.button(label=self.tr("button.browse", "Browse"), command=lambda *_args, k=key, f=folder, ff=file_filter: self.browse(k, f, ff))

        cmds.setParent("..")



    def browse(self, key: str, folder: bool, file_filter: str) -> None:

        if folder:

            result = cmds.fileDialog2(fileMode=3, dialogStyle=2)

        else:

            result = cmds.fileDialog2(fileMode=1, dialogStyle=2, fileFilter=file_filter)

        if result:

            cmds.textField(self.controls[key], edit=True, text=norm_path(result[0]))



    def read(self) -> None:

        for key in ["input_folder", "output_folder", "report_folder", "source_rest", "target_file", "mapping_json"]:

            if key in self.controls:

                setattr(self, key, norm_path(cmds.textField(self.controls[key], query=True, text=True)))

        if "max_files" in self.controls:

            self.max_files = int(cmds.intField(self.controls["max_files"], query=True, value=True))



    def current_settings(self) -> Dict[str, Any]:

        return {

            "input_folder": self.input_folder,

            "output_folder": self.output_folder,

            "report_folder": self.report_folder,

            "source_rest": self.source_rest,

            "target_file": self.target_file,

            "mapping_json": self.mapping_json,

            "max_files": int(self.max_files),

        }



    def save_current_settings(self) -> None:

        self.read()

        save_settings(self.current_settings())

        self.log("Settings saved: %s" % settings_path())



    def make_config(self):

        alpha = self.alpha

        cfg = alpha.ToolConfig()

        cfg.input_folder = norm_path(self.input_folder)

        cfg.output_folder = norm_path(self.output_folder)

        cfg.report_folder = norm_path(self.report_folder)

        cfg.bad_folder = norm_path(os.path.join(os.path.dirname(cfg.output_folder), "BadOrNeedsFix_Retargeting"))

        cfg.good_folder = norm_path(os.path.join(os.path.dirname(cfg.output_folder), "Good_Retargeting"))

        cfg.source_skeleton_file = norm_path(self.source_rest)

        cfg.target_skeleton_file = norm_path(self.target_file)

        cfg.mapping_json = norm_path(self.mapping_json)

        cfg.include_fbx = True

        cfg.include_npz = False

        cfg.recursive_scan = False

        cfg.force_frame_rate = True

        cfg.target_frame_rate = 30.0

        cfg.scan_only = False

        cfg.retarget_enabled = True

        cfg.export_enabled = True

        cfg.correction_enabled = False

        cfg.retarget_method = "humanik_batch"

        cfg.retarget_use_source_rest_file = True

        cfg.auto_find_source_rest_file = True

        cfg.skip_bad_files_before_retarget = False

        cfg.auto_retarget_fallback = False

        cfg.delete_source_after_bake = True

        cfg.export_selected_target_only = True

        cfg.export_force_key_target_joints = True

        cfg.humanik_post_align_root = True

        cfg.humanik_post_align_use_pelvis = True

        cfg.humanik_post_align_use_floor = True

        cfg.humanik_post_align_strength = 1.0

        cfg.humanik_post_align_floor_weight = 0.0

        cfg.humanik_use_rest_characterized_source = True

        cfg.humanik_copy_live_animation_to_rest_source = True

        cfg.humanik_copy_live_fingers_to_rest_source = False

        cfg.humanik_post_matrix_arm_transfer = False

        cfg.humanik_post_source_guided_arm_ik = True

        cfg.alpha_v3_contact_aware_pose_classify = True

        cfg.alpha_v3_lap_up_fraction_threshold = 0.56

        cfg.alpha_v3_clasp_pair_distance_threshold = 18.0

        cfg.alpha_v3_free_pair_distance_threshold = 30.0

        cfg.humanik_source_guided_arm_ik_strength = 1.0

        cfg.humanik_source_guided_arm_ik_pole_strength = 1.0

        cfg.humanik_source_guided_arm_ik_max_pull_units = 95.0

        cfg.humanik_source_guided_arm_ik_reach_limit = 0.94

        cfg.humanik_source_guided_arm_ik_same_side_lock_min_units = 2.0

        cfg.humanik_source_guided_arm_ik_use_virtual_source_rest = True

        cfg.humanik_source_guided_arm_ik_virtual_rest_strength = 1.0

        cfg.humanik_source_guided_arm_ik_use_shoulder_relative_local_mapping = True

        cfg.humanik_source_guided_arm_ik_include_clavicle_chain = False

        cfg.humanik_source_guided_arm_ik_reset_hik_arm_to_rest_before_solve = True

        cfg.humanik_source_guided_arm_ik_preserve_hik_clavicles = True

        cfg.humanik_source_guided_arm_ik_clavicle_hik_rotation_blend = 0.03

        cfg.humanik_source_guided_arm_ik_enable_hand_contact_aim = False

        cfg.humanik_source_guided_arm_ik_enable_source_palm_delta = False

        cfg.humanik_source_guided_arm_ik_enable_soft_clavicle_aim = False

        cfg.humanik_source_guided_arm_ik_transfer_source_fingers = False

        cfg.humanik_source_guided_arm_ik_key_fingers_to_rest = False

        cfg.humanik_source_guided_arm_ik_stabilize_target_finger_correctives = False

        cfg.humanik_source_guided_arm_ik_bake_hand_rotation = False

        cfg.humanik_source_guided_arm_ik_restore_hik_hand_rotation = True

        cfg.humanik_source_guided_arm_ik_enable_anchor_hand_fit = False

        cfg.humanik_source_guided_arm_ik_use_reference_clasp_template = False

        cfg.humanik_source_guided_arm_ik_use_reference_clasp_palm_pose = False

        cfg.humanik_source_guided_arm_ik_use_reference_clasp_finger_template = False

        cfg.humanik_source_guided_arm_ik_use_user_clasp_pose_template = False

        cfg.humanik_source_guided_arm_ik_enable_paired_hand_convergence = False

        cfg.humanik_source_guided_arm_ik_pair_strength = 0.0

        cfg.humanik_source_guided_arm_ik_contact_pose_mode = True

        cfg.humanik_source_guided_arm_ik_contact_min_up_fraction = 0.08

        cfg.humanik_source_guided_arm_ik_contact_max_up_fraction = 0.62

        cfg.humanik_source_guided_arm_ik_contact_max_forward_abs_units = 70.0

        cfg.humanik_source_guided_arm_ik_use_thigh_clearance = False

        cfg.humanik_source_guided_arm_ik_use_analytic_aim_solver = True

        cfg.alpha_v3_enable_lap_palm_roll_fix = False

        cfg.alpha_v3_enable_lap_palm_euler_offset_fix = False

        cfg.alpha_v3_enable_auto_palm_frame_solver = True

        cfg.alpha_v3_auto_palm_use_source_frame = True

        cfg.alpha_v3_strict_source_hand_direction_match = True

        cfg.alpha_v3_auto_palm_frame_blend = 1.0

        cfg.alpha_v3_auto_palm_frame_classes = "LOW_OR_LAP_HANDS,LOW_CLASP_OR_HAND_CONTACT,CHEST_CLASP_OR_HAND_CONTACT"

        cfg.alpha_v3_low_clasp_min_up_fraction = 0.46

        cfg.alpha_v3_lap_palm_force_body_down_normal = True

        cfg.alpha_v3_lap_palm_body_down_blend = 1.0

        cfg.alpha_v3_enable_post_palm_finger_finish = False

        cfg.alpha_v3_post_palm_finger_finish_pair_distance = 24.0

        cfg.alpha_v3_post_palm_finger_finish_blend = 0.42

        cfg.alpha_v3_post_palm_finger_finish_curl_mcp = 22.0

        cfg.alpha_v3_post_palm_finger_finish_curl_pip = 28.0

        cfg.alpha_v3_post_palm_finger_finish_curl_dip = 10.0

        cfg.alpha_v3_enable_wrist_anatomy_guard = False

        cfg.alpha_v3_wrist_anatomy_limit_scale = 1.0

        cfg.alpha_v3_wrist_forward_max_degrees = 95.0

        cfg.alpha_v3_wrist_restore_hik_on_violation = False

        cfg.alpha_v3_auto_palm_temporal_stabilize = True

        cfg.max_files = int(self.max_files or 0)

        return cfg



    def run_retargeting(self) -> None:

        try:

            self.read()

            self.save_current_settings()

            ensure_dir(self.output_folder)

            ensure_dir(self.report_folder)

            cfg = self.make_config()

            ensure_dir(cfg.bad_folder)

            ensure_dir(cfg.good_folder)

            self.log(self.tr("log.retarget_started", "Retargeting started."))

            processor = self.alpha.BatchProcessor(cfg, log_callback=self.log)

            processor.run()

            self.log(self.tr("log.done", "Done."))

        except Exception as exc:

            self.log("ERROR: %s" % exc)

            self.log(traceback.format_exc())



    def open_output_folder(self) -> None:

        self.read()

        folder = ensure_dir(self.output_folder)

        try:

            if sys.platform.startswith("win"):

                os.startfile(folder)

            elif sys.platform == "darwin":

                import subprocess

                subprocess.Popen(["open", folder])

            else:

                import subprocess

                subprocess.Popen(["xdg-open", folder])

        except Exception as exc:

            self.log("Could not open folder: %s" % exc)



    def log(self, message: str) -> None:

        text = "[%s] %s" % (time.strftime("%H:%M:%S"), str(message))

        print(text)

        if self.log_ctrl:

            try:

                old = cmds.scrollField(self.log_ctrl, query=True, text=True) or ""

                new_text = old + text + "\n"

                cmds.scrollField(self.log_ctrl, edit=True, text=new_text)

                try:

                    cmds.scrollField(self.log_ctrl, edit=True, insertionPosition=len(new_text))

                except Exception:

                    pass

            except Exception:

                pass





_UI = None





def show():

    global _UI

    maya_required()

    _UI = ALPHARetargetingUI()

    _UI.show()

    return _UI





if __name__ == "__main__":

    if cmds is not None:

        show()

