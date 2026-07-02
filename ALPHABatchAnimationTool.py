                       



from __future__ import annotations



import os

import re

import sys

import csv

import json

import math

import time

import shutil

import traceback

import datetime

from dataclasses import dataclass, field, asdict

from typing import Dict, List, Optional, Tuple, Any, Iterable



try:

    import maya.cmds as cmds

    import maya.mel as mel

    MAYA_AVAILABLE = True

except Exception:                                        

    cmds = None

    mel = None

    MAYA_AVAILABLE = False



try:

    import numpy as _np                                       

    NUMPY_AVAILABLE = True

except Exception:

    _np = None

    NUMPY_AVAILABLE = False





                                                                               

                      

                                                                               



TOOL_NAME = "ALPHA Batch Animation Tool"

TOOL_VERSION = ""

WINDOW_NAME = "ALPHABatchAnimationToolWindow"



STATUS_GOOD = "GOOD"

STATUS_NEEDS_FIX = "NEEDS_FIX"

STATUS_BAD = "BAD"

STATUS_SKIPPED = "SKIPPED"

STATUS_FAILED = "FAILED"



SEVERITY_INFO = "INFO"

SEVERITY_WARNING = "WARNING"

SEVERITY_ERROR = "ERROR"

SEVERITY_FATAL = "FATAL"



SUPPORTED_FBX_EXTENSIONS = {".fbx"}

SUPPORTED_NPZ_EXTENSIONS = {".npz"}



DEFAULT_REPORT_BASENAME = "ALPHABatchAnimationReport"

AUTHOR_EMAIL = "official@axiox.net"

MAX_UI_LOG_LINES = 5000

TRANSLATION_FILE_NAME = "ALPHA_UI_zh_CN.json"

LANGUAGE_ENGLISH = "en"

LANGUAGE_CHINESE_SIMPLIFIED = "zh_CN"



                                                                                             

                                                                                                 

DEFAULT_JOINT_ALIASES: Dict[str, List[str]] = {

    "root": ["root", "Root", "ROOT", "Hips_Root", "Armature", "Reference"],

    "pelvis": ["pelvis", "Pelvis", "hips", "Hips", "hip", "mixamorig:Hips", "CC_Base_Hip"],

    "spine_01": ["spine_01", "Spine", "spine", "spine1", "Spine1", "mixamorig:Spine", "CC_Base_Spine01"],

    "spine_02": ["spine_02", "Spine1", "spine2", "Spine2", "mixamorig:Spine1", "CC_Base_Spine02"],

    "spine_03": ["spine_03", "Spine2", "spine3", "Spine3", "mixamorig:Spine2", "CC_Base_Spine03"],

    "spine_04": ["spine_04", "Spine3", "spine4", "Spine4", "CC_Base_Spine04"],

    "spine_05": ["spine_05", "Spine4", "spine5", "Spine5", "CC_Base_Spine05"],

    "neck_01": ["neck_01", "Neck", "neck", "neck1", "Neck1", "mixamorig:Neck", "CC_Base_NeckTwist01"],

    "neck_02": ["neck_02", "neck2", "Neck2", "CC_Base_NeckTwist02"],

    "head": ["head", "Head", "mixamorig:Head", "CC_Base_Head"],



    "clavicle_l": ["clavicle_l", "LeftShoulder", "leftShoulder", "l_clavicle", "L_Clavicle", "mixamorig:LeftShoulder", "CC_Base_L_Clavicle"],

    "upperarm_l": ["upperarm_l", "LeftArm", "leftArm", "l_upperarm", "L_UpperArm", "mixamorig:LeftArm", "CC_Base_L_Upperarm"],

    "lowerarm_l": ["lowerarm_l", "LeftForeArm", "leftForeArm", "l_lowerarm", "L_Forearm", "mixamorig:LeftForeArm", "CC_Base_L_Forearm"],

    "hand_l": ["hand_l", "LeftHand", "leftHand", "l_hand", "L_Hand", "mixamorig:LeftHand", "CC_Base_L_Hand"],

    "clavicle_r": ["clavicle_r", "RightShoulder", "rightShoulder", "r_clavicle", "R_Clavicle", "mixamorig:RightShoulder", "CC_Base_R_Clavicle"],

    "upperarm_r": ["upperarm_r", "RightArm", "rightArm", "r_upperarm", "R_UpperArm", "mixamorig:RightArm", "CC_Base_R_Upperarm"],

    "lowerarm_r": ["lowerarm_r", "RightForeArm", "rightForeArm", "r_lowerarm", "R_Forearm", "mixamorig:RightForeArm", "CC_Base_R_Forearm"],

    "hand_r": ["hand_r", "RightHand", "rightHand", "r_hand", "R_Hand", "mixamorig:RightHand", "CC_Base_R_Hand"],



    "thigh_l": ["thigh_l", "LeftUpLeg", "leftUpLeg", "l_thigh", "L_Thigh", "mixamorig:LeftUpLeg", "CC_Base_L_Thigh"],

    "calf_l": ["calf_l", "LeftLeg", "leftLeg", "l_calf", "L_Calf", "mixamorig:LeftLeg", "CC_Base_L_Calf"],

    "foot_l": ["foot_l", "LeftFoot", "leftFoot", "l_foot", "L_Foot", "mixamorig:LeftFoot", "CC_Base_L_Foot"],

    "ball_l": ["ball_l", "LeftToeBase", "leftToeBase", "l_ball", "L_Toe", "mixamorig:LeftToeBase", "CC_Base_L_ToeBase"],

    "thigh_r": ["thigh_r", "RightUpLeg", "rightUpLeg", "r_thigh", "R_Thigh", "mixamorig:RightUpLeg", "CC_Base_R_Thigh"],

    "calf_r": ["calf_r", "RightLeg", "rightLeg", "r_calf", "R_Calf", "mixamorig:RightLeg", "CC_Base_R_Calf"],

    "foot_r": ["foot_r", "RightFoot", "rightFoot", "r_foot", "R_Foot", "mixamorig:RightFoot", "CC_Base_R_Foot"],

    "ball_r": ["ball_r", "RightToeBase", "rightToeBase", "r_ball", "R_Toe", "mixamorig:RightToeBase", "CC_Base_R_ToeBase"],

}



DEFAULT_REQUIRED_CANONICAL = [

    "root", "pelvis", "spine_01", "neck_01", "head",

    "clavicle_l", "upperarm_l", "lowerarm_l", "hand_l",

    "clavicle_r", "upperarm_r", "lowerarm_r", "hand_r",

]



DEFAULT_RETARGET_CANONICAL_ORDER = [

    "root", "pelvis", "spine_01", "spine_02", "spine_03", "spine_04", "spine_05",

    "neck_01", "neck_02", "head",

    "clavicle_l", "upperarm_l", "lowerarm_l", "hand_l",

    "clavicle_r", "upperarm_r", "lowerarm_r", "hand_r",

    "thigh_l", "calf_l", "foot_l", "ball_l",

    "thigh_r", "calf_r", "foot_r", "ball_r",

]



ROTATE_ATTRS = ["rotateX", "rotateY", "rotateZ"]

TRANSLATE_ATTRS = ["translateX", "translateY", "translateZ"]

SCALE_ATTRS = ["scaleX", "scaleY", "scaleZ"]





                                                                 

                                                                       

HIK_BONE_IDS: Dict[str, int] = {

    "root": 0,

    "pelvis": 1,

    "thigh_l": 2,

    "calf_l": 3,

    "foot_l": 4,

    "thigh_r": 5,

    "calf_r": 6,

    "foot_r": 7,

    "spine_01": 8,

    "upperarm_l": 9,

    "lowerarm_l": 10,

    "hand_l": 11,

    "upperarm_r": 12,

    "lowerarm_r": 13,

    "hand_r": 14,

    "head": 15,

    "ball_l": 16,

    "ball_r": 17,

    "clavicle_l": 18,

    "clavicle_r": 19,

    "neck_01": 20,

    "spine_02": 23,

    "spine_03": 24,

}



HIK_REQUIRED_CANONICAL = [

    "pelvis", "spine_01", "head",

    "upperarm_l", "lowerarm_l", "hand_l",

    "upperarm_r", "lowerarm_r", "hand_r",

    "thigh_l", "calf_l", "foot_l",

    "thigh_r", "calf_r", "foot_r",

]





                                                                               

                 

                                                                               



@dataclass

class ScanIssue:

    code: str

    severity: str

    message: str

    joint: str = ""

    frame: Optional[float] = None

    value: Optional[float] = None

    threshold: Optional[float] = None



    def to_dict(self) -> Dict[str, Any]:

        return asdict(self)





@dataclass

class ScanResult:

    file_path: str

    status: str = STATUS_GOOD

    started_at: str = ""

    finished_at: str = ""

    duration_seconds: float = 0.0

    source_type: str = ""

    output_path: str = ""

    issues: List[ScanIssue] = field(default_factory=list)

    stats: Dict[str, Any] = field(default_factory=dict)



    def add_issue(self, code: str, severity: str, message: str,

                  joint: str = "", frame: Optional[float] = None,

                  value: Optional[float] = None, threshold: Optional[float] = None) -> None:

        self.issues.append(ScanIssue(code, severity, message, joint, frame, value, threshold))

        self.status = status_from_issues(self.issues)



    def to_dict(self) -> Dict[str, Any]:

        data = asdict(self)

        data["issues"] = [x.to_dict() for x in self.issues]

        return data





@dataclass

class ToolConfig:

    config_version: str = TOOL_VERSION



           

    input_folder: str = ""

    output_folder: str = ""

    report_folder: str = ""

    bad_folder: str = ""

    good_folder: str = ""

    source_skeleton_file: str = ""

    target_skeleton_file: str = ""

    mapping_json: str = ""

    npz_schema_json: str = ""



                                                                                 

    ui_language: str = LANGUAGE_ENGLISH



                    

    include_fbx: bool = True

    include_npz: bool = True

    recursive_scan: bool = True

    scan_only: bool = False

    retarget_enabled: bool = True

                                                                                                                                       

    correction_enabled: bool = False

    export_enabled: bool = True

    overwrite_outputs: bool = True

    preserve_folder_structure: bool = True

    copy_bad_files: bool = True

    copy_good_files: bool = False

    sort_originals_instead_of_copy: bool = False

    dry_run: bool = False

                                                                                             

                                                                               

    skip_bad_files_before_retarget: bool = False

                                                                                       

                                                                           

    auto_retarget_fallback: bool = False

    max_files: int = 0                



                     

                                                                                              

    force_frame_rate: bool = True

    target_frame_rate: float = 30.0

    sample_every_n_frames: int = 5

    bake_sample_by: float = 1.0



                      

                                                                                                           

    validate_required_bones: bool = False

    validate_empty_clip: bool = True

    validate_animation_length: bool = True

    min_anim_length_frames: float = 2.0

    max_anim_length_frames: float = 6000.0

    validate_scale: bool = True

    min_scale_value: float = 0.001

    max_scale_value: float = 100.0

    validate_extreme_rotation: bool = True

    extreme_rotation_degrees: float = 240.0

    validate_rotation_spikes: bool = True

    rotation_spike_degrees: float = 120.0

    validate_translation_spikes: bool = True

    translation_spike_units: float = 80.0

    validate_root_motion: bool = True

    max_root_offset_units: float = 10000.0

    validate_shoulder_pose: bool = True

    shoulder_raise_angle_degrees: float = 82.0

    validate_neck_pose: bool = True

    neck_extreme_degrees: float = 95.0

    validate_arm_twist: bool = True

    arm_twist_degrees: float = 150.0

    validate_hand_flip: bool = True

    hand_flip_degrees: float = 165.0



                       

    fix_rotation_spikes: bool = True

    fix_translation_spikes: bool = False

    fix_scale_values: bool = True

    fix_shoulder_pose: bool = True

    fix_neck_pose: bool = True

    fix_arm_twist: bool = True

    fix_hand_flip: bool = True

    correction_strength: float = 0.65

    smoothing_passes: int = 1

    conservative_mode: bool = True



                       

                                                                           

                                                                                                        

    retarget_use_point_constraint_for_root: bool = False

    retarget_use_point_constraint_for_pelvis: bool = True

                                                                                                 

                                                                                                   

                                                                                       

                                                                                                    

    retarget_method: str = "humanik_batch"

                                                                                            

                                                                                   

    retarget_use_source_rest_file: bool = True

    auto_find_source_rest_file: bool = True

    require_source_rest_for_matrix_delta: bool = True

    matrix_delta_order: str = "rest_inv_current"                                        

                                                                                   

    retarget_copy_pelvis_translation: bool = True

    retarget_translation_scale: float = 1.0

                                                                                                                         

    retarget_maintain_offset: bool = True

    retarget_rotate_order: str = "xyz"

    delete_source_after_bake: bool = True

    fail_if_no_target_animation: bool = True

    export_selected_target_only: bool = True

    export_include_target_meshes: bool = True

    export_force_key_target_joints: bool = True

    export_validate_file: bool = True



                                                                                   

                                                                                

                                                                                    

                                                                                     

                                                       

    humanik_post_align_root: bool = True

    humanik_post_align_use_pelvis: bool = True

    humanik_post_align_use_floor: bool = True

    humanik_post_align_strength: float = 1.0

    humanik_post_align_floor_weight: float = 0.35

                                                                                    

                                                                                      

                                                                                     

                                                                          

    humanik_use_compressed_femalestd_spine_slots: bool = True

                                                                                     

                                                                                      

                                                                                  

    humanik_force_pelvis_world_match: bool = True

    humanik_pelvis_world_match_strength: float = 1.0

    humanik_log_alignment_samples: bool = True

                                                                                   

                                                                                           

                                                                                           

                                                                                  

                                                                                         

                                                                              

    humanik_use_rest_characterized_source: bool = True

    humanik_copy_live_animation_to_rest_source: bool = True

    humanik_copy_all_source_translates_to_rest_source: bool = False



                                                                                           

                                                                                              

                                                                                              

                                                                                               

    humanik_pre_calibrate_target_arm_reference_pose: bool = False

    humanik_pre_calibrate_target_arm_reference_pose_strength: float = 1.0

                                                                                               

                                                                                            

                                                                                              

                                 

    humanik_apply_inverse_reference_pose_offset_to_arms: bool = False



                                                                                              

                                                                                        

                                                                                        

                                                                                    

                                                          

    humanik_post_matrix_arm_transfer: bool = False

    humanik_matrix_arm_transfer_include_clavicles: bool = True

    humanik_matrix_arm_transfer_include_hands: bool = True

    humanik_matrix_arm_transfer_preserve_translates: bool = True

    humanik_matrix_arm_transfer_filter_curves: bool = True

    humanik_matrix_arm_transfer_order: str = "target_rest_source_delta"



                                                                                     

                                                                                  

    humanik_post_source_guided_arm_ik: bool = True

    humanik_source_guided_arm_ik_strength: float = 1.0

    humanik_source_guided_arm_ik_pole_strength: float = 0.82

    humanik_source_guided_arm_ik_max_pull_units: float = 115.0

    humanik_source_guided_arm_ik_reach_limit: float = 0.94

    humanik_source_guided_arm_ik_same_side_lock_min_units: float = 6.0

    humanik_source_guided_arm_ik_key_fingers_to_rest: bool = False

                                                                                                            

                                                                                            

    humanik_source_guided_arm_ik_bake_hand_rotation: bool = False

    humanik_source_guided_arm_ik_restore_hik_hand_rotation: bool = True

                                                                  

                                                                                            

                                                                                         

                                                                                            

                                                                

    alpha_v3_enable_lap_palm_roll_fix: bool = False                                      

    alpha_v3_lap_palm_roll_l: float = 0.0                                               

    alpha_v3_lap_palm_roll_r: float = 0.0                                               

    alpha_v3_lap_palm_roll_axis: str = "rotateX"                                        

    alpha_v3_enable_lap_palm_euler_offset_fix: bool = False                                      

    alpha_v3_lap_palm_offset_x_l: float = 0.0

    alpha_v3_lap_palm_offset_y_l: float = 0.0

    alpha_v3_lap_palm_offset_z_l: float = 0.0

    alpha_v3_lap_palm_offset_x_r: float = 0.0

    alpha_v3_lap_palm_offset_y_r: float = 0.0

    alpha_v3_lap_palm_offset_z_r: float = 0.0

    alpha_v3_enable_auto_palm_frame_solver: bool = False

                                                                                            

                                                                                          

                                                                                                                

                                                                                         

                                                                                             

                                                                                         

    alpha_v3_auto_palm_use_source_frame: bool = False

                                                                                                

                                                                                               

                                                                                                                

    alpha_v3_strict_source_hand_direction_match: bool = False

                                                                                              

                                                                                                

                                                                                        

    alpha_v3_lap_palm_force_body_down_normal: bool = True

    alpha_v3_lap_palm_body_down_blend: float = 1.0

    alpha_v3_auto_palm_frame_blend: float = 1.0

                                                                                                         

                                                                                                 

                                                                                                  

                                             

    alpha_v3_auto_palm_frame_classes: str = "LOW_OR_LAP_HANDS,LOW_CLASP_OR_HAND_CONTACT,CHEST_CLASP_OR_HAND_CONTACT"

    alpha_v3_low_clasp_min_up_fraction: float = 0.46

    alpha_v3_enable_post_palm_finger_finish: bool = False

    alpha_v3_post_palm_finger_finish_pair_distance: float = 24.0

    alpha_v3_post_palm_finger_finish_blend: float = 0.42

    alpha_v3_post_palm_finger_finish_curl_mcp: float = 22.0

    alpha_v3_post_palm_finger_finish_curl_pip: float = 28.0

    alpha_v3_post_palm_finger_finish_curl_dip: float = 10.0

    alpha_v3_enable_wrist_anatomy_guard: bool = False

    alpha_v3_wrist_anatomy_limit_scale: float = 1.05

    alpha_v3_wrist_forward_max_degrees: float = 95.0

    alpha_v3_auto_palm_temporal_stabilize: bool = True

                                                                                                   

                                                                                                              

                                           

    humanik_source_guided_arm_ik_use_virtual_source_rest: bool = True

    humanik_source_guided_arm_ik_virtual_rest_strength: float = 1.0

                                                                                           

                                                                                                

                                                                                               

                                                                            

    humanik_source_guided_arm_ik_invert_forward_axis: bool = False

                                                                                        

                                                                                      

                                                                                                   

    humanik_source_guided_arm_ik_use_shoulder_relative_local_mapping: bool = True

                                                                                 

                                                                                                               

                                                                                                                         

    humanik_source_guided_arm_ik_include_clavicle_chain: bool = False

                                                                                        

                                                                                                      

    humanik_source_guided_arm_ik_reset_hik_arm_to_rest_before_solve: bool = True

                                                                                         

                                                                                                     

                                                                          

    humanik_source_guided_arm_ik_preserve_hik_clavicles: bool = True

                                                                                                                      

                                                                                                        

    humanik_source_guided_arm_ik_clavicle_hik_rotation_blend: float = 0.05

                                                                                                        

                                                                                                        

                                                                                                                  

                                                         

    humanik_source_guided_arm_ik_enable_hand_contact_aim: bool = False

                                                                                       

                                                                                         

                                                                                              

    humanik_source_guided_arm_ik_hand_contact_aim_rotation_blend: float = 0.0

                                                                                            

                                                                                                                   

    humanik_source_guided_arm_ik_enable_source_palm_delta: bool = False

    humanik_source_guided_arm_ik_source_palm_delta_blend: float = 0.0

    humanik_source_guided_arm_ik_source_palm_delta_clamp_degrees: float = 0.0

                                                                                          

                                                                                       

                                                                                          

    humanik_source_guided_arm_ik_enable_soft_clavicle_aim: bool = False

    humanik_source_guided_arm_ik_soft_clavicle_aim_strength: float = 0.00

                                                                                          

                                                                                                      

                                                                                                 

                                                                                                  

                                                                                                       

                                                  

    humanik_copy_live_fingers_to_rest_source: bool = False

    humanik_source_guided_arm_ik_transfer_source_fingers: bool = False

    humanik_source_guided_arm_ik_source_finger_rotation_blend: float = 0.12

                                                                                                       

                                                                                                        

    humanik_source_guided_arm_ik_source_finger_delta_clamp_degrees: float = 10.0

                                                                                                       

                                                                                                         

                                                                                                

    humanik_source_guided_arm_ik_hand_aim_maintain_offset: bool = True

    humanik_source_guided_arm_ik_finger_axis_mode: str = "bend_only"

    humanik_source_guided_arm_ik_finger_bend_axis_blend: float = 0.18

    humanik_source_guided_arm_ik_finger_splay_axis_blend: float = 0.0

    humanik_source_guided_arm_ik_reference_clasp_finger_curl_boost_degrees: float = 2.0

    humanik_source_guided_arm_ik_stabilize_target_finger_correctives: bool = False

                                                                                                      

                                                                                                                              

    humanik_source_guided_arm_ik_enable_anchor_hand_fit: bool = True

    humanik_source_guided_arm_ik_anchor_hand: str = "l"

    humanik_source_guided_arm_ik_anchor_hand_strength: float = 0.82

    humanik_source_guided_arm_ik_follower_hand_strength: float = 0.88

    humanik_source_guided_arm_ik_enable_palm_frame_diagnostics: bool = True

                                                                                                          

                                                                                                                

                                                                                                             

                                                                                                              

    humanik_source_guided_arm_ik_use_reference_clasp_template: bool = False

    humanik_source_guided_arm_ik_reference_clasp_center_up_lift_units: float = 0.0

    humanik_source_guided_arm_ik_reference_clasp_center_min_fraction: float = 0.61

    humanik_source_guided_arm_ik_reference_clasp_center_max_fraction: float = 0.70

    humanik_source_guided_arm_ik_reference_clasp_forward_offset_units: float = -0.75

    humanik_source_guided_arm_ik_reference_clasp_pair_distance: float = 10.75

    humanik_source_guided_arm_ik_reference_clasp_left_up_offset: float = 0.85

    humanik_source_guided_arm_ik_reference_clasp_right_up_offset: float = -0.85

    humanik_source_guided_arm_ik_reference_clasp_left_forward_offset: float = -0.65

    humanik_source_guided_arm_ik_reference_clasp_right_forward_offset: float = 0.65

    humanik_source_guided_arm_ik_reference_clasp_strength: float = 0.0

                                                                                                         

                                                                                                                 

    humanik_source_guided_arm_ik_use_reference_clasp_palm_pose: bool = True

    humanik_source_guided_arm_ik_reference_clasp_palm_pose_blend: float = 0.58

    humanik_source_guided_arm_ik_reference_clasp_left_hand_offset: Tuple[float, float, float] = (0.0, -11.0, 13.0)

    humanik_source_guided_arm_ik_reference_clasp_right_hand_offset: Tuple[float, float, float] = (0.0, 11.0, -13.0)

                                                                                                      

                                                                                     

    humanik_source_guided_arm_ik_use_reference_clasp_finger_template: bool = True

    humanik_source_guided_arm_ik_reference_clasp_finger_template_blend: float = 0.72

    humanik_source_guided_arm_ik_reference_clasp_finger_mcp_curl: float = 28.0

    humanik_source_guided_arm_ik_reference_clasp_finger_pip_curl: float = 34.0

    humanik_source_guided_arm_ik_reference_clasp_finger_dip_curl: float = 14.0

    humanik_source_guided_arm_ik_reference_clasp_thumb_blend: float = 0.18

                                                                                                     

                                                                                                 

                                                                                              

                                                                                                 

                                                                                                 

    humanik_source_guided_arm_ik_use_user_clasp_pose_template: bool = True

    humanik_source_guided_arm_ik_user_clasp_pose_template_path: str = ""

    humanik_source_guided_arm_ik_user_clasp_pose_template_blend: float = 1.0

    humanik_source_guided_arm_ik_user_clasp_pose_template_apply_hands: bool = True

    humanik_source_guided_arm_ik_user_clasp_pose_template_apply_fingers: bool = True

    humanik_source_guided_arm_ik_user_clasp_pose_template_apply_correctives: bool = False

    humanik_source_guided_arm_ik_user_clasp_pose_template_apply_clavicles: bool = True

    humanik_source_guided_arm_ik_user_clasp_pose_template_apply_arm_chain: bool = True



                                                                                           

                                                                                          

                                                                                                 

                                                                                             

                                                                                                 

    humanik_source_guided_arm_ik_user_clasp_pose_template_use_delta: bool = True

    humanik_source_guided_arm_ik_user_clasp_pose_template_pose_match: bool = True

                                                                                                        

                                                                                         

    humanik_source_guided_arm_ik_user_clasp_pose_template_center_threshold: float = 3.0

    humanik_source_guided_arm_ik_user_clasp_pose_template_wrist_threshold: float = 4.0

    humanik_source_guided_arm_ik_user_clasp_pose_template_elbow_threshold: float = 5.0

    humanik_source_guided_arm_ik_user_clasp_pose_template_pair_threshold: float = 2.0

    humanik_source_guided_arm_ik_user_clasp_pose_template_rotation_threshold: float = 18.0

    humanik_source_guided_arm_ik_user_clasp_pose_template_require_driver: bool = True

    humanik_source_guided_arm_ik_user_clasp_pose_template_lock_to_source_file: bool = True

    humanik_source_guided_arm_ik_skip_custom_arm_solver_on_template_source_mismatch: bool = False

    humanik_source_guided_arm_ik_current_source_file_path: str = ""

    humanik_source_guided_arm_ik_save_pre_user_template_raw_cache: bool = True

                                                                                                                            

                                                                                                                                            

    humanik_source_guided_arm_ik_use_thigh_clearance: bool = True

    humanik_source_guided_arm_ik_thigh_clearance_units: float = 14.0

    humanik_source_guided_arm_ik_thigh_clearance_up_bias: float = 0.85



                                                                                                              

                                                                                                   

                                                                                                     

                                                                        

    humanik_source_guided_arm_ik_enable_paired_hand_convergence: bool = True

    humanik_source_guided_arm_ik_pair_source_distance_threshold: float = 28.0

    humanik_source_guided_arm_ik_pair_strength: float = 0.68

    humanik_source_guided_arm_ik_pair_distance_scale: float = 0.85

    humanik_source_guided_arm_ik_pair_min_distance: float = 12.0

    humanik_source_guided_arm_ik_pair_max_distance: float = 20.0

    humanik_source_guided_arm_ik_pair_center_blend: float = 0.62

    humanik_source_guided_arm_ik_pair_chest_height_bias: float = 0.74

    humanik_source_guided_arm_ik_pair_max_target_pull_units: float = 12.0

                                                                                                   

                                                                                          

    humanik_source_guided_arm_ik_contact_pose_mode: bool = True

    humanik_source_guided_arm_ik_contact_use_source_center_absolute: bool = True

    humanik_source_guided_arm_ik_contact_body_scale: bool = True

    humanik_source_guided_arm_ik_contact_elbow_side_guard: bool = True

    humanik_source_guided_arm_ik_contact_elbow_side_margin_units: float = 3.0

    humanik_source_guided_arm_ik_contact_min_up_fraction: float = 0.42

    humanik_source_guided_arm_ik_contact_max_up_fraction: float = 0.78

    humanik_source_guided_arm_ik_contact_max_forward_abs_units: float = 48.0

                                                                                                                     

    humanik_source_guided_arm_ik_use_analytic_aim_solver: bool = True



                                                                                                          

                                                                                                                 

    humanik_arm_diagnostics_enabled: bool = True

    humanik_arm_diagnostics_include_rest_report: bool = True

    humanik_arm_diagnostics_include_final_after_bake: bool = True

    humanik_arm_diagnostics_max_sample_frames: int = 5





                                                                                         

                                                                                                    

                                                                                                

    humanik_post_override_arms_from_source: bool = False

    humanik_arm_override_include_clavicles: bool = False

    humanik_arm_override_include_hands: bool = False

    humanik_arm_override_key_fingers_to_rest: bool = False



                                                                                             

                                                                                          

                                                                                        

                                                                                     

    humanik_post_match_hands: bool = False

    humanik_hand_match_strength: float = 0.25

    humanik_hand_match_pole_strength: float = 0.25

    humanik_hand_match_max_pull_units: float = 12.0

    humanik_hand_match_reach_limit: float = 0.90

    humanik_hand_match_key_fingers_to_rest: bool = False



                                                                                           

                                                                                                

                                                                      

    humanik_post_correct_hands_to_leg_front: bool = False

    humanik_hand_front_strength: float = 0.85

    humanik_hand_front_side_strength: float = 1.00

    humanik_hand_front_up_strength: float = 0.10

    humanik_hand_front_max_pull_units: float = 110.0

    humanik_hand_front_reach_limit: float = 0.95

    humanik_hand_front_min_knee_fraction: float = 0.38

                                                                                           

    humanik_hand_front_same_side_lock_min_units: float = 18.0



                                                                                                                               

                                                                                     

                                                                                   

                                                                                

    humanik_post_refine_limbs: bool = False

    humanik_post_refine_hands: bool = False

    humanik_post_refine_feet: bool = False

    humanik_post_refine_poles: bool = False

    humanik_post_refine_strength: float = 0.0

    humanik_post_refine_arm_strength: float = 0.0

    humanik_post_refine_leg_strength: float = 0.0

    humanik_post_refine_pole_strength: float = 0.0



                                                              

    shoulder_clamp_axes: str = "XYZ"

    neck_clamp_axes: str = "XYZ"

    arm_twist_axis: str = "X"

    hand_flip_axes: str = "XYZ"



                                                                                 

    required_canonical_bones: str = ",".join(DEFAULT_REQUIRED_CANONICAL)



    def to_dict(self) -> Dict[str, Any]:

        return asdict(self)



    @classmethod

    def from_dict(cls, data: Dict[str, Any]) -> "ToolConfig":

        cfg = cls()

        data = data or {}

        for key, value in data.items():

            if hasattr(cfg, key):

                setattr(cfg, key, value)



                                                                                   

                                                                                           

                                                                                      

        if data.get("config_version") != TOOL_VERSION:

            cfg.force_frame_rate = True

            cfg.target_frame_rate = 30.0

            cfg.retarget_maintain_offset = True

            cfg.retarget_use_point_constraint_for_root = False

            cfg.retarget_use_point_constraint_for_pelvis = True

            cfg.retarget_method = "humanik_batch"

            cfg.retarget_use_source_rest_file = True

            cfg.auto_find_source_rest_file = True

            cfg.require_source_rest_for_matrix_delta = True

            cfg.matrix_delta_order = "target_rest_delta"

            cfg.retarget_copy_pelvis_translation = True

            cfg.retarget_translation_scale = 1.0

            cfg.delete_source_after_bake = True

            cfg.fail_if_no_target_animation = True

            cfg.export_selected_target_only = True

            cfg.export_force_key_target_joints = True

            cfg.humanik_post_align_root = True

            cfg.humanik_post_align_use_pelvis = True

            cfg.humanik_post_align_use_floor = True

            cfg.humanik_post_align_strength = 1.0

            cfg.humanik_post_align_floor_weight = 0.0

            cfg.humanik_use_compressed_femalestd_spine_slots = True

            cfg.humanik_force_pelvis_world_match = True

            cfg.humanik_pelvis_world_match_strength = 1.0

            cfg.humanik_log_alignment_samples = True

            cfg.humanik_pre_calibrate_target_arm_reference_pose = False

            cfg.humanik_apply_inverse_reference_pose_offset_to_arms = False

            cfg.humanik_post_source_guided_arm_ik = True

            cfg.humanik_source_guided_arm_ik_strength = 1.0

            cfg.humanik_source_guided_arm_ik_pole_strength = 0.82

            cfg.humanik_source_guided_arm_ik_max_pull_units = 115.0

            cfg.humanik_source_guided_arm_ik_reach_limit = 0.94

            cfg.humanik_source_guided_arm_ik_same_side_lock_min_units = 6.0

            cfg.humanik_source_guided_arm_ik_key_fingers_to_rest = False

            cfg.humanik_source_guided_arm_ik_bake_hand_rotation = False

            cfg.humanik_source_guided_arm_ik_restore_hik_hand_rotation = True

            cfg.humanik_source_guided_arm_ik_use_virtual_source_rest = True

            cfg.humanik_source_guided_arm_ik_virtual_rest_strength = 1.0

            cfg.humanik_source_guided_arm_ik_invert_forward_axis = False

            cfg.humanik_source_guided_arm_ik_use_shoulder_relative_local_mapping = True

            cfg.humanik_source_guided_arm_ik_include_clavicle_chain = False

            cfg.humanik_source_guided_arm_ik_reset_hik_arm_to_rest_before_solve = True

            cfg.humanik_source_guided_arm_ik_preserve_hik_clavicles = True

            cfg.humanik_source_guided_arm_ik_clavicle_hik_rotation_blend = 0.05

            cfg.humanik_source_guided_arm_ik_enable_hand_contact_aim = False

            cfg.humanik_source_guided_arm_ik_hand_contact_aim_rotation_blend = 0.0

            cfg.humanik_source_guided_arm_ik_enable_source_palm_delta = False

            cfg.humanik_source_guided_arm_ik_source_palm_delta_blend = 0.0

            cfg.humanik_source_guided_arm_ik_source_palm_delta_clamp_degrees = 0.0

            cfg.humanik_source_guided_arm_ik_enable_soft_clavicle_aim = False

            cfg.humanik_source_guided_arm_ik_soft_clavicle_aim_strength = 0.00

            cfg.humanik_copy_live_fingers_to_rest_source = False

            cfg.humanik_source_guided_arm_ik_transfer_source_fingers = False

            cfg.humanik_source_guided_arm_ik_source_finger_rotation_blend = 0.12

            cfg.humanik_source_guided_arm_ik_source_finger_delta_clamp_degrees = 10.0

            cfg.humanik_source_guided_arm_ik_hand_aim_maintain_offset = True

            cfg.humanik_source_guided_arm_ik_enable_anchor_hand_fit = True

            cfg.humanik_source_guided_arm_ik_anchor_hand = "l"

            cfg.humanik_source_guided_arm_ik_anchor_hand_strength = 0.82

            cfg.humanik_source_guided_arm_ik_follower_hand_strength = 0.88

            cfg.humanik_source_guided_arm_ik_enable_palm_frame_diagnostics = True

            cfg.humanik_source_guided_arm_ik_use_reference_clasp_template = False

            cfg.humanik_source_guided_arm_ik_reference_clasp_center_up_lift_units = 0.0

            cfg.humanik_source_guided_arm_ik_reference_clasp_center_min_fraction = 0.61

            cfg.humanik_source_guided_arm_ik_reference_clasp_center_max_fraction = 0.70

            cfg.humanik_source_guided_arm_ik_reference_clasp_forward_offset_units = -0.75

            cfg.humanik_source_guided_arm_ik_reference_clasp_pair_distance = 10.75

            cfg.humanik_source_guided_arm_ik_reference_clasp_left_up_offset = 0.85

            cfg.humanik_source_guided_arm_ik_reference_clasp_right_up_offset = -0.85

            cfg.humanik_source_guided_arm_ik_reference_clasp_left_forward_offset = -0.65

            cfg.humanik_source_guided_arm_ik_reference_clasp_right_forward_offset = 0.65

            cfg.humanik_source_guided_arm_ik_reference_clasp_strength = 0.0

            cfg.humanik_source_guided_arm_ik_use_reference_clasp_palm_pose = True

            cfg.humanik_source_guided_arm_ik_reference_clasp_palm_pose_blend = 0.58

            cfg.humanik_source_guided_arm_ik_reference_clasp_left_hand_offset = (0.0, -11.0, 13.0)

            cfg.humanik_source_guided_arm_ik_reference_clasp_right_hand_offset = (0.0, 11.0, -13.0)

            cfg.humanik_source_guided_arm_ik_use_reference_clasp_finger_template = True

            cfg.humanik_source_guided_arm_ik_reference_clasp_finger_template_blend = 0.72

            cfg.humanik_source_guided_arm_ik_reference_clasp_finger_mcp_curl = 28.0

            cfg.humanik_source_guided_arm_ik_reference_clasp_finger_pip_curl = 34.0

            cfg.humanik_source_guided_arm_ik_reference_clasp_finger_dip_curl = 14.0

            cfg.humanik_source_guided_arm_ik_reference_clasp_thumb_blend = 0.18

            cfg.humanik_source_guided_arm_ik_finger_axis_mode = "bend_only"

            cfg.humanik_source_guided_arm_ik_finger_bend_axis_blend = 0.18

            cfg.humanik_source_guided_arm_ik_finger_splay_axis_blend = 0.0

            cfg.humanik_source_guided_arm_ik_reference_clasp_finger_curl_boost_degrees = 2.0

            cfg.humanik_source_guided_arm_ik_stabilize_target_finger_correctives = False

            cfg.alpha_v3_enable_auto_palm_frame_solver = False

            cfg.alpha_v3_auto_palm_use_source_frame = False

            cfg.alpha_v3_enable_post_palm_finger_finish = False

            cfg.humanik_source_guided_arm_ik_use_thigh_clearance = True

            cfg.humanik_source_guided_arm_ik_thigh_clearance_units = 14.0

            cfg.humanik_source_guided_arm_ik_thigh_clearance_up_bias = 0.85

            cfg.humanik_source_guided_arm_ik_enable_paired_hand_convergence = True

            cfg.humanik_source_guided_arm_ik_pair_source_distance_threshold = 28.0

            cfg.humanik_source_guided_arm_ik_pair_strength = 0.68

            cfg.humanik_source_guided_arm_ik_pair_distance_scale = 0.85

            cfg.humanik_source_guided_arm_ik_pair_min_distance = 12.0

            cfg.humanik_source_guided_arm_ik_pair_max_distance = 20.0

            cfg.humanik_source_guided_arm_ik_pair_center_blend = 0.62

            cfg.humanik_source_guided_arm_ik_pair_chest_height_bias = 0.74

            cfg.humanik_source_guided_arm_ik_pair_max_target_pull_units = 12.0

            cfg.humanik_post_override_arms_from_source = False

            cfg.humanik_arm_override_include_clavicles = False

            cfg.humanik_arm_override_include_hands = False

            cfg.humanik_arm_override_key_fingers_to_rest = False

            cfg.humanik_post_correct_hands_to_leg_front = False

            cfg.humanik_post_match_hands = False

            cfg.humanik_hand_match_strength = 0.25

            cfg.humanik_hand_match_pole_strength = 0.25

            cfg.humanik_hand_match_max_pull_units = 12.0

            cfg.humanik_hand_match_reach_limit = 0.90

            cfg.humanik_hand_match_key_fingers_to_rest = False

            cfg.humanik_post_refine_limbs = False

            cfg.humanik_post_refine_hands = False

            cfg.humanik_post_refine_feet = False

            cfg.humanik_post_refine_poles = False

            cfg.humanik_post_refine_strength = 0.0

            cfg.humanik_post_refine_arm_strength = 0.0

            cfg.humanik_post_refine_leg_strength = 0.0

            cfg.humanik_post_refine_pole_strength = 0.0

            cfg.skip_bad_files_before_retarget = False

            cfg.auto_retarget_fallback = False

            cfg.export_enabled = True

            cfg.retarget_enabled = True

            cfg.validate_required_bones = False

                                                                                                       

                                                  

            cfg.correction_enabled = False

        cfg.config_version = TOOL_VERSION

        return cfg





                                                                               

                   

                                                                               



def now_iso() -> str:

    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")





def normalize_path(path: str) -> str:

    if not path:

        return ""

    return os.path.normpath(os.path.expandvars(os.path.expanduser(path))).replace("\\", "/")





def ensure_dir(path: str) -> str:

    path = normalize_path(path)

    if path and not os.path.isdir(path):

        os.makedirs(path, exist_ok=True)

    return path





def safe_filename(name: str) -> str:

    name = re.sub(r"[^A-Za-z0-9_.\-]+", "_", name)

    return name.strip("._") or "unnamed"





def clamp(value: float, min_value: float, max_value: float) -> float:

    return max(min_value, min(max_value, value))





def is_finite(value: Any) -> bool:

    try:

        return math.isfinite(float(value))

    except Exception:

        return False





def angular_delta(a: float, b: float) -> float:

    return (b - a + 180.0) % 360.0 - 180.0





def vector_sub(a: Iterable[float], b: Iterable[float]) -> Tuple[float, float, float]:

    ax, ay, az = a

    bx, by, bz = b

    return ax - bx, ay - by, az - bz





def vector_len(v: Iterable[float]) -> float:

    x, y, z = v

    return math.sqrt(x * x + y * y + z * z)





def vector_dot(a: Iterable[float], b: Iterable[float]) -> float:

    ax, ay, az = a

    bx, by, bz = b

    return ax * bx + ay * by + az * bz





def vector_angle_degrees(a: Iterable[float], b: Iterable[float]) -> float:

    la = vector_len(a)

    lb = vector_len(b)

    if la <= 1e-8 or lb <= 1e-8:

        return 0.0

    d = clamp(vector_dot(a, b) / (la * lb), -1.0, 1.0)

    return math.degrees(math.acos(d))





def strip_namespace(node: str) -> str:

    return node.split(":")[-1] if node else node





def short_name(node: str) -> str:

    return strip_namespace(node.split("|")[-1]) if node else node





def quote_mel_path(path: str) -> str:

    return normalize_path(path).replace('"', '\\"')





def status_from_issues(issues: List[ScanIssue]) -> str:

    severities = {issue.severity for issue in issues}

    if SEVERITY_FATAL in severities:

        return STATUS_BAD

    if SEVERITY_ERROR in severities:

        return STATUS_BAD

    if SEVERITY_WARNING in severities:

        return STATUS_NEEDS_FIX

    return STATUS_GOOD





def config_default_path() -> str:

    if MAYA_AVAILABLE:

        prefs = cmds.internalVar(userPrefDir=True)

        return normalize_path(os.path.join(prefs, "ALPHABatchAnimationTool_config.json"))

    return normalize_path(os.path.join(os.path.expanduser("~"), "ALPHABatchAnimationTool_config.json"))





def parse_csv_text(value: str) -> List[str]:

    return [x.strip() for x in (value or "").split(",") if x.strip()]





def relative_output_path(input_file: str, input_folder: str, output_folder: str, extension: str = ".fbx") -> str:

    input_file = normalize_path(input_file)

    input_folder = normalize_path(input_folder)

    output_folder = normalize_path(output_folder)

    try:

        rel = os.path.relpath(input_file, input_folder)

    except Exception:

        rel = os.path.basename(input_file)

    rel_no_ext = os.path.splitext(rel)[0]

    return normalize_path(os.path.join(output_folder, rel_no_ext + extension))









def script_directory() -> str:

    try:

        return normalize_path(os.path.dirname(os.path.abspath(__file__)))

    except Exception:

        return normalize_path(os.getcwd())





def find_existing_file_by_names(names: List[str], search_dirs: List[str]) -> str:

    clean_names = [n for n in (names or []) if n]

    clean_dirs = []

    for d in search_dirs or []:

        d = normalize_path(d)

        if d and os.path.isdir(d) and d not in clean_dirs:

            clean_dirs.append(d)

    for d in clean_dirs:

        for name in clean_names:

            candidate = normalize_path(os.path.join(d, name))

            if os.path.isfile(candidate):

                return candidate

                                                                                                      

    for d in clean_dirs:

        base = os.path.basename(d).lower()

        if base not in {"alphamayabatchanimtool_v1_0_6", "alphamayabatchanimtool_v1_0_5", "presets", "smplh_femalestd", "smplh"}:

            continue

        try:

            for root, _, files in os.walk(d):

                for f in files:

                    for name in clean_names:

                        if f.lower() == os.path.basename(name).lower():

                            return normalize_path(os.path.join(root, f))

        except Exception:

            pass

    return ""



def load_json_file(path: str) -> Dict[str, Any]:

    path = normalize_path(path)

    if not path or not os.path.isfile(path):

        return {}

    with open(path, "r", encoding="utf-8") as handle:

        return json.load(handle)





def save_json_file(path: str, data: Any) -> None:

    ensure_dir(os.path.dirname(path))

    with open(path, "w", encoding="utf-8") as handle:

        json.dump(data, handle, indent=4, ensure_ascii=False)







                                                                               

                               

                                                                               



def is_real_joint_mapping_json(path: str) -> bool:

    try:

        data = load_json_file(path)

    except Exception:

        return False

    if not isinstance(data, dict):

        return False

    joints = data.get("joints")

    return isinstance(joints, dict) and len(joints) >= 8





def looks_like_safe_config_json(path: str) -> bool:

    path = normalize_path(path)

    name = os.path.basename(path).lower()

    if "safe_config" in name:

        return True

    try:

        data = load_json_file(path)

    except Exception:

        return False

    return isinstance(data, dict) and "mapping_json" in data and "joints" not in data





def resolve_real_mapping_json(path: str, search_dirs: Optional[List[str]] = None, log_callback=None) -> str:

    original_path = normalize_path(path or "")

    if original_path and is_real_joint_mapping_json(original_path):

        return original_path



    dirs: List[str] = []

    for d in (search_dirs or []):

        if d:

            nd = normalize_path(d)

            if nd and nd not in dirs:

                dirs.append(nd)

    if original_path:

        d = normalize_path(os.path.dirname(original_path))

        if d and d not in dirs:

            dirs.insert(0, d)

    tool_dir = script_directory()

    for d in [tool_dir, os.path.join(tool_dir, "Presets"), os.path.join(tool_dir, "Presets", "SMPLH_FemaleStd")]:

        nd = normalize_path(d)

        if nd not in dirs:

            dirs.append(nd)



                                                                   

    candidate = ""

    if original_path and os.path.isfile(original_path):

        try:

            data = load_json_file(original_path)

            if isinstance(data, dict):

                candidate = data.get("mapping_json") or ""

        except Exception:

            candidate = ""

    if candidate:

        candidates = []

        c = normalize_path(candidate)

        candidates.append(c)

        if not os.path.isabs(c):

            if original_path:

                candidates.append(normalize_path(os.path.join(os.path.dirname(original_path), c)))

            candidates.append(normalize_path(os.path.join(tool_dir, c)))

        for cpath in candidates:

            if is_real_joint_mapping_json(cpath):

                if log_callback:

                    log_callback("Joint Mapping JSON was a config file. Auto-resolved real mapping: %s" % cpath)

                return cpath



                             

    found = find_existing_file_by_names([

        "smplh_to_femalestd_body_mapping.json",

        "SMPLH_to_FemaleStd_body_mapping.json",

        "body_mapping.json",

    ], dirs)

    if found and is_real_joint_mapping_json(found):

        if log_callback:

            log_callback("Auto-resolved Joint Mapping JSON: %s" % found)

        return found



    return original_path



                                                                               

                 

                                                                               



                                                                                   

                                                                                  

DEFAULT_ZH_CN_TRANSLATIONS: Dict[str, str] = {

    "tool_window_title": "ALPHA 批量动画工具",

    "header": "Maya 2024 批量动画扫描 / 重定向 / 修正工具",

    "button.change_to_chinese": "切换到中文",

    "button.change_to_english": "Change To English",

    "section.progress": "批处理进度",

    "progress.ready": "就绪",

    "section.paths": "1. 路径",

    "section.batch": "2. 批处理选项",

    "section.validation": "3. 验证 / 扫描规则",

    "section.correction": "4. 自动修正流程",

    "section.retarget": "5. 重定向 / 导出选项",

    "section.actions": "6. 操作",

    "label.input_folder": "输入文件夹",

    "label.output_folder": "输出文件夹",

    "label.report_folder": "报告文件夹",

    "label.bad_folder": "错误 / 需修正文件夹",

    "label.good_folder": "正常文件夹",

    "label.source_skeleton_file": "源骨架文件",

    "label.target_skeleton_file": "目标骨架文件",

    "label.mapping_json": "关节映射 JSON",

    "label.npz_schema_json": "NPZ 结构 JSON",

    "label.include_fbx": "包含 FBX",

    "label.include_npz": "包含 NPZ",

    "label.recursive_scan": "递归扫描",

    "label.scan_only": "仅扫描 - 不重定向/导出",

    "label.retarget_enabled": "启用重定向",

    "label.correction_enabled": "启用修正",

    "label.export_enabled": "启用导出",

    "label.overwrite_outputs": "覆盖输出文件",

    "label.preserve_folder_structure": "保留文件夹结构",

    "label.copy_bad_files": "复制错误/需修正文件",

    "label.copy_good_files": "复制正常文件",

    "label.sort_originals_instead_of_copy": "移动原始文件而不是复制 - 危险",

    "label.dry_run": "试运行",

    "label.skip_bad_files_before_retarget": "重定向前跳过 BAD 文件 - 默认关闭",

    "label.auto_retarget_fallback": "自动重定向备用方案 - HumanIK 生产模式建议关闭",

    "label.max_files": "最大文件数 (0 = 全部)",

    "label.force_frame_rate": "强制帧率",

    "label.target_frame_rate": "目标帧率",

    "label.sample_every_n_frames": "验证每 N 帧采样",

    "label.bake_sample_by": "烘焙采样间隔",

    "label.required_canonical_bones": "必需标准骨骼",

    "label.validate_required_bones": "验证必需骨骼",

    "label.validate_empty_clip": "验证空/损坏动画片段",

    "label.validate_animation_length": "验证动画长度",

    "label.validate_scale": "验证缩放值",

    "label.validate_extreme_rotation": "验证极端局部旋转",

    "label.validate_rotation_spikes": "验证旋转突变",

    "label.validate_translation_spikes": "验证位移突变",

    "label.validate_root_motion": "验证 Root Motion 偏移",

    "label.validate_shoulder_pose": "验证肩部姿态",

    "label.validate_neck_pose": "验证颈部姿态",

    "label.validate_arm_twist": "验证手臂扭曲",

    "label.validate_hand_flip": "验证手/手腕翻转",

    "label.min_anim_length_frames": "最小动画长度帧数",

    "label.max_anim_length_frames": "最大动画长度帧数",

    "label.min_scale_value": "最小缩放值",

    "label.max_scale_value": "最大缩放值",

    "label.extreme_rotation_degrees": "极端旋转阈值 Degrees",

    "label.rotation_spike_degrees": "旋转突变阈值 Degrees",

    "label.translation_spike_units": "位移突变阈值 Units",

    "label.max_root_offset_units": "最大 Root 偏移 Units",

    "label.shoulder_raise_angle_degrees": "肩部抬起灵敏度 Degrees",

    "label.neck_extreme_degrees": "颈部极端阈值 Degrees",

    "label.arm_twist_degrees": "手臂扭曲阈值 Degrees",

    "label.hand_flip_degrees": "手/手腕翻转阈值 Degrees",

    "label.fix_rotation_spikes": "修正旋转突变",

    "label.fix_translation_spikes": "修正位移突变",

    "label.fix_scale_values": "修正缩放值",

    "label.fix_shoulder_pose": "修正肩部姿态",

    "label.fix_neck_pose": "修正颈部姿态",

    "label.fix_arm_twist": "修正手臂扭曲",

    "label.fix_hand_flip": "修正手/手腕翻转",

    "label.conservative_mode": "保守模式 - 更安全的限制",

    "label.correction_strength": "修正强度 0-1",

    "label.smoothing_passes": "额外平滑次数",

    "label.shoulder_clamp_axes": "肩部限制轴 XYZ",

    "label.neck_clamp_axes": "颈部限制轴 XYZ",

    "label.arm_twist_axis": "手臂扭曲轴 X/Y/Z",

    "label.hand_flip_axes": "手/手腕翻转轴 XYZ",

    "label.retarget_method": "重定向方法: humanik_batch / positional_ik_solver / hierarchical_world_matrix / world_euler_delta_constraints / rest_world_delta_constraints / local_matrix_delta / local_euler_delta / constraints",

    "label.retarget_translation_scale": "Pelvis 位移缩放",

    "label.matrix_delta_order": "Delta 顺序: target_rest_delta / delta_target_rest / rest_inv_current / current_rest_inv",

    "label.retarget_use_source_rest_file": "使用源骨架文件作为 Rest/T-Pose 参考",

    "label.auto_find_source_rest_file": "从映射/预设自动查找源 Rest 文件",

    "label.require_source_rest_for_matrix_delta": "Matrix Delta 必须使用源 Rest 文件",

    "label.retarget_copy_pelvis_translation": "复制 Pelvis 位移差值",

    "label.retarget_use_point_constraint_for_root": "Root 使用 Parent/Point Constraint - constraints 模式",

    "label.retarget_use_point_constraint_for_pelvis": "Pelvis 使用 Point Constraint - constraints 模式",

    "label.retarget_maintain_offset": "保持 Constraint Offset - constraints 模式",

    "label.delete_source_after_bake": "导出前删除源骨架",

    "label.fail_if_no_target_animation": "目标没有动画曲线时导出失败",

    "label.export_selected_target_only": "仅导出目标选择 - 推荐",

    "label.export_include_target_meshes": "导出时包含目标网格 - UE 安全",

    "label.export_force_key_target_joints": "导出前强制给目标关节打 Key",

    "label.export_validate_file": "验证导出的 FBX 文件",

    "label.humanik_post_align_root": "HumanIK 后处理 Root 对齐 - 推荐",

    "label.humanik_post_align_use_pelvis": "使用 Pelvis 对齐",

    "label.humanik_post_align_use_floor": "使用脚底/地面对齐",

    "label.humanik_post_align_strength": "HumanIK 对齐强度 0-1",

    "label.humanik_post_align_floor_weight": "地面对齐权重 0-1",

    "label.humanik_post_match_hands": "HumanIK 安全手腕匹配 - 推荐",

    "label.humanik_hand_match_key_fingers_to_rest": "手部匹配后稳定手指",

    "label.humanik_hand_match_strength": "HumanIK 手部匹配强度 0-1",

    "label.humanik_hand_match_pole_strength": "HumanIK 手肘方向强度 0-1",

    "label.humanik_hand_match_max_pull_units": "HumanIK 手部最大拉动距离",

    "label.humanik_hand_match_reach_limit": "HumanIK 手臂可达限制 0-1",

    "label.humanik_post_refine_limbs": "HumanIK 后处理四肢精修 - 实验性",

    "label.humanik_post_refine_hands": "精修手部位置",

    "label.humanik_post_refine_feet": "精修脚部/膝盖位置",

    "label.humanik_post_refine_poles": "精修膝盖/肘部弯曲方向",

    "label.humanik_post_refine_strength": "HumanIK 四肢精修总强度 0-1",

    "label.humanik_post_refine_arm_strength": "手臂精修强度 0-1",

    "label.humanik_post_refine_leg_strength": "腿部精修强度 0-1",

    "label.humanik_post_refine_pole_strength": "膝盖/肘部方向精修强度 0-1",

    "label.retarget_rotate_order": "目标 Rotate Order",

    "button.apply_smplh_defaults": "应用 SMPL-H -> FemaleStd 安全默认值",

    "button.run_scan_only": "仅运行扫描",

    "button.run_full_batch": "运行完整批处理",

    "button.stop_batch": "停止批处理",

    "button.save_config": "保存配置",

    "button.load_config": "加载配置",

    "button.example_mapping_json": "示例映射 JSON",

    "button.example_npz_schema": "示例 NPZ 结构",

    "button.open_report_folder": "打开报告文件夹",

    "button.browse": "浏览",

    "dialog.select": "选择",

    "dialog.contact_email": "联系邮箱",

    "dialog.ok": "确定"

}





def translation_default_path() -> str:

    return normalize_path(os.path.join(script_directory(), TRANSLATION_FILE_NAME))





def ensure_default_translation_file() -> str:

    path = translation_default_path()

    payload = {

        "language": LANGUAGE_CHINESE_SIMPLIFIED,

        "name": "Simplified Chinese UI translations for ALPHA Batch Animation Tool",

        "note": "Edit values only. Do not translate technical tokens such as XYZ, X/Y/Z, rest_world_delta_constraints, local_matrix_delta, local_euler_delta, constraints, target_rest_delta, delta_target_rest, rest_inv_current, current_rest_inv, Root Motion, FBX, NPZ, JSON, UE.",

        "translations": DEFAULT_ZH_CN_TRANSLATIONS,

    }

    if os.path.isfile(path):

        try:

            existing = load_json_file(path)

            translations = existing.get("translations", existing)

            changed = False

            if not isinstance(translations, dict):

                translations = {}

                changed = True

            for key, value in DEFAULT_ZH_CN_TRANSLATIONS.items():

                if key not in translations:

                    translations[key] = value

                    changed = True

            if "translations" in existing:

                existing["translations"] = translations

                existing.setdefault("language", LANGUAGE_CHINESE_SIMPLIFIED)

                existing.setdefault("note", payload["note"])

                payload_to_save = existing

            else:

                payload_to_save = payload

                payload_to_save["translations"] = translations

                changed = True

            if changed:

                save_json_file(path, payload_to_save)

        except Exception:

            save_json_file(path, payload)

    else:

        save_json_file(path, payload)

    return path





def load_chinese_translations() -> Dict[str, str]:

    path = ensure_default_translation_file()

    try:

        data = load_json_file(path)

        translations = data.get("translations", data)

        if isinstance(translations, dict):

            return {str(k): str(v) for k, v in translations.items()}

    except Exception:

        pass

    return dict(DEFAULT_ZH_CN_TRANSLATIONS)





                                                                               

              

                                                                               



def require_maya() -> None:

    if not MAYA_AVAILABLE:

        raise RuntimeError("This tool must be executed inside Autodesk Maya Python.")





def safe_cmds_exists(node: str) -> bool:

    if not node or not MAYA_AVAILABLE:

        return False

    try:

        return bool(cmds.objExists(node))

    except Exception:

        return False





def load_fbx_plugin() -> None:

    require_maya()

    try:

        if not cmds.pluginInfo("fbxmaya", query=True, loaded=True):

            cmds.loadPlugin("fbxmaya")

    except Exception as exc:

        raise RuntimeError("Could not load Maya FBX plugin 'fbxmaya': %s" % exc)





def reset_scene() -> None:

    require_maya()

    cmds.file(new=True, force=True)





def import_maya_or_fbx(path: str, namespace: Optional[str] = None) -> List[str]:

    require_maya()

    path = normalize_path(path)

    if not os.path.isfile(path):

        raise FileNotFoundError(path)



    before = set(cmds.ls(long=True) or [])

    ext = os.path.splitext(path)[1].lower()

    kwargs = dict(i=True, ignoreVersion=True, preserveReferences=True)

    if namespace:

        kwargs.update(namespace=namespace, mergeNamespacesOnClash=False)

    if ext == ".fbx":

        load_fbx_plugin()

                                                                           

        cmds.file(path, type="FBX", **kwargs)

    elif ext == ".ma":

        cmds.file(path, type="mayaAscii", **kwargs)

    elif ext == ".mb":

        cmds.file(path, type="mayaBinary", **kwargs)

    else:

        raise ValueError("Unsupported import file type: %s" % ext)

    after = set(cmds.ls(long=True) or [])

    return sorted(after - before)





def import_animation_fbx(path: str, namespace: Optional[str] = None) -> List[str]:

    return import_maya_or_fbx(path, namespace=namespace)





def delete_namespace_nodes(namespaces: List[str], log_callback=None) -> int:

    require_maya()

    deleted = 0

    for ns in namespaces or []:

        try:

            nodes = cmds.ls("%s:*" % ns, long=True) or []

        except Exception:

            nodes = []

        if not nodes:

            continue

                                                                                                          

        dag_nodes = []

        non_dag_nodes = []

        for node in nodes:

            try:

                if cmds.objectType(node, isAType="dagNode"):

                    dag_nodes.append(node)

                else:

                    non_dag_nodes.append(node)

            except Exception:

                non_dag_nodes.append(node)

        top_dag = []

        dag_set = set(dag_nodes)

        for node in dag_nodes:

            parent = (cmds.listRelatives(node, parent=True, fullPath=True) or [None])[0]

            if parent not in dag_set:

                top_dag.append(node)

        to_delete = sorted(set(top_dag + non_dag_nodes))

        try:

            cmds.delete(to_delete)

            deleted += len(to_delete)

            if log_callback:

                log_callback("Deleted %d source namespace nodes from %s before export." % (len(to_delete), ns))

        except Exception as exc:

            if log_callback:

                log_callback("WARNING: Could not fully delete source namespace %s before export: %s" % (ns, exc))

        try:

            if cmds.namespace(exists=ns):

                cmds.namespace(removeNamespace=ns, mergeNamespaceWithRoot=True)

        except Exception:

            pass

    return deleted





def delete_hierarchy_roots_for_joints(joints: List[str], log_callback=None) -> int:

    require_maya()

    roots = []

    for jnt in joints or []:

        if not safe_cmds_exists(jnt):

            continue

        current = jnt

        while True:

            parent = (cmds.listRelatives(current, parent=True, fullPath=True) or [None])[0]

            if not parent:

                break

            current = parent

        if current and safe_cmds_exists(current):

            roots.append(current)

    roots = sorted(set(roots))

    if not roots:

        return 0

    try:

        cmds.delete(roots)

        if log_callback:

            log_callback("Deleted %d source DAG root(s) before export." % len(roots))

        return len(roots)

    except Exception as exc:

        if log_callback:

            log_callback("WARNING: Could not delete some source DAG roots before export: %s" % exc)

        return 0





def count_anim_curves_on_nodes(nodes: List[str]) -> int:

    require_maya()

    curves = set()

    for node in nodes or []:

        if not safe_cmds_exists(node):

            continue

        for attr in TRANSLATE_ATTRS + ROTATE_ATTRS + SCALE_ATTRS:

            full_attr = "%s.%s" % (node, attr)

            if not cmds.objExists(full_attr):

                continue

            for curve in cmds.listConnections(full_attr, source=True, destination=False, type="animCurve") or []:

                curves.add(curve)

    return len(curves)





def force_key_transform_nodes(nodes: List[str], start: float, end: float) -> int:

    require_maya()

    keyed = 0

    frame_values = [float(start)]

    if abs(float(end) - float(start)) > 0.001:

        frame_values.append(float(end))

    attrs = TRANSLATE_ATTRS + ROTATE_ATTRS + SCALE_ATTRS

    for node in nodes or []:

        if not safe_cmds_exists(node) or cmds.nodeType(node) != "joint":

            continue

        unlock_transform_attrs(node)

        for frame in frame_values:

            try:

                cmds.currentTime(frame, edit=True)

                cmds.setKeyframe(node, attribute=attrs, time=frame)

                keyed += len(attrs)

            except Exception:

                                                                                               

                pass

    return keyed





def find_bound_mesh_transforms_for_joints(joints: List[str]) -> List[str]:

    require_maya()

    joint_set = set(joints or [])

    short_joint_set = {short_name(j) for j in joint_set}

    mesh_transforms = []

    for mesh_shape in cmds.ls(type="mesh", long=True) or []:

        parents = cmds.listRelatives(mesh_shape, parent=True, fullPath=True) or []

        if not parents:

            continue

        mesh_transform = parents[0]

        history = cmds.listHistory(mesh_shape, pruneDagObjects=True) or []

        skins = [h for h in history if cmds.nodeType(h) == "skinCluster"]

        for skin in skins:

            try:

                influences = cmds.skinCluster(skin, query=True, influence=True) or []

            except Exception:

                influences = []

            if any(inf in joint_set or short_name(inf) in short_joint_set for inf in influences):

                mesh_transforms.append(mesh_transform)

                break

    return sorted(set(mesh_transforms))





def select_export_nodes_for_target(root: str, include_meshes: bool = True) -> List[str]:

    require_maya()

    if not root or not cmds.objExists(root):

        raise RuntimeError("Cannot export: target root does not exist: %s" % root)



    joints = get_hierarchy(root, node_type="joint")

    if not joints:

        if cmds.nodeType(root) == "joint":

            joints = [root]

        else:

            joints = cmds.listRelatives(root, allDescendents=True, fullPath=True, type="joint") or []

    if not joints:

        raise RuntimeError("Cannot export: target hierarchy has no joints under root: %s" % root)



    export_nodes = list(joints)

    if include_meshes:

        export_nodes.extend(find_bound_mesh_transforms_for_joints(joints))



                                                                                 

    seen = set()

    final_nodes = []

    for node in export_nodes:

        if node and node not in seen and cmds.objExists(node):

            final_nodes.append(node)

            seen.add(node)



    if not final_nodes:

        raise RuntimeError("Cannot export: no valid export nodes were selected.")

    cmds.select(final_nodes, replace=True)

    return final_nodes





def export_fbx_selected(path: str, start: float, end: float, selected_only: bool = True) -> None:

    require_maya()

    load_fbx_plugin()

    path = normalize_path(path)

    ensure_dir(os.path.dirname(path))



    selected_nodes = cmds.ls(selection=True, long=True) or []

    if selected_only and not selected_nodes:

        raise RuntimeError("FBX export failed before start: selected export list is empty.")



                                                                                       

    mel.eval("FBXResetExport;")

    mel.eval("FBXExportInAscii -v false;")

    mel.eval("FBXExportAnimationOnly -v false;")

    mel.eval("FBXExportBakeComplexAnimation -v true;")

    mel.eval("FBXExportBakeComplexStart -v %s;" % float(start))

    mel.eval("FBXExportBakeComplexEnd -v %s;" % float(end))

    mel.eval("FBXExportBakeComplexStep -v 1;")

    mel.eval("FBXExportSkins -v true;")

    mel.eval("FBXExportShapes -v true;")

    mel.eval("FBXExportConstraints -v false;")

    mel.eval("FBXExportInputConnections -v false;")

                                                                                               

    for command in (

        "FBXExportSkeletonDefinitions -v true;",

        "FBXExportEmbeddedTextures -v false;",

        "FBXExportReferencedAssetsContent -v true;",

        "FBXExportQuaternion -v euler;",

        "FBXExportUpAxis y;",

    ):

        try:

            mel.eval(command)

        except Exception:

            pass



    flag = " -s" if selected_only else ""

    mel.eval('FBXExport -f "%s"%s;' % (quote_mel_path(path), flag))



                                                                                                        

    if not os.path.isfile(path) or os.path.getsize(path) < 512:

        raise RuntimeError("FBX export produced an empty or missing file: %s" % path)





def get_all_joints() -> List[str]:

    require_maya()

    return cmds.ls(type="joint", long=True) or []





def get_root_joints(nodes: Optional[List[str]] = None) -> List[str]:

    require_maya()

    joints = nodes or get_all_joints()

    roots = []

    for jnt in joints:

        parent = cmds.listRelatives(jnt, parent=True, fullPath=True) or []

        if not parent or cmds.nodeType(parent[0]) != "joint":

            roots.append(jnt)

    return roots





def get_hierarchy(root: str, node_type: Optional[str] = None) -> List[str]:

    require_maya()

    if not root or not cmds.objExists(root):

        return []

    children = cmds.listRelatives(root, allDescendents=True, fullPath=True, type=node_type) or []

    ordered = list(reversed(children))

    if node_type is None or cmds.nodeType(root) == node_type:

        ordered.insert(0, root)

    return ordered



def duplicate_rest_reference_joints(rest_joints: List[str], namespace: str = "SRCREST_REF", log_callback=None) -> List[str]:

    require_maya()

    rest_joints = [j for j in (rest_joints or []) if safe_cmds_exists(j)]

    if not rest_joints:

        return []

    try:

        if not cmds.namespace(exists=namespace):

            cmds.namespace(add=namespace)

    except Exception:

        pass



    roots = get_root_joints(rest_joints)

    duplicated_joints: List[str] = []

    used_names = set()



    for root in roots:

        original_chain = get_hierarchy(root, node_type="joint")

        if not original_chain:

            continue

        dup_nodes = cmds.duplicate(root, renameChildren=True) or []

        if not dup_nodes:

            continue

        dup_root = dup_nodes[0]

        dup_chain = get_hierarchy(dup_root, node_type="joint")

        if len(dup_chain) != len(original_chain) and log_callback:

            log_callback("WARNING: Rest reference duplicate joint-count mismatch for %s: original=%d duplicate=%d" % (short_name(root), len(original_chain), len(dup_chain)))



                                                                                                      

        count = min(len(original_chain), len(dup_chain))

        for index in range(count):

            orig = original_chain[index]

            dup = dup_chain[index]

            base = short_name(orig)

            if not base:

                base = "RestJoint_%d" % index

            candidate_base = base

            suffix = 1

            while candidate_base.lower() in used_names:

                suffix += 1

                candidate_base = "%s_%02d" % (base, suffix)

            used_names.add(candidate_base.lower())

            try:

                new_name = cmds.rename(dup, "%s:%s" % (namespace, candidate_base))

            except Exception:

                                                                                                                 

                new_name = cmds.rename(dup, "%s_%s" % (namespace, candidate_base))

            duplicated_joints.append(new_name)

                                                                                     

            try:

                dup_chain = get_hierarchy(duplicated_joints[0], node_type="joint")

            except Exception:

                pass



    for jnt in duplicated_joints:

        try:

            cmds.setAttr("%s.visibility" % jnt, 0)

        except Exception:

            pass

    if log_callback:

        log_callback("Created protected source rest reference duplicate: %d joints in namespace %s" % (len(duplicated_joints), namespace))

    return duplicated_joints





def count_keyed_transform_joints(joints: List[str]) -> int:

    count = 0

    for jnt in joints or []:

        if get_connected_anim_curves(jnt, ROTATE_ATTRS + TRANSLATE_ATTRS + SCALE_ATTRS):

            count += 1

    return count





def first_existing_attr(node: str, attrs: List[str]) -> Optional[str]:

    for attr in attrs:

        full = "%s.%s" % (node, attr)

        if cmds.objExists(full):

            return full

    return None





def get_connected_anim_curves(node: str, attrs: Optional[List[str]] = None) -> List[str]:

    require_maya()

    curves = []

    attrs = attrs or (ROTATE_ATTRS + TRANSLATE_ATTRS + SCALE_ATTRS)

    for attr in attrs:

        full_attr = "%s.%s" % (node, attr)

        if not cmds.objExists(full_attr):

            continue

        conns = cmds.listConnections(full_attr, source=True, destination=False, type="animCurve") or []

        curves.extend(conns)

    return sorted(set(curves))





def get_scene_anim_curves() -> List[str]:

    require_maya()

    return cmds.ls(type="animCurve") or []





def get_anim_time_range(anim_curves: Optional[List[str]] = None) -> Tuple[float, float]:

    require_maya()

    anim_curves = anim_curves if anim_curves is not None else get_scene_anim_curves()

    min_time = None

    max_time = None

    for curve in anim_curves:

        try:

            times = cmds.keyframe(curve, query=True, timeChange=True) or []

        except Exception:

            times = []

        for t in times:

            if min_time is None or t < min_time:

                min_time = t

            if max_time is None or t > max_time:

                max_time = t

    if min_time is None or max_time is None:

        try:

            return float(cmds.playbackOptions(q=True, min=True)), float(cmds.playbackOptions(q=True, max=True))

        except Exception:

            return 1.0, 1.0

    return float(min_time), float(max_time)





def set_timeline(start: float, end: float) -> None:

    require_maya()

    cmds.playbackOptions(min=start, max=end, animationStartTime=start, animationEndTime=end)



def fps_to_maya_time_unit(fps: float) -> str:

    fps = float(fps or 30.0)

    known = {

        15.0: "game",

        24.0: "film",

        25.0: "pal",

        30.0: "ntsc",

        48.0: "show",

        50.0: "palf",

        60.0: "ntscf",

    }

    for key, value in known.items():

        if abs(fps - key) < 0.001:

            return value

                                                                                     

                                                       

    if abs(fps - round(fps)) < 0.001:

        return "%dfps" % int(round(fps))

    return "%.3ffps" % fps





def set_scene_frame_rate(fps: float, log_callback=None) -> str:

    require_maya()

    unit = fps_to_maya_time_unit(fps)

    try:

        cmds.currentUnit(time=unit)

    except Exception:

                                                                                   

        unit = "ntsc"

        cmds.currentUnit(time=unit)

    if log_callback:

        try:

            log_callback("Scene frame rate set to %.3f fps (%s)." % (float(fps), unit))

        except Exception:

            pass

    return unit





def get_scene_time_unit() -> str:

    require_maya()

    try:

        return cmds.currentUnit(query=True, time=True)

    except Exception:

        return "unknown"





def sample_frames(start: float, end: float, every_n_frames: int) -> List[float]:

    every_n_frames = max(1, int(every_n_frames or 1))

    if end < start:

        start, end = end, start

    frames = []

    t = float(start)

    while t <= float(end) + 0.001:

        frames.append(t)

        t += every_n_frames

    if not frames or abs(frames[-1] - end) > 0.001:

        frames.append(float(end))

    return frames





def get_world_position(node: str) -> Tuple[float, float, float]:

    require_maya()

    pos = cmds.xform(node, query=True, worldSpace=True, translation=True)

    return float(pos[0]), float(pos[1]), float(pos[2])





def get_world_rotation(node: str) -> Tuple[float, float, float]:

    require_maya()

    rot = cmds.xform(node, query=True, worldSpace=True, rotation=True)

    return float(rot[0]), float(rot[1]), float(rot[2])





def get_local_rotation(node: str) -> Tuple[float, float, float]:

    require_maya()

    vals = []

    for attr in ROTATE_ATTRS:

        try:

            vals.append(float(cmds.getAttr("%s.%s" % (node, attr))))

        except Exception:

            vals.append(0.0)

    return vals[0], vals[1], vals[2]





def select_root_hierarchy(root: str) -> List[str]:

    require_maya()

    nodes = get_hierarchy(root, node_type="joint")

    cmds.select(nodes, replace=True)

    return nodes





def unlock_transform_attrs(node: str) -> None:

    for attr in TRANSLATE_ATTRS + ROTATE_ATTRS + SCALE_ATTRS:

        full = "%s.%s" % (node, attr)

        if cmds.objExists(full):

            try:

                cmds.setAttr(full, lock=False, keyable=True, channelBox=True)

            except Exception:

                pass





def set_rotate_order(node: str, rotate_order: str) -> None:

    orders = {"xyz": 0, "yzx": 1, "zxy": 2, "xzy": 3, "yxz": 4, "zyx": 5}

    value = orders.get((rotate_order or "xyz").lower(), 0)

    if cmds.objExists("%s.rotateOrder" % node):

        try:

            cmds.setAttr("%s.rotateOrder" % node, value)

        except Exception:

            pass





                                                                               

               

                                                                               



class JointMapping:



    def __init__(self, mapping_data: Optional[Dict[str, Any]] = None):

        self.mapping_data = mapping_data or {}

        self.aliases: Dict[str, List[str]] = dict(DEFAULT_JOINT_ALIASES)

        custom_aliases = self.mapping_data.get("aliases", {})

        if isinstance(custom_aliases, dict):

            for key, values in custom_aliases.items():

                if isinstance(values, str):

                    values = [values]

                self.aliases.setdefault(key, [])

                self.aliases[key].extend(values)

        self.joint_pairs: Dict[str, str] = self.mapping_data.get("joints", {}) or {}

        self.offsets: Dict[str, Dict[str, Any]] = self.mapping_data.get("offsets", {}) or {}

                                                                              

                                                                                     

        self.axis_remap: Dict[str, Dict[str, Any]] = self.mapping_data.get("axis_remap", {}) or {}



    @staticmethod

    def _matches_name(node: str, alias: str) -> bool:

        node_short = short_name(node)

        alias_short = short_name(alias)

        if node_short == alias_short:

            return True

        if node == alias:

            return True

                                                                    

        return node_short.lower() == alias_short.lower()



    def find_by_alias(self, joints: List[str], canonical: str) -> Optional[str]:

        aliases = self.aliases.get(canonical, [])

        for alias in aliases:

            for jnt in joints:

                if self._matches_name(jnt, alias):

                    return jnt

                                                

        for jnt in joints:

            if self._matches_name(jnt, canonical):

                return jnt

        return None



    def find_exact_or_alias(self, joints: List[str], name_or_canonical: str) -> Optional[str]:

        if not name_or_canonical:

            return None

        for jnt in joints:

            if self._matches_name(jnt, name_or_canonical):

                return jnt

        return self.find_by_alias(joints, name_or_canonical)



    def build_canonical_map(self, joints: List[str]) -> Dict[str, str]:

        result = {}

        for canonical in DEFAULT_RETARGET_CANONICAL_ORDER:

            found = self.find_by_alias(joints, canonical)

            if found:

                result[canonical] = found

        return result



    def build_source_target_pairs(self, source_joints: List[str], target_joints: List[str]) -> Dict[str, Tuple[str, str]]:

        pairs: Dict[str, Tuple[str, str]] = {}



                                                                                           

        for target_name, source_name in self.joint_pairs.items():

            src = self.find_exact_or_alias(source_joints, source_name)

            tgt = self.find_exact_or_alias(target_joints, target_name)

            canonical = target_name

            if tgt and src:

                pairs[canonical] = (src, tgt)



                                                        

        source_map = self.build_canonical_map(source_joints)

        target_map = self.build_canonical_map(target_joints)

        for canonical in DEFAULT_RETARGET_CANONICAL_ORDER:

            if canonical in pairs:

                continue

            src = source_map.get(canonical)

            tgt = target_map.get(canonical)

            if src and tgt:

                pairs[canonical] = (src, tgt)



        return pairs



    def required_bones_missing(self, joints: List[str], required: List[str]) -> List[str]:

        missing = []

        for canonical in required:

            if not self.find_exact_or_alias(joints, canonical):

                missing.append(canonical)

        return missing





                                                                               

               

                                                                               



class ReportWriter:

    def __init__(self, report_folder: str, basename: str = DEFAULT_REPORT_BASENAME):

        self.report_folder = ensure_dir(report_folder)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        self.basename = "%s_%s" % (basename, timestamp)

        self.json_path = normalize_path(os.path.join(self.report_folder, self.basename + ".json"))

        self.csv_path = normalize_path(os.path.join(self.report_folder, self.basename + ".csv"))

        self.summary_path = normalize_path(os.path.join(self.report_folder, self.basename + ".txt"))



    def write(self, results: List[ScanResult], config: ToolConfig) -> Dict[str, str]:

        self._write_json(results, config)

        self._write_csv(results)

        self._write_summary(results, config)

        return {"json": self.json_path, "csv": self.csv_path, "summary": self.summary_path}



    def _write_json(self, results: List[ScanResult], config: ToolConfig) -> None:

        data = {

            "tool": TOOL_NAME,

            "version": TOOL_VERSION,

            "generated_at": now_iso(),

            "config": config.to_dict(),

            "results": [r.to_dict() for r in results],

        }

        save_json_file(self.json_path, data)



    def _write_csv(self, results: List[ScanResult]) -> None:

        ensure_dir(os.path.dirname(self.csv_path))

        with open(self.csv_path, "w", newline="", encoding="utf-8-sig") as handle:

            writer = csv.writer(handle)

            writer.writerow([

                "file", "status", "source_type", "output_path", "duration_seconds",

                "issue_count", "fatal_count", "error_count", "warning_count",

                "codes", "messages"

            ])

            for result in results:

                codes = ";".join(sorted({i.code for i in result.issues}))

                messages = " | ".join("%s:%s:%s" % (i.severity, i.code, i.message) for i in result.issues)

                fatal_count = sum(1 for i in result.issues if i.severity == SEVERITY_FATAL)

                error_count = sum(1 for i in result.issues if i.severity == SEVERITY_ERROR)

                warning_count = sum(1 for i in result.issues if i.severity == SEVERITY_WARNING)

                writer.writerow([

                    result.file_path, result.status, result.source_type, result.output_path,

                    "%.3f" % result.duration_seconds, len(result.issues), fatal_count,

                    error_count, warning_count, codes, messages

                ])



    def _write_summary(self, results: List[ScanResult], config: ToolConfig) -> None:

        counts: Dict[str, int] = {}

        for r in results:

            counts[r.status] = counts.get(r.status, 0) + 1

        lines = []

        lines.append("%s v%s" % (TOOL_NAME, TOOL_VERSION))

        lines.append("Generated: %s" % now_iso())

        lines.append("Input: %s" % config.input_folder)

        lines.append("Output: %s" % config.output_folder)

        lines.append("")

        lines.append("Counts:")

        for status in [STATUS_GOOD, STATUS_NEEDS_FIX, STATUS_BAD, STATUS_SKIPPED, STATUS_FAILED]:

            lines.append("  %s: %s" % (status, counts.get(status, 0)))

        lines.append("")

        lines.append("Problem files:")

        for r in results:

            if r.status in {STATUS_BAD, STATUS_NEEDS_FIX, STATUS_FAILED, STATUS_SKIPPED}:

                lines.append("- [%s] %s" % (r.status, r.file_path))

                for issue in r.issues[:10]:

                    extra = []

                    if issue.joint:

                        extra.append("joint=%s" % issue.joint)

                    if issue.frame is not None:

                        extra.append("frame=%s" % issue.frame)

                    if issue.value is not None:

                        extra.append("value=%.3f" % issue.value)

                    if issue.threshold is not None:

                        extra.append("threshold=%.3f" % issue.threshold)

                    suffix = " (%s)" % ", ".join(extra) if extra else ""

                    lines.append("    %s %s: %s%s" % (issue.severity, issue.code, issue.message, suffix))

                if len(r.issues) > 10:

                    lines.append("    ... %d more issues" % (len(r.issues) - 10))

        with open(self.summary_path, "w", encoding="utf-8") as handle:

            handle.write("\n".join(lines))





                                                                               

                      

                                                                               



class AnimationScanner:

    def __init__(self, config: ToolConfig, mapping: JointMapping, log_callback=None):

        self.config = config

        self.mapping = mapping

        self.log_callback = log_callback



    def log(self, message: str) -> None:

        if self.log_callback:

            self.log_callback(message)



    def scan_scene(self, result: ScanResult, source_joints: Optional[List[str]] = None) -> ScanResult:

        require_maya()

        source_joints = source_joints or get_all_joints()

        anim_curves = get_scene_anim_curves()

        start, end = get_anim_time_range(anim_curves)

        length = end - start

        result.stats.update({

            "joint_count": len(source_joints),

            "anim_curve_count": len(anim_curves),

            "start_frame": start,

            "end_frame": end,

            "length_frames": length,

        })



        if self.config.validate_empty_clip:

            self._validate_empty_clip(result, anim_curves, length)

        if self.config.validate_required_bones:

            required = parse_csv_text(self.config.required_canonical_bones)

            self._validate_required_bones(result, source_joints, required)

        if self.config.validate_animation_length:

            self._validate_animation_length(result, length)

        if self.config.validate_scale:

            self._validate_scale(result, source_joints)

        if self.config.validate_extreme_rotation:

            self._validate_extreme_rotation(result, source_joints)

        if self.config.validate_rotation_spikes or self.config.validate_translation_spikes:

            self._validate_transform_spikes(result, source_joints, start, end)

        if self.config.validate_root_motion:

            self._validate_root_motion(result, source_joints, start, end)

        if self.config.validate_shoulder_pose:

            self._validate_shoulder_pose(result, source_joints, start, end)

        if self.config.validate_neck_pose:

            self._validate_neck_pose(result, source_joints, start, end)

        if self.config.validate_arm_twist:

            self._validate_arm_twist(result, source_joints)

        if self.config.validate_hand_flip:

            self._validate_hand_flip(result, source_joints, start, end)



        result.status = status_from_issues(result.issues)

        return result



    def _validate_empty_clip(self, result: ScanResult, anim_curves: List[str], length: float) -> None:

        if not anim_curves:

            result.add_issue("EMPTY_CLIP", SEVERITY_ERROR, "No animation curves found.")

        elif length <= 0.001:

            result.add_issue("ZERO_LENGTH", SEVERITY_ERROR, "Animation has no usable frame range.", value=length)



    def _validate_required_bones(self, result: ScanResult, joints: List[str], required: List[str]) -> None:

        missing = self.mapping.required_bones_missing(joints, required)

        if missing:

            result.add_issue(

                "MISSING_REQUIRED_BONES",

                SEVERITY_ERROR,

                "Missing required humanoid bones: %s" % ", ".join(missing),

                value=float(len(missing)),

                threshold=0.0,

            )



    def _validate_animation_length(self, result: ScanResult, length: float) -> None:

        if length < self.config.min_anim_length_frames:

            result.add_issue("ANIM_TOO_SHORT", SEVERITY_WARNING,

                             "Animation is shorter than minimum configured length.",

                             value=length, threshold=self.config.min_anim_length_frames)

        if length > self.config.max_anim_length_frames:

            result.add_issue("ANIM_TOO_LONG", SEVERITY_WARNING,

                             "Animation is longer than maximum configured length.",

                             value=length, threshold=self.config.max_anim_length_frames)



    def _validate_scale(self, result: ScanResult, joints: List[str]) -> None:

        for jnt in joints:

            for attr in SCALE_ATTRS:

                full = "%s.%s" % (jnt, attr)

                if not cmds.objExists(full):

                    continue

                values = []

                curves = cmds.listConnections(full, source=True, destination=False, type="animCurve") or []

                if curves:

                    for curve in curves:

                        values.extend(cmds.keyframe(curve, q=True, valueChange=True) or [])

                else:

                    try:

                        values.append(cmds.getAttr(full))

                    except Exception:

                        continue

                for value in values:

                    if not is_finite(value):

                        result.add_issue("NON_FINITE_SCALE", SEVERITY_ERROR, "Scale has NaN/Inf value.", joint=jnt)

                        continue

                    value = float(value)

                    if value < self.config.min_scale_value or value > self.config.max_scale_value:

                        result.add_issue("ABNORMAL_SCALE", SEVERITY_WARNING,

                                         "Scale value outside configured range.",

                                         joint=jnt, value=value,

                                         threshold=self.config.max_scale_value)

                        break



    def _validate_extreme_rotation(self, result: ScanResult, joints: List[str]) -> None:

        threshold = abs(float(self.config.extreme_rotation_degrees))

        for jnt in joints:

            for attr in ROTATE_ATTRS:

                full = "%s.%s" % (jnt, attr)

                if not cmds.objExists(full):

                    continue

                curves = cmds.listConnections(full, source=True, destination=False, type="animCurve") or []

                values = []

                for curve in curves:

                    values.extend(cmds.keyframe(curve, q=True, valueChange=True) or [])

                if not values:

                    try:

                        values = [cmds.getAttr(full)]

                    except Exception:

                        values = []

                for value in values:

                    if not is_finite(value):

                        result.add_issue("NON_FINITE_ROTATION", SEVERITY_ERROR, "Rotation has NaN/Inf value.", joint=jnt)

                        continue

                    if abs(float(value)) > threshold:

                        result.add_issue("EXTREME_ROTATION", SEVERITY_WARNING,

                                         "Local rotation exceeds configured threshold.",

                                         joint=jnt, value=float(value), threshold=threshold)

                        break



    def _validate_transform_spikes(self, result: ScanResult, joints: List[str], start: float, end: float) -> None:

        frames = sample_frames(start, end, self.config.sample_every_n_frames)

        previous_rot: Dict[str, Tuple[float, float, float]] = {}

        previous_pos: Dict[str, Tuple[float, float, float]] = {}

        rot_threshold = float(self.config.rotation_spike_degrees)

        pos_threshold = float(self.config.translation_spike_units)

        max_issues_per_rule = 100

        rot_issue_count = 0

        pos_issue_count = 0



        for frame in frames:

            cmds.currentTime(frame, edit=True)

            for jnt in joints:

                if self.config.validate_rotation_spikes:

                    rot = get_world_rotation(jnt)

                    if jnt in previous_rot:

                        delta = max(abs(angular_delta(previous_rot[jnt][i], rot[i])) for i in range(3))

                        if delta > rot_threshold and rot_issue_count < max_issues_per_rule:

                            result.add_issue("ROTATION_SPIKE", SEVERITY_WARNING,

                                             "Sudden world rotation change detected.",

                                             joint=jnt, frame=frame, value=delta, threshold=rot_threshold)

                            rot_issue_count += 1

                    previous_rot[jnt] = rot



                if self.config.validate_translation_spikes:

                    pos = get_world_position(jnt)

                    if jnt in previous_pos:

                        delta_pos = vector_len(vector_sub(pos, previous_pos[jnt]))

                        if delta_pos > pos_threshold and pos_issue_count < max_issues_per_rule:

                            result.add_issue("TRANSLATION_SPIKE", SEVERITY_WARNING,

                                             "Sudden world translation change detected.",

                                             joint=jnt, frame=frame, value=delta_pos, threshold=pos_threshold)

                            pos_issue_count += 1

                    previous_pos[jnt] = pos



    def _validate_root_motion(self, result: ScanResult, joints: List[str], start: float, end: float) -> None:

        root = self.mapping.find_exact_or_alias(joints, "root") or (get_root_joints(joints)[0] if get_root_joints(joints) else None)

        if not root:

            result.add_issue("NO_ROOT", SEVERITY_ERROR, "Could not identify root joint for root-motion validation.")

            return

        cmds.currentTime(start, edit=True)

        start_pos = get_world_position(root)

        cmds.currentTime(end, edit=True)

        end_pos = get_world_position(root)

        offset = vector_len(vector_sub(end_pos, start_pos))

        result.stats["root_motion_offset"] = offset

        if offset > self.config.max_root_offset_units:

            result.add_issue("ABNORMAL_ROOT_OFFSET", SEVERITY_WARNING,

                             "Root offset exceeds configured range.",

                             joint=root, value=offset, threshold=self.config.max_root_offset_units)



    def _validate_shoulder_pose(self, result: ScanResult, joints: List[str], start: float, end: float) -> None:

        canonical = self.mapping.build_canonical_map(joints)

        frames = sample_frames(start, end, self.config.sample_every_n_frames)

        threshold = float(self.config.shoulder_raise_angle_degrees)

        pairs = [

            ("L", canonical.get("clavicle_l"), canonical.get("upperarm_l"), canonical.get("neck_01") or canonical.get("head"), canonical.get("pelvis")),

            ("R", canonical.get("clavicle_r"), canonical.get("upperarm_r"), canonical.get("neck_01") or canonical.get("head"), canonical.get("pelvis")),

        ]

        for side, clavicle, upperarm, neck, pelvis in pairs:

            if not (clavicle and upperarm and neck and pelvis):

                continue

            for frame in frames:

                cmds.currentTime(frame, edit=True)

                clav_pos = get_world_position(clavicle)

                arm_pos = get_world_position(upperarm)

                neck_pos = get_world_position(neck)

                pelvis_pos = get_world_position(pelvis)

                arm_vec = vector_sub(arm_pos, clav_pos)

                up_vec = vector_sub(neck_pos, pelvis_pos)

                angle_to_up = vector_angle_degrees(arm_vec, up_vec)

                                                                                                   

                if angle_to_up < (90.0 - threshold * 0.5):

                    result.add_issue("ABNORMAL_SHOULDER_POSE", SEVERITY_WARNING,

                                     "%s shoulder/upperarm appears over-raised or collapsed." % side,

                                     joint=upperarm, frame=frame, value=angle_to_up, threshold=(90.0 - threshold * 0.5))

                    break



    def _validate_neck_pose(self, result: ScanResult, joints: List[str], start: float, end: float) -> None:

        canonical = self.mapping.build_canonical_map(joints)

        necks = [x for x in [canonical.get("neck_01"), canonical.get("neck_02"), canonical.get("head")] if x]

        threshold = float(self.config.neck_extreme_degrees)

        frames = sample_frames(start, end, self.config.sample_every_n_frames)

        for node in necks:

            for frame in frames:

                cmds.currentTime(frame, edit=True)

                rot = get_local_rotation(node)

                max_abs = max(abs(v) for v in rot)

                if max_abs > threshold:

                    result.add_issue("NECK_ORIENTATION_MISMATCH", SEVERITY_WARNING,

                                     "Neck/head local rotation exceeds configured threshold.",

                                     joint=node, frame=frame, value=max_abs, threshold=threshold)

                    break



    def _validate_arm_twist(self, result: ScanResult, joints: List[str]) -> None:

        canonical = self.mapping.build_canonical_map(joints)

        axis_index = axis_to_index(self.config.arm_twist_axis)

        threshold = float(self.config.arm_twist_degrees)

        for key in ["upperarm_l", "lowerarm_l", "upperarm_r", "lowerarm_r"]:

            node = canonical.get(key)

            if not node:

                continue

            attr = ROTATE_ATTRS[axis_index]

            full = "%s.%s" % (node, attr)

            curves = cmds.listConnections(full, source=True, destination=False, type="animCurve") or []

            values = []

            for curve in curves:

                values.extend(cmds.keyframe(curve, q=True, valueChange=True) or [])

            if not values:

                try:

                    values = [cmds.getAttr(full)]

                except Exception:

                    values = []

            for value in values:

                if is_finite(value) and abs(float(value)) > threshold:

                    result.add_issue("ARM_TWIST", SEVERITY_WARNING,

                                     "Arm twist axis exceeds configured threshold.",

                                     joint=node, value=float(value), threshold=threshold)

                    break



    def _validate_hand_flip(self, result: ScanResult, joints: List[str], start: float, end: float) -> None:

        canonical = self.mapping.build_canonical_map(joints)

        hands = [x for x in [canonical.get("hand_l"), canonical.get("hand_r")] if x]

        frames = sample_frames(start, end, self.config.sample_every_n_frames)

        threshold = float(self.config.hand_flip_degrees)

        for hand in hands:

            prev = None

            for frame in frames:

                cmds.currentTime(frame, edit=True)

                rot = get_world_rotation(hand)

                if prev is not None:

                    max_delta = max(abs(angular_delta(prev[i], rot[i])) for i in range(3))

                    if max_delta > threshold:

                        result.add_issue("HAND_FLIP", SEVERITY_WARNING,

                                         "Large wrist/hand world rotation flip detected.",

                                         joint=hand, frame=frame, value=max_delta, threshold=threshold)

                        break

                prev = rot





                                                                               

                   

                                                                               



def axis_to_index(axis: str) -> int:

    axis = (axis or "X").upper()

    if axis.startswith("Y"):

        return 1

    if axis.startswith("Z"):

        return 2

    return 0





def axes_from_text(text: str) -> List[int]:

    text = (text or "XYZ").upper()

    result = []

    if "X" in text:

        result.append(0)

    if "Y" in text:

        result.append(1)

    if "Z" in text:

        result.append(2)

    return result or [0, 1, 2]





class AnimationCorrector:

    def __init__(self, config: ToolConfig, mapping: JointMapping, log_callback=None):

        self.config = config

        self.mapping = mapping

        self.log_callback = log_callback



    def log(self, message: str) -> None:

        if self.log_callback:

            self.log_callback(message)



    def apply_all(self, target_joints: List[str], start: float, end: float) -> Dict[str, Any]:

        require_maya()

        stats = {}

        if not self.config.correction_enabled:

            return stats



        canonical = self.mapping.build_canonical_map(target_joints)

        if self.config.fix_scale_values:

            stats["scale_fixed_keys"] = self.fix_scale(target_joints)

        if self.config.fix_rotation_spikes:

            stats["rotation_spike_fixed_keys"] = self.fix_rotation_spikes(target_joints)

        if self.config.fix_translation_spikes:

            stats["translation_spike_fixed_keys"] = self.fix_translation_spikes(target_joints)

        if self.config.fix_shoulder_pose:

            stats["shoulder_fixed_keys"] = self.fix_shoulders(canonical)

        if self.config.fix_neck_pose:

            stats["neck_fixed_keys"] = self.fix_neck(canonical)

        if self.config.fix_arm_twist:

            stats["arm_twist_fixed_keys"] = self.fix_arm_twist(canonical)

        if self.config.fix_hand_flip:

            stats["hand_flip_fixed_keys"] = self.fix_hand_flip(canonical)



                                                             

        for _ in range(max(0, int(self.config.smoothing_passes))):

            stats["final_smoothing_keys"] = stats.get("final_smoothing_keys", 0) + self.smooth_rotation_curves(target_joints, strength=0.15)

        return stats



    def fix_scale(self, joints: List[str]) -> int:

        fixed = 0

        min_s = float(self.config.min_scale_value)

        max_s = float(self.config.max_scale_value)

        for jnt in joints:

            for attr in SCALE_ATTRS:

                full = "%s.%s" % (jnt, attr)

                curves = cmds.listConnections(full, source=True, destination=False, type="animCurve") or []

                if curves:

                    for curve in curves:

                        fixed += clamp_anim_curve_values(curve, min_s, max_s)

                else:

                    try:

                        value = float(cmds.getAttr(full))

                        if value < min_s or value > max_s or not is_finite(value):

                            cmds.setAttr(full, clamp(value if is_finite(value) else 1.0, min_s, max_s))

                            fixed += 1

                    except Exception:

                        pass

        return fixed



    def fix_rotation_spikes(self, joints: List[str]) -> int:

        fixed = 0

        threshold = float(self.config.rotation_spike_degrees)

        for jnt in joints:

            for attr in ROTATE_ATTRS:

                curves = cmds.listConnections("%s.%s" % (jnt, attr), source=True, destination=False, type="animCurve") or []

                for curve in curves:

                    fixed += smooth_spikes_in_curve(curve, threshold=threshold, strength=self.config.correction_strength)

        return fixed



    def fix_translation_spikes(self, joints: List[str]) -> int:

        fixed = 0

        threshold = float(self.config.translation_spike_units)

        for jnt in joints:

            for attr in TRANSLATE_ATTRS:

                curves = cmds.listConnections("%s.%s" % (jnt, attr), source=True, destination=False, type="animCurve") or []

                for curve in curves:

                    fixed += smooth_spikes_in_curve(curve, threshold=threshold, strength=self.config.correction_strength)

        return fixed



    def fix_shoulders(self, canonical: Dict[str, str]) -> int:

        fixed = 0

        axes = axes_from_text(self.config.shoulder_clamp_axes)

        strength = clamp(float(self.config.correction_strength), 0.0, 1.0)

        max_rot = 75.0 if self.config.conservative_mode else 100.0

        for key in ["clavicle_l", "clavicle_r", "upperarm_l", "upperarm_r"]:

            node = canonical.get(key)

            if not node:

                continue

            for axis_index in axes:

                attr = ROTATE_ATTRS[axis_index]

                curves = cmds.listConnections("%s.%s" % (node, attr), source=True, destination=False, type="animCurve") or []

                for curve in curves:

                    fixed += damp_clamp_curve(curve, max_abs=max_rot, strength=strength)

        return fixed



    def fix_neck(self, canonical: Dict[str, str]) -> int:

        fixed = 0

        axes = axes_from_text(self.config.neck_clamp_axes)

        strength = clamp(float(self.config.correction_strength), 0.0, 1.0)

        max_rot = float(self.config.neck_extreme_degrees)

        if self.config.conservative_mode:

            max_rot = min(max_rot, 70.0)

        for key in ["neck_01", "neck_02", "head"]:

            node = canonical.get(key)

            if not node:

                continue

            for axis_index in axes:

                attr = ROTATE_ATTRS[axis_index]

                curves = cmds.listConnections("%s.%s" % (node, attr), source=True, destination=False, type="animCurve") or []

                for curve in curves:

                    fixed += damp_clamp_curve(curve, max_abs=max_rot, strength=strength)

                                                                                     

        head = canonical.get("head")

        neck = canonical.get("neck_01")

        if head and neck and not self.config.conservative_mode:

            fixed += redistribute_head_to_neck(head, neck, weight_to_neck=0.25)

        return fixed



    def fix_arm_twist(self, canonical: Dict[str, str]) -> int:

        fixed = 0

        axis_index = axis_to_index(self.config.arm_twist_axis)

        attr = ROTATE_ATTRS[axis_index]

        threshold = float(self.config.arm_twist_degrees)

        if self.config.conservative_mode:

            threshold = min(threshold, 110.0)

        for key in ["upperarm_l", "lowerarm_l", "upperarm_r", "lowerarm_r"]:

            node = canonical.get(key)

            if not node:

                continue

            curves = cmds.listConnections("%s.%s" % (node, attr), source=True, destination=False, type="animCurve") or []

            for curve in curves:

                fixed += damp_clamp_curve(curve, max_abs=threshold, strength=self.config.correction_strength)

        return fixed



    def fix_hand_flip(self, canonical: Dict[str, str]) -> int:

        fixed = 0

        axes = axes_from_text(self.config.hand_flip_axes)

        max_rot = float(self.config.hand_flip_degrees)

        if self.config.conservative_mode:

            max_rot = min(max_rot, 135.0)

        for key in ["hand_l", "hand_r"]:

            node = canonical.get(key)

            if not node:

                continue

            for axis_index in axes:

                attr = ROTATE_ATTRS[axis_index]

                curves = cmds.listConnections("%s.%s" % (node, attr), source=True, destination=False, type="animCurve") or []

                for curve in curves:

                    fixed += damp_clamp_curve(curve, max_abs=max_rot, strength=self.config.correction_strength)

                    fixed += smooth_spikes_in_curve(curve, threshold=self.config.hand_flip_degrees, strength=self.config.correction_strength)

        return fixed



    def smooth_rotation_curves(self, joints: List[str], strength: float = 0.15) -> int:

        fixed = 0

        for jnt in joints:

            for attr in ROTATE_ATTRS:

                curves = cmds.listConnections("%s.%s" % (jnt, attr), source=True, destination=False, type="animCurve") or []

                for curve in curves:

                    fixed += light_smooth_curve(curve, strength=strength)

        return fixed





def get_curve_key_data(curve: str) -> Tuple[List[float], List[float]]:

    times = cmds.keyframe(curve, query=True, timeChange=True) or []

    values = cmds.keyframe(curve, query=True, valueChange=True) or []

    return [float(x) for x in times], [float(x) for x in values]





def set_curve_value(curve: str, time_value: float, value: float) -> None:

    cmds.keyframe(curve, edit=True, time=(time_value, time_value), valueChange=float(value))





def clamp_anim_curve_values(curve: str, min_value: float, max_value: float) -> int:

    times, values = get_curve_key_data(curve)

    fixed = 0

    for t, v in zip(times, values):

        if not is_finite(v):

            new_value = 1.0

        else:

            new_value = clamp(v, min_value, max_value)

        if abs(new_value - v) > 1e-6:

            set_curve_value(curve, t, new_value)

            fixed += 1

    return fixed





def smooth_spikes_in_curve(curve: str, threshold: float, strength: float = 0.65) -> int:

    times, values = get_curve_key_data(curve)

    if len(values) < 3:

        return 0

    fixed = 0

    strength = clamp(strength, 0.0, 1.0)

    new_values = list(values)

    for i in range(1, len(values) - 1):

        prev_v = values[i - 1]

        cur_v = values[i]

        next_v = values[i + 1]

        if not (is_finite(prev_v) and is_finite(cur_v) and is_finite(next_v)):

            avg = 0.5 * ((prev_v if is_finite(prev_v) else 0.0) + (next_v if is_finite(next_v) else 0.0))

            new_values[i] = avg

            fixed += 1

            continue

        prev_delta = abs(cur_v - prev_v)

        next_delta = abs(cur_v - next_v)

        neighbor_delta = abs(next_v - prev_v)

        if prev_delta > threshold and next_delta > threshold and neighbor_delta < threshold:

            avg = 0.5 * (prev_v + next_v)

            new_values[i] = cur_v * (1.0 - strength) + avg * strength

            fixed += 1

    for t, old, new in zip(times, values, new_values):

        if abs(old - new) > 1e-6:

            set_curve_value(curve, t, new)

    return fixed





def damp_clamp_curve(curve: str, max_abs: float, strength: float = 0.65) -> int:

    times, values = get_curve_key_data(curve)

    fixed = 0

    strength = clamp(strength, 0.0, 1.0)

    for t, v in zip(times, values):

        if not is_finite(v):

            target = 0.0

        elif abs(v) > max_abs:

            target = clamp(v, -max_abs, max_abs)

        else:

            continue

        new_value = v * (1.0 - strength) + target * strength if is_finite(v) else target

        set_curve_value(curve, t, new_value)

        fixed += 1

    return fixed





def light_smooth_curve(curve: str, strength: float = 0.15) -> int:

    times, values = get_curve_key_data(curve)

    if len(values) < 3:

        return 0

    strength = clamp(strength, 0.0, 1.0)

    changed = 0

    new_values = list(values)

    for i in range(1, len(values) - 1):

        avg = 0.5 * (values[i - 1] + values[i + 1])

        new_values[i] = values[i] * (1.0 - strength) + avg * strength

        if abs(new_values[i] - values[i]) > 1e-5:

            changed += 1

    for t, old, new in zip(times, values, new_values):

        if abs(old - new) > 1e-5:

            set_curve_value(curve, t, new)

    return changed





def redistribute_head_to_neck(head: str, neck: str, weight_to_neck: float = 0.25) -> int:

    fixed = 0

    weight_to_neck = clamp(weight_to_neck, 0.0, 1.0)

    for attr in ROTATE_ATTRS:

        head_curves = cmds.listConnections("%s.%s" % (head, attr), source=True, destination=False, type="animCurve") or []

        neck_curves = cmds.listConnections("%s.%s" % (neck, attr), source=True, destination=False, type="animCurve") or []

        if not head_curves:

            continue

        head_curve = head_curves[0]

        times, values = get_curve_key_data(head_curve)

        if not neck_curves:

                                                 

            for t in times:

                cmds.setKeyframe(neck, attribute=attr, time=t)

            neck_curves = cmds.listConnections("%s.%s" % (neck, attr), source=True, destination=False, type="animCurve") or []

        if not neck_curves:

            continue

        neck_curve = neck_curves[0]

        neck_times, neck_values = get_curve_key_data(neck_curve)

        neck_by_time = dict(zip(neck_times, neck_values))

        for t, v in zip(times, values):

            shift = v * weight_to_neck

            set_curve_value(head_curve, t, v - shift)

            neck_v = neck_by_time.get(t, 0.0)

            set_curve_value(neck_curve, t, neck_v + shift)

            fixed += 2

    return fixed





                                                                               

             

                                                                               



class NPZImporter:



    def __init__(self, config: ToolConfig, mapping: JointMapping, log_callback=None):

        self.config = config

        self.mapping = mapping

        self.log_callback = log_callback



    def log(self, message: str) -> None:

        if self.log_callback:

            self.log_callback(message)



    def import_npz_to_source_skeleton(self, npz_path: str) -> Tuple[List[str], Tuple[float, float]]:

        require_maya()

        if not NUMPY_AVAILABLE:

            raise RuntimeError("NumPy is not available in this Maya Python environment. Cannot import NPZ.")

        if not self.config.source_skeleton_file:

            raise RuntimeError("NPZ import needs a Source Skeleton File. NPZ contains motion data, not a Maya joint hierarchy.")



        schema = load_json_file(self.config.npz_schema_json) if self.config.npz_schema_json else {}

        if not schema:

            schema = {

                "joint_names_key": "joint_names",

                "local_euler_key": "local_euler",

                "root_translation_key": "root_translation",

                "degrees": True,

                "start_frame": 1,

                "fps": self.config.target_frame_rate,

            }



        import_maya_or_fbx(self.config.source_skeleton_file, namespace="SRC")

        source_joints = get_all_joints()

        if not source_joints:

            raise RuntimeError("Source skeleton imported for NPZ, but no joints were found.")



        data = _np.load(normalize_path(npz_path), allow_pickle=True)

        joint_names = self._get_joint_names(data, schema)

        rotations, rotation_format = self._get_rotations(data, schema, len(joint_names))

        root_translation = self._get_root_translation(data, schema)

        start_frame = float(schema.get("start_frame", 1))

        frames = int(rotations.shape[0])

        end_frame = start_frame + frames - 1

        set_timeline(start_frame, end_frame)



        joint_lookup = self._build_npz_joint_lookup(source_joints, joint_names)

        degrees = bool(schema.get("degrees", True))



        for frame_index in range(frames):

            frame = start_frame + frame_index

            for joint_index, joint_name in enumerate(joint_names):

                maya_joint = joint_lookup.get(joint_name)

                if not maya_joint:

                    continue

                rot_triplet = rotations[frame_index, joint_index]

                if rotation_format == "axis_angle":

                    euler = axis_angle_to_euler_xyz(rot_triplet)

                                                           

                else:

                    euler = [float(x) for x in rot_triplet]

                    if not degrees:

                        euler = [math.degrees(x) for x in euler]

                for attr, value in zip(ROTATE_ATTRS, euler):

                    cmds.setKeyframe(maya_joint, attribute=attr, time=frame, value=float(value))



            if root_translation is not None and frame_index < len(root_translation):

                root = self.mapping.find_exact_or_alias(source_joints, "root") or get_root_joints(source_joints)[0]

                for attr, value in zip(TRANSLATE_ATTRS, root_translation[frame_index]):

                    cmds.setKeyframe(root, attribute=attr, time=frame, value=float(value))



        return source_joints, (start_frame, end_frame)



    def _get_joint_names(self, data, schema: Dict[str, Any]) -> List[str]:

        key = schema.get("joint_names_key", "joint_names")

        if key in data:

            raw = data[key]

            names = []

            for value in raw.tolist():

                if isinstance(value, bytes):

                    names.append(value.decode("utf-8"))

                else:

                    names.append(str(value))

            return names

        names = schema.get("joint_names", [])

        if names:

            return [str(x) for x in names]

        raise RuntimeError("NPZ schema does not provide joint names, and the NPZ file has no joint_names array.")



    def _get_rotations(self, data, schema: Dict[str, Any], joint_count: int):

        local_euler_key = schema.get("local_euler_key", "local_euler")

        poses_key = schema.get("poses_key", "poses")

        if local_euler_key in data:

            arr = data[local_euler_key]

            rotation_format = "euler"

        elif poses_key in data:

            arr = data[poses_key]

            rotation_format = schema.get("rotation_format", "axis_angle")

        else:

            raise RuntimeError("NPZ file does not contain local_euler or poses array based on schema.")

        arr = _np.asarray(arr, dtype=float)

        if arr.ndim == 2:

            expected = joint_count * 3

            if arr.shape[1] < expected:

                raise RuntimeError("NPZ rotation array has %d columns, expected at least %d." % (arr.shape[1], expected))

            arr = arr[:, :expected].reshape((arr.shape[0], joint_count, 3))

        elif arr.ndim == 3 and arr.shape[2] == 3:

            pass

        else:

            raise RuntimeError("Unsupported NPZ rotation array shape: %s" % (arr.shape,))

        return arr, rotation_format



    def _get_root_translation(self, data, schema: Dict[str, Any]):

        key = schema.get("root_translation_key", "root_translation")

        if key and key in data:

            arr = _np.asarray(data[key], dtype=float)

            if arr.ndim == 2 and arr.shape[1] >= 3:

                return arr[:, :3]

        return None



    def _build_npz_joint_lookup(self, maya_joints: List[str], joint_names: List[str]) -> Dict[str, str]:

        lookup = {}

        for name in joint_names:

            found = self.mapping.find_exact_or_alias(maya_joints, name)

            if found:

                lookup[name] = found

        return lookup





def axis_angle_to_euler_xyz(axis_angle: Iterable[float]) -> Tuple[float, float, float]:

    x, y, z = [float(v) for v in axis_angle]

    angle = math.sqrt(x * x + y * y + z * z)

    if angle < 1e-8:

        return 0.0, 0.0, 0.0

    ax, ay, az = x / angle, y / angle, z / angle

    c = math.cos(angle)

    s = math.sin(angle)

    t = 1.0 - c

                                      

    m00 = c + ax * ax * t

    m11 = c + ay * ay * t

    m22 = c + az * az * t

    m01 = ax * ay * t - az * s

    m02 = ax * az * t + ay * s

    m10 = ay * ax * t + az * s

    m12 = ay * az * t - ax * s

    m20 = az * ax * t - ay * s

    m21 = az * ay * t + ax * s

                           

    if abs(m02) < 0.999999:

        y_angle = math.asin(clamp(m02, -1.0, 1.0))

        x_angle = math.atan2(-m12, m22)

        z_angle = math.atan2(-m01, m00)

    else:

        y_angle = math.asin(clamp(m02, -1.0, 1.0))

        x_angle = math.atan2(m21, m11)

        z_angle = 0.0

    return math.degrees(x_angle), math.degrees(y_angle), math.degrees(z_angle)





                                                                               

            

                                                                               



class AnimationRetargeter:

    def __init__(self, config: ToolConfig, mapping: JointMapping, log_callback=None):

        self.config = config

        self.mapping = mapping

        self.log_callback = log_callback



    def log(self, message: str) -> None:

        if self.log_callback:

            self.log_callback(message)



    def retarget_current_scene(

        self,

        source_joints: List[str],

        target_joints: List[str],

        start: float,

        end: float,

        source_rest_joints: Optional[List[str]] = None,

    ) -> Dict[str, Any]:

        method = (self.config.retarget_method or "humanik_batch").strip().lower()

        if method in {"humanik_batch", "humanik", "maya_hik", "hik_batch", "hik"}:

            return self._retarget_with_humanik_batch(source_joints, target_joints, start, end, source_rest_joints)

        if method in {"positional_ik_solver", "ik_pose_solver", "directional_ik", "positional"}:

            return self._retarget_with_positional_ik_solver(source_joints, target_joints, start, end, source_rest_joints)

        if method in {"hierarchical_world_matrix", "world_matrix_delta_direct", "safe_world_matrix", "hierarchical_matrix"}:

            return self._retarget_with_hierarchical_world_matrix(source_joints, target_joints, start, end, source_rest_joints)

        if method in {"constraint", "constraints", "old"}:

            return self._retarget_with_constraints(source_joints, target_joints, start, end)

        if method in {"direct_constraints_no_offset", "direct_no_offset", "direct_constraints"}:

            return self._retarget_with_direct_constraints_no_offset(source_joints, target_joints, start, end)

        if method in {"world_euler_delta_constraints", "world_euler_delta", "world_euler", "euler_world"}:

            return self._retarget_with_world_euler_delta_constraints(source_joints, target_joints, start, end, source_rest_joints)

        if method in {"local_euler_delta", "euler", "local_euler"}:

            return self._retarget_with_local_euler_delta(source_joints, target_joints, start, end, source_rest_joints)

        if method in {"local_matrix_delta", "matrix", "matrix_delta"}:

            return self._retarget_with_local_matrix_delta(source_joints, target_joints, start, end, source_rest_joints)

        return self._retarget_with_rest_world_delta_constraints(source_joints, target_joints, start, end, source_rest_joints)





                                                                        

                                                            

                                                                        



    @staticmethod

    def _mel_quote(value: str) -> str:

        return str(value or "").replace('\\', '/').replace('"', '\\"')



    def _hik_source_required_scripts(self) -> None:

        require_maya()

        self.log("HumanIK: loading plugins and MEL scripts...")

        for plugin in ("mayaHIK", "mayaCharacterization", "retargeterNodes"):

            try:

                if not cmds.pluginInfo(plugin, query=True, loaded=True):

                    cmds.loadPlugin(plugin, quiet=True)

                self.log("HumanIK: plugin loaded/available: %s" % plugin)

            except Exception as exc:

                                                                                   

                                                                                 

                self.log("HumanIK WARNING: could not load plugin %s: %s" % (plugin, exc))



        maya_location = os.environ.get("MAYA_LOCATION", "")

        script_candidates = []

        if maya_location:

            script_candidates.extend([

                os.path.join(maya_location, "scripts", "others", "hikGlobalUtils.mel"),

                os.path.join(maya_location, "scripts", "others", "hikCharacterControlsUI.mel"),

                os.path.join(maya_location, "scripts", "others", "hikDefinitionOperations.mel"),

                os.path.join(maya_location, "scripts", "others", "CharacterPipeline.mel"),

                os.path.join(maya_location, "scripts", "others", "characterSelector.mel"),

            ])

                                                                                     

                                                                                    

                                                                                      

                                                                                      

        if maya_location:

            others_dir = os.path.join(maya_location, "scripts", "others")

            try:

                import glob

                for pattern in ("hik*.mel", "HIK*.mel", "Character*.mel", "character*.mel"):

                    for path in glob.glob(os.path.join(others_dir, pattern)):

                        if path not in script_candidates:

                            script_candidates.append(path)

            except Exception as exc:

                self.log("HumanIK WARNING: could not enumerate extra HIK MEL scripts: %s" % exc)



        sourced = set()

        for script in script_candidates:

            try:

                if os.path.isfile(script) and script not in sourced:

                    mel.eval('source "%s"' % self._mel_quote(script))

                    sourced.add(script)

                    self.log("HumanIK: sourced %s" % os.path.basename(script))

            except Exception as exc:

                                                                                       

                                                                                      

                self.log("HumanIK WARNING: could not source %s: %s" % (script, exc))



                                                                                      

                                                                       

        for proc in ("setCharacterObject", "mayaHIKsetCharacterInput", "hikBakeCharacter", "hikBakeToSkeleton"):

            try:

                exists = bool(mel.eval('exists "%s"' % proc))

            except Exception:

                exists = False

            self.log("HumanIK: MEL procedure %s available=%s" % (proc, exists))



        try:

            mel.eval("HIKCharacterControlsTool;")

        except Exception as exc:

            raise RuntimeError("HumanIK Character Controls could not be opened/initialized. HumanIK is unavailable in this Maya session: %s" % exc)



    def _hik_create_character(self, name: str) -> str:

        name = re.sub(r"[^A-Za-z0-9_]", "_", name or "ALPHA_HIK")

        before = set(cmds.ls(type="HIKCharacterNode") or [])

        char = ""

        errors = []

        for cmd in (

            'CreateHIKCharacterWithName "%s"' % self._mel_quote(name),

            'hikCreateCharacter("%s")' % self._mel_quote(name),

        ):

            try:

                result = mel.eval(cmd)

                if result:

                    char = str(result)

                    break

            except Exception as exc:

                errors.append("%s -> %s" % (cmd, exc))

        after = set(cmds.ls(type="HIKCharacterNode") or [])

        if not char:

            created = list(after - before)

            if created:

                char = created[0]

        if not char or not cmds.objExists(char):

            raise RuntimeError("HumanIK character creation failed. Tried commands: %s" % " | ".join(errors))

        try:

            mel.eval('hikSetCurrentCharacter("%s")' % self._mel_quote(char))

            mel.eval('hikUpdateCharacterList()')

            mel.eval('hikSelectDefinitionTab()')

        except Exception:

            pass

        self.log("HumanIK: created character definition: %s" % char)

        return char



    def _hik_unlock_transform_channels(self, nodes: Iterable[str]) -> None:

        for node in nodes:

            if not safe_cmds_exists(node):

                continue

            for attr in ("tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"):

                plug = node + "." + attr

                if cmds.objExists(plug):

                    try:

                        cmds.setAttr(plug, lock=False, keyable=True)

                    except Exception:

                        pass



    def _hik_build_canonical_map(self, joints: List[str], pairs: Dict[str, Tuple[str, str]], index: int) -> Dict[str, str]:

        out: Dict[str, str] = {}

        for canonical, pair in pairs.items():

            try:

                node = pair[index]

            except Exception:

                continue

            if node and safe_cmds_exists(node):

                out[canonical] = node

        for canonical in DEFAULT_RETARGET_CANONICAL_ORDER:

            if canonical not in out:

                found = self.mapping.find_by_alias(joints, canonical)

                if found:

                    out[canonical] = found

                                                                                           

                                                                                           

        if "root" not in out and "pelvis" in out:

            try:

                parent = cmds.listRelatives(out["pelvis"], parent=True, fullPath=True) or []

                if parent:

                    out["root"] = parent[0]

            except Exception:

                pass

        return out





    def _hik_copy_live_source_animation_to_rest_character_source(

        self,

        live_source_map: Dict[str, str],

        rest_character_source_map: Dict[str, str],

        start: float,

        end: float,

    ) -> Dict[str, Any]:

        frames = self._build_sample_frames(start, end)

        canonical_keys = [c for c in DEFAULT_RETARGET_CANONICAL_ORDER if c in live_source_map and c in rest_character_source_map]



                                                                                            

                                                                                                  

                                                                         

        def _finger_descendants_by_short(_hand_node):

            out = {}

            if not (_hand_node and safe_cmds_exists(_hand_node)):

                return out

            try:

                descendants = cmds.listRelatives(_hand_node, allDescendents=True, type="joint", fullPath=True) or []

            except Exception:

                descendants = []

            for n in descendants:

                sn = short_name(n)

                low = sn.lower()

                if any(tok in low for tok in ("thumb", "index", "middle", "ring", "pinky")):

                    out[sn] = n

            return out



        finger_pairs = []

        if bool(getattr(self.config, "humanik_copy_live_fingers_to_rest_source", True)):

            for _side in ("l", "r"):

                _lh = live_source_map.get("hand_%s" % _side)

                _rh = rest_character_source_map.get("hand_%s" % _side)

                _live_f = _finger_descendants_by_short(_lh)

                _rest_f = _finger_descendants_by_short(_rh)

                for _sn, _src in sorted(_live_f.items()):

                    _dst = _rest_f.get(_sn)

                    if _dst and safe_cmds_exists(_src) and safe_cmds_exists(_dst):

                        finger_pairs.append((_src, _dst, _sn))

                                             

            _seen = set()

            _dedup = []

            for _src, _dst, _sn in finger_pairs:

                _key = (_src, _dst)

                if _key not in _seen:

                    _seen.add(_key)

                    _dedup.append((_src, _dst, _sn))

            finger_pairs = _dedup



        if len(canonical_keys) < 8:

            raise RuntimeError(

                "HumanIK rest-character source animation copy failed: too few live/rest source pairs (%d)." % len(canonical_keys)

            )



                                                                                                      

        rest_nodes = sorted(set([rest_character_source_map[c] for c in canonical_keys if safe_cmds_exists(rest_character_source_map.get(c, ""))] + [dst for _src, dst, _sn in finger_pairs if safe_cmds_exists(dst)]))

        for node in rest_nodes:

            unlock_transform_attrs(node)

            for curve in get_connected_anim_curves(node, ROTATE_ATTRS + TRANSLATE_ATTRS):

                try:

                    cmds.delete(curve)

                except Exception:

                    pass



        copy_all_translate = bool(getattr(self.config, "humanik_copy_all_source_translates_to_rest_source", False))

        keyed_rotate = 0

        keyed_translate = 0

        failed = 0

        preview = []

        self.log(

            "HumanIK v1.3.0: copying live source animation onto rest-characterized source duplicate: pairs=%d frames=%d copy_all_translate=%s"

            % (len(canonical_keys), len(frames), copy_all_translate)

        )

        if finger_pairs:

            self.log("HumanIK v2.22 source-copy: copying animated source fingers onto rest-character source: finger_pairs=%d preview=%s" % (len(finger_pairs), ",".join(_sn for _src, _dst, _sn in finger_pairs[:20])))



        for frame in frames:

            cmds.currentTime(frame, edit=True, update=True)

            try:

                cmds.refresh(force=True)

            except Exception:

                pass

            for canonical in canonical_keys:

                src = live_source_map.get(canonical)

                dst = rest_character_source_map.get(canonical)

                if not (src and dst and safe_cmds_exists(src) and safe_cmds_exists(dst)):

                    failed += 1

                    continue

                try:

                                                                                                  

                                                                                                     

                    rot = self._get_vec(src, ROTATE_ATTRS)

                    self._set_vec(dst, ROTATE_ATTRS, rot)

                    for attr in ROTATE_ATTRS:

                        cmds.setKeyframe(dst, attribute=attr, time=frame)

                        keyed_rotate += 1



                                                                                              

                                                                                                   

                                                                                                   

                                                                                                 

                    if copy_all_translate or canonical in {"root", "pelvis"}:

                        trans = self._get_vec(src, TRANSLATE_ATTRS)

                        self._set_vec(dst, TRANSLATE_ATTRS, trans)

                        for attr in TRANSLATE_ATTRS:

                            cmds.setKeyframe(dst, attribute=attr, time=frame)

                            keyed_translate += 1

                    if len(preview) < 6 and abs(float(frame) - float(start)) < 0.0001:

                        preview.append("%s:%s->%s r=%s" % (canonical, short_name(src), short_name(dst), tuple(round(x, 3) for x in rot)))

                except Exception as exc:

                    failed += 1

                    if failed <= 8:

                        self.log("HumanIK source-copy WARNING: %s %s -> %s at frame %.3f failed: %s" % (canonical, short_name(src), short_name(dst), frame, exc))



            for _src, _dst, _sn in finger_pairs:

                try:

                    rot = self._get_vec(_src, ROTATE_ATTRS)

                    self._set_vec(_dst, ROTATE_ATTRS, rot)

                    for attr in ROTATE_ATTRS:

                        cmds.setKeyframe(_dst, attribute=attr, time=frame)

                        keyed_rotate += 1

                except Exception as exc:

                    failed += 1

                    if failed <= 8:

                        self.log("HumanIK source-copy WARNING: finger %s %s -> %s at frame %.3f failed: %s" % (_sn, short_name(_src), short_name(_dst), frame, exc))



        cmds.currentTime(start, edit=True)

        anim_curves = count_anim_curves_on_nodes(rest_nodes)

        self.log("HumanIK v1.3.0 source-copy preview: %s" % "; ".join(preview))

        self.log(

            "HumanIK v1.3.0 source-copy finished: rest_source_nodes=%d frames=%d keyed_rotate=%d keyed_translate=%d anim_curves=%d failed_samples=%d"

            % (len(rest_nodes), len(frames), keyed_rotate, keyed_translate, anim_curves, failed)

        )

        if anim_curves < 20:

            raise RuntimeError("HumanIK rest-character source received too few animation curves (%d)." % anim_curves)

        return {

            "humanik_rest_character_source_enabled": True,

            "humanik_rest_character_source_pair_count": len(canonical_keys),

            "humanik_rest_character_source_frame_count": len(frames),

            "humanik_rest_character_source_keyed_rotate_samples": keyed_rotate,

            "humanik_rest_character_source_keyed_translate_samples": keyed_translate,

            "humanik_rest_character_source_anim_curves": anim_curves,

            "humanik_rest_character_source_failed_samples": failed,

            "humanik_rest_character_source_finger_pair_count": len(finger_pairs),

        }





    def _pre_calibrate_target_hik_arm_reference_pose(self, target_map: Dict[str, str]) -> Dict[str, Any]:

        stats: Dict[str, Any] = {"humanik_pre_target_arm_reference_pose_enabled": False}

        if not bool(getattr(self.config, "humanik_pre_calibrate_target_arm_reference_pose", False)):

            self.log("HumanIK Option1 v2.2 target arm reference pre-calibration skipped: disabled.")

            return stats



        required = ["pelvis", "head", "thigh_l", "thigh_r", "upperarm_l", "lowerarm_l", "hand_l", "upperarm_r", "lowerarm_r", "hand_r"]

        missing = [c for c in required if not target_map.get(c) or not safe_cmds_exists(target_map.get(c))]

        if missing:

            self.log("HumanIK Option1 v2.2 target arm reference pre-calibration skipped: missing %s" % ", ".join(missing))

            return stats



        try:

            self._hik_unlock_transform_channels(target_map.values())

        except Exception:

            pass



        pelvis = get_world_position(target_map["pelvis"])

        head = get_world_position(target_map["head"])

        lhip = get_world_position(target_map["thigh_l"])

        rhip = get_world_position(target_map["thigh_r"])

        side_axis = self._v_norm(self._v_sub(rhip, lhip), fallback=(1.0, 0.0, 0.0))

        up_raw = self._v_sub(head, pelvis)

        up_axis = self._v_sub(up_raw, self._v_mul(side_axis, self._v_dot(up_raw, side_axis)))

        up_axis = self._v_norm(up_axis, fallback=(0.0, 1.0, 0.0))

        front_axis = self._v_norm(self._v_cross(side_axis, up_axis), fallback=(0.0, 0.0, 1.0))

        up_axis = self._v_norm(self._v_cross(front_axis, side_axis), fallback=up_axis)

        front_axis = self._v_norm(self._v_cross(side_axis, up_axis), fallback=front_axis)

        strength = max(0.0, min(1.0, float(getattr(self.config, "humanik_pre_calibrate_target_arm_reference_pose_strength", 1.0) or 0.0)))



        temp_nodes: List[str] = []

        constraints: List[str] = []

        fixed = 0

        samples: List[str] = []

        for side, sign in (("l", -1.0), ("r", 1.0)):

            upper_c = "upperarm_%s" % side

            lower_c = "lowerarm_%s" % side

            hand_c = "hand_%s" % side

            upper = target_map.get(upper_c)

            lower = target_map.get(lower_c)

            hand = target_map.get(hand_c)

            if not (upper and lower and hand and safe_cmds_exists(upper) and safe_cmds_exists(lower) and safe_cmds_exists(hand)):

                continue

            sh = get_world_position(upper)

            el = get_world_position(lower)

            wr = get_world_position(hand)

            upper_len = max(self._v_len(self._v_sub(el, sh)), 1.0)

            lower_len = max(self._v_len(self._v_sub(wr, el)), 1.0)

            arm_dir = self._v_mul(side_axis, sign)

                                                                                                    

                                                                                               

            desired_wrist = self._v_add(sh, self._v_mul(arm_dir, (upper_len + lower_len) * 0.98))

            desired_wrist = self._v_add(desired_wrist, self._v_mul(up_axis, -0.03 * (upper_len + lower_len)))

            desired_elbow = self._v_add(sh, self._v_mul(arm_dir, upper_len * 0.98))

            desired_elbow = self._v_add(desired_elbow, self._v_mul(up_axis, -0.05 * upper_len))

            desired_elbow = self._v_add(desired_elbow, self._v_mul(front_axis, 0.06 * upper_len))

            if strength < 0.999:

                desired_wrist = self._v_add(wr, self._v_mul(self._v_sub(desired_wrist, wr), strength))

                desired_elbow = self._v_add(el, self._v_mul(self._v_sub(desired_elbow, el), strength))

            end_loc = self._make_temp_locator("ALPHA_HIKRefPose_%s_END_LOC" % side, desired_wrist)

            pole_loc = self._make_temp_locator("ALPHA_HIKRefPose_%s_POLE_LOC" % side, self._v_add(desired_elbow, self._v_mul(front_axis, max(upper_len + lower_len, 10.0))))

            temp_nodes.extend([end_loc, pole_loc])

            handle = self._create_ik_handle_safe("ALPHA_HIKRefPose_%s_IKH" % side, upper, hand)

            if not handle:

                self.log("HumanIK Option1 v2.2 WARNING: could not create reference-pose IK for %s arm." % side)

                continue

            temp_nodes.append(handle)

            try:

                constraints.append(cmds.pointConstraint(end_loc, handle, maintainOffset=False)[0])

            except Exception as exc:

                self.log("HumanIK Option1 v2.2 WARNING: could not constrain reference-pose IK end for %s: %s" % (side, exc))

            try:

                constraints.append(cmds.poleVectorConstraint(pole_loc, handle)[0])

            except Exception as exc:

                self.log("HumanIK Option1 v2.2 WARNING: could not constrain reference-pose IK pole for %s: %s" % (side, exc))

            try:

                cmds.currentTime(cmds.currentTime(q=True), edit=True, update=True)

                cmds.refresh(force=True)

            except Exception:

                pass

            try:

                new_el = get_world_position(lower)

                new_wr = get_world_position(hand)

                upper_vec = self._v_sub(new_el, sh)

                lower_vec = self._v_sub(new_wr, new_el)

                side_align_upper = self._v_dot(self._v_norm(upper_vec), arm_dir)

                side_align_lower = self._v_dot(self._v_norm(lower_vec), arm_dir)

                samples.append("%s upperAlign=%.3f lowerAlign=%.3f" % (side, side_align_upper, side_align_lower))

            except Exception:

                pass

            fixed += 1

                                                                                                         

        for n in constraints + temp_nodes:

            try:

                if n and safe_cmds_exists(n):

                    cmds.delete(n)

            except Exception:

                pass

        self.log("HumanIK Option1 v2.2 target arm reference pre-calibration: fixed_sides=%d strength=%.2f %s" % (fixed, strength, "; ".join(samples[:4])))

        stats.update({

            "humanik_pre_target_arm_reference_pose_enabled": fixed > 0,

            "humanik_pre_target_arm_reference_pose_fixed_sides": fixed,

            "humanik_pre_target_arm_reference_pose_strength": strength,

            "humanik_pre_target_arm_reference_pose_samples": samples,

        })

        return stats





    def _post_apply_inverse_hik_reference_pose_offset_to_arms(

        self,

        target_map: Dict[str, str],

        target_bake_joints: List[str],

        start: float,

        end: float,

        original_rest_local_matrices: Dict[str, Any],

        hik_reference_local_matrices: Dict[str, Any],

        original_rest_local_translates: Dict[str, Tuple[float, float, float]],

    ) -> Dict[str, Any]:

        stats: Dict[str, Any] = {"humanik_inverse_reference_arm_offset_enabled": False}

        if not bool(getattr(self.config, "humanik_apply_inverse_reference_pose_offset_to_arms", True)):

            self.log("HumanIK Option1 v2.2.1 inverse reference-pose arm offset skipped: disabled.")

            return stats



        arm_keys = [

            "clavicle_l", "upperarm_l", "lowerarm_l", "hand_l",

            "clavicle_r", "upperarm_r", "lowerarm_r", "hand_r",

        ]

        usable = []

        missing = []

        for canonical in arm_keys:

            node = target_map.get(canonical)

            if not (node and safe_cmds_exists(node)):

                missing.append(canonical)

                continue

            if canonical not in original_rest_local_matrices or canonical not in hik_reference_local_matrices:

                missing.append(canonical)

                continue

            usable.append((canonical, node))

        if not usable:

            self.log("HumanIK Option1 v2.2.1 inverse reference-pose arm offset skipped: no usable arm joints.")

            return stats



        frames = []

        sample_by = max(float(self.config.bake_sample_by or 1.0), 0.001)

        frame = float(start)

        while frame <= float(end) + 0.0001:

            frames.append(round(frame, 6))

            frame += sample_by

        if frames and frames[-1] < float(end):

            frames.append(float(end))

        if not frames:

            frames = [float(start)]



        keyed = 0

        max_matrix_delta = 0.0

        samples = []

        for frame in frames:

            cmds.currentTime(frame, edit=True)

            for canonical, node in usable:

                try:

                    baked_local = self._matrix_from_node_local(node)

                    original_rest = original_rest_local_matrices[canonical]

                    hik_ref = hik_reference_local_matrices[canonical]

                    delta = hik_ref.inverse() * baked_local

                    final_local = original_rest * delta

                    before = self._matrix_to_list(baked_local)

                    self._apply_local_matrix_to_joint(node, final_local, keep_translate=original_rest_local_translates.get(canonical))

                    after = self._matrix_to_list(self._matrix_from_node_local(node))

                    max_matrix_delta = max(max_matrix_delta, sum(abs(after[i] - before[i]) for i in range(16)))

                    cmds.setKeyframe(node, attribute=ROTATE_ATTRS, time=frame)

                    keyed += 3

                    if len(samples) < 6 and frame in (frames[0], frames[len(frames)//2], frames[-1]):

                        samples.append("f=%.2f %s" % (frame, canonical))

                except Exception as exc:

                    if len(samples) < 6:

                        samples.append("%s failed:%s" % (canonical, exc))



        bake_nodes = [node for _canonical, node in usable if node in target_bake_joints or safe_cmds_exists(node)]

        if bake_nodes:

            try:

                cmds.bakeResults(

                    bake_nodes,

                    time=(start, end),

                    simulation=True,

                    sampleBy=sample_by,

                    disableImplicitControl=True,

                    preserveOutsideKeys=True,

                    sparseAnimCurveBake=False,

                    removeBakedAttributeFromLayer=False,

                    removeBakedAnimFromLayer=False,

                    bakeOnOverrideLayer=False,

                    minimizeRotation=True,

                    controlPoints=False,

                    shape=False,

                )

            except Exception as exc:

                self.log("HumanIK Option1 v2.2.1 inverse reference-pose arm offset bake warning: %s" % exc)



        self.log(

            "HumanIK Option1 v2.2.1 inverse reference-pose arm offset applied: joints=%d frames=%d keyed_rotate_samples=%d max_matrix_delta=%.3f missing=%s samples=%s"

            % (len(usable), len(frames), keyed, max_matrix_delta, ",".join(missing[:8]), "; ".join(samples[:6]))

        )

        stats.update({

            "humanik_inverse_reference_arm_offset_enabled": True,

            "humanik_inverse_reference_arm_offset_joint_count": len(usable),

            "humanik_inverse_reference_arm_offset_frame_count": len(frames),

            "humanik_inverse_reference_arm_offset_keyed_rotate_samples": keyed,

            "humanik_inverse_reference_arm_offset_max_matrix_delta": max_matrix_delta,

            "humanik_inverse_reference_arm_offset_missing": missing,

        })

        return stats



    def _hik_assign_character_definition(self, char: str, canonical_to_node: Dict[str, str], label: str) -> Dict[str, Any]:

        assigned: Dict[str, str] = {}

        missing_required = []

        self._hik_unlock_transform_channels(canonical_to_node.values())

        try:

            mel.eval('hikSetCurrentCharacter("%s")' % self._mel_quote(char))

            mel.eval('hikUpdateCharacterList()')

            mel.eval('hikSelectDefinitionTab()')

        except Exception:

            pass



        for canonical, slot_id in HIK_BONE_IDS.items():

                                                                                                   

                                                                                                   

                                                                                               

                                                                                                      

                                      

            if canonical == "root":

                self.log("HumanIK: skipping optional Reference/root slot for %s definition; root placement is handled after bake." % label)

                continue

            node = canonical_to_node.get(canonical)

            if not node or not safe_cmds_exists(node):

                continue

            try:

                mel.eval('setCharacterObject("%s","%s",%d,0)' % (self._mel_quote(node), self._mel_quote(char), int(slot_id)))

                assigned[canonical] = node

            except Exception as exc:

                self.log("HumanIK WARNING: could not assign %s %s -> slot %d: %s" % (label, node, slot_id, exc))

        for required in HIK_REQUIRED_CANONICAL:

            if required not in assigned:

                missing_required.append(required)

        if missing_required:

            raise RuntimeError("HumanIK %s definition missing required slots: %s" % (label, ", ".join(missing_required)))



                                                                                          

        try:

            prop = ""

            try:

                prop = mel.eval('getProperty2StateFromCharacter("%s")' % self._mel_quote(char))

            except Exception:

                conn = cmds.listConnections(char + ".propertyState", source=True, destination=False) or []

                prop = conn[0] if conn else ""

            if prop and cmds.objExists(prop):

                quality_attrs = {

                    "ForceActorSpace": 0,

                    "ScaleCompensationMode": 1,

                    "Mirror": 0,

                    "HipsHeightCompensationMode": 1,

                    "AnkleProximityCompensationMode": 1,

                    "AnkleHeightCompensationMode": 0,

                    "MassCenterCompensationMode": 1,

                }

                for attr, value in quality_attrs.items():

                    plug = prop + "." + attr

                    if cmds.objExists(plug):

                        try:

                            cmds.setAttr(plug, value)

                        except Exception:

                            pass

        except Exception as exc:

            self.log("HumanIK WARNING: could not set property node quality attrs for %s: %s" % (char, exc))



                                                                                             

        try:

            mel.eval('hikSetCurrentCharacter("%s")' % self._mel_quote(char))

            locked = False

            if cmds.objExists(char + ".InputCharacterizationLock"):

                locked = bool(cmds.getAttr(char + ".InputCharacterizationLock"))

            if not locked:

                mel.eval('hikToggleLockDefinition')

            if cmds.objExists(char + ".InputCharacterizationLock") and not bool(cmds.getAttr(char + ".InputCharacterizationLock")):

                raise RuntimeError("definition remains unlocked")

        except Exception as exc:

            raise RuntimeError("HumanIK %s character definition could not be locked/validated: %s" % (label, exc))



        self.log("HumanIK: %s character assigned %d slots. Required OK. Character=%s" % (label, len(assigned), char))

        return {

            "%s_hik_character" % label: char,

            "%s_hik_assigned_count" % label: len(assigned),

            "%s_hik_assigned_slots" % label: sorted(assigned.keys()),

        }



    def _hik_set_target_source(self, target_char: str, source_char: str) -> None:

        self.log("HumanIK: setting target source: target=%s source=%s" % (target_char, source_char))

        try:

            mel.eval('HIKCharacterControlsTool;')

        except Exception:

            pass

        try:

            mel.eval('hikSetCurrentCharacter("%s")' % self._mel_quote(target_char))

            mel.eval('hikUpdateCharacterList()')

        except Exception:

            pass

        attempts = [

            'mayaHIKsetCharacterInput("%s","%s")' % (self._mel_quote(target_char), self._mel_quote(source_char)),

            'hikSetCurrentSourceFromCharacter("%s")' % self._mel_quote(source_char),

            'hikSetCurrentSource("%s")' % self._mel_quote(source_char),

        ]

        errors = []

        any_success = False

        for cmd in attempts:

            try:

                mel.eval(cmd)

                any_success = True

            except Exception as exc:

                errors.append("%s -> %s" % (cmd, exc))

        for cmd in ('hikUpdateSourceList()', 'hikUpdateCurrentSourceFromUI()', 'hikUpdateContextualUI()', 'updateHIKCharacterToolEnableCheckBox()'):

            try:

                mel.eval(cmd)

            except Exception:

                pass

        if not any_success:

            raise RuntimeError("Could not set HumanIK source character. Errors: %s" % " | ".join(errors))

        cmds.refresh(force=True)



    def _hik_bake_target(self, target_char: str, target_joints_to_bake: List[str], start: float, end: float) -> int:

        self.log("HumanIK: baking solved retarget to target skeleton from %.3f to %.3f" % (start, end))

        try:

            mel.eval('hikSetCurrentCharacter("%s")' % self._mel_quote(target_char))

            mel.eval('hikUpdateCharacterList()')

            try:

                mel.eval('hikUpdateCurrentSourceFromUI()')

            except Exception:

                pass

                                                                                         

                                                                                            

                                                                                               

                                                                                             

                                                                                                 

            old_min = cmds.playbackOptions(q=True, min=True)

            old_max = cmds.playbackOptions(q=True, max=True)

            old_ast = cmds.playbackOptions(q=True, ast=True)

            old_aet = cmds.playbackOptions(q=True, aet=True)

            try:

                cmds.playbackOptions(e=True, min=start, max=end, ast=start, aet=end)

            except Exception:

                pass

            bake_errors = []

            baked = False

            bake_attempts = (

                'hikBakeCharacter "%s";' % self._mel_quote(target_char),

                'hikBakeCharacter("%s");' % self._mel_quote(target_char),

                'hikBakeToSkeleton 0;',

                'hikBakeToSkeleton(0);',

                'hikBakeToSkeleton 0',

            )

            for bake_cmd in bake_attempts:

                try:

                    mel.eval(bake_cmd)

                    self.log("HumanIK: native bake command succeeded: %s" % bake_cmd)

                    baked = True

                    break

                except Exception as exc:

                    bake_errors.append("%s -> %s" % (bake_cmd, exc))

            try:

                cmds.playbackOptions(e=True, min=old_min, max=old_max, ast=old_ast, aet=old_aet)

            except Exception:

                pass

            if not baked:

                raise RuntimeError(" | ".join(bake_errors))

        except Exception as exc:

            self.log("HumanIK ERROR: native HumanIK bake failed. Refusing to export a low-quality fallback result. Reason: %s" % exc)

            raise RuntimeError("Native HumanIK bake failed. This build no longer falls back to plain bakeResults because that produced visibly wrong retargets. Reason: %s" % exc)

            try:

                cmds.select(target_joints_to_bake, replace=True)

            except Exception:

                pass

            cmds.bakeResults(

                target_joints_to_bake,

                simulation=True,

                time=(start, end),

                sampleBy=max(float(self.config.bake_sample_by or 1.0), 0.001),

                disableImplicitControl=False,

                preserveOutsideKeys=False,

                sparseAnimCurveBake=False,

                removeBakedAttributeFromLayer=False,

                bakeOnOverrideLayer=False,

                minimizeRotation=True,

                at=["tx", "ty", "tz", "rx", "ry", "rz"],

            )

        cmds.refresh(force=True)

        return count_anim_curves_on_nodes(target_joints_to_bake)



    @staticmethod

    def _safe_min_y(nodes: Iterable[str]) -> Optional[float]:

        values = []

        for node in nodes or []:

            if node and safe_cmds_exists(node):

                try:

                    values.append(float(get_world_position(node)[1]))

                except Exception:

                    pass

        return min(values) if values else None



    def _post_align_humanik_target_root(

        self,

        source_map: Dict[str, str],

        target_map: Dict[str, str],

        start: float,

        end: float,

    ) -> Dict[str, Any]:

        stats: Dict[str, Any] = {

            "humanik_post_align_enabled": False,

            "humanik_post_align_frames": 0,

        }

        if not bool(getattr(self.config, "humanik_post_align_root", True)):

            return stats



        src_pelvis = source_map.get("pelvis")

        tgt_pelvis = target_map.get("pelvis")

        tgt_root = target_map.get("root") or tgt_pelvis

        if not (src_pelvis and tgt_pelvis and tgt_root and safe_cmds_exists(src_pelvis) and safe_cmds_exists(tgt_pelvis) and safe_cmds_exists(tgt_root)):

            self.log("HumanIK post-align skipped: missing source pelvis / target pelvis / target root.")

            return stats



        source_floor_nodes = [source_map.get(k) for k in ("foot_l", "ball_l", "foot_r", "ball_r") if source_map.get(k)]

        target_floor_nodes = [target_map.get(k) for k in ("foot_l", "ball_l", "foot_r", "ball_r") if target_map.get(k)]

        strength = max(0.0, min(1.0, float(getattr(self.config, "humanik_post_align_strength", 1.0) or 0.0)))

        floor_weight = max(0.0, min(1.0, float(getattr(self.config, "humanik_post_align_floor_weight", 0.35) or 0.0)))

        use_pelvis = bool(getattr(self.config, "humanik_post_align_use_pelvis", True))

        use_floor = bool(getattr(self.config, "humanik_post_align_use_floor", True))

        sample_by = max(float(getattr(self.config, "bake_sample_by", 1.0) or 1.0), 0.001)

        frames = self._build_sample_frames(start, end)

        if sample_by != 1.0:

            frames = []

            f = float(start)

            while f <= float(end) + 0.0001:

                frames.append(f)

                f += sample_by

            if frames and abs(frames[-1] - float(end)) > 0.0001:

                frames.append(float(end))



        self.log(

            "HumanIK post-align: root=%s pelvis=%s source_pelvis=%s frames=%d strength=%.3f floor_weight=%.3f pelvis_world_match=%s"

            % (short_name(tgt_root), short_name(tgt_pelvis), short_name(src_pelvis), len(frames), strength, floor_weight, bool(getattr(self.config, "humanik_force_pelvis_world_match", True)))

        )

        if bool(getattr(self.config, "humanik_log_alignment_samples", True)):

            for sample_frame in [start, (float(start) + float(end)) * 0.5, end]:

                try:

                    cmds.currentTime(sample_frame, edit=True)

                    self.log("HumanIK align sample f=%.2f srcPelvis=%s tgtPelvis=%s tgtRoot=%s" % (sample_frame, get_world_position(src_pelvis), get_world_position(tgt_pelvis), get_world_position(tgt_root)))

                except Exception:

                    pass



        max_delta = 0.0

        accumulated_y = 0.0

        keyed = 0

        for frame in frames:

            cmds.currentTime(frame, edit=True)

            try:

                cmds.refresh(force=True)

            except Exception:

                pass



            src_p = get_world_position(src_pelvis)

            tgt_p = get_world_position(tgt_pelvis)

            delta = [0.0, 0.0, 0.0]

            if use_pelvis:

                delta[0] = src_p[0] - tgt_p[0]

                delta[1] = src_p[1] - tgt_p[1]

                delta[2] = src_p[2] - tgt_p[2]



            if use_floor and source_floor_nodes and target_floor_nodes:

                src_floor = self._safe_min_y(source_floor_nodes)

                tgt_floor = self._safe_min_y(target_floor_nodes)

                if src_floor is not None and tgt_floor is not None:

                    floor_delta_y = src_floor - tgt_floor

                    if use_pelvis:

                        delta[1] = (delta[1] * (1.0 - floor_weight)) + (floor_delta_y * floor_weight)

                    else:

                        delta[1] = floor_delta_y



            delta = [d * strength for d in delta]

            root_p = get_world_position(tgt_root)

            new_p = (root_p[0] + delta[0], root_p[1] + delta[1], root_p[2] + delta[2])

            try:

                cmds.xform(tgt_root, worldSpace=True, translation=new_p)

                for attr in TRANSLATE_ATTRS:

                    try:

                        cmds.setKeyframe(tgt_root, attribute=attr, time=frame)

                        keyed += 1

                    except Exception:

                        pass



                                                                                       

                                                                                        

                                                                                           

                                                                               

                if bool(getattr(self.config, "humanik_force_pelvis_world_match", True)):

                    try:

                        pelvis_strength = max(0.0, min(1.0, float(getattr(self.config, "humanik_pelvis_world_match_strength", 1.0) or 0.0)))

                        cmds.refresh(force=True)

                        src_p2 = get_world_position(src_pelvis)

                        tgt_p2 = get_world_position(tgt_pelvis)

                        pelvis_delta = [

                            (src_p2[0] - tgt_p2[0]) * pelvis_strength,

                            (src_p2[1] - tgt_p2[1]) * pelvis_strength,

                            (src_p2[2] - tgt_p2[2]) * pelvis_strength,

                        ]

                        if vector_len(tuple(pelvis_delta)) > 0.0001:

                            new_tgt_p = (tgt_p2[0] + pelvis_delta[0], tgt_p2[1] + pelvis_delta[1], tgt_p2[2] + pelvis_delta[2])

                            cmds.xform(tgt_pelvis, worldSpace=True, translation=new_tgt_p)

                            for attr in TRANSLATE_ATTRS:

                                try:

                                    cmds.setKeyframe(tgt_pelvis, attribute=attr, time=frame)

                                    keyed += 1

                                except Exception:

                                    pass

                            max_delta = max(max_delta, vector_len(tuple(pelvis_delta)))

                    except Exception as exc2:

                        self.log("HumanIK post-align WARNING: pelvis world match failed at frame %.3f: %s" % (frame, exc2))



                max_delta = max(max_delta, vector_len(tuple(delta)))

                accumulated_y += delta[1]

            except Exception as exc:

                self.log("HumanIK post-align WARNING: failed at frame %.3f: %s" % (frame, exc))



        stats.update({

            "humanik_post_align_enabled": True,

            "humanik_post_align_frames": len(frames),

            "humanik_post_align_keyed_translate_samples": keyed,

            "humanik_post_align_max_delta": max_delta,

            "humanik_post_align_average_y_delta": (accumulated_y / float(len(frames))) if frames else 0.0,

        })

        self.log(

            "HumanIK post-align finished: frames=%d keyed_translate_samples=%d max_delta=%.3f avg_y_delta=%.3f"

            % (len(frames), keyed, max_delta, stats["humanik_post_align_average_y_delta"])

        )

        return stats







    def _post_apply_humanik_matrix_arm_transfer_from_source(

        self,

        source_map: Dict[str, str],

        target_map: Dict[str, str],

        target_joints_to_bake: List[str],

        start: float,

        end: float,

        source_rest_local_matrices: Dict[str, Any],

        target_rest_local_matrices: Dict[str, Any],

        target_rest_local_translates: Dict[str, Tuple[float, float, float]],

    ) -> Dict[str, Any]:

        stats: Dict[str, Any] = {

            "humanik_matrix_arm_transfer_enabled": False,

            "humanik_matrix_arm_transfer_frames": 0,

            "humanik_matrix_arm_transfer_keyed_rotate_samples": 0,

        }

        if not bool(getattr(self.config, "humanik_post_matrix_arm_transfer", False)):

            self.log("HumanIK matrix arm transfer skipped: disabled. User clasp template is handled later in the source-guided arm solve.")

            return stats



        frames = self._build_sample_frames(start, end)

        if not frames:

            return stats



        include_clavicles = bool(getattr(self.config, "humanik_matrix_arm_transfer_include_clavicles", True))

        include_hands = bool(getattr(self.config, "humanik_matrix_arm_transfer_include_hands", True))

        preserve_translates = bool(getattr(self.config, "humanik_matrix_arm_transfer_preserve_translates", True))

        filter_curves = bool(getattr(self.config, "humanik_matrix_arm_transfer_filter_curves", True))

        order = str(getattr(self.config, "humanik_matrix_arm_transfer_order", "target_rest_source_delta") or "target_rest_source_delta").strip().lower()



        arm_canonicals: List[str] = []

        for side in ("l", "r"):

            if include_clavicles:

                arm_canonicals.append("clavicle_%s" % side)

            arm_canonicals.extend(["upperarm_%s" % side, "lowerarm_%s" % side])

            if include_hands:

                arm_canonicals.append("hand_%s" % side)



        valid: List[Tuple[str, str, str]] = []

        missing: List[str] = []

        for canon in arm_canonicals:

            src = source_map.get(canon)

            tgt = target_map.get(canon)

            if not (src and tgt and safe_cmds_exists(src) and safe_cmds_exists(tgt)):

                missing.append(canon)

                continue

            if canon not in source_rest_local_matrices or canon not in target_rest_local_matrices:

                missing.append(canon + "_rest")

                continue

            valid.append((canon, src, tgt))



        if len(valid) < 4:

            self.log("HumanIK v2.29.0 Source-Pose Delta User Template skipped: too few valid arm joints. Missing: %s" % ", ".join(missing[:12]))

            stats["humanik_matrix_arm_transfer_missing"] = missing

            return stats



        def _make_arm_output(canon: str, src_current_local):

            src_rest = source_rest_local_matrices[canon]

            tgt_rest = target_rest_local_matrices[canon]

                                                                                                             

                                                                                           

            if order in {"source_delta_target_rest", "source_delta_then_target_rest"}:

                return (src_rest.inverse() * src_current_local) * tgt_rest

            if order in {"delta_target_rest", "current_rest_inv_target_rest"}:

                return (src_current_local * src_rest.inverse()) * tgt_rest

            if order in {"target_rest_current_rest_inv"}:

                return tgt_rest * (src_current_local * src_rest.inverse())

            return tgt_rest * (src_rest.inverse() * src_current_local)



        self.log(

            "HumanIK Option1 v2.29.0 FULL-ARM USER CLASP TEMPLATE: overriding arms after HIK. frames=%d joints=%d include_clavicles=%s include_hands=%s preserve_translates=%s order=%s filter_curves=%s. Source/target rest matrices are used; no wrist IK, no paired-hand pull."

            % (len(frames), len(valid), str(include_clavicles), str(include_hands), str(preserve_translates), order, str(filter_curves))

        )



        keyed = 0

        failed = 0

        debug_samples: List[str] = []

        sample_frames = set([frames[0], frames[len(frames)//2], frames[-1]]) if frames else set()

        baked_nodes = []



        for frame in frames:

            cmds.currentTime(frame, edit=True, update=True)

            for canon, src, tgt in valid:

                try:

                    src_current = self._matrix_from_node_local(src)

                    out = _make_arm_output(canon, src_current)

                    keep_t = target_rest_local_translates.get(canon) if preserve_translates else None

                    self._apply_local_matrix_to_joint(tgt, out, keep_translate=keep_t)

                    cmds.setKeyframe(tgt, attribute=ROTATE_ATTRS, time=frame)

                    keyed += 3

                    baked_nodes.append(tgt)

                    if frame in sample_frames and canon in {"upperarm_l", "lowerarm_l", "hand_l", "upperarm_r", "lowerarm_r", "hand_r"}:

                        try:

                            r = self._get_vec(tgt, ROTATE_ATTRS)

                            debug_samples.append("f=%.2f %s rot=(%.2f, %.2f, %.2f)" % (frame, canon, r[0], r[1], r[2]))

                        except Exception:

                            pass

                except Exception as exc:

                    failed += 1

                    if failed <= 8:

                        self.log("HumanIK v2.29.0 Source-Pose Delta User Template WARNING: %s failed at frame %.3f: %s" % (canon, frame, exc))



        baked_nodes = list(dict.fromkeys(baked_nodes))

        if filter_curves and baked_nodes:

            try:

                attrs = []

                for node in baked_nodes:

                    for attr in ROTATE_ATTRS:

                        attrs.append(node + "." + attr)

                cmds.select(attrs, replace=True)

                cmds.filterCurve()

                cmds.select(clear=True)

            except Exception:

                try:

                    cmds.filterCurve()

                except Exception:

                    pass



        for line in debug_samples[:10]:

            self.log("HumanIK matrix arm diagnostic sample: %s" % line)



        curves_after = count_anim_curves_on_nodes(baked_nodes)

        self.log(

            "HumanIK Option1 v2.8.0 Contact-Pose IK finished: frames=%d arm_joints=%d keyed_rotate_channels=%d failures=%d target_arm_anim_curves=%d"

            % (len(frames), len(baked_nodes), keyed, failed, curves_after)

        )

        stats.update({

            "humanik_matrix_arm_transfer_enabled": True,

            "humanik_matrix_arm_transfer_frames": len(frames),

            "humanik_matrix_arm_transfer_valid_joint_count": len(valid),

            "humanik_matrix_arm_transfer_keyed_rotate_samples": keyed,

            "humanik_matrix_arm_transfer_failures": failed,

            "humanik_matrix_arm_transfer_anim_curves": curves_after,

            "humanik_matrix_arm_transfer_order": order,

        })

        return stats







    def _post_solve_humanik_arms_from_source_positions(

        self,

        source_map: Dict[str, str],

        target_map: Dict[str, str],

        target_joints_to_bake: List[str],

        start: float,

        end: float,

        source_rest_positions: Optional[Dict[str, Tuple[float, float, float]]] = None,

        target_rest_positions: Optional[Dict[str, Tuple[float, float, float]]] = None,

        target_rest_local_rotations: Optional[Dict[str, Tuple[float, float, float]]] = None,

        source_rest_local_rotations: Optional[Dict[str, Tuple[float, float, float]]] = None,

    ) -> Dict[str, Any]:

        stats: Dict[str, Any] = {

            "humanik_source_guided_arm_ik_enabled": False,

            "humanik_source_guided_arm_ik_frames": 0,

            "humanik_source_guided_arm_ik_corrections": 0,

        }

        if not bool(getattr(self.config, "humanik_post_source_guided_arm_ik", True)):

            self.log("HumanIK source-guided arm IK skipped: disabled.")

            return stats



        required = ["pelvis", "head", "thigh_l", "thigh_r", "calf_l", "calf_r", "upperarm_l", "lowerarm_l", "hand_l", "upperarm_r", "lowerarm_r", "hand_r"]

        if bool(getattr(self.config, "humanik_source_guided_arm_ik_include_clavicle_chain", True)):

            required += ["clavicle_l", "clavicle_r"]

        missing = []

        for c in required:

            if not source_map.get(c) or not target_map.get(c) or not safe_cmds_exists(source_map.get(c)) or not safe_cmds_exists(target_map.get(c)):

                missing.append(c)

        if missing:

            self.log("HumanIK source-guided arm IK skipped: missing mapped joints: %s" % ", ".join(missing))

            return stats



                                                                             

        try:

            setattr(self.config, "_alpha_v29_disable_user_template_this_file", False)

        except Exception:

            pass



                                                                                                

                                                                                                     

                                                                                                    

                                                                                                   

        try:

            _tpl_path_for_guard = str(getattr(self.config, "humanik_source_guided_arm_ik_user_clasp_pose_template_path", "") or "")

            _tpl_enabled_for_guard = bool(getattr(self.config, "humanik_source_guided_arm_ik_use_user_clasp_pose_template", False))

            _lock_file_for_guard = bool(getattr(self.config, "humanik_source_guided_arm_ik_user_clasp_pose_template_lock_to_source_file", True))

            _skip_solver_for_guard = bool(getattr(self.config, "humanik_source_guided_arm_ik_skip_custom_arm_solver_on_template_source_mismatch", True))

            if _tpl_enabled_for_guard and _tpl_path_for_guard and _lock_file_for_guard and os.path.isfile(_tpl_path_for_guard):

                import json as _json_guard

                with open(_tpl_path_for_guard, "r") as _guard_fh:

                    _tpl_guard = _json_guard.load(_guard_fh)

                _captured_file = _tpl_guard.get("source_file", {}) if isinstance(_tpl_guard, dict) else {}

                _captured_base = str(_captured_file.get("basename", "") or "") if isinstance(_captured_file, dict) else ""

                _captured_size = int(_captured_file.get("size", -1) or -1) if isinstance(_captured_file, dict) else -1

                _current_path = str(getattr(self.config, "humanik_source_guided_arm_ik_current_source_file_path", "") or "")

                _current_base = os.path.basename(_current_path) if _current_path else ""

                try:

                    _current_size = int(os.path.getsize(_current_path)) if _current_path and os.path.isfile(_current_path) else -2

                except Exception:

                    _current_size = -2

                if _captured_base and (_captured_base != _current_base or (_captured_size >= 0 and _current_size >= 0 and _captured_size != _current_size)):

                    try:

                        setattr(self.config, "_alpha_v29_disable_user_template_this_file", True)

                    except Exception:

                        pass

                    self.log("HumanIK Option1 v2.29.0 SOURCE FILE GUARD: user template captured from %s(size=%s), current source is %s(size=%s). Skipping USER TEMPLATE ONLY for this file; core source-guided arm solver stays ON so arms do not fall back to bad native HIK." % (_captured_base, str(_captured_size), _current_base or "<unknown>", str(_current_size)))

        except Exception as _guard_exc:

            self.log("HumanIK Option1 v2.29.0 SOURCE FILE GUARD WARNING: %s" % _guard_exc)



        frames = self._build_sample_frames(start, end)

        if not frames:

            return stats



        strength = max(0.0, min(1.0, float(getattr(self.config, "humanik_source_guided_arm_ik_strength", 0.95) or 0.0)))

        pole_strength = max(0.0, min(1.0, float(getattr(self.config, "humanik_source_guided_arm_ik_pole_strength", 1.0) or 0.0)))

        max_pull = max(0.0, float(getattr(self.config, "humanik_source_guided_arm_ik_max_pull_units", 120.0) or 0.0))

        reach_limit = max(0.1, min(1.15, float(getattr(self.config, "humanik_source_guided_arm_ik_reach_limit", 0.98) or 0.98)))

        same_side_min = max(0.0, float(getattr(self.config, "humanik_source_guided_arm_ik_same_side_lock_min_units", 4.0) or 0.0))

        use_virtual_rest = bool(getattr(self.config, "humanik_source_guided_arm_ik_use_virtual_source_rest", True))

        virtual_rest_strength = max(0.0, min(1.0, float(getattr(self.config, "humanik_source_guided_arm_ik_virtual_rest_strength", 0.65) or 0.0)))

        invert_forward_axis = bool(getattr(self.config, "humanik_source_guided_arm_ik_invert_forward_axis", False))

        use_shoulder_relative_mapping = bool(getattr(self.config, "humanik_source_guided_arm_ik_use_shoulder_relative_local_mapping", True))

        include_clavicle_chain = bool(getattr(self.config, "humanik_source_guided_arm_ik_include_clavicle_chain", False))

        reset_hik_arm_to_rest = bool(getattr(self.config, "humanik_source_guided_arm_ik_reset_hik_arm_to_rest_before_solve", True))

        preserve_hik_clavicles = bool(getattr(self.config, "humanik_source_guided_arm_ik_preserve_hik_clavicles", False))

        clavicle_hik_rotation_blend = max(0.0, min(1.0, float(getattr(self.config, "humanik_source_guided_arm_ik_clavicle_hik_rotation_blend", 0.18 if preserve_hik_clavicles else 0.0) or 0.0)))

        hand_contact_aim = bool(getattr(self.config, "humanik_source_guided_arm_ik_enable_hand_contact_aim", True))

        hand_contact_aim_blend = max(0.0, min(1.0, float(getattr(self.config, "humanik_source_guided_arm_ik_hand_contact_aim_rotation_blend", 0.24) or 0.0)))

        hand_aim_maintain_offset = bool(getattr(self.config, "humanik_source_guided_arm_ik_hand_aim_maintain_offset", True))

        source_palm_delta = bool(getattr(self.config, "humanik_source_guided_arm_ik_enable_source_palm_delta", True))

        source_palm_delta_blend = max(0.0, min(1.0, float(getattr(self.config, "humanik_source_guided_arm_ik_source_palm_delta_blend", 0.78) or 0.0)))

        source_palm_delta_clamp = max(1.0, float(getattr(self.config, "humanik_source_guided_arm_ik_source_palm_delta_clamp_degrees", 58.0) or 58.0))

        anchor_hand_fit = bool(getattr(self.config, "humanik_source_guided_arm_ik_enable_anchor_hand_fit", True))

        anchor_hand_side = str(getattr(self.config, "humanik_source_guided_arm_ik_anchor_hand", "l") or "l").lower()

        if anchor_hand_side not in ("l", "r"):

            anchor_hand_side = "l"

        anchor_hand_strength = max(0.0, min(1.0, float(getattr(self.config, "humanik_source_guided_arm_ik_anchor_hand_strength", 0.82) or 0.82)))

        follower_hand_strength = max(0.0, min(1.0, float(getattr(self.config, "humanik_source_guided_arm_ik_follower_hand_strength", 0.88) or 0.88)))

        palm_frame_diagnostics = bool(getattr(self.config, "humanik_source_guided_arm_ik_enable_palm_frame_diagnostics", True))

        reference_clasp_template = bool(getattr(self.config, "humanik_source_guided_arm_ik_use_reference_clasp_template", True))

        reference_clasp_center_up_lift = float(getattr(self.config, "humanik_source_guided_arm_ik_reference_clasp_center_up_lift_units", 6.25) or 0.0)

        reference_clasp_center_min_fraction = max(0.0, min(1.0, float(getattr(self.config, "humanik_source_guided_arm_ik_reference_clasp_center_min_fraction", 0.61) or 0.61)))

        reference_clasp_center_max_fraction = max(reference_clasp_center_min_fraction, min(1.0, float(getattr(self.config, "humanik_source_guided_arm_ik_reference_clasp_center_max_fraction", 0.70) or 0.70)))

        reference_clasp_forward_offset = float(getattr(self.config, "humanik_source_guided_arm_ik_reference_clasp_forward_offset_units", -0.75) or 0.0)

        reference_clasp_pair_distance = max(6.0, float(getattr(self.config, "humanik_source_guided_arm_ik_reference_clasp_pair_distance", 10.75) or 10.75))

        reference_clasp_left_up_offset = float(getattr(self.config, "humanik_source_guided_arm_ik_reference_clasp_left_up_offset", 0.85) or 0.0)

        reference_clasp_right_up_offset = float(getattr(self.config, "humanik_source_guided_arm_ik_reference_clasp_right_up_offset", -0.85) or 0.0)

        reference_clasp_left_forward_offset = float(getattr(self.config, "humanik_source_guided_arm_ik_reference_clasp_left_forward_offset", -0.65) or 0.0)

        reference_clasp_right_forward_offset = float(getattr(self.config, "humanik_source_guided_arm_ik_reference_clasp_right_forward_offset", 0.65) or 0.0)

        reference_clasp_strength = max(0.0, min(1.0, float(getattr(self.config, "humanik_source_guided_arm_ik_reference_clasp_strength", 0.92) or 0.92)))

        reference_clasp_palm_pose = bool(getattr(self.config, "humanik_source_guided_arm_ik_use_reference_clasp_palm_pose", True))

        reference_clasp_palm_pose_blend = max(0.0, min(1.0, float(getattr(self.config, "humanik_source_guided_arm_ik_reference_clasp_palm_pose_blend", 0.74) or 0.74)))

        reference_clasp_left_hand_offset = tuple(getattr(self.config, "humanik_source_guided_arm_ik_reference_clasp_left_hand_offset", (0.0, -18.0, 20.0)) or (0.0, -18.0, 20.0))

        reference_clasp_right_hand_offset = tuple(getattr(self.config, "humanik_source_guided_arm_ik_reference_clasp_right_hand_offset", (0.0, 18.0, -20.0)) or (0.0, 18.0, -20.0))

        reference_clasp_finger_template = bool(getattr(self.config, "humanik_source_guided_arm_ik_use_reference_clasp_finger_template", True))

        reference_clasp_finger_template_blend = max(0.0, min(1.0, float(getattr(self.config, "humanik_source_guided_arm_ik_reference_clasp_finger_template_blend", 0.78) or 0.78)))

        reference_clasp_finger_mcp_curl = float(getattr(self.config, "humanik_source_guided_arm_ik_reference_clasp_finger_mcp_curl", 22.0) or 22.0)

        reference_clasp_finger_pip_curl = float(getattr(self.config, "humanik_source_guided_arm_ik_reference_clasp_finger_pip_curl", 28.0) or 28.0)

        reference_clasp_finger_dip_curl = float(getattr(self.config, "humanik_source_guided_arm_ik_reference_clasp_finger_dip_curl", 12.0) or 12.0)

        reference_clasp_thumb_blend = max(0.0, min(1.0, float(getattr(self.config, "humanik_source_guided_arm_ik_reference_clasp_thumb_blend", 0.30) or 0.30)))

        user_clasp_template_enabled = bool(getattr(self.config, "humanik_source_guided_arm_ik_use_user_clasp_pose_template", False)) and not bool(getattr(self.config, "_alpha_v29_disable_user_template_this_file", False))

        user_clasp_template_path = str(getattr(self.config, "humanik_source_guided_arm_ik_user_clasp_pose_template_path", "") or "")

        user_clasp_template_blend = max(0.0, min(1.0, float(getattr(self.config, "humanik_source_guided_arm_ik_user_clasp_pose_template_blend", 1.0) or 1.0)))

        user_clasp_template_apply_hands = bool(getattr(self.config, "humanik_source_guided_arm_ik_user_clasp_pose_template_apply_hands", True))

        user_clasp_template_apply_fingers = bool(getattr(self.config, "humanik_source_guided_arm_ik_user_clasp_pose_template_apply_fingers", True))

        user_clasp_template_apply_correctives = bool(getattr(self.config, "humanik_source_guided_arm_ik_user_clasp_pose_template_apply_correctives", False))

        user_clasp_template_apply_clavicles = bool(getattr(self.config, "humanik_source_guided_arm_ik_user_clasp_pose_template_apply_clavicles", True))

        user_clasp_template_apply_arm_chain = bool(getattr(self.config, "humanik_source_guided_arm_ik_user_clasp_pose_template_apply_arm_chain", True))

        user_clasp_template_use_delta = bool(getattr(self.config, "humanik_source_guided_arm_ik_user_clasp_pose_template_use_delta", True))

        user_clasp_template_pose_match = bool(getattr(self.config, "humanik_source_guided_arm_ik_user_clasp_pose_template_pose_match", True))

        user_clasp_template_center_threshold = max(0.5, float(getattr(self.config, "humanik_source_guided_arm_ik_user_clasp_pose_template_center_threshold", 3.0) or 3.0))

        user_clasp_template_wrist_threshold = max(0.5, float(getattr(self.config, "humanik_source_guided_arm_ik_user_clasp_pose_template_wrist_threshold", 4.0) or 4.0))

        user_clasp_template_elbow_threshold = max(0.5, float(getattr(self.config, "humanik_source_guided_arm_ik_user_clasp_pose_template_elbow_threshold", 5.0) or 5.0))

        user_clasp_template_pair_threshold = max(0.5, float(getattr(self.config, "humanik_source_guided_arm_ik_user_clasp_pose_template_pair_threshold", 2.0) or 2.0))

        user_clasp_template_rotation_threshold = max(1.0, float(getattr(self.config, "humanik_source_guided_arm_ik_user_clasp_pose_template_rotation_threshold", 18.0) or 18.0))

        user_clasp_template_require_driver = bool(getattr(self.config, "humanik_source_guided_arm_ik_user_clasp_pose_template_require_driver", True))

        user_clasp_template_lock_to_source_file = bool(getattr(self.config, "humanik_source_guided_arm_ik_user_clasp_pose_template_lock_to_source_file", True))

        user_clasp_template_skip_custom_arm_on_mismatch = bool(getattr(self.config, "humanik_source_guided_arm_ik_skip_custom_arm_solver_on_template_source_mismatch", False))

        user_clasp_template_save_raw_cache = bool(getattr(self.config, "humanik_source_guided_arm_ik_save_pre_user_template_raw_cache", True))

        soft_clavicle_aim = bool(getattr(self.config, "humanik_source_guided_arm_ik_enable_soft_clavicle_aim", False))

        soft_clavicle_strength = max(0.0, min(1.0, float(getattr(self.config, "humanik_source_guided_arm_ik_soft_clavicle_aim_strength", 0.0) or 0.0)))

        use_thigh_clearance = bool(getattr(self.config, "humanik_source_guided_arm_ik_use_thigh_clearance", True))

        thigh_clearance = max(0.0, float(getattr(self.config, "humanik_source_guided_arm_ik_thigh_clearance_units", 14.0) or 0.0))

        thigh_clearance_up_bias = max(0.0, min(1.0, float(getattr(self.config, "humanik_source_guided_arm_ik_thigh_clearance_up_bias", 0.85) or 0.0)))

        pair_convergence = bool(getattr(self.config, "humanik_source_guided_arm_ik_enable_paired_hand_convergence", True))

        pair_source_threshold = max(0.0, float(getattr(self.config, "humanik_source_guided_arm_ik_pair_source_distance_threshold", 28.0) or 0.0))

        pair_strength = max(0.0, min(1.0, float(getattr(self.config, "humanik_source_guided_arm_ik_pair_strength", 0.38) or 0.0)))

        pair_distance_scale = max(0.05, float(getattr(self.config, "humanik_source_guided_arm_ik_pair_distance_scale", 0.80) or 1.15))

        pair_min_distance = max(0.0, float(getattr(self.config, "humanik_source_guided_arm_ik_pair_min_distance", 6.0) or 0.0))

        pair_max_distance = max(pair_min_distance, float(getattr(self.config, "humanik_source_guided_arm_ik_pair_max_distance", 18.0) or 22.0))

        pair_center_blend = max(0.0, min(1.0, float(getattr(self.config, "humanik_source_guided_arm_ik_pair_center_blend", 0.28) or 0.0)))

        pair_chest_height_bias = max(0.0, min(1.0, float(getattr(self.config, "humanik_source_guided_arm_ik_pair_chest_height_bias", 0.08) or 0.0)))

        pair_max_target_pull = max(0.0, float(getattr(self.config, "humanik_source_guided_arm_ik_pair_max_target_pull_units", 0.0) or 0.0))

        contact_pose_mode = bool(getattr(self.config, "humanik_source_guided_arm_ik_contact_pose_mode", True))

        contact_use_source_center_absolute = bool(getattr(self.config, "humanik_source_guided_arm_ik_contact_use_source_center_absolute", True))

        contact_body_scale = bool(getattr(self.config, "humanik_source_guided_arm_ik_contact_body_scale", True))

        contact_elbow_side_guard = bool(getattr(self.config, "humanik_source_guided_arm_ik_contact_elbow_side_guard", True))

        contact_elbow_side_margin = max(0.0, float(getattr(self.config, "humanik_source_guided_arm_ik_contact_elbow_side_margin_units", 6.0) or 0.0))

        contact_min_up_fraction = max(0.0, min(1.0, float(getattr(self.config, "humanik_source_guided_arm_ik_contact_min_up_fraction", 0.22) or 0.0)))

        contact_max_up_fraction = max(contact_min_up_fraction, min(1.0, float(getattr(self.config, "humanik_source_guided_arm_ik_contact_max_up_fraction", 0.72) or 1.0)))

        contact_max_forward_abs = max(0.0, float(getattr(self.config, "humanik_source_guided_arm_ik_contact_max_forward_abs_units", 70.0) or 0.0))

        analytic_aim_solver = bool(getattr(self.config, "humanik_source_guided_arm_ik_use_analytic_aim_solver", True))

        arm_diag_enabled = bool(getattr(self.config, "humanik_arm_diagnostics_enabled", True))

        arm_diag_rest = bool(getattr(self.config, "humanik_arm_diagnostics_include_rest_report", True))

        arm_diag_final = bool(getattr(self.config, "humanik_arm_diagnostics_include_final_after_bake", True))

        arm_diag_max_samples = max(3, min(9, int(getattr(self.config, "humanik_arm_diagnostics_max_sample_frames", 5) or 5)))

        source_rest_positions = source_rest_positions or {}

        target_rest_positions = target_rest_positions or {}

        target_rest_local_rotations = target_rest_local_rotations or {}

        source_rest_local_rotations = source_rest_local_rotations or {}



        def _basis_from_map(map_obj: Dict[str, str]):

            pelvis = get_world_position(map_obj["pelvis"])

            head_node = map_obj.get("head") or map_obj.get("neck_01") or map_obj.get("spine_03")

            head = get_world_position(head_node)



                                                   

                                                                         

                                                                                         

                                                                                                        

                                                                                                              

            l_hip = get_world_position(map_obj["thigh_l"])

            r_hip = get_world_position(map_obj["thigh_r"])

            side_axis = self._v_norm(self._v_sub(r_hip, l_hip), fallback=(1.0, 0.0, 0.0))

            up_raw = self._v_sub(head, pelvis)

            up_axis = self._v_sub(up_raw, self._v_mul(side_axis, self._v_dot(up_raw, side_axis)))

            up_axis = self._v_norm(up_axis, fallback=(0.0, 1.0, 0.0))

            front_axis = self._v_norm(self._v_cross(side_axis, up_axis), fallback=(0.0, 0.0, 1.0))

            up_axis = self._v_norm(self._v_cross(front_axis, side_axis), fallback=up_axis)

            front_axis = self._v_norm(self._v_cross(side_axis, up_axis), fallback=front_axis)

            return pelvis, side_axis, up_axis, front_axis



        def _basis_from_position_dict(pos_obj: Dict[str, Tuple[float, float, float]]):

            pelvis = pos_obj.get("pelvis")

            head = pos_obj.get("head") or pos_obj.get("neck_01") or pos_obj.get("spine_03")

                                                                                                      

            l_side = pos_obj.get("thigh_l") or pos_obj.get("upperarm_l")

            r_side = pos_obj.get("thigh_r") or pos_obj.get("upperarm_r")

            if not (pelvis and head and l_side and r_side):

                return None

            side_axis = self._v_norm(self._v_sub(r_side, l_side), fallback=(1.0, 0.0, 0.0))

            up_raw = self._v_sub(head, pelvis)

            up_axis = self._v_sub(up_raw, self._v_mul(side_axis, self._v_dot(up_raw, side_axis)))

            up_axis = self._v_norm(up_axis, fallback=(0.0, 1.0, 0.0))

            front_axis = self._v_norm(self._v_cross(side_axis, up_axis), fallback=(0.0, 0.0, 1.0))

            up_axis = self._v_norm(self._v_cross(front_axis, side_axis), fallback=up_axis)

            front_axis = self._v_norm(self._v_cross(side_axis, up_axis), fallback=front_axis)

            return pelvis, side_axis, up_axis, front_axis



        def _to_local(pos, basis):

            origin, side_axis, up_axis, front_axis = basis

            v = self._v_sub(pos, origin)

            return (self._v_dot(v, side_axis), self._v_dot(v, up_axis), self._v_dot(v, front_axis))



        def _dir_to_world(local_vec, basis):

            _origin, side_axis, up_axis, front_axis = basis

            return self._v_add(self._v_add(self._v_mul(side_axis, local_vec[0]), self._v_mul(up_axis, local_vec[1])), self._v_mul(front_axis, local_vec[2]))



        def _local_to_world(local_pos, basis):

            origin, side_axis, up_axis, front_axis = basis

            return self._v_add(origin, _dir_to_world(local_pos, basis))



        def _dir_to_local(vec, basis):

            _origin, side_axis, up_axis, front_axis = basis

            return (self._v_dot(vec, side_axis), self._v_dot(vec, up_axis), self._v_dot(vec, front_axis))



        def _maybe_invert_forward(local_vec):

                                                                           

                                                                                               

                                                                                             

                                                                                              

            if invert_forward_axis:

                return (local_vec[0], local_vec[1], -local_vec[2])

            return local_vec



        def _closest_point_on_segment(point, a, b):

            ab = self._v_sub(b, a)

            denom = self._v_dot(ab, ab)

            if denom <= 1e-8:

                return a

            t = max(0.0, min(1.0, self._v_dot(self._v_sub(point, a), ab) / denom))

            return self._v_add(a, self._v_mul(ab, t))



        sides = [

            ("l", "upperarm_l", "lowerarm_l", "hand_l"),

            ("r", "upperarm_r", "lowerarm_r", "hand_r"),

        ]



                                                            

                                                                                              

                                                                                                         

        source_rest_basis = _basis_from_position_dict(source_rest_positions) if use_virtual_rest else None

        target_rest_basis = _basis_from_position_dict(target_rest_positions) if use_virtual_rest else None

        source_rest_local: Dict[str, Tuple[float, float, float]] = {}

        target_virtual_rest_local: Dict[str, Dict[str, Tuple[float, float, float]]] = {}

        if use_virtual_rest and source_rest_basis and target_rest_basis:

            for _side, _start_c, _mid_c, _end_c in sides:

                if not all(k in source_rest_positions for k in (_start_c, _mid_c, _end_c)) or not all(k in target_rest_positions for k in (_start_c, _mid_c, _end_c)):

                    continue

                s_start_l = _maybe_invert_forward(_to_local(source_rest_positions[_start_c], source_rest_basis))

                s_mid_l = _maybe_invert_forward(_to_local(source_rest_positions[_mid_c], source_rest_basis))

                s_end_l = _maybe_invert_forward(_to_local(source_rest_positions[_end_c], source_rest_basis))

                t_start_l = _to_local(target_rest_positions[_start_c], target_rest_basis)

                t_mid_l = _to_local(target_rest_positions[_mid_c], target_rest_basis)

                t_end_l = _to_local(target_rest_positions[_end_c], target_rest_basis)

                source_rest_local[_start_c] = s_start_l

                source_rest_local[_mid_c] = s_mid_l

                source_rest_local[_end_c] = s_end_l

                target_upper_len = max(self._v_len(self._v_sub(t_mid_l, t_start_l)), 1.0)

                target_lower_len = max(self._v_len(self._v_sub(t_end_l, t_mid_l)), 1.0)

                src_upper_dir = self._v_norm(self._v_sub(s_mid_l, s_start_l), fallback=self._v_norm(self._v_sub(t_mid_l, t_start_l)))

                src_lower_dir = self._v_norm(self._v_sub(s_end_l, s_mid_l), fallback=self._v_norm(self._v_sub(t_end_l, t_mid_l)))

                v_mid_l = self._v_add(t_start_l, self._v_mul(src_upper_dir, target_upper_len))

                v_end_l = self._v_add(v_mid_l, self._v_mul(src_lower_dir, target_lower_len))

                target_virtual_rest_local[_side] = {"shoulder": t_start_l, "elbow": v_mid_l, "wrist": v_end_l}

            if target_virtual_rest_local:

                self.log("HumanIK Option1 v2.1.7 virtual source-rest arm calibration active: sides=%d strength=%.2f" % (len(target_virtual_rest_local), virtual_rest_strength))

            else:

                use_virtual_rest = False

                self.log("HumanIK Option1 v2.1.7 virtual source-rest arm calibration unavailable: missing rest arm positions; using old source-guided IK.")

        elif use_virtual_rest:

            use_virtual_rest = False

            self.log("HumanIK Option1 v2.1.7 virtual source-rest arm calibration unavailable: missing rest body basis; using old source-guided IK.")



        def _body_scale_ratio():

            if not contact_body_scale:

                return 1.0

            try:

                if source_rest_positions and target_rest_positions and "pelvis" in source_rest_positions and "head" in source_rest_positions and "pelvis" in target_rest_positions and "head" in target_rest_positions:

                    src_h = max(self._v_len(self._v_sub(source_rest_positions["head"], source_rest_positions["pelvis"])), 1.0)

                    tgt_h = max(self._v_len(self._v_sub(target_rest_positions["head"], target_rest_positions["pelvis"])), 1.0)

                    return max(0.65, min(1.45, tgt_h / src_h))

            except Exception:

                pass

            return 1.0



        body_scale_ratio = _body_scale_ratio()





                                                                                               

                                                                                                 

                                                                                                  

                                                                                             

        alpha_v3_pose_class = "LEGACY"

        alpha_v3_pose_metrics = {}

        if bool(getattr(self.config, "alpha_v3_contact_aware_pose_classify", False)):

            try:

                _sample_frames_for_class = sorted(set([frames[0], frames[len(frames)//2], frames[-1]])) if frames else []

                _up_fracs = []

                _pair_dists = []

                _forward_vals = []

                _center_side_abs = []

                for _cf in _sample_frames_for_class:

                    try:

                        cmds.currentTime(_cf, edit=True, update=True)

                    except Exception:

                        pass

                    _sb = _basis_from_map(source_map)

                    _swl = _maybe_invert_forward(_to_local(get_world_position(source_map["hand_l"]), _sb))

                    _swr = _maybe_invert_forward(_to_local(get_world_position(source_map["hand_r"]), _sb))

                    _head_l = _maybe_invert_forward(_to_local(get_world_position(source_map.get("head") or source_map.get("neck_01")), _sb))

                    _pel_l = _maybe_invert_forward(_to_local(get_world_position(source_map["pelvis"]), _sb))

                    _span = max(abs(_head_l[1] - _pel_l[1]), 1.0)

                    _center = self._v_mul(self._v_add(_swl, _swr), 0.5)

                    _up_fracs.append((_center[1] - _pel_l[1]) / _span)

                    _pair_dists.append(self._v_len(self._v_sub(_swl, _swr)))

                    _forward_vals.append(_center[2])

                    _center_side_abs.append(abs(_center[0]))

                _avg_up_frac = sum(_up_fracs) / max(len(_up_fracs), 1)

                _avg_pair = sum(_pair_dists) / max(len(_pair_dists), 1)

                _avg_forward = sum(_forward_vals) / max(len(_forward_vals), 1)

                _avg_side_abs = sum(_center_side_abs) / max(len(_center_side_abs), 1)

                alpha_v3_pose_metrics = {"avgUpFraction": _avg_up_frac, "avgPairDistance": _avg_pair, "avgForward": _avg_forward, "avgCenterSideAbs": _avg_side_abs}



                _lap_up_threshold = float(getattr(self.config, "alpha_v3_lap_up_fraction_threshold", 0.56) or 0.56)

                _clasp_pair_threshold = float(getattr(self.config, "alpha_v3_clasp_pair_distance_threshold", 18.0) or 18.0)

                _free_pair_threshold = float(getattr(self.config, "alpha_v3_free_pair_distance_threshold", 30.0) or 30.0)

                _low_clasp_up_threshold = float(getattr(self.config, "alpha_v3_low_clasp_min_up_fraction", 0.46) or 0.46)



                                                                                                          

                                                                                                       

                                                                                                           

                if _avg_pair <= _clasp_pair_threshold and _avg_up_frac >= _low_clasp_up_threshold:

                    if _avg_up_frac > _lap_up_threshold:

                        alpha_v3_pose_class = "CHEST_CLASP_OR_HAND_CONTACT"

                        pair_convergence = True

                        anchor_hand_fit = True

                        pair_strength = min(pair_strength, 0.42)

                        pair_chest_height_bias = min(pair_chest_height_bias, 0.18)

                    else:

                        alpha_v3_pose_class = "LOW_CLASP_OR_HAND_CONTACT"

                                                                                                                

                        pair_convergence = False

                        anchor_hand_fit = False

                        pair_strength = 0.0

                        pair_chest_height_bias = 0.0

                    reference_clasp_template = False

                    reference_clasp_palm_pose = False

                    reference_clasp_finger_template = False

                    user_clasp_template_enabled = False

                    contact_pose_mode = True

                    contact_min_up_fraction = 0.08

                    contact_max_up_fraction = min(0.68, max(0.46, _avg_up_frac + 0.12))

                    hand_contact_aim = False

                    source_palm_delta = False

                    use_thigh_clearance = False

                    bake_hand_rotation = False

                    restore_hik_hand_rotation = True

                    clavicle_hik_rotation_blend = min(clavicle_hik_rotation_blend, 0.03)

                elif _avg_up_frac <= _lap_up_threshold:

                    alpha_v3_pose_class = "LOW_OR_LAP_HANDS"

                                                                                                   

                    pair_convergence = False

                    anchor_hand_fit = False

                    reference_clasp_template = False

                    reference_clasp_palm_pose = False

                    reference_clasp_finger_template = False

                    user_clasp_template_enabled = False

                    contact_pose_mode = True

                    contact_min_up_fraction = 0.08

                    contact_max_up_fraction = min(0.60, max(0.42, _avg_up_frac + 0.10))

                    pair_strength = 0.0

                    hand_contact_aim = False

                    source_palm_delta = False

                    use_thigh_clearance = False

                    bake_hand_rotation = False

                    restore_hik_hand_rotation = True

                    clavicle_hik_rotation_blend = min(clavicle_hik_rotation_blend, 0.03)

                elif _avg_pair >= _free_pair_threshold:

                    alpha_v3_pose_class = "FREE_OR_SEPARATE_HANDS"

                    pair_convergence = False

                    anchor_hand_fit = False

                    reference_clasp_template = False

                    reference_clasp_palm_pose = False

                    reference_clasp_finger_template = False

                    user_clasp_template_enabled = False

                    contact_pose_mode = False

                    hand_contact_aim = False

                    source_palm_delta = False

                    bake_hand_rotation = False

                    restore_hik_hand_rotation = True

                else:

                    alpha_v3_pose_class = "AMBIGUOUS_CONTACT_KEEP_SOURCE"

                    pair_convergence = False

                    anchor_hand_fit = False

                    reference_clasp_template = False

                    reference_clasp_palm_pose = False

                    reference_clasp_finger_template = False

                    hand_contact_aim = False

                    source_palm_delta = False

                    bake_hand_rotation = False

                    restore_hik_hand_rotation = True



                self.log("ALPHA_V3_POSE_CLASS: class=%s avgUpFraction=%.3f avgPairDist=%.2f avgForward=%.2f avgCenterSideAbs=%.2f pairConvergence=%s bakeHandRotation=%s restoreHIKHandRotation=%s contactUpClamp=[%.2f,%.2f]" % (alpha_v3_pose_class, _avg_up_frac, _avg_pair, _avg_forward, _avg_side_abs, str(pair_convergence), str(bake_hand_rotation), str(restore_hik_hand_rotation), contact_min_up_fraction, contact_max_up_fraction))

            except Exception as _v3_class_exc:

                alpha_v3_pose_class = "CLASSIFIER_FAILED_LEGACY_SAFE"

                pair_convergence = False

                anchor_hand_fit = False

                reference_clasp_template = False

                reference_clasp_palm_pose = False

                reference_clasp_finger_template = False

                hand_contact_aim = False

                source_palm_delta = False

                bake_hand_rotation = False

                restore_hik_hand_rotation = True

                self.log("ALPHA_V3_POSE_CLASS WARNING: classifier failed, using safe no-pair hand mode. Reason: %s" % _v3_class_exc)



        def _fmt3(v):

            try:

                return "(%.2f,%.2f,%.2f)" % (float(v[0]), float(v[1]), float(v[2]))

            except Exception:

                return "(nan,nan,nan)"



        def _safe_dist(a, b):

            try:

                return self._v_len(self._v_sub(a, b))

            except Exception:

                return 0.0



        def _safe_angle(a, b):

            try:

                la = max(self._v_len(a), 1e-8)

                lb = max(self._v_len(b), 1e-8)

                d = max(-1.0, min(1.0, self._v_dot(a, b) / (la * lb)))

                return math.degrees(math.acos(d))

            except Exception:

                return 0.0



        def _local_pair_distance(a_l, b_l):

            try:

                return self._v_len(self._v_sub(a_l, b_l))

            except Exception:

                return 0.0



        def _arm_diag_rest_report():

            if not (arm_diag_enabled and arm_diag_rest):

                return

            try:

                self.log("ALPHA_ARM_DIAG REST: body_scale=%.3f contact_up_fraction=[%.2f,%.2f] forward_abs=%.1f pair_dist=[%.1f,%.1f] pair_strength=%.2f same_side_min=%.1f" % (body_scale_ratio, contact_min_up_fraction, contact_max_up_fraction, contact_max_forward_abs, pair_min_distance, pair_max_distance, pair_strength, same_side_min))

                if source_rest_basis and target_rest_basis:

                    s_forward = source_rest_basis[3]

                    t_forward = target_rest_basis[3]

                    self.log("ALPHA_ARM_DIAG REST_BASIS: srcSide=%s srcUp=%s srcFwd=%s | tgtSide=%s tgtUp=%s tgtFwd=%s | forwardAngle=%.2f" % (_fmt3(source_rest_basis[1]), _fmt3(source_rest_basis[2]), _fmt3(source_rest_basis[3]), _fmt3(target_rest_basis[1]), _fmt3(target_rest_basis[2]), _fmt3(target_rest_basis[3]), _safe_angle(s_forward, t_forward)))

                for _side, _start_c, _mid_c, _end_c in sides:

                    if not all(k in source_rest_positions for k in (_start_c, _mid_c, _end_c)) or not all(k in target_rest_positions for k in (_start_c, _mid_c, _end_c)):

                        continue

                    src_upper = _safe_dist(source_rest_positions[_start_c], source_rest_positions[_mid_c])

                    src_lower = _safe_dist(source_rest_positions[_mid_c], source_rest_positions[_end_c])

                    tgt_upper = _safe_dist(target_rest_positions[_start_c], target_rest_positions[_mid_c])

                    tgt_lower = _safe_dist(target_rest_positions[_mid_c], target_rest_positions[_end_c])

                    src_w_l = _maybe_invert_forward(_to_local(source_rest_positions[_end_c], source_rest_basis)) if source_rest_basis else (0,0,0)

                    tgt_w_l = _to_local(target_rest_positions[_end_c], target_rest_basis) if target_rest_basis else (0,0,0)

                    src_el_l = _maybe_invert_forward(_to_local(source_rest_positions[_mid_c], source_rest_basis)) if source_rest_basis else (0,0,0)

                    tgt_el_l = _to_local(target_rest_positions[_mid_c], target_rest_basis) if target_rest_basis else (0,0,0)

                    src_upper_v = self._v_sub(source_rest_positions[_mid_c], source_rest_positions[_start_c])

                    tgt_upper_v = self._v_sub(target_rest_positions[_mid_c], target_rest_positions[_start_c])

                    src_lower_v = self._v_sub(source_rest_positions[_end_c], source_rest_positions[_mid_c])

                    tgt_lower_v = self._v_sub(target_rest_positions[_end_c], target_rest_positions[_mid_c])

                    self.log("ALPHA_ARM_DIAG REST side=%s srcLen=(%.2f,%.2f) tgtLen=(%.2f,%.2f) ratio=(%.3f,%.3f) restAngle=(upper %.1f lower %.1f) srcElL=%s srcWrL=%s tgtElL=%s tgtWrL=%s" % (_side, src_upper, src_lower, tgt_upper, tgt_lower, tgt_upper/max(src_upper,1e-5), tgt_lower/max(src_lower,1e-5), _safe_angle(src_upper_v, tgt_upper_v), _safe_angle(src_lower_v, tgt_lower_v), _fmt3(src_el_l), _fmt3(src_w_l), _fmt3(tgt_el_l), _fmt3(tgt_w_l)))

                                                                                                               

                def _diag_finger_nodes_under(_root):

                    if not _root or not safe_cmds_exists(_root):

                        return []

                    try:

                        _desc = cmds.listRelatives(_root, allDescendents=True, type="joint", fullPath=True) or []

                    except Exception:

                        _desc = []

                    _tokens = ("thumb", "index", "middle", "ring", "pinky", "little", "finger", "metacarpal")

                    _out = []

                    for _n in _desc:

                        _sn = short_name(_n).lower()

                        if any(_t in _sn for _t in _tokens):

                            _out.append(_n)

                    return list(dict.fromkeys(_out))

                for _side in ("l", "r"):

                    _src_hand = source_map.get("hand_" + _side)

                    _tgt_hand = target_map.get("hand_" + _side)

                    _src_fingers = _diag_finger_nodes_under(_src_hand)

                    _tgt_fingers = _diag_finger_nodes_under(_tgt_hand)

                    self.log("ALPHA_FINGER_DIAG REST side=%s sourceFingerCount=%d targetFingerCount=%d sourceFingerNames=%s targetFingerNames=%s" % (_side, len(_src_fingers), len(_tgt_fingers), ",".join(short_name(_n) for _n in _src_fingers[:80]), ",".join(short_name(_n) for _n in _tgt_fingers[:120])))

                try:

                    _body_keys = ["pelvis", "spine_01", "spine_02", "spine_03", "spine_04", "spine_05", "neck_01", "head"]

                    _parts = []

                    for _c in _body_keys:

                        _sn = source_map.get(_c)

                        _tn = target_map.get(_c)

                        if _sn and _tn and safe_cmds_exists(_sn) and safe_cmds_exists(_tn) and source_rest_basis and target_rest_basis:

                            _parts.append("%s:srcL=%s tgtL=%s" % (_c, _fmt3(_maybe_invert_forward(_to_local(get_world_position(_sn), source_rest_basis))), _fmt3(_to_local(get_world_position(_tn), target_rest_basis))))

                    self.log("ALPHA_BODY_DIAG REST %s" % " | ".join(_parts))

                except Exception as _body_exc:

                    self.log("ALPHA_BODY_DIAG REST WARNING: %s" % _body_exc)

            except Exception as exc:

                self.log("ALPHA_ARM_DIAG REST WARNING: %s" % exc)



        def _scale_local_from_source_to_target(local_vec):

            return (local_vec[0] * body_scale_ratio, local_vec[1] * body_scale_ratio, local_vec[2] * body_scale_ratio)



        def _clamp_contact_local(local_vec, target_basis):

            if not contact_pose_mode:

                return local_vec

            try:

                head_l = _to_local(get_world_position(target_map.get("head") or target_map.get("neck_01")), target_basis)

                pelvis_l = _to_local(get_world_position(target_map["pelvis"]), target_basis)

                span = max(abs(head_l[1] - pelvis_l[1]), 1.0)

                min_up = pelvis_l[1] + span * contact_min_up_fraction

                max_up = pelvis_l[1] + span * contact_max_up_fraction

                up = max(min_up, min(max_up, local_vec[1]))

            except Exception:

                up = local_vec[1]

            forward = local_vec[2]

            if contact_max_forward_abs > 0.0:

                forward = max(-contact_max_forward_abs, min(contact_max_forward_abs, forward))

            return (local_vec[0], up, forward)



        def _two_bone_elbow_position(shoulder_pos, wrist_pos, preferred_elbow_pos, upper_len, lower_len):

            sw = self._v_sub(wrist_pos, shoulder_pos)

            d_raw = self._v_len(sw)

            upper_len = max(float(upper_len), 1.0)

            lower_len = max(float(lower_len), 1.0)

            min_d = abs(upper_len - lower_len) + 1e-4

            max_d = (upper_len + lower_len) - 1e-4

            if d_raw <= 1e-6:

                direction = self._v_norm(self._v_sub(preferred_elbow_pos, shoulder_pos), fallback=(1.0, 0.0, 0.0))

                wrist_pos = self._v_add(shoulder_pos, self._v_mul(direction, min_d))

                sw = self._v_sub(wrist_pos, shoulder_pos)

                d_raw = self._v_len(sw)

            if d_raw < min_d or d_raw > max_d:

                direction = self._v_norm(sw, fallback=(1.0, 0.0, 0.0))

                d_clamped = max(min_d, min(max_d, d_raw))

                wrist_pos = self._v_add(shoulder_pos, self._v_mul(direction, d_clamped))

                sw = self._v_sub(wrist_pos, shoulder_pos)

                d_raw = max(self._v_len(sw), 1e-6)

            axis = self._v_norm(sw, fallback=(1.0, 0.0, 0.0))

            x = (upper_len * upper_len - lower_len * lower_len + d_raw * d_raw) / (2.0 * d_raw)

            h2 = max(0.0, upper_len * upper_len - x * x)

            h = math.sqrt(h2)

            center = self._v_add(shoulder_pos, self._v_mul(axis, x))

            pole = self._v_sub(preferred_elbow_pos, center)

            pole = self._v_sub(pole, self._v_mul(axis, self._v_dot(pole, axis)))

            if self._v_len(pole) <= 1e-5:

                pole = self._v_cross(axis, (0.0, 0.0, 1.0))

                if self._v_len(pole) <= 1e-5:

                    pole = self._v_cross(axis, (0.0, 1.0, 0.0))

            pole = self._v_norm(pole, fallback=(0.0, 1.0, 0.0))

            return self._v_add(center, self._v_mul(pole, h)), wrist_pos



        def _local_axis_from_joint_to_world_point(joint_node, world_point):

            loc = None

            try:

                loc = self._create_driver_locator("ALPHA_LocalAxisProbe_LOC")

                cmds.xform(loc, worldSpace=True, translation=world_point)

                cmds.parent(loc, joint_node)

                local_t = cmds.getAttr(loc + ".translate")[0]

                v = (float(local_t[0]), float(local_t[1]), float(local_t[2]))

                if self._v_len(v) <= 1e-5:

                    return (1.0, 0.0, 0.0)

                return self._v_norm(v, fallback=(1.0, 0.0, 0.0))

            except Exception:

                return (1.0, 0.0, 0.0)

            finally:

                try:

                    if loc and safe_cmds_exists(loc):

                        cmds.delete(loc)

                except Exception:

                    pass



        def _safe_local_up_vector(aim_vec, candidate_vec):

            aim = self._v_norm(aim_vec, fallback=(1.0, 0.0, 0.0))

            cand = self._v_norm(candidate_vec, fallback=(0.0, 1.0, 0.0))

            if abs(self._v_dot(aim, cand)) < 0.88:

                return cand

            choices = [(0.0, 1.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, 1.0), (0.0, 0.0, -1.0), (1.0, 0.0, 0.0), (-1.0, 0.0, 0.0)]

            best = choices[0]

            best_dot = 999.0

            for c in choices:

                d = abs(self._v_dot(aim, c))

                if d < best_dot:

                    best_dot = d

                    best = c

            return best



        bake_hand_rotation = bool(getattr(self.config, "humanik_source_guided_arm_ik_bake_hand_rotation", True))

        restore_hik_hand_rotation = bool(getattr(self.config, "humanik_source_guided_arm_ik_restore_hik_hand_rotation", False))



        temp_nodes: List[str] = []

        constraints: List[str] = []

        ik_handles: List[str] = []

        end_locs: Dict[str, str] = {}

        elbow_locs: Dict[str, str] = {}

        pole_locs: Dict[str, str] = {}

        shoulder_locs: Dict[str, str] = {}

        arm_bake_nodes: List[str] = []

        debug_samples: List[str] = []

        pair_debug_samples: List[str] = []

        correction_count = 0

        max_wrist_delta = 0.0

        max_reach_clamp = 0.0

        side_corrections = 0

        thigh_clearance_corrections = 0

        max_thigh_clearance_push = 0.0



        for side, start_c, mid_c, end_c in sides:

            label = "src_guided_arm_%s" % side

            end_locs[label] = self._create_driver_locator("ALPHA_SourceGuidedArm_%s_Wrist_LOC" % side)

            elbow_locs[label] = self._create_driver_locator("ALPHA_SourceGuidedArm_%s_Elbow_LOC" % side)

            pole_locs[label] = self._create_driver_locator("ALPHA_SourceGuidedArm_%s_Pole_LOC" % side)

            shoulder_locs[label] = self._create_driver_locator("ALPHA_SourceGuidedArm_%s_Shoulder_LOC" % side)

            temp_nodes.extend([end_locs[label], elbow_locs[label], pole_locs[label], shoulder_locs[label]])

            clav_c = "clavicle_%s" % side

            if (include_clavicle_chain or soft_clavicle_aim) and target_map.get(clav_c) and safe_cmds_exists(target_map.get(clav_c)):

                bake_chain = (clav_c, start_c, mid_c, end_c) if bake_hand_rotation else (clav_c, start_c, mid_c)

            else:

                bake_chain = (start_c, mid_c, end_c) if bake_hand_rotation else (start_c, mid_c)

            for c in bake_chain:

                n = target_map.get(c)

                if n and safe_cmds_exists(n):

                    arm_bake_nodes.append(n)

        arm_bake_nodes = list(dict.fromkeys(arm_bake_nodes))



        hik_hand_rotations = {}

        if restore_hik_hand_rotation:

            for frame in frames:

                cmds.currentTime(frame, edit=True, update=True)

                for _side, _start_c, _mid_c, _end_c in sides:

                    hand_node = target_map.get(_end_c)

                    if hand_node and safe_cmds_exists(hand_node):

                        try:

                            hik_hand_rotations[(hand_node, frame)] = tuple(float(v) for v in cmds.getAttr(hand_node + ".rotate")[0])

                        except Exception:

                            pass

                                                                                

                                                                                                     

                                                                                                  

                                                                                                  

        reset_keys = 0

        if reset_hik_arm_to_rest and target_rest_local_rotations:

            reset_canonicals = ["upperarm_l", "lowerarm_l", "hand_l", "upperarm_r", "lowerarm_r", "hand_r"] if preserve_hik_clavicles else ["clavicle_l", "upperarm_l", "lowerarm_l", "hand_l", "clavicle_r", "upperarm_r", "lowerarm_r", "hand_r"]

            for frame in frames:

                cmds.currentTime(frame, edit=True, update=False)

                for _canon in reset_canonicals:

                    _node = target_map.get(_canon)

                    _rot = target_rest_local_rotations.get(_canon)

                    if _node and _rot is not None and safe_cmds_exists(_node):

                        try:

                            unlock_transform_attrs(_node)

                            cmds.setAttr(_node + ".rotate", float(_rot[0]), float(_rot[1]), float(_rot[2]))

                            cmds.setKeyframe(_node, attribute=ROTATE_ATTRS, time=frame)

                            reset_keys += 3

                        except Exception:

                            pass

            self.log("HumanIK Option1 v2.29.0: reset baked HIK arm rotations to target rest before custom solve, keys=%d preserve_hik_clavicles=%s reset_joints=%s" % (reset_keys, str(preserve_hik_clavicles), ",".join(reset_canonicals)))

        elif reset_hik_arm_to_rest:

            self.log("HumanIK Option1 v2.1.7 WARNING: arm reset requested but target rest rotations were unavailable.")



                                          

                                                                                                                       

                                                                                                        

                                                                                                                   

        clavicle_guard_keys = 0

        if preserve_hik_clavicles and target_rest_local_rotations and clavicle_hik_rotation_blend < 0.999:

            def _short_blend_euler(_base, _target, _blend):

                _out = []

                for _b, _t in zip(_base, _target):

                    _d = float(_t) - float(_b)

                    while _d > 180.0:

                        _d -= 360.0

                    while _d < -180.0:

                        _d += 360.0

                    _out.append(float(_b) + _d * float(_blend))

                return tuple(_out)

            for _frame in frames:

                try:

                    cmds.currentTime(_frame, edit=True, update=False)

                except Exception:

                    pass

                for _canon in ("clavicle_l", "clavicle_r"):

                    _node = target_map.get(_canon)

                    _rest = target_rest_local_rotations.get(_canon)

                    if _node and _rest is not None and safe_cmds_exists(_node):

                        try:

                            _hik = self._get_vec(_node, ROTATE_ATTRS)

                            _out = _short_blend_euler(_rest, _hik, clavicle_hik_rotation_blend)

                            self._set_vec(_node, ROTATE_ATTRS, _out)

                            for _attr in ROTATE_ATTRS:

                                cmds.setKeyframe(_node, attribute=_attr, time=_frame)

                                clavicle_guard_keys += 1

                        except Exception:

                            pass

            self.log("HumanIK Option1 v2.29.0 clavicle silhouette guard: preserveHIK=True blend=%.2f keys=%d. Clavicles are not solved by IK/aim; they are softly clamped between rest and HIK." % (clavicle_hik_rotation_blend, clavicle_guard_keys))



        _arm_diag_rest_report()



        self.log(

            "HumanIK Option1 v2.29.0 SAFE CORE-ARMS MAIN-FINGERS TEMPLATE: solving arms from source elbow/wrist torso-space pose. frames=%d strength=%.2f pole=%.2f max_pull=%.1f reach=%.2f same_side_min=%.1f body_scale=%.3f contact_pose=%s invert_forward_axis=%s shoulder_relative_mapping=%s clavicle_chain=%s pair_convergence=%s pair_strength=%.2f pair_src_threshold=%.1f pair_dist=[%.1f,%.1f] bake_hand_rotation=%s restore_hik_hand_rotation=%s reset_hik_arm_to_rest=%s thigh_clearance=%s/%.1f analytic_aim_solver=%s preserve_hik_clavicles=%s hand_contact_aim=%s hand_aim_blend=%.2f sourcePalmDelta=%s sourcePalmBlend=%.2f sourcePalmClamp=%.1f anchorFit=%s anchorSide=%s anchorStrength=%.2f followerStrength=%.2f palmFrameDiag=%s soft_clavicle_aim=%s soft_clavicle_strength=%.2f clavicleHIKBlend=%.2f referenceClaspTemplate=%s refPair=%.2f refLift=%.2f refPalmPose=%s refFingerTemplate=%s userTemplate=%s userTemplateBlend=%.2f userTemplateDelta=%s userTemplatePoseMatch=%s"

            % (len(frames), strength, pole_strength, max_pull, reach_limit, same_side_min, body_scale_ratio, str(contact_pose_mode), str(invert_forward_axis), str(use_shoulder_relative_mapping), str(include_clavicle_chain), str(pair_convergence), pair_strength, pair_source_threshold, pair_min_distance, pair_max_distance, bake_hand_rotation, restore_hik_hand_rotation, reset_hik_arm_to_rest, str(use_thigh_clearance), thigh_clearance, str(analytic_aim_solver), str(preserve_hik_clavicles), str(hand_contact_aim), hand_contact_aim_blend, str(source_palm_delta), source_palm_delta_blend, source_palm_delta_clamp, str(anchor_hand_fit), anchor_hand_side, anchor_hand_strength, follower_hand_strength, str(palm_frame_diagnostics), str(soft_clavicle_aim), soft_clavicle_strength, clavicle_hik_rotation_blend, str(reference_clasp_template), reference_clasp_pair_distance, reference_clasp_center_up_lift, str(reference_clasp_palm_pose), str(reference_clasp_finger_template), str(user_clasp_template_enabled), user_clasp_template_blend, str(user_clasp_template_use_delta), str(user_clasp_template_pose_match))

        )



        sample_indices = sorted(set([0, len(frames)//4, len(frames)//2, (len(frames)*3)//4, len(frames)-1]))

        if arm_diag_max_samples < len(sample_indices):

            sample_indices = sample_indices[:arm_diag_max_samples]

        sample_frames = set(frames[i] for i in sample_indices if i >= 0 and i < len(frames))

        keyed_driver_channels = 0

        pair_convergence_frames = 0

        pair_convergence_total_pull = 0.0

        pair_convergence_max_pull = 0.0

        pair_convergence_max_source_distance = 0.0



        def _apply_same_side_guard(side, target_basis, shoulder_pos, wrist_pos):

                                                                                      

                                                                                                       

            if same_side_min <= 0.0:

                return wrist_pos, False

            sh_l = _to_local(shoulder_pos, target_basis)

            wr_l = _to_local(wrist_pos, target_basis)

            side_sign = 1.0 if sh_l[0] >= 0.0 else -1.0

            min_side = min(abs(sh_l[0]) * 0.75, same_side_min)

            if wr_l[0] * side_sign < min_side:

                side_fix = side_sign * min_side - wr_l[0]

                return self._v_add(wrist_pos, self._v_mul(target_basis[1], side_fix)), True

            return wrist_pos, False



        for frame in frames:

            cmds.currentTime(frame, edit=True, update=True)

            try:

                cmds.refresh(force=True)

            except Exception:

                pass

            src_basis = _basis_from_map(source_map)

            tgt_basis = _basis_from_map(target_map)

            tgt_front_axis = tgt_basis[3]



            frame_targets: Dict[str, Dict[str, Any]] = {}

            frame_source_wrist_local: Dict[str, Tuple[float, float, float]] = {}



            for side, start_c, mid_c, end_c in sides:

                label = "src_guided_arm_%s" % side

                src_sh = get_world_position(source_map[start_c])

                src_el = get_world_position(source_map[mid_c])

                src_wr = get_world_position(source_map[end_c])

                tgt_sh = get_world_position(target_map[start_c])

                tgt_el = get_world_position(target_map[mid_c])

                tgt_wr = get_world_position(target_map[end_c])



                target_upper_len = max(self._v_len(self._v_sub(tgt_el, tgt_sh)), 1.0)

                target_lower_len = max(self._v_len(self._v_sub(tgt_wr, tgt_el)), 1.0)



                if use_shoulder_relative_mapping:

                                                                                                

                                                                                                       

                    src_sh_local_abs = _maybe_invert_forward(_to_local(src_sh, src_basis))

                    src_el_local_abs = _maybe_invert_forward(_to_local(src_el, src_basis))

                    src_wr_local_abs = _maybe_invert_forward(_to_local(src_wr, src_basis))

                    tgt_sh_local_abs = _to_local(tgt_sh, tgt_basis)



                    src_upper_len_ref = max(self._v_len(self._v_sub(src_el, src_sh)), 1.0)

                    src_lower_len_ref = max(self._v_len(self._v_sub(src_wr, src_el)), 1.0)

                    arm_scale = (target_upper_len + target_lower_len) / max(src_upper_len_ref + src_lower_len_ref, 1.0)



                    if contact_pose_mode:

                                                                                                        

                                                                                                          

                                                                                                          

                                                                                                    

                        desired_elbow_local = _clamp_contact_local(_scale_local_from_source_to_target(src_el_local_abs), tgt_basis)

                        desired_wrist_local = _clamp_contact_local(_scale_local_from_source_to_target(src_wr_local_abs), tgt_basis)

                    else:

                        desired_elbow_local = self._v_add(tgt_sh_local_abs, self._v_mul(self._v_sub(src_el_local_abs, src_sh_local_abs), arm_scale))

                        desired_wrist_local = self._v_add(tgt_sh_local_abs, self._v_mul(self._v_sub(src_wr_local_abs, src_sh_local_abs), arm_scale))

                    desired_elbow = _local_to_world(desired_elbow_local, tgt_basis)

                    desired_wrist_raw = _local_to_world(desired_wrist_local, tgt_basis)

                                                                                                

                                                                                                     

                                                                                               

                    if contact_pose_mode:

                        desired_shoulder_local = _scale_local_from_source_to_target(src_sh_local_abs)

                    else:

                        desired_shoulder_local = tgt_sh_local_abs

                    desired_shoulder_world = _local_to_world((

                        tgt_sh_local_abs[0] * (1.0 - soft_clavicle_strength) + desired_shoulder_local[0] * soft_clavicle_strength,

                        tgt_sh_local_abs[1] * (1.0 - soft_clavicle_strength) + desired_shoulder_local[1] * soft_clavicle_strength,

                        tgt_sh_local_abs[2] * (1.0 - soft_clavicle_strength) + desired_shoulder_local[2] * soft_clavicle_strength,

                    ), tgt_basis)

                    frame_source_wrist_local[side] = _scale_local_from_source_to_target(src_wr_local_abs) if contact_pose_mode else src_wr_local_abs

                else:

                    src_upper_local = _maybe_invert_forward(_dir_to_local(self._v_sub(src_el, src_sh), src_basis))

                    src_lower_local = _maybe_invert_forward(_dir_to_local(self._v_sub(src_wr, src_el), src_basis))

                    src_upper_dir = self._v_norm(_dir_to_world(src_upper_local, tgt_basis), fallback=self._v_sub(tgt_el, tgt_sh))

                    src_lower_dir = self._v_norm(_dir_to_world(src_lower_local, tgt_basis), fallback=self._v_sub(tgt_wr, tgt_el))

                    desired_elbow = self._v_add(tgt_sh, self._v_mul(src_upper_dir, target_upper_len))

                    desired_wrist_raw = self._v_add(desired_elbow, self._v_mul(src_lower_dir, target_lower_len))

                    desired_shoulder_world = tgt_sh

                    frame_source_wrist_local[side] = _maybe_invert_forward(_to_local(src_wr, src_basis))



                    if use_virtual_rest and side in target_virtual_rest_local and mid_c in source_rest_local and end_c in source_rest_local:

                        src_el_local_abs = _maybe_invert_forward(_to_local(src_el, src_basis))

                        src_wr_local_abs = _maybe_invert_forward(_to_local(src_wr, src_basis))

                        src_el_delta = self._v_sub(src_el_local_abs, source_rest_local[mid_c])

                        src_wr_delta = self._v_sub(src_wr_local_abs, source_rest_local[end_c])

                        virtual_elbow_local = self._v_add(target_virtual_rest_local[side]["elbow"], src_el_delta)

                        virtual_wrist_local = self._v_add(target_virtual_rest_local[side]["wrist"], src_wr_delta)

                        virtual_elbow_world = _local_to_world(virtual_elbow_local, tgt_basis)

                        virtual_wrist_world = _local_to_world(virtual_wrist_local, tgt_basis)

                        desired_elbow = self._v_add(desired_elbow, self._v_mul(self._v_sub(virtual_elbow_world, desired_elbow), virtual_rest_strength))

                        desired_wrist_raw = self._v_add(desired_wrist_raw, self._v_mul(self._v_sub(virtual_wrist_world, desired_wrist_raw), virtual_rest_strength))



                desired_wrist = self._v_add(tgt_wr, self._v_mul(self._v_sub(desired_wrist_raw, tgt_wr), strength))

                desired_elbow = self._v_add(tgt_el, self._v_mul(self._v_sub(desired_elbow, tgt_el), max(0.35, min(1.0, pole_strength))))



                if contact_pose_mode and contact_elbow_side_guard:

                                                                                                                

                                                                                          

                    try:

                        sh_l = _to_local(tgt_sh, tgt_basis)

                        el_l = _to_local(desired_elbow, tgt_basis)

                        side_sign = 1.0 if sh_l[0] >= 0.0 else -1.0

                        min_out = sh_l[0] + side_sign * contact_elbow_side_margin

                        if el_l[0] * side_sign < min_out * side_sign:

                            el_l = (min_out, el_l[1], el_l[2])

                            desired_elbow = _local_to_world(el_l, tgt_basis)

                    except Exception:

                        pass



                frame_targets[side] = {

                    "label": label,

                    "start_c": start_c,

                    "mid_c": mid_c,

                    "end_c": end_c,

                    "src_sh": src_sh,

                    "src_el": src_el,

                    "src_wr": src_wr,

                    "tgt_sh": tgt_sh,

                    "tgt_el": tgt_el,

                    "tgt_wr": tgt_wr,

                    "src_sh_local": _maybe_invert_forward(_to_local(src_sh, src_basis)),

                    "src_el_local": _maybe_invert_forward(_to_local(src_el, src_basis)),

                    "src_wr_local": _maybe_invert_forward(_to_local(src_wr, src_basis)),

                    "hik_el_local": _to_local(tgt_el, tgt_basis),

                    "hik_wr_local": _to_local(tgt_wr, tgt_basis),

                    "desired_elbow_pre_pair_local": _to_local(desired_elbow, tgt_basis),

                    "desired_wrist_pre_pair_local": _to_local(desired_wrist, tgt_basis),

                    "desired_elbow": desired_elbow,

                    "desired_wrist": desired_wrist,

                    "desired_shoulder": desired_shoulder_world if 'desired_shoulder_world' in locals() else tgt_sh,

                    "target_upper_len": target_upper_len,

                    "target_lower_len": target_lower_len,

                }



                                             

                                                                                                             

                                                                                                                

                                                                               

            if pair_convergence and pair_strength > 0.0 and "l" in frame_targets and "r" in frame_targets and "l" in frame_source_wrist_local and "r" in frame_source_wrist_local:

                src_l_local = frame_source_wrist_local["l"]

                src_r_local = frame_source_wrist_local["r"]

                src_pair_delta = self._v_sub(src_r_local, src_l_local)

                src_pair_dist = self._v_len(src_pair_delta)

                pair_convergence_max_source_distance = max(pair_convergence_max_source_distance, src_pair_dist)

                if src_pair_dist <= pair_source_threshold:

                    l_des_local = _to_local(frame_targets["l"]["desired_wrist"], tgt_basis)

                    r_des_local = _to_local(frame_targets["r"]["desired_wrist"], tgt_basis)

                    current_center_local = self._v_mul(self._v_add(l_des_local, r_des_local), 0.5)

                    source_center_local = self._v_mul(self._v_add(src_l_local, src_r_local), 0.5)



                                                         

                                                                                                      

                                                                                                        

                                                                                                        

                                                             

                    source_center_local = _clamp_contact_local(source_center_local, tgt_basis)

                    midline_source_center_local = (0.0 if contact_pose_mode else source_center_local[0], source_center_local[1], source_center_local[2])

                    paired_center_local = (

                        current_center_local[0] * (1.0 - pair_center_blend) + midline_source_center_local[0] * pair_center_blend,

                        current_center_local[1] * (1.0 - pair_center_blend) + midline_source_center_local[1] * pair_center_blend,

                        current_center_local[2] * (1.0 - pair_center_blend) + midline_source_center_local[2] * pair_center_blend,

                    )



                                                                                                          

                    head_local = _to_local(get_world_position(target_map.get("head") or target_map.get("neck_01")), tgt_basis)

                    pelvis_local = _to_local(get_world_position(target_map["pelvis"]), tgt_basis)

                    chest_up = pelvis_local[1] + (head_local[1] - pelvis_local[1]) * 0.58

                    if paired_center_local[1] < chest_up:

                        paired_center_local = (

                            paired_center_local[0],

                            paired_center_local[1] * (1.0 - pair_chest_height_bias) + chest_up * pair_chest_height_bias,

                            paired_center_local[2],

                        )

                    paired_center_local = _clamp_contact_local(paired_center_local, tgt_basis)



                                                                                                              

                    desired_pair_distance = max(pair_min_distance, min(pair_max_distance, src_pair_dist * pair_distance_scale))

                    src_pair_dir = self._v_norm(src_pair_delta, fallback=(1.0, 0.0, 0.0))

                    half_delta_local = self._v_mul(src_pair_dir, desired_pair_distance * 0.5)

                    paired_l_local = self._v_sub(paired_center_local, half_delta_local)

                    paired_r_local = self._v_add(paired_center_local, half_delta_local)

                    paired_l_world = _local_to_world(paired_l_local, tgt_basis)

                    paired_r_world = _local_to_world(paired_r_local, tgt_basis)



                                                                                                         

                                                                                                             

                                                                                                         

                    if anchor_hand_fit:

                        try:

                            if anchor_hand_side == "r":

                                _anchor_before = frame_targets["r"]["desired_wrist"]

                                _anchor_pair = paired_r_world

                                _anchor_world = self._v_add(_anchor_before, self._v_mul(self._v_sub(_anchor_pair, _anchor_before), anchor_hand_strength))

                                _anchor_local = _to_local(_anchor_world, tgt_basis)

                                _follower_local = self._v_sub(_anchor_local, self._v_mul(src_pair_dir, desired_pair_distance))

                                _follower_pair_world = _local_to_world(_follower_local, tgt_basis)

                                paired_r_world = _anchor_world

                                paired_l_world = self._v_add(paired_l_world, self._v_mul(self._v_sub(_follower_pair_world, paired_l_world), follower_hand_strength))

                            else:

                                _anchor_before = frame_targets["l"]["desired_wrist"]

                                _anchor_pair = paired_l_world

                                _anchor_world = self._v_add(_anchor_before, self._v_mul(self._v_sub(_anchor_pair, _anchor_before), anchor_hand_strength))

                                _anchor_local = _to_local(_anchor_world, tgt_basis)

                                _follower_local = self._v_add(_anchor_local, self._v_mul(src_pair_dir, desired_pair_distance))

                                _follower_pair_world = _local_to_world(_follower_local, tgt_basis)

                                paired_l_world = _anchor_world

                                paired_r_world = self._v_add(paired_r_world, self._v_mul(self._v_sub(_follower_pair_world, paired_r_world), follower_hand_strength))

                        except Exception:

                            pass



                                                                                                        

                                                                                                                

                                                                                                             

                                                                                                           

                                                                                          

                    if reference_clasp_template and contact_pose_mode:

                        try:

                            _head_l = _to_local(get_world_position(target_map.get("head") or target_map.get("neck_01")), tgt_basis)

                            _pelvis_l = _to_local(get_world_position(target_map["pelvis"]), tgt_basis)

                            _span = max(abs(_head_l[1] - _pelvis_l[1]), 1.0)

                            _min_y = _pelvis_l[1] + _span * reference_clasp_center_min_fraction

                            _max_y = _pelvis_l[1] + _span * reference_clasp_center_max_fraction

                            _template_center = (

                                paired_center_local[0] * 0.18,

                                max(_min_y, min(_max_y, source_center_local[1] + reference_clasp_center_up_lift)),

                                source_center_local[2] + reference_clasp_forward_offset,

                            )

                            _dist = max(pair_min_distance, min(pair_max_distance, reference_clasp_pair_distance))

                            _l_template_local = (

                                _template_center[0] - _dist * 0.5,

                                _template_center[1] + reference_clasp_left_up_offset,

                                _template_center[2] + reference_clasp_left_forward_offset,

                            )

                            _r_template_local = (

                                _template_center[0] + _dist * 0.5,

                                _template_center[1] + reference_clasp_right_up_offset,

                                _template_center[2] + reference_clasp_right_forward_offset,

                            )

                            _l_template_world = _local_to_world(_l_template_local, tgt_basis)

                            _r_template_world = _local_to_world(_r_template_local, tgt_basis)

                            paired_l_world = self._v_add(paired_l_world, self._v_mul(self._v_sub(_l_template_world, paired_l_world), reference_clasp_strength))

                            paired_r_world = self._v_add(paired_r_world, self._v_mul(self._v_sub(_r_template_world, paired_r_world), reference_clasp_strength))

                            if arm_diag_enabled and frame in sample_frames:

                                pair_debug_samples.append("f=%.2f REFERENCE_CLASP_TEMPLATE center=%s dist=%.2f lTemplate=%s rTemplate=%s strength=%.2f" % (frame, _fmt3(_template_center), _dist, _fmt3(_l_template_local), _fmt3(_r_template_local), reference_clasp_strength))

                        except Exception as _ref_exc:

                            if arm_diag_enabled and frame in sample_frames:

                                pair_debug_samples.append("f=%.2f referenceClaspTemplateFailed=%s" % (frame, _ref_exc))



                    before_l = frame_targets["l"]["desired_wrist"]

                    before_r = frame_targets["r"]["desired_wrist"]

                    new_l = self._v_add(before_l, self._v_mul(self._v_sub(paired_l_world, before_l), pair_strength))

                    new_r = self._v_add(before_r, self._v_mul(self._v_sub(paired_r_world, before_r), pair_strength))

                    if pair_max_target_pull > 0.0:

                        dl = self._v_sub(new_l, before_l)

                        dr = self._v_sub(new_r, before_r)

                        dl_len = self._v_len(dl)

                        dr_len = self._v_len(dr)

                        if dl_len > pair_max_target_pull:

                            new_l = self._v_add(before_l, self._v_mul(self._v_norm(dl), pair_max_target_pull))

                        if dr_len > pair_max_target_pull:

                            new_r = self._v_add(before_r, self._v_mul(self._v_norm(dr), pair_max_target_pull))

                    frame_targets["l"]["desired_wrist"] = new_l

                    frame_targets["r"]["desired_wrist"] = new_r



                                                                                          

                                                                                             

                                                                                                  

                    try:

                        anti_cross_min = max(pair_min_distance * 0.40, same_side_min, 5.5)

                        for _side_key, _sign in (("l", -1.0), ("r", 1.0)):

                            _w_l = _to_local(frame_targets[_side_key]["desired_wrist"], tgt_basis)

                            if _w_l[0] * _sign < anti_cross_min:

                                _w_l = (_sign * anti_cross_min, _w_l[1], _w_l[2])

                                frame_targets[_side_key]["desired_wrist"] = _local_to_world(_w_l, tgt_basis)

                    except Exception:

                        pass



                    if arm_diag_enabled and frame in sample_frames:

                        try:

                            after_l_local = _to_local(frame_targets["l"]["desired_wrist"], tgt_basis)

                            after_r_local = _to_local(frame_targets["r"]["desired_wrist"], tgt_basis)

                            before_l_local = _to_local(before_l, tgt_basis)

                            before_r_local = _to_local(before_r, tgt_basis)

                            pair_debug_samples.append("f=%.2f anchorFit=%s anchorSide=%s srcPairDist=%.2f targetPrePairDist=%.2f desiredPairDist=%.2f afterPairDist=%.2f srcCenter=%s currentCenter=%s pairedCenter=%s beforeL=%s beforeR=%s afterL=%s afterR=%s" % (frame, str(anchor_hand_fit), anchor_hand_side, src_pair_dist, _local_pair_distance(l_des_local, r_des_local), desired_pair_distance, _local_pair_distance(after_l_local, after_r_local), _fmt3(source_center_local), _fmt3(current_center_local), _fmt3(paired_center_local), _fmt3(before_l_local), _fmt3(before_r_local), _fmt3(after_l_local), _fmt3(after_r_local)))

                        except Exception as exc:

                            pair_debug_samples.append("f=%.2f pairDiagnosticFailed=%s" % (frame, exc))



                    pull_l = self._v_len(self._v_sub(frame_targets["l"]["desired_wrist"], before_l))

                    pull_r = self._v_len(self._v_sub(frame_targets["r"]["desired_wrist"], before_r))

                    pair_convergence_frames += 1

                    pair_convergence_total_pull += pull_l + pull_r

                    pair_convergence_max_pull = max(pair_convergence_max_pull, pull_l, pull_r)



            for side, start_c, mid_c, end_c in sides:

                if side not in frame_targets:

                    continue

                data = frame_targets[side]

                label = data["label"]

                desired_wrist = data["desired_wrist"]

                desired_elbow = data["desired_elbow"]

                tgt_sh = data["tgt_sh"]

                tgt_wr = data["tgt_wr"]

                target_upper_len = data["target_upper_len"]

                target_lower_len = data["target_lower_len"]



                desired_wrist, did_side_fix = _apply_same_side_guard(side, tgt_basis, tgt_sh, desired_wrist)

                if did_side_fix:

                    side_corrections += 1



                if use_thigh_clearance and thigh_clearance > 0.0:

                    thigh_node = target_map.get("thigh_%s" % side)

                    calf_node = target_map.get("calf_%s" % side)

                    if thigh_node and calf_node and safe_cmds_exists(thigh_node) and safe_cmds_exists(calf_node):

                        thigh_pos = get_world_position(thigh_node)

                        calf_pos = get_world_position(calf_node)

                        closest = _closest_point_on_segment(desired_wrist, thigh_pos, calf_pos)

                        away = self._v_sub(desired_wrist, closest)

                        d = self._v_len(away)

                        if d < thigh_clearance:

                            push_dir = self._v_norm(self._v_add(away, self._v_mul(tgt_basis[2], thigh_clearance_up_bias)), fallback=tgt_basis[2])

                            push_len = thigh_clearance - d

                            desired_wrist = self._v_add(desired_wrist, self._v_mul(push_dir, push_len))

                            thigh_clearance_corrections += 1

                            max_thigh_clearance_push = max(max_thigh_clearance_push, push_len)



                shoulder_to_wrist = self._v_sub(desired_wrist, tgt_sh)

                reach = self._v_len(shoulder_to_wrist)

                max_reach = (target_upper_len + target_lower_len) * reach_limit

                if reach > max_reach:

                    excess = reach - max_reach

                    max_reach_clamp = max(max_reach_clamp, excess)

                    desired_wrist = self._v_add(tgt_sh, self._v_mul(self._v_norm(shoulder_to_wrist), max_reach))



                delta = self._v_sub(desired_wrist, tgt_wr)

                delta_len = self._v_len(delta)

                max_wrist_delta = max(max_wrist_delta, delta_len)

                if max_pull > 0.0 and delta_len > max_pull:

                    desired_wrist = self._v_add(tgt_wr, self._v_mul(self._v_norm(delta), max_pull))



                                                                                             

                                                                                                       

                                                                                                     

                if analytic_aim_solver:

                    desired_elbow, desired_wrist = _two_bone_elbow_position(tgt_sh, desired_wrist, desired_elbow, target_upper_len, target_lower_len)



                self._set_and_key_locator_pos(end_locs[label], desired_wrist, frame)

                self._set_and_key_locator_pos(elbow_locs[label], desired_elbow, frame)

                if soft_clavicle_aim and shoulder_locs.get(label):

                    self._set_and_key_locator_pos(shoulder_locs[label], data.get("desired_shoulder", tgt_sh), frame)

                    keyed_driver_channels += 3

                keyed_driver_channels += 6

                pole_target = self._make_pole_position(tgt_sh, desired_elbow, desired_wrist, fallback_axis=tgt_front_axis, scale=1.05)

                self._set_and_key_locator_pos(pole_locs[label], pole_target, frame)

                keyed_driver_channels += 3

                correction_count += 1



                if frame in sample_frames:

                    wr_local = _to_local(tgt_wr, tgt_basis)

                    des_local = _to_local(desired_wrist, tgt_basis)

                    src_wr_local = frame_source_wrist_local.get(side) or _maybe_invert_forward(_to_local(data["src_wr"], src_basis))

                    src_el_local = data.get("src_el_local") or _maybe_invert_forward(_to_local(data["src_el"], src_basis))

                    hik_el_local = data.get("hik_el_local") or _to_local(data["tgt_el"], tgt_basis)

                    des_el_local = _to_local(desired_elbow, tgt_basis)

                    pre_wr_local = data.get("desired_wrist_pre_pair_local") or des_local

                    debug_samples.append(

                        "f=%.2f side=%s mode=%s paired=%s analyticAim=%s invertFwd=%s srcElL=%s srcWrL=%s hikElL=%s hikWrL=%s preWrL=%s finalDesiredElL=%s finalDesiredWrL=%s srcElWrDist=%.2f targetElWrDist=%.2f desiredElWrDist=%.2f wristDeltaFromHIK=%.2f"

                        % (frame, side, "shoulderRelative" if use_shoulder_relative_mapping else "virtualRestDelta", str(pair_convergence and pair_convergence_frames > 0), str(analytic_aim_solver), str(invert_forward_axis), _fmt3(src_el_local), _fmt3(src_wr_local), _fmt3(hik_el_local), _fmt3(wr_local), _fmt3(pre_wr_local), _fmt3(des_el_local), _fmt3(des_local), _safe_dist(data["src_el"], data["src_wr"]), _safe_dist(data["tgt_el"], data["tgt_wr"]), _safe_dist(desired_elbow, desired_wrist), delta_len)

                    )





        def _target_joint_by_short_any(names):

            _names = [str(n).lower() for n in names]

            try:

                _joints = get_all_joints()

            except Exception:

                _joints = target_joints_to_bake

            for _j in _joints:

                _sn = short_name(_j).lower()

                if _sn in _names:

                    return _j

            return None



        def _finger_tip_for_side_contact(_side):

            suffix = "_" + _side

            return _target_joint_by_short_any([

                "middle_03" + suffix, "middle_02" + suffix,

                "index_03" + suffix, "index_02" + suffix,

                "ring_03" + suffix, "ring_02" + suffix,

            ])



        for side, start_c, mid_c, end_c in sides:

            label = "src_guided_arm_%s" % side

            if analytic_aim_solver:

                                            

                                                                                                             

                                                                                                                

                                                                                                                 

                                                                                                     

                upper_node = target_map.get(start_c)

                lower_node = target_map.get(mid_c)

                hand_node = target_map.get(end_c)

                if not (upper_node and lower_node and hand_node and safe_cmds_exists(upper_node) and safe_cmds_exists(lower_node) and safe_cmds_exists(hand_node)):

                    continue

                try:

                    cmds.currentTime(frames[0], edit=True, update=True)

                except Exception:

                    pass

                                                                                                 

                                                                                                    

                                                                                                       

                if soft_clavicle_aim:

                    try:

                        clav_node = target_map.get("clavicle_%s" % side)

                        if clav_node and safe_cmds_exists(clav_node) and shoulder_locs.get(label):

                            clav_aim = _local_axis_from_joint_to_world_point(clav_node, get_world_position(upper_node))

                            clav_up = _safe_local_up_vector(clav_aim, _local_axis_from_joint_to_world_point(clav_node, get_world_position(pole_locs[label])))

                            _clav_con = cmds.aimConstraint(shoulder_locs[label], clav_node, maintainOffset=True, aimVector=clav_aim, upVector=clav_up, worldUpType="object", worldUpObject=pole_locs[label])[0]

                                                                                                                       

                                                                                                                              

                                                                                             

                            try:

                                _aliases = cmds.aimConstraint(_clav_con, query=True, weightAliasList=True) or []

                                if _aliases:

                                    cmds.setAttr(_clav_con + "." + _aliases[0], soft_clavicle_strength)

                            except Exception:

                                pass

                            constraints.append(_clav_con)

                            self.log("HumanIK Option1 v2.29.0 user-calibrated-clasp aim: %s clavAim=%s clavUp=%s strength=%.2f maintainOffset=True constraintWeight=%.2f. Right-clavicle indentation guard active." % (side, _fmt3(clav_aim), _fmt3(clav_up), soft_clavicle_strength, soft_clavicle_strength))

                    except Exception as exc:

                        self.log("HumanIK soft-clavicle aim WARNING: could not create clavicle aim for %s: %s" % (side, exc))

                upper_aim = _local_axis_from_joint_to_world_point(upper_node, get_world_position(lower_node))

                lower_aim = _local_axis_from_joint_to_world_point(lower_node, get_world_position(hand_node))

                                                                                                      

                                                                                                      

                                                                                                     

                upper_up = _safe_local_up_vector(upper_aim, _local_axis_from_joint_to_world_point(upper_node, get_world_position(pole_locs[label])))

                lower_up = _safe_local_up_vector(lower_aim, _local_axis_from_joint_to_world_point(lower_node, get_world_position(pole_locs[label])))

                try:

                    constraints.append(cmds.aimConstraint(elbow_locs[label], upper_node, maintainOffset=False, aimVector=upper_aim, upVector=upper_up, worldUpType="object", worldUpObject=pole_locs[label])[0])

                    constraints.append(cmds.aimConstraint(end_locs[label], lower_node, maintainOffset=False, aimVector=lower_aim, upVector=lower_up, worldUpType="object", worldUpObject=pole_locs[label])[0])

                    self.log("HumanIK Option1 v2.29.0 user-calibrated-clasp arm chain: %s upperAim=%s upperUp=%s lowerAim=%s lowerUp=%s. IK handle disabled for this arm." % (side, _fmt3(upper_aim), _fmt3(upper_up), _fmt3(lower_aim), _fmt3(lower_up)))

                except Exception as exc:

                    self.log("HumanIK clavicle-hand WARNING: could not create aim constraints for %s: %s" % (side, exc))

                continue



            clav_c = "clavicle_%s" % side

            ik_start_c = clav_c if (include_clavicle_chain and target_map.get(clav_c) and safe_cmds_exists(target_map.get(clav_c))) else start_c

            handle = self._create_ik_handle_safe("ALPHA_SourceGuidedArm_%s_IKH" % side, target_map.get(ik_start_c), target_map.get(end_c))

            if handle and ik_start_c != start_c:

                self.log("HumanIK Option1 v2.1.8: %s IK starts at %s -> %s to include clavicle/shoulder motion." % (side, ik_start_c, end_c))

            if not handle:

                continue

            temp_nodes.append(handle)

            ik_handles.append(handle)

            try:

                constraints.append(cmds.pointConstraint(end_locs[label], handle, maintainOffset=False)[0])

            except Exception as exc:

                self.log("HumanIK source-guided arm IK WARNING: could not pointConstraint %s: %s" % (label, exc))

            try:

                constraints.append(cmds.poleVectorConstraint(pole_locs[label], handle)[0])

            except Exception as exc:

                self.log("HumanIK source-guided arm IK WARNING: could not poleVectorConstraint %s: %s" % (label, exc))





                                                                                                    

                                                                                                

        hand_aim_constraints = 0

        if analytic_aim_solver and hand_contact_aim:

            for side, _start_c, _mid_c, end_c in sides:

                label = "src_guided_arm_%s" % side

                other_side = "r" if side == "l" else "l"

                other_label = "src_guided_arm_%s" % other_side

                hand_node = target_map.get(end_c)

                finger_tip = _finger_tip_for_side_contact(side)

                if not (hand_node and safe_cmds_exists(hand_node) and finger_tip and safe_cmds_exists(finger_tip) and end_locs.get(other_label)):

                    continue

                try:

                    cmds.currentTime(frames[0], edit=True, update=True)

                    hand_aim = _local_axis_from_joint_to_world_point(hand_node, get_world_position(finger_tip))

                    hand_up = _safe_local_up_vector(hand_aim, _local_axis_from_joint_to_world_point(hand_node, get_world_position(pole_locs[label])))

                    constraints.append(cmds.aimConstraint(end_locs[other_label], hand_node, maintainOffset=hand_aim_maintain_offset, aimVector=hand_aim, upVector=hand_up, worldUpType="object", worldUpObject=pole_locs[label])[0])

                    hand_aim_constraints += 1

                    self.log("HumanIK Option1 v2.21.0 source-palm-frame contact aim: %s handAim=%s handUp=%s maintainOffset=%s target=other_hand. Wrist position remains analytic." % (side, _fmt3(hand_aim), _fmt3(hand_up), str(hand_aim_maintain_offset)))

                except Exception as exc:

                    self.log("HumanIK hand-contact aim WARNING: could not create hand aim for %s: %s" % (side, exc))



        for line in debug_samples[:12]:

            self.log("ALPHA_ARM_DIAG SAMPLE: %s" % line)

        for line in pair_debug_samples[:8]:

            self.log("ALPHA_ARM_DIAG PAIR: %s" % line)

        self.log(

            "HumanIK Option1 v2.29.0 user-calibrated-clasp hand-guard arm solver: corrections=%d pair_frames=%d pair_total_pull=%.3f pair_max_pull=%.3f pair_max_src_dist=%.3f side_corrections=%d thigh_clearance_corrections=%d max_thigh_push=%.3f max_wrist_delta=%.3f max_reach_clamp=%.3f constraints=%d ik_handles=%d hand_aim_constraints=%d analytic_aim_solver=%s. Baking arm chains only..."

            % (correction_count, pair_convergence_frames, pair_convergence_total_pull, pair_convergence_max_pull, pair_convergence_max_source_distance, side_corrections, thigh_clearance_corrections, max_thigh_clearance_push, max_wrist_delta, max_reach_clamp, len(constraints), len(ik_handles), hand_aim_constraints if 'hand_aim_constraints' in locals() else 0, str(analytic_aim_solver))

        )



        bake_stats = self._manual_sample_solved_joint_animation(

            arm_bake_nodes,

            frames,

            translate_key_nodes=set(),

            temp_nodes=constraints + temp_nodes,

            label="humanik_source_guided_arm_ik",

        )





                                                       

                                                                                               

                                                                                                

                                                                                             

                                                                                               

        source_palm_delta_keys = 0

        if analytic_aim_solver and source_palm_delta:

            def _short_delta_clamped(_cur, _rest, _clamp):

                _d = float(_cur) - float(_rest)

                while _d > 180.0:

                    _d -= 360.0

                while _d < -180.0:

                    _d += 360.0

                if _d > _clamp:

                    _d = _clamp

                elif _d < -_clamp:

                    _d = -_clamp

                return _d

            for frame in frames:

                try:

                    cmds.currentTime(frame, edit=True, update=True)

                except Exception:

                    pass

                for _side, _start_c, _mid_c, _end_c in sides:

                    _src_hand = source_map.get(_end_c)

                    _tgt_hand = target_map.get(_end_c)

                    _src_rest = source_rest_local_rotations.get(_end_c)

                    _tgt_rest = target_rest_local_rotations.get(_end_c)

                    if not (_src_hand and _tgt_hand and _src_rest is not None and _tgt_rest is not None and safe_cmds_exists(_src_hand) and safe_cmds_exists(_tgt_hand)):

                        continue

                    try:

                        _src_cur = self._get_vec(_src_hand, ROTATE_ATTRS)

                        _out = []

                        for _i in range(3):

                            _d = _short_delta_clamped(_src_cur[_i], _src_rest[_i], source_palm_delta_clamp)

                            _out.append(float(_tgt_rest[_i]) + _d * source_palm_delta_blend)

                        self._set_vec(_tgt_hand, ROTATE_ATTRS, tuple(_out))

                        for _attr in ROTATE_ATTRS:

                            cmds.setKeyframe(_tgt_hand, attribute=_attr, time=frame)

                            source_palm_delta_keys += 1

                    except Exception:

                        pass

            self.log("HumanIK Option1 v2.29.0 user-calibrated clasp transfer: enabled=%s blend=%.2f clamp=%.1f keys=%d. Wrist position remains analytic; palm/hand local rotation follows calibrated source delta." % (str(source_palm_delta), source_palm_delta_blend, source_palm_delta_clamp, source_palm_delta_keys))



                                                                                            

                                                                                                 

                                                                                              

        hand_aim_soften_keys = 0

        if analytic_aim_solver and hand_contact_aim and hand_contact_aim_blend < 0.999:

            def _short_euler_blend(_base, _target, _blend):

                _out = []

                for _b, _t in zip(_base, _target):

                    _d = float(_t) - float(_b)

                    while _d > 180.0:

                        _d -= 360.0

                    while _d < -180.0:

                        _d += 360.0

                    _out.append(float(_b) + _d * _blend)

                return tuple(_out)

            for frame in frames:

                try:

                    cmds.currentTime(frame, edit=True, update=False)

                except Exception:

                    pass

                for _side, _start_c, _mid_c, _end_c in sides:

                    _hand = target_map.get(_end_c)

                    _rest = target_rest_local_rotations.get(_end_c)

                    if _hand and _rest is not None and safe_cmds_exists(_hand):

                        try:

                            _cur = self._get_vec(_hand, ROTATE_ATTRS)

                            _out = _short_euler_blend(_rest, _cur, hand_contact_aim_blend)

                            self._set_vec(_hand, ROTATE_ATTRS, _out)

                            for attr in ROTATE_ATTRS:

                                cmds.setKeyframe(_hand, attribute=attr, time=frame)

                                hand_aim_soften_keys += 1

                        except Exception:

                            pass

            self.log("HumanIK Option1 v2.29.0 user-calibrated guarded palm-contact aim: blend=%.2f keys=%d" % (hand_contact_aim_blend, hand_aim_soften_keys))



                                                                                                       

                                                                                                   

                                                                                                               

        reference_palm_pose_keys = 0

        if analytic_aim_solver and reference_clasp_palm_pose:

            def _short_euler_offset(_base, _offset, _blend):

                _out = []

                for _b, _o in zip(_base, _offset):

                    _out.append(float(_b) + float(_o) * float(_blend))

                return tuple(_out)

            for frame in frames:

                try:

                    cmds.currentTime(frame, edit=True, update=False)

                except Exception:

                    pass

                for _side, _start_c, _mid_c, _end_c in sides:

                    _hand = target_map.get(_end_c)

                    _rest = target_rest_local_rotations.get(_end_c)

                    if not (_hand and _rest is not None and safe_cmds_exists(_hand)):

                        continue

                    try:

                        _offset = reference_clasp_left_hand_offset if _side == "l" else reference_clasp_right_hand_offset

                        _out = _short_euler_offset(_rest, _offset, reference_clasp_palm_pose_blend)

                        self._set_vec(_hand, ROTATE_ATTRS, _out)

                        for attr in ROTATE_ATTRS:

                            cmds.setKeyframe(_hand, attribute=attr, time=frame)

                            reference_palm_pose_keys += 1

                    except Exception:

                        pass

            self.log("HumanIK Option1 v2.29.0 user-calibrated clasp palm pose: blend=%.2f leftOffset=%s rightOffset=%s keys=%d" % (reference_clasp_palm_pose_blend, _fmt3(reference_clasp_left_hand_offset), _fmt3(reference_clasp_right_hand_offset), reference_palm_pose_keys))



                                                                                                      

                                                                                         

                                                                                            

                                                                                    

        def _user_template_cache_path(_template_path):

            try:

                _base, _ext = os.path.splitext(_template_path or "")

                if not _base:

                    return ""

                return _base + "_RawSolveCache.json"

            except Exception:

                return ""



        def _collect_user_template_target_nodes():

            _all_target_joints = get_all_joints()

            _by_short = {short_name(_j).lower(): _j for _j in _all_target_joints}

            _wanted = set((

                "clavicle_l", "upperarm_l", "lowerarm_l", "hand_l",

                "clavicle_r", "upperarm_r", "lowerarm_r", "hand_r",

            ))

            for _hand_short in ("hand_l", "hand_r"):

                _h = _by_short.get(_hand_short)

                if not (_h and safe_cmds_exists(_h)):

                    continue

                try:

                    _desc = cmds.listRelatives(_h, allDescendents=True, type="joint", fullPath=True) or []

                except Exception:

                    _desc = []

                for _n in _desc:

                    _sn = short_name(_n).lower()

                    if any(_tok in _sn for _tok in ("thumb", "index", "middle", "ring", "pinky", "metacarpal")):

                        _wanted.add(_sn)

            _selected = []

            for _sn in sorted(_wanted):

                _node = _by_short.get(_sn)

                if _node and safe_cmds_exists(_node):

                    _selected.append((_node, _sn))

            return _selected



        raw_cache_written = False

        raw_cache_path = _user_template_cache_path(user_clasp_template_path)

        if user_clasp_template_save_raw_cache and raw_cache_path:

            try:

                import json as _json

                _cache_nodes = _collect_user_template_target_nodes()

                _frame_cache = {}

                _source_driver_frames = {}



                def _make_source_driver_signature_for_current_frame():

                    try:

                        _basis = _basis_from_map(source_map)

                        _locals = {}

                        _rotations = {}

                        for _canon in ("clavicle_l", "upperarm_l", "lowerarm_l", "hand_l", "clavicle_r", "upperarm_r", "lowerarm_r", "hand_r"):

                            _node = source_map.get(_canon)

                            if _node and safe_cmds_exists(_node):

                                _locals[_canon] = list(_maybe_invert_forward(_to_local(get_world_position(_node), _basis)))

                                try:

                                    _r = cmds.getAttr(_node + ".rotate")[0]

                                    _rotations[_canon] = [float(_r[0]), float(_r[1]), float(_r[2])]

                                except Exception:

                                    pass

                        if "hand_l" not in _locals or "hand_r" not in _locals:

                            return None

                        _pl = _locals["hand_l"]

                        _pr = _locals["hand_r"]

                        _center = [(_pl[0] + _pr[0]) * 0.5, (_pl[1] + _pr[1]) * 0.5, (_pl[2] + _pr[2]) * 0.5]

                        _pair = self._v_len(self._v_sub(tuple(_pl), tuple(_pr)))

                        return {"locals": _locals, "rotations": _rotations, "metrics": {"center": _center, "pair_distance": float(_pair)}}

                    except Exception:

                        return None



                for frame in frames:

                    try:

                        cmds.currentTime(frame, edit=True, update=True)

                    except Exception:

                        pass

                    _frame_key = ("%.3f" % float(frame)).rstrip("0").rstrip(".")

                    _frame_cache[_frame_key] = {}

                    for _node, _sn in _cache_nodes:

                        try:

                            _r = cmds.getAttr(_node + ".rotate")[0]

                            _frame_cache[_frame_key][_sn] = [float(_r[0]), float(_r[1]), float(_r[2])]

                        except Exception:

                            pass

                    _driver_sig = _make_source_driver_signature_for_current_frame()

                    if isinstance(_driver_sig, dict):

                        _source_driver_frames[_frame_key] = _driver_sig

                _cache_data = {

                    "version": "2.29.0",

                    "type": "ALPHA_PreUserTemplateRawSolveCache",

                    "mode": "target_local_rotations_before_user_delta_and_source_pose_driver",

                    "frame_range": [float(frames[0]) if frames else 0.0, float(frames[-1]) if frames else 0.0],

                    "nodes": [sn for _node, sn in _cache_nodes],

                    "frames": _frame_cache,

                    "source_driver_frames": _source_driver_frames,

                    "source_file": (lambda _p: {"path": _p, "basename": os.path.basename(_p) if _p else "", "size": int(os.path.getsize(_p)) if _p and os.path.isfile(_p) else -1})(str(getattr(self.config, "humanik_source_guided_arm_ik_current_source_file_path", "") or "")),

                }

                try:

                    ensure_dir(os.path.dirname(raw_cache_path))

                except Exception:

                    pass

                with open(raw_cache_path, "w") as _fh:

                    _json.dump(_cache_data, _fh, indent=2, sort_keys=True)

                raw_cache_written = True

                self.log("HumanIK Option1 v2.29.0 pre-user-template raw solve cache: written=True frames=%d nodes=%d sourceDriverFrames=%d path=%s" % (len(_frame_cache), len(_cache_nodes), len(_source_driver_frames), raw_cache_path))

            except Exception as _cache_exc:

                self.log("HumanIK Option1 v2.29.0 pre-user-template raw solve cache WARNING: %s" % _cache_exc)



                                                                                         

                                                                                        

                                                                                             

                                                                                                     

        user_clasp_template_keys = 0

        user_clasp_template_loaded = False

        user_clasp_template_nodes = 0

        user_clasp_template_close_frames = 0

        user_clasp_template_rejected_frames = 0

        user_clasp_template_weight_sum = 0.0

        user_clasp_template_max_weight = 0.0

        user_clasp_template_mode = "none"

        if user_clasp_template_enabled and user_clasp_template_path:

            try:

                import json as _json

                if os.path.isfile(user_clasp_template_path):

                    with open(user_clasp_template_path, "r") as _fh:

                        _tpl = _json.load(_fh)

                    _rotations_abs = _tpl.get("rotations", {}) if isinstance(_tpl, dict) else {}

                    _rotations_delta = _tpl.get("rotation_deltas", {}) if isinstance(_tpl, dict) else {}

                    _driver = _tpl.get("source_driver_signature", {}) if isinstance(_tpl, dict) else {}

                    _tpl_mode = str(_tpl.get("mode", "") if isinstance(_tpl, dict) else "")

                    _use_delta = bool(user_clasp_template_use_delta and isinstance(_rotations_delta, dict) and _rotations_delta)

                    _rotations = _rotations_delta if _use_delta else _rotations_abs

                    user_clasp_template_mode = "delta" if _use_delta else "absolute"

                    if user_clasp_template_pose_match and user_clasp_template_require_driver and not isinstance(_driver, dict):

                        self.log("HumanIK Option1 v2.29.0 user clasp template ignored: missing source_driver_signature. Re-capture with button 4 in v2.29.0.")

                        _rotations = {}

                    if isinstance(_rotations, dict) and _rotations:

                        _all_target_joints = get_all_joints()

                        _by_short = {}

                        for _j in _all_target_joints:

                            _by_short[short_name(_j).lower()] = _j

                        _selected = []

                        for _short, _rot in _rotations.items():

                            _short_l = str(_short).lower()

                            _is_hand = _short_l in ("hand_l", "hand_r")

                            _is_clav = _short_l in ("clavicle_l", "clavicle_r")

                            _is_arm_chain = _short_l in (

                                "clavicle_l", "upperarm_l", "lowerarm_l", "hand_l",

                                "clavicle_r", "upperarm_r", "lowerarm_r", "hand_r",

                            )

                            _finger_parts = _short_l.split("_")

                            _is_main_finger = (

                                len(_finger_parts) == 3

                                and _finger_parts[0] in ("thumb", "index", "middle", "ring", "pinky")

                                and _finger_parts[1] in ("01", "02", "03")

                                and _finger_parts[2] in ("l", "r")

                            )

                            _is_finger = any(_tok in _short_l for _tok in ("thumb", "index", "middle", "ring", "pinky", "metacarpal"))

                                                                                                             

                                                                                                       

                            _is_corrective = _is_finger and (not _is_main_finger)

                            if _is_arm_chain and not user_clasp_template_apply_arm_chain:

                                continue

                            if _is_hand and not user_clasp_template_apply_hands:

                                continue

                            if _is_clav and not user_clasp_template_apply_clavicles:

                                continue

                            if _is_corrective and not user_clasp_template_apply_correctives:

                                continue

                            if _is_finger and not user_clasp_template_apply_fingers:

                                continue

                            if (not _is_arm_chain) and (not _is_finger):

                                continue

                            _node = _by_short.get(_short_l)

                            if _node and safe_cmds_exists(_node) and isinstance(_rot, (list, tuple)) and len(_rot) >= 3:

                                _selected.append((_node, (float(_rot[0]), float(_rot[1]), float(_rot[2])), _short_l))

                        if _selected:

                            _arm_chain_names = set((

                                "clavicle_l", "upperarm_l", "lowerarm_l", "hand_l",

                                "clavicle_r", "upperarm_r", "lowerarm_r", "hand_r",

                            ))

                            _selected_arm_chain = sum(1 for _node, _rot, _short_l in _selected if _short_l in _arm_chain_names)

                            if user_clasp_template_apply_arm_chain and _selected_arm_chain < 8:

                                self.log("HumanIK Option1 v2.29.0 user clasp template WARNING: template has only %d/8 full-arm chain rotations. Re-capture with button 4 in v2.29.0." % _selected_arm_chain)



                            _driver_locals = _driver.get("locals", {}) if isinstance(_driver, dict) else {}

                            _driver_rotations = _driver.get("rotations", {}) if isinstance(_driver, dict) else {}

                            _driver_metrics = _driver.get("metrics", {}) if isinstance(_driver, dict) else {}

                            _has_driver = isinstance(_driver_locals, dict) and all(k in _driver_locals for k in ("hand_l", "hand_r"))

                            _has_rotation_driver = isinstance(_driver_rotations, dict) and any(k in _driver_rotations for k in ("hand_l", "hand_r", "lowerarm_l", "lowerarm_r"))

                            if user_clasp_template_pose_match and not _has_driver:

                                self.log("HumanIK Option1 v2.29.0 user clasp template WARNING: source driver signature missing/incomplete; pose-match will reject all frames." if user_clasp_template_require_driver else "HumanIK Option1 v2.29.0 user clasp template WARNING: source driver signature missing; falling back to pair-distance only.")



                            def _frame_key(_frame):

                                return ("%.3f" % float(_frame)).rstrip("0").rstrip(".")



                            def _as3(_v):

                                try:

                                    return (float(_v[0]), float(_v[1]), float(_v[2]))

                                except Exception:

                                    return None



                            def _smooth_inv(_x):

                                _x = max(0.0, min(1.0, float(_x)))

                                return 1.0 - (_x * _x * (3.0 - 2.0 * _x))



                            def _source_pose_match_weight():

                                if not user_clasp_template_pose_match:

                                    return 1.0

                                _src_lh = source_map.get("hand_l")

                                _src_rh = source_map.get("hand_r")

                                if not (_src_lh and _src_rh and safe_cmds_exists(_src_lh) and safe_cmds_exists(_src_rh)):

                                    return 0.0 if user_clasp_template_require_driver else 1.0

                                try:

                                    _src_basis_now = _basis_from_map(source_map)

                                    _lh_l = _maybe_invert_forward(_to_local(get_world_position(_src_lh), _src_basis_now))

                                    _rh_l = _maybe_invert_forward(_to_local(get_world_position(_src_rh), _src_basis_now))

                                    _pair_now = _local_pair_distance(_lh_l, _rh_l)

                                    if not _has_driver:

                                        return 0.0 if user_clasp_template_require_driver else (1.0 if _pair_now <= pair_source_threshold else 0.0)

                                    _lh_ref = _as3(_driver_locals.get("hand_l"))

                                    _rh_ref = _as3(_driver_locals.get("hand_r"))

                                    if not (_lh_ref and _rh_ref):

                                        return 0.0

                                    _center_now = self._v_mul(self._v_add(_lh_l, _rh_l), 0.5)

                                    _center_ref = _as3(_driver_metrics.get("center")) or self._v_mul(self._v_add(_lh_ref, _rh_ref), 0.5)

                                    _pair_ref = float(_driver_metrics.get("pair_distance", _local_pair_distance(_lh_ref, _rh_ref)))

                                    _center_err = _safe_dist(_center_now, _center_ref)

                                    _lh_err = _safe_dist(_lh_l, _lh_ref)

                                    _rh_err = _safe_dist(_rh_l, _rh_ref)

                                    _pair_err = abs(_pair_now - _pair_ref)

                                    _score = max(

                                        _center_err / user_clasp_template_center_threshold,

                                        _lh_err / user_clasp_template_wrist_threshold,

                                        _rh_err / user_clasp_template_wrist_threshold,

                                        _pair_err / user_clasp_template_pair_threshold,

                                    )

                                    for _side in ("l", "r"):

                                        _src_el = source_map.get("lowerarm_" + _side)

                                        _ref_el = _as3(_driver_locals.get("lowerarm_" + _side))

                                        if _src_el and _ref_el and safe_cmds_exists(_src_el):

                                            _el_l = _maybe_invert_forward(_to_local(get_world_position(_src_el), _src_basis_now))

                                            _score = max(_score, _safe_dist(_el_l, _ref_el) / user_clasp_template_elbow_threshold)

                                                                                                              

                                                                                                                 

                                                                                          

                                    if _has_rotation_driver:

                                        def _short_angle_abs(_a, _b):

                                            _d = float(_a) - float(_b)

                                            while _d > 180.0:

                                                _d -= 360.0

                                            while _d < -180.0:

                                                _d += 360.0

                                            return abs(_d)

                                        _rot_errs = []

                                        for _canon in ("clavicle_l", "upperarm_l", "lowerarm_l", "hand_l", "clavicle_r", "upperarm_r", "lowerarm_r", "hand_r"):

                                            _src_node = source_map.get(_canon)

                                            _ref_rot = _as3(_driver_rotations.get(_canon))

                                            if _src_node and _ref_rot and safe_cmds_exists(_src_node):

                                                try:

                                                    _cur_rot = cmds.getAttr(_src_node + ".rotate")[0]

                                                    _rot_errs.append(max(_short_angle_abs(_cur_rot[0], _ref_rot[0]), _short_angle_abs(_cur_rot[1], _ref_rot[1]), _short_angle_abs(_cur_rot[2], _ref_rot[2])))

                                                except Exception:

                                                    pass

                                        if _rot_errs:

                                            _score = max(_score, (sum(_rot_errs) / float(len(_rot_errs))) / user_clasp_template_rotation_threshold)

                                    elif user_clasp_template_require_driver:

                                        return 0.0

                                    if _score >= 1.0:

                                        return 0.0

                                    return _smooth_inv(_score)

                                except Exception:

                                    return 0.0 if user_clasp_template_require_driver else 1.0



                            for frame in frames:

                                try:

                                    cmds.currentTime(frame, edit=True, update=True)

                                except Exception:

                                    pass

                                _match_weight = _source_pose_match_weight()

                                if _match_weight <= 0.001:

                                    user_clasp_template_rejected_frames += 1

                                    continue

                                _frame_blend = user_clasp_template_blend * _match_weight

                                user_clasp_template_close_frames += 1

                                user_clasp_template_weight_sum += _match_weight

                                user_clasp_template_max_weight = max(user_clasp_template_max_weight, _match_weight)

                                for _node, _rot, _short_l in _selected:

                                    try:

                                        _cur = self._get_vec(_node, ROTATE_ATTRS)

                                        def _sd(_target, _current):

                                            _d = float(_target) - float(_current)

                                            while _d > 180.0:

                                                _d -= 360.0

                                            while _d < -180.0:

                                                _d += 360.0

                                            return _d

                                        if _use_delta:

                                            _out = (

                                                _cur[0] + float(_rot[0]) * _frame_blend,

                                                _cur[1] + float(_rot[1]) * _frame_blend,

                                                _cur[2] + float(_rot[2]) * _frame_blend,

                                            )

                                        else:

                                            _out = (

                                                _cur[0] + _sd(_rot[0], _cur[0]) * _frame_blend,

                                                _cur[1] + _sd(_rot[1], _cur[1]) * _frame_blend,

                                                _cur[2] + _sd(_rot[2], _cur[2]) * _frame_blend,

                                            )

                                        self._set_vec(_node, ROTATE_ATTRS, _out)

                                        for _attr in ROTATE_ATTRS:

                                            cmds.setKeyframe(_node, attribute=_attr, time=frame)

                                            user_clasp_template_keys += 1

                                    except Exception:

                                        pass

                            user_clasp_template_loaded = True

                            user_clasp_template_nodes = len(_selected)

                            try:

                                self.log("HumanIK Option1 v2.29.0 source-pose delta user template selection: nodes=%d armChain=%d/8 hands=%d fingersAndCorrectives=%d mode=%s hasDriver=%s" % (

                                    len(_selected),

                                    sum(1 for _node, _rot, _short_l in _selected if _short_l in _arm_chain_names),

                                    sum(1 for _node, _rot, _short_l in _selected if _short_l in ("hand_l", "hand_r")),

                                    sum(1 for _node, _rot, _short_l in _selected if any(_tok in _short_l for _tok in ("thumb", "index", "middle", "ring", "pinky", "metacarpal"))),

                                    user_clasp_template_mode,

                                    str(_has_driver),

                                ))

                                self.log("HumanIK Option1 v2.29.0 strict pose-match thresholds: center=%.2f wrist=%.2f elbow=%.2f pair=%.2f rotation=%.2f hasRotationDriver=%s sourceFileLock=%s" % (user_clasp_template_center_threshold, user_clasp_template_wrist_threshold, user_clasp_template_elbow_threshold, user_clasp_template_pair_threshold, user_clasp_template_rotation_threshold, str(_has_rotation_driver), str(user_clasp_template_lock_to_source_file)))

                            except Exception:

                                pass

                    else:

                        self.log("HumanIK Option1 v2.29.0 user clasp template ignored: no rotations/deltas in %s" % user_clasp_template_path)

                else:

                    self.log("HumanIK Option1 v2.29.0 user clasp template not found: %s" % user_clasp_template_path)

            except Exception as _tpl_exc:

                self.log("HumanIK Option1 v2.29.0 user clasp template WARNING: %s" % _tpl_exc)

        if user_clasp_template_enabled:

            _avg_w = (user_clasp_template_weight_sum / float(user_clasp_template_close_frames)) if user_clasp_template_close_frames else 0.0

            self.log("HumanIK Option1 v2.29.0 user-calibrated source-pose delta template: loaded=%s nodes=%d appliedFrames=%d rejectedFrames=%d avgWeight=%.3f maxWeight=%.3f blend=%.2f mode=%s keys=%d rawCacheWritten=%s path=%s" % (str(user_clasp_template_loaded), user_clasp_template_nodes, user_clasp_template_close_frames, user_clasp_template_rejected_frames, _avg_w, user_clasp_template_max_weight, user_clasp_template_blend, user_clasp_template_mode, user_clasp_template_keys, str(raw_cache_written), user_clasp_template_path or "<empty>"))



                                                                                                         

                                                                                                           

                                                                                                      

                                                                                               

        source_finger_transfer_keys = 0

        source_finger_transfer_pairs = []

        corrective_finger_stabilize_keys = 0

        if bool(getattr(self.config, "humanik_source_guided_arm_ik_transfer_source_fingers", True)) and not user_clasp_template_loaded:

            def _finger_desc_by_short(_hand_node):

                out = {}

                if not (_hand_node and safe_cmds_exists(_hand_node)):

                    return out

                try:

                    desc = cmds.listRelatives(_hand_node, allDescendents=True, type="joint", fullPath=True) or []

                except Exception:

                    desc = []

                for n in desc:

                    out[short_name(n).lower()] = n

                return out



            def _src_finger_name(_side, _finger, _idx):

                prefix = "l_" if _side == "l" else "r_"

                return prefix + _finger + str(_idx)



            def _tgt_finger_name(_side, _finger, _idx):

                return _finger + "_%02d_" % int(_idx) + _side



            fingers = ["thumb", "index", "middle", "ring", "pinky"]

            blend = max(0.0, min(1.0, float(getattr(self.config, "humanik_source_guided_arm_ik_source_finger_rotation_blend", 0.24) or 0.24)))

            delta_clamp = max(1.0, float(getattr(self.config, "humanik_source_guided_arm_ik_source_finger_delta_clamp_degrees", 16.0) or 16.0))

            finger_axis_mode = str(getattr(self.config, "humanik_source_guided_arm_ik_finger_axis_mode", "bend_only") or "bend_only").lower()

            bend_axis_blend = max(0.0, min(1.0, float(getattr(self.config, "humanik_source_guided_arm_ik_finger_bend_axis_blend", 0.42) or 0.42)))

            splay_axis_blend = max(0.0, min(1.0, float(getattr(self.config, "humanik_source_guided_arm_ik_finger_splay_axis_blend", 0.03) or 0.03)))

            curl_boost = float(getattr(self.config, "humanik_source_guided_arm_ik_reference_clasp_finger_curl_boost_degrees", 8.0) or 0.0)

            target_main_nodes = set()

            target_corrective_nodes = []

            target_rest_rot = {}

            try:

                cmds.currentTime(frames[0], edit=True, update=True)

            except Exception:

                pass

            for _side in ("l", "r"):

                _src_hand = source_map.get("hand_%s" % _side)

                _tgt_hand = target_map.get("hand_%s" % _side)

                _src_desc = _finger_desc_by_short(_src_hand)

                _tgt_desc = _finger_desc_by_short(_tgt_hand)

                for _finger in fingers:

                    for _idx in (1, 2, 3):

                        _src = _src_desc.get(_src_finger_name(_side, _finger, _idx))

                        _tgt = _tgt_desc.get(_tgt_finger_name(_side, _finger, _idx))

                        if _src and _tgt and safe_cmds_exists(_src) and safe_cmds_exists(_tgt):

                            source_finger_transfer_pairs.append((_src, _tgt, "%s_%s_%d" % (_side, _finger, _idx)))

                            target_main_nodes.add(_tgt)

                            try:

                                target_rest_rot[_tgt] = self._get_vec(_tgt, ROTATE_ATTRS)

                            except Exception:

                                target_rest_rot[_tgt] = (0.0, 0.0, 0.0)

                                                                                                         

                                                                                                        

                                                                    

                if bool(getattr(self.config, "humanik_source_guided_arm_ik_stabilize_target_finger_correctives", False)):

                    for _name, _node in _tgt_desc.items():

                        if _node in target_main_nodes:

                            continue

                        if any(tok in _name for tok in ("thumb", "index", "middle", "ring", "pinky", "metacarpal")):

                            if _node not in target_corrective_nodes:

                                target_corrective_nodes.append(_node)

                                try:

                                    target_rest_rot[_node] = self._get_vec(_node, ROTATE_ATTRS)

                                except Exception:

                                    target_rest_rot[_node] = (0.0, 0.0, 0.0)



                                                                         

            all_finger_nodes = list(dict.fromkeys([_tgt for _src, _tgt, _name in source_finger_transfer_pairs] + target_corrective_nodes))

            try:

                if all_finger_nodes:

                    cmds.cutKey(all_finger_nodes, time=(frames[0], frames[-1]), attribute=ROTATE_ATTRS, option="keys")

            except Exception:

                pass



            for frame in frames:

                cmds.currentTime(frame, edit=True, update=True)

                for _src, _tgt, _name in source_finger_transfer_pairs:

                    try:

                        sr = self._get_vec(_src, ROTATE_ATTRS)

                        tr = target_rest_rot.get(_tgt, (0.0, 0.0, 0.0))

                                                                                                      

                                                                                                            

                                                                                                          

                                                                                                   

                                                                                       

                        def _short_delta(a, b):

                            d = float(a) - float(b)

                            while d > 180.0:

                                d -= 360.0

                            while d < -180.0:

                                d += 360.0

                            if d > delta_clamp:

                                d = delta_clamp

                            elif d < -delta_clamp:

                                d = -delta_clamp

                            return d

                        if reference_clasp_finger_template and finger_axis_mode == "bend_only" and ("thumb" not in _name.lower()):

                                                                                                        

                                                                                                        

                                                                                                         

                                                                                            

                            _parts = _name.split("_")

                            try:

                                _idx = int(_parts[-1])

                            except Exception:

                                _idx = 1

                            _template_curl = {1: reference_clasp_finger_mcp_curl, 2: reference_clasp_finger_pip_curl, 3: reference_clasp_finger_dip_curl}.get(_idx, reference_clasp_finger_pip_curl * 0.5)

                            _source_curl = _short_delta(sr[2], tr[2]) * max(0.0, min(0.22, bend_axis_blend * 0.25))

                            out = (

                                tr[0] + _short_delta(sr[0], tr[0]) * 0.01,

                                tr[1] + _short_delta(sr[1], tr[1]) * 0.01,

                                tr[2] + (_template_curl + _source_curl) * reference_clasp_finger_template_blend,

                            )

                        elif finger_axis_mode == "bend_only" and ("thumb" not in _name.lower()):

                                                                                                       

                            _parts = _name.split("_")

                            try:

                                _idx = int(_parts[-1])

                            except Exception:

                                _idx = 1

                            _curl_weight = {1: 1.00, 2: 0.75, 3: 0.35}.get(_idx, 0.50)

                            out = (

                                tr[0] + _short_delta(sr[0], tr[0]) * splay_axis_blend,

                                tr[1] + _short_delta(sr[1], tr[1]) * splay_axis_blend,

                                tr[2] + _short_delta(sr[2], tr[2]) * bend_axis_blend + curl_boost * _curl_weight,

                            )

                        else:

                            _thumb_blend = reference_clasp_thumb_blend if (reference_clasp_finger_template and "thumb" in _name.lower()) else (blend * 0.55 if "thumb" in _name.lower() else blend)

                            out = (

                                tr[0] + _short_delta(sr[0], tr[0]) * _thumb_blend,

                                tr[1] + _short_delta(sr[1], tr[1]) * _thumb_blend,

                                tr[2] + _short_delta(sr[2], tr[2]) * _thumb_blend,

                            )

                        self._set_vec(_tgt, ROTATE_ATTRS, out)

                        for attr in ROTATE_ATTRS:

                            cmds.setKeyframe(_tgt, attribute=attr, time=frame)

                            source_finger_transfer_keys += 1

                    except Exception:

                        pass

                if bool(getattr(self.config, "humanik_source_guided_arm_ik_stabilize_target_finger_correctives", False)):

                    for _node in target_corrective_nodes:

                        try:

                            rr = target_rest_rot.get(_node, self._get_vec(_node, ROTATE_ATTRS))

                            self._set_vec(_node, ROTATE_ATTRS, rr)

                            for attr in ROTATE_ATTRS:

                                cmds.setKeyframe(_node, attribute=attr, time=frame)

                                corrective_finger_stabilize_keys += 1

                        except Exception:

                            pass

            if source_finger_transfer_pairs or target_corrective_nodes:

                self.log("HumanIK Option1 v2.29.0 user-calibrated-template bend-axis finger transfer: main_pairs=%d blend=%.2f axisMode=%s bendBlend=%.2f splayBlend=%.2f curlBoost=%.1f delta_clamp=%.1f refTemplate=%s refBlend=%.2f main_keys=%d corrective_nodes=%d corrective_keys=%d preview=%s" % (len(source_finger_transfer_pairs), blend, finger_axis_mode, bend_axis_blend, splay_axis_blend, curl_boost, delta_clamp, str(reference_clasp_finger_template), reference_clasp_finger_template_blend, source_finger_transfer_keys, len(target_corrective_nodes), corrective_finger_stabilize_keys, ",".join(_name for _src, _tgt, _name in source_finger_transfer_pairs[:20])))

        elif not user_clasp_template_loaded:

            self.log("HumanIK Option1 v2.29.0 generic source-finger transfer skipped: OFF by default. Main fingers/corrective helpers are untouched unless a strict user template frame matches.")



        if arm_diag_enabled and arm_diag_final:

            try:

                def _target_joint_by_short(names):

                    _names = [str(n).lower() for n in names]

                    try:

                        _joints = get_all_joints()

                    except Exception:

                        _joints = target_joints_to_bake

                    for _j in _joints:

                        _sn = short_name(_j).lower()

                        if _sn in _names:

                            return _j

                    return None

                def _finger_tip_for_side(_side):

                    suffix = "_" + _side

                    return _target_joint_by_short([

                        "middle_03" + suffix, "index_03" + suffix, "ring_03" + suffix,

                        "middle_02" + suffix, "index_02" + suffix, "ring_02" + suffix

                    ])

                def _diag_rot(_node):

                    try:

                        return _fmt3(cmds.getAttr(_node + ".rotate")[0])

                    except Exception:

                        return "na"

                def _diag_parent_name(_node):

                    try:

                        _p = cmds.listRelatives(_node, parent=True, fullPath=True) or []

                        return short_name(_p[0]) if _p else "none"

                    except Exception:

                        return "na"

                def _diag_finger_nodes_under(_root):

                    if not _root or not safe_cmds_exists(_root):

                        return []

                    try:

                        _desc = cmds.listRelatives(_root, allDescendents=True, type="joint", fullPath=True) or []

                    except Exception:

                        _desc = []

                    _tokens = ("thumb", "index", "middle", "ring", "pinky", "little", "finger", "metacarpal")

                    _out = []

                    for _n in _desc:

                        _sn = short_name(_n).lower()

                        if any(_t in _sn for _t in _tokens):

                            _out.append(_n)

                    return list(dict.fromkeys(_out))

                def _diag_finger_group(_name):

                    _n = _name.lower()

                    for _g in ("thumb", "index", "middle", "ring", "pinky", "little"):

                        if _g in _n:

                            return "pinky" if _g == "little" else _g

                    return "other"

                def _diag_tip_by_group(_nodes):

                    _groups = {}

                    for _n in _nodes:

                        _g = _diag_finger_group(short_name(_n))

                        if _g == "other":

                            continue

                                                                                                                                                

                        _old = _groups.get(_g)

                        if _old is None or len(short_name(_n)) >= len(short_name(_old)):

                            _groups[_g] = _n

                    return _groups

                def _diag_node_local(_node, _basis, _invert=False):

                    _l = _to_local(get_world_position(_node), _basis)

                    return _maybe_invert_forward(_l) if _invert else _l

                def _diag_body_frame(_frame, _src_basis, _tgt_basis):

                    try:

                        _body_keys = ["pelvis", "spine_01", "spine_02", "spine_03", "spine_04", "spine_05", "neck_01", "head"]

                        _parts = []

                        for _c in _body_keys:

                            _sn = source_map.get(_c)

                            _tn = target_map.get(_c)

                            if _sn and _tn and safe_cmds_exists(_sn) and safe_cmds_exists(_tn):

                                _sl = _scale_local_from_source_to_target(_maybe_invert_forward(_to_local(get_world_position(_sn), _src_basis)))

                                _tl = _to_local(get_world_position(_tn), _tgt_basis)

                                _parts.append("%s:srcL=%s tgtL=%s err=%s srcRot=%s tgtRot=%s" % (_c, _fmt3(_sl), _fmt3(_tl), _fmt3(self._v_sub(_tl, _sl)), _diag_rot(_sn), _diag_rot(_tn)))

                        self.log("ALPHA_BODY_DIAG FINAL f=%.2f %s" % (_frame, " | ".join(_parts)))

                    except Exception as _exc:

                        self.log("ALPHA_BODY_DIAG FINAL WARNING f=%.2f %s" % (_frame, _exc))

                def _diag_chain_frame(_frame, _side, _src_basis, _tgt_basis):

                    try:

                        _keys = ["clavicle_" + _side, "upperarm_" + _side, "lowerarm_" + _side, "hand_" + _side]

                        _parts = []

                        _src_world = {}

                        _tgt_world = {}

                        for _c in _keys:

                            _sn = source_map.get(_c)

                            _tn = target_map.get(_c)

                            if _sn and safe_cmds_exists(_sn):

                                _src_world[_c] = get_world_position(_sn)

                            if _tn and safe_cmds_exists(_tn):

                                _tgt_world[_c] = get_world_position(_tn)

                            if _sn and _tn and safe_cmds_exists(_sn) and safe_cmds_exists(_tn):

                                _sl = _scale_local_from_source_to_target(_maybe_invert_forward(_to_local(get_world_position(_sn), _src_basis)))

                                _tl = _to_local(get_world_position(_tn), _tgt_basis)

                                _parts.append("%s:srcL=%s tgtL=%s err=%s srcRot=%s tgtRot=%s tgtParent=%s" % (_c, _fmt3(_sl), _fmt3(_tl), _fmt3(self._v_sub(_tl, _sl)), _diag_rot(_sn), _diag_rot(_tn), _diag_parent_name(_tn)))

                        def _len(_m, _a, _b):

                            return _safe_dist(_m[_a], _m[_b]) if _a in _m and _b in _m else 0.0

                        _src_lens = (_len(_src_world, _keys[0], _keys[1]), _len(_src_world, _keys[1], _keys[2]), _len(_src_world, _keys[2], _keys[3]))

                        _tgt_lens = (_len(_tgt_world, _keys[0], _keys[1]), _len(_tgt_world, _keys[1], _keys[2]), _len(_tgt_world, _keys[2], _keys[3]))

                        _src_bend = _safe_angle(self._v_sub(_src_world.get(_keys[1], (0,0,0)), _src_world.get(_keys[2], (0,0,0))), self._v_sub(_src_world.get(_keys[3], (0,0,0)), _src_world.get(_keys[2], (0,0,0)))) if all(k in _src_world for k in _keys[1:4]) else -1.0

                        _tgt_bend = _safe_angle(self._v_sub(_tgt_world.get(_keys[1], (0,0,0)), _tgt_world.get(_keys[2], (0,0,0))), self._v_sub(_tgt_world.get(_keys[3], (0,0,0)), _tgt_world.get(_keys[2], (0,0,0)))) if all(k in _tgt_world for k in _keys[1:4]) else -1.0

                        self.log("ALPHA_CHAIN_DIAG FINAL f=%.2f side=%s srcLens=(%.2f,%.2f,%.2f) tgtLens=(%.2f,%.2f,%.2f) srcBend=%.1f tgtBend=%.1f %s" % (_frame, _side, _src_lens[0], _src_lens[1], _src_lens[2], _tgt_lens[0], _tgt_lens[1], _tgt_lens[2], _src_bend, _tgt_bend, " | ".join(_parts)))

                    except Exception as _exc:

                        self.log("ALPHA_CHAIN_DIAG FINAL WARNING f=%.2f side=%s %s" % (_frame, _side, _exc))

                def _diag_fingers_frame(_frame, _side, _src_basis, _tgt_basis, _l_final, _r_final):

                    try:

                        _src_hand = source_map.get("hand_" + _side)

                        _tgt_hand = target_map.get("hand_" + _side)

                        _src_fingers = _diag_finger_nodes_under(_src_hand)

                        _tgt_fingers = _diag_finger_nodes_under(_tgt_hand)

                        _other = _r_final if _side == "l" else _l_final

                        _hand_l = _to_local(get_world_position(_tgt_hand), _tgt_basis) if _tgt_hand and safe_cmds_exists(_tgt_hand) else (0,0,0)

                        _to_other = self._v_norm(self._v_sub(_other, _hand_l), fallback=(0,0,-1))

                        _src_tips = _diag_tip_by_group(_src_fingers)

                        _tgt_tips = _diag_tip_by_group(_tgt_fingers)

                        _summary = []

                        for _g in ("thumb", "index", "middle", "ring", "pinky"):

                            _tn = _tgt_tips.get(_g)

                            _sn = _src_tips.get(_g)

                            if _tn and safe_cmds_exists(_tn):

                                _tl = _to_local(get_world_position(_tn), _tgt_basis)

                                _rel = self._v_sub(_tl, _hand_l)

                                _ang = _safe_angle(self._v_norm(_rel, fallback=(0,0,-1)), _to_other)

                                _src_txt = "src=na"

                                if _sn and safe_cmds_exists(_sn):

                                    _sl = _scale_local_from_source_to_target(_maybe_invert_forward(_to_local(get_world_position(_sn), _src_basis)))

                                    _src_txt = "src=%s err=%s" % (_fmt3(_sl), _fmt3(self._v_sub(_tl, _sl)))

                                _summary.append("%s:%s tgt=%s relHand=%s angleToOther=%.1f rot=%s" % (_g, _src_txt, _fmt3(_tl), _fmt3(_rel), _ang, _diag_rot(_tn)))

                        self.log("ALPHA_FINGER_DIAG FINAL f=%.2f side=%s sourceFingerCount=%d targetFingerCount=%d tips={%s}" % (_frame, _side, len(_src_fingers), len(_tgt_fingers), " || ".join(_summary)))

                        for _idx, _tn in enumerate(_tgt_fingers[:80]):

                            if not safe_cmds_exists(_tn):

                                continue

                            _tl = _to_local(get_world_position(_tn), _tgt_basis)

                            _rel = self._v_sub(_tl, _hand_l)

                            _dir_ang = _safe_angle(self._v_norm(_rel, fallback=(0,0,-1)), _to_other)

                            self.log("ALPHA_FINGER_JOINT_DIAG FINAL f=%.2f side=%s idx=%d name=%s parent=%s tgtL=%s relHand=%s rot=%s angleToOther=%.1f" % (_frame, _side, _idx, short_name(_tn), _diag_parent_name(_tn), _fmt3(_tl), _fmt3(_rel), _diag_rot(_tn), _dir_ang))

                    except Exception as _exc:

                        self.log("ALPHA_FINGER_DIAG FINAL WARNING f=%.2f side=%s %s" % (_frame, _side, _exc))

                for frame in sorted(sample_frames):

                    cmds.currentTime(frame, edit=True, update=True)

                    src_basis_final = _basis_from_map(source_map)

                    tgt_basis_final = _basis_from_map(target_map)

                    l_final = _to_local(get_world_position(target_map["hand_l"]), tgt_basis_final)

                    r_final = _to_local(get_world_position(target_map["hand_r"]), tgt_basis_final)

                    l_src = _scale_local_from_source_to_target(_maybe_invert_forward(_to_local(get_world_position(source_map["hand_l"]), src_basis_final)))

                    r_src = _scale_local_from_source_to_target(_maybe_invert_forward(_to_local(get_world_position(source_map["hand_r"]), src_basis_final)))

                    final_pair = _local_pair_distance(l_final, r_final)

                    src_pair = _local_pair_distance(l_src, r_src)

                    if palm_frame_diagnostics:

                        try:

                            _src_center = self._v_mul(self._v_add(l_src, r_src), 0.5)

                            _final_center = self._v_mul(self._v_add(l_final, r_final), 0.5)

                            _center_err = self._v_sub(_final_center, _src_center)

                            _l_wr_err = self._v_sub(l_final, l_src)

                            _r_wr_err = self._v_sub(r_final, r_src)

                            _asym = abs(_l_wr_err[0]) - abs(_r_wr_err[0])

                            self.log("ALPHA_CLASP_SUMMARY FINAL f=%.2f anchorFit=%s anchorSide=%s pairSrc=%.2f pairFinal=%.2f pairErr=%.2f centerErr=%s lWrErr=%s rWrErr=%s lrSideAsym=%.2f" % (frame, str(anchor_hand_fit), anchor_hand_side, src_pair, final_pair, final_pair - src_pair, _fmt3(_center_err), _fmt3(_l_wr_err), _fmt3(_r_wr_err), _asym))

                        except Exception as _exc:

                            self.log("ALPHA_CLASP_SUMMARY FINAL WARNING f=%.2f %s" % (frame, _exc))

                    _diag_body_frame(frame, src_basis_final, tgt_basis_final)

                    _diag_chain_frame(frame, "l", src_basis_final, tgt_basis_final)

                    _diag_chain_frame(frame, "r", src_basis_final, tgt_basis_final)

                    _diag_fingers_frame(frame, "l", src_basis_final, tgt_basis_final, l_final, r_final)

                    _diag_fingers_frame(frame, "r", src_basis_final, tgt_basis_final, l_final, r_final)

                    for _side, _sign in (("l", -1.0), ("r", 1.0)):

                        _hand = target_map["hand_%s" % _side]

                        _el = target_map["lowerarm_%s" % _side]

                        _up = target_map["upperarm_%s" % _side]

                        _clav = target_map.get("clavicle_%s" % _side)

                        _src_hand = source_map["hand_%s" % _side]

                        _src_el = source_map["lowerarm_%s" % _side]

                        final_wr_l = _to_local(get_world_position(_hand), tgt_basis_final)

                        final_el_l = _to_local(get_world_position(_el), tgt_basis_final)

                        final_up_l = _to_local(get_world_position(_up), tgt_basis_final)

                        src_wr_l = _scale_local_from_source_to_target(_maybe_invert_forward(_to_local(get_world_position(_src_hand), src_basis_final)))

                        src_el_l = _scale_local_from_source_to_target(_maybe_invert_forward(_to_local(get_world_position(_src_el), src_basis_final)))

                        side_ok = (final_wr_l[0] * _sign) >= 0.0

                        _other_l = r_final if _side == "l" else l_final

                        _to_other_l = self._v_norm(self._v_sub(_other_l, final_wr_l), fallback=(0.0, 0.0, -1.0))

                        _finger = _finger_tip_for_side(_side)

                        _finger_l = None

                        _finger_to_other_angle = -1.0

                        if _finger and safe_cmds_exists(_finger):

                            _finger_l = _to_local(get_world_position(_finger), tgt_basis_final)

                            _finger_dir_l = self._v_norm(self._v_sub(_finger_l, final_wr_l), fallback=(0.0, 0.0, -1.0))

                            _finger_to_other_angle = _safe_angle(_finger_dir_l, _to_other_l)

                        _bend = _safe_angle(self._v_sub(final_up_l, final_el_l), self._v_sub(final_wr_l, final_el_l))

                        _clav_rot = "na"

                        _hand_rot = "na"

                        try:

                            if _clav and safe_cmds_exists(_clav):

                                _clav_rot = _fmt3(cmds.getAttr(_clav + ".rotate")[0])

                            _hand_rot = _fmt3(cmds.getAttr(_hand + ".rotate")[0])

                        except Exception:

                            pass

                        self.log("ALPHA_ARM_DIAG FINAL f=%.2f side=%s srcElL=%s srcWrL=%s finalUpperL=%s finalElL=%s finalWrL=%s errWrLocal=%s finalElWrDist=%.2f bendDeg=%.1f sideOK=%s pairSrcDist=%.2f pairFinalDist=%.2f fingerTipL=%s fingerToOtherDeg=%.1f clavRot=%s handRot=%s" % (frame, _side, _fmt3(src_el_l), _fmt3(src_wr_l), _fmt3(final_up_l), _fmt3(final_el_l), _fmt3(final_wr_l), _fmt3(self._v_sub(final_wr_l, src_wr_l)), _safe_dist(get_world_position(_el), get_world_position(_hand)), _bend, str(side_ok), src_pair, final_pair, _fmt3(_finger_l) if _finger_l else "na", _finger_to_other_angle, _clav_rot, _hand_rot))

            except Exception as exc:

                self.log("ALPHA_ARM_DIAG FINAL WARNING: %s" % exc)



        restored_hand_keys = 0

        if restore_hik_hand_rotation and hik_hand_rotations:

            for frame in frames:

                cmds.currentTime(frame, edit=True, update=False)

                for _side, _start_c, _mid_c, _end_c in sides:

                    hand_node = target_map.get(_end_c)

                    rot = hik_hand_rotations.get((hand_node, frame))

                    if hand_node and rot is not None and safe_cmds_exists(hand_node):

                        try:

                            cmds.setAttr(hand_node + ".rotate", rot[0], rot[1], rot[2])

                            cmds.setKeyframe(hand_node, attribute=ROTATE_ATTRS, time=frame)

                            restored_hand_keys += 3

                        except Exception:

                            pass

            self.log("HumanIK source-guided arm IK: restored native HIK hand/wrist rotations, keys=%d" % restored_hand_keys)



                                               

                                                                                             

                                                                                                           

                                                                                                                  

                                                                                                                   

        try:

            def _audit_find_named_joint(_root, _names):

                _want = set([str(_n).lower() for _n in _names])

                _candidates = []

                if _root and safe_cmds_exists(_root):

                    _candidates.append(_root)

                    try:

                        _candidates.extend(cmds.listRelatives(_root, allDescendents=True, type="joint", fullPath=True) or [])

                    except Exception:

                        pass

                try:

                    _candidates.extend(get_all_joints())

                except Exception:

                    pass

                _seen = set()

                for _j in _candidates:

                    if not (_j and safe_cmds_exists(_j)) or _j in _seen:

                        continue

                    _seen.add(_j)

                    if short_name(_j).lower() in _want:

                        return _j

                return None



            def _audit_hand_nodes(_side, _source=True):

                _hand = source_map.get("hand_" + _side) if _source else target_map.get("hand_" + _side)

                if _source:

                    _prefix = "L_" if _side == "l" else "R_"

                    return {

                        "hand": _hand,

                        "lower": source_map.get("lowerarm_" + _side),

                        "upper": source_map.get("upperarm_" + _side),

                        "thumb": _audit_find_named_joint(_hand, [_prefix + "Thumb1", _prefix + "Thumb2", _prefix + "Thumb3"]),

                        "index": _audit_find_named_joint(_hand, [_prefix + "Index1", _prefix + "Index2", _prefix + "Index3"]),

                        "middle": _audit_find_named_joint(_hand, [_prefix + "Middle1", _prefix + "Middle2", _prefix + "Middle3"]),

                        "ring": _audit_find_named_joint(_hand, [_prefix + "Ring1", _prefix + "Ring2", _prefix + "Ring3"]),

                        "pinky": _audit_find_named_joint(_hand, [_prefix + "Pinky1", _prefix + "Pinky2", _prefix + "Pinky3"]),

                    }

                _suffix = "_" + _side

                return {

                    "hand": _hand,

                    "lower": target_map.get("lowerarm_" + _side),

                    "upper": target_map.get("upperarm_" + _side),

                    "thumb": _audit_find_named_joint(_hand, ["thumb_01" + _suffix, "thumb_02" + _suffix, "thumb_03" + _suffix]),

                    "index": _audit_find_named_joint(_hand, ["index_01" + _suffix, "index_02" + _suffix, "index_03" + _suffix]),

                    "middle": _audit_find_named_joint(_hand, ["middle_01" + _suffix, "middle_02" + _suffix, "middle_03" + _suffix]),

                    "ring": _audit_find_named_joint(_hand, ["ring_01" + _suffix, "ring_02" + _suffix, "ring_03" + _suffix]),

                    "pinky": _audit_find_named_joint(_hand, ["pinky_01" + _suffix, "pinky_02" + _suffix, "pinky_03" + _suffix]),

                }



            def _audit_avg_pos(_nodes):

                _pts = [get_world_position(_n) for _n in _nodes if _n and safe_cmds_exists(_n)]

                if not _pts:

                    return None

                return (sum(_p[0] for _p in _pts) / len(_pts), sum(_p[1] for _p in _pts) / len(_pts), sum(_p[2] for _p in _pts) / len(_pts))



            def _audit_hand_frame(_side, _source, _basis):

                _nodes = _audit_hand_nodes(_side, _source)

                _hand = _nodes.get("hand")

                _lower = _nodes.get("lower")

                if not (_hand and _lower and safe_cmds_exists(_hand) and safe_cmds_exists(_lower)):

                    return None

                _hp = get_world_position(_hand)

                _lp = get_world_position(_lower)

                _forearm_w = self._v_norm(self._v_sub(_hp, _lp), fallback=(0.0, 0.0, -1.0))

                _base_center = _audit_avg_pos([_nodes.get("index"), _nodes.get("middle"), _nodes.get("ring"), _nodes.get("pinky")])

                if _base_center is None:

                    _base_center = _audit_avg_pos([_nodes.get("middle"), _nodes.get("index"), _nodes.get("ring")])

                _fwd_w = self._v_norm(self._v_sub(_base_center, _hp), fallback=_forearm_w) if _base_center else _forearm_w

                _idx = _nodes.get("index")

                _pky = _nodes.get("pinky")

                if _idx and _pky and safe_cmds_exists(_idx) and safe_cmds_exists(_pky):

                    _side_w = self._v_norm(self._v_sub(get_world_position(_idx), get_world_position(_pky)), fallback=(1.0, 0.0, 0.0))

                else:

                    _side_w = self._v_norm(self._v_cross(_fwd_w, _basis[1]), fallback=(1.0, 0.0, 0.0))

                _normal_w = self._v_norm(self._v_cross(_side_w, _fwd_w), fallback=_basis[1])

                _thumb = _nodes.get("thumb")

                if _thumb and safe_cmds_exists(_thumb):

                    _thumb_dir = self._v_norm(self._v_sub(get_world_position(_thumb), _hp), fallback=_normal_w)

                    if self._v_dot(_normal_w, _thumb_dir) < 0.0:

                        _normal_w = self._v_mul(_normal_w, -1.0)

                _normal_w = self._v_norm(self._v_sub(_normal_w, self._v_mul(_fwd_w, self._v_dot(_normal_w, _fwd_w))), fallback=_basis[1])

                _side_w = self._v_norm(self._v_cross(_fwd_w, _normal_w), fallback=_side_w)

                _rot = (0.0, 0.0, 0.0)

                try:

                    _rot = tuple(float(_v) for _v in cmds.getAttr(_hand + ".rotate")[0])

                except Exception:

                    pass

                return {

                    "hand": _hand,

                    "handPos": _hp,

                    "rot": _rot,

                    "forearmW": _forearm_w,

                    "fwdW": _fwd_w,

                    "normalW": _normal_w,

                    "sideW": _side_w,

                    "forearmL": _dir_to_local(_forearm_w, _basis),

                    "fwdL": _dir_to_local(_fwd_w, _basis),

                    "normalL": _dir_to_local(_normal_w, _basis),

                    "sideL": _dir_to_local(_side_w, _basis),

                    "nodes": _nodes,

                }



            def _audit_map_source_dir_to_target_world(_vec_w, _src_basis, _tgt_basis):

                _src_l = _maybe_invert_forward(_dir_to_local(_vec_w, _src_basis))

                return self._v_norm(_dir_to_world(_src_l, _tgt_basis), fallback=_vec_w), _src_l



            def _audit_bool_flip(_mapped_src, _target_vec):

                _ang = _safe_angle(_mapped_src, _target_vec)

                _flip_ang = _safe_angle(self._v_mul(_mapped_src, -1.0), _target_vec)

                return _ang, _flip_ang, bool(_flip_ang + 5.0 < _ang)



            _audit_frames = sorted(set([frames[0], frames[len(frames)//2], frames[-1]])) if frames else []

            _threshold_warn = 45.0

            _threshold_bad = 70.0

            for _af in _audit_frames:

                cmds.currentTime(_af, edit=True, update=True)

                _src_basis_a = _basis_from_map(source_map)

                _tgt_basis_a = _basis_from_map(target_map)

                for _side_a in ("l", "r"):

                    _src_f = _audit_hand_frame(_side_a, True, _src_basis_a)

                    _tgt_f = _audit_hand_frame(_side_a, False, _tgt_basis_a)

                    if not (_src_f and _tgt_f):

                        self.log("ALPHA_HAND_DIRECTION_AUDIT_BEFORE_FIX WARNING f=%.2f side=%s missing source/target hand frame" % (_af, _side_a))

                        continue

                    _mapped_forearm_w, _src_forearm_l = _audit_map_source_dir_to_target_world(_src_f["forearmW"], _src_basis_a, _tgt_basis_a)

                    _mapped_fwd_w, _src_fwd_l = _audit_map_source_dir_to_target_world(_src_f["fwdW"], _src_basis_a, _tgt_basis_a)

                    _mapped_normal_w, _src_normal_l = _audit_map_source_dir_to_target_world(_src_f["normalW"], _src_basis_a, _tgt_basis_a)

                    _mapped_side_w, _src_side_l = _audit_map_source_dir_to_target_world(_src_f["sideW"], _src_basis_a, _tgt_basis_a)

                    _forearm_ang, _forearm_flip, _forearm_inverted = _audit_bool_flip(_mapped_forearm_w, _tgt_f["forearmW"])

                    _fwd_ang, _fwd_flip, _fwd_inverted = _audit_bool_flip(_mapped_fwd_w, _tgt_f["fwdW"])

                    _normal_ang, _normal_flip, _normal_inverted = _audit_bool_flip(_mapped_normal_w, _tgt_f["normalW"])

                    _side_ang, _side_flip, _side_inverted = _audit_bool_flip(_mapped_side_w, _tgt_f["sideW"])

                    _body_up = _tgt_basis_a[2]

                    _body_forward = _tgt_basis_a[3]

                    _body_down = self._v_mul(_body_up, -1.0)

                    _tgt_up_dot = self._v_dot(_tgt_f["normalW"], _body_up)

                    _tgt_down_dot = self._v_dot(_tgt_f["normalW"], _body_down)

                    _tgt_forward_dot = self._v_dot(_tgt_f["fwdW"], _body_forward)

                    _mapped_up_dot = self._v_dot(_mapped_normal_w, _body_up)

                    _mapped_forward_dot = self._v_dot(_mapped_fwd_w, _body_forward)

                    _verdict = "OK"

                    if max(_fwd_ang, _normal_ang, _side_ang) >= _threshold_bad:

                        _verdict = "BAD_DIRECTION"

                    elif max(_fwd_ang, _normal_ang, _side_ang) >= _threshold_warn:

                        _verdict = "WARN_DIRECTION"

                    self.log(

                        "ALPHA_HAND_DIRECTION_AUDIT_BEFORE_FIX FINAL f=%.2f side=%s verdict=%s anglesWorld forearm=%.1f/flip%.1f palmFwd=%.1f/flip%.1f palmNormal=%.1f/flip%.1f handSide=%.1f/flip%.1f invertedCandidates(fwd=%s normal=%s side=%s) tgtDots(normalUp=%.2f normalDown=%.2f fwdBodyForward=%.2f) srcMappedDots(normalUp=%.2f fwdBodyForward=%.2f) srcLocal forearm=%s fwd=%s normal=%s side=%s tgtLocal forearm=%s fwd=%s normal=%s side=%s srcWorld fwd=%s normal=%s side=%s tgtWorld fwd=%s normal=%s side=%s srcRot=%s tgtRot=%s"

                        % (

                            _af, _side_a, _verdict,

                            _forearm_ang, _forearm_flip,

                            _fwd_ang, _fwd_flip,

                            _normal_ang, _normal_flip,

                            _side_ang, _side_flip,

                            str(_fwd_inverted), str(_normal_inverted), str(_side_inverted),

                            _tgt_up_dot, _tgt_down_dot, _tgt_forward_dot,

                            _mapped_up_dot, _mapped_forward_dot,

                            _fmt3(_src_forearm_l), _fmt3(_src_fwd_l), _fmt3(_src_normal_l), _fmt3(_src_side_l),

                            _fmt3(_tgt_f["forearmL"]), _fmt3(_tgt_f["fwdL"]), _fmt3(_tgt_f["normalL"]), _fmt3(_tgt_f["sideL"]),

                            _fmt3(_src_f["fwdW"]), _fmt3(_src_f["normalW"]), _fmt3(_src_f["sideW"]),

                            _fmt3(_tgt_f["fwdW"]), _fmt3(_tgt_f["normalW"]), _fmt3(_tgt_f["sideW"]),

                            _fmt3(_src_f["rot"]), _fmt3(_tgt_f["rot"]),

                        )

                    )

            self.log("ALPHA_HAND_DIRECTION_AUDIT_BEFORE_FIX SUMMARY: compared post-restore source vs target hand directions before the v3.1.6 mirrored-left-palm normal fix pass.")

        except Exception as _hand_audit_exc:

            self.log("ALPHA_HAND_DIRECTION_AUDIT_BEFORE_FIX WARNING: %s" % _hand_audit_exc)



                                                                                              

                                                                                                       

                                                                                                        

                                                                                                  

                                                                              

                                                                                                

        auto_palm_keys = 0

        auto_palm_constraints = 0

        auto_palm_clamps = 0

        auto_palm_temporal_holds = 0

        auto_palm_hik_restores = 0

        auto_palm_unsafe_frames = 0

        auto_palm_hik_backup = {"l": {}, "r": {}}

        _auto_classes = set([c.strip().upper() for c in str(getattr(self.config, "alpha_v3_auto_palm_frame_classes", "") or "").split(",") if c.strip()])

        _auto_class_ok = (not _auto_classes) or (str(alpha_v3_pose_class).upper() in _auto_classes)

        if bool(getattr(self.config, "alpha_v3_enable_auto_palm_frame_solver", False)) and _auto_class_ok:

            _auto_blend = max(0.0, min(1.0, float(getattr(self.config, "alpha_v3_auto_palm_frame_blend", 1.0) or 1.0)))

            _limit_scale = max(1.0, float(getattr(self.config, "alpha_v3_wrist_anatomy_limit_scale", 1.05) or 1.05))

            _max_wrist_angle = max(35.0, float(getattr(self.config, "alpha_v3_wrist_forward_max_degrees", 55.0) or 55.0)) * _limit_scale

            _temporal = bool(getattr(self.config, "alpha_v3_auto_palm_temporal_stabilize", True))

            _restore_unsafe = bool(getattr(self.config, "alpha_v3_wrist_restore_hik_on_violation", True))



                                                                                 

                                                                                                               

            for _side_bak, _hand_key_bak in (("l", "hand_l"), ("r", "hand_r")):

                _hand_bak = target_map.get(_hand_key_bak)

                if _hand_bak and safe_cmds_exists(_hand_bak):

                    for _frame_bak in frames:

                        try:

                            cmds.currentTime(_frame_bak, edit=True, update=False)

                            _r = cmds.getAttr(_hand_bak + ".rotate")[0]

                            auto_palm_hik_backup[_side_bak][_frame_bak] = (float(_r[0]), float(_r[1]), float(_r[2]))

                        except Exception:

                            pass



            def _all_joints_by_short():

                try:

                    _js = get_all_joints()

                except Exception:

                    _js = list(target_joints_to_bake or [])

                return {short_name(_j).lower(): _j for _j in _js if _j and safe_cmds_exists(_j)}



            def _find_named_joint(_root, _names):

                _want = set([str(n).lower() for n in _names])

                _candidates = []

                if _root and safe_cmds_exists(_root):

                    _candidates.append(_root)

                    try:

                        _candidates.extend(cmds.listRelatives(_root, allDescendents=True, type="joint", fullPath=True) or [])

                    except Exception:

                        pass

                try:

                    _candidates.extend(get_all_joints())

                except Exception:

                    pass

                _seen = set()

                for _j in _candidates:

                    if not (_j and safe_cmds_exists(_j)) or _j in _seen:

                        continue

                    _seen.add(_j)

                    _sn = short_name(_j).lower()

                    if _sn in _want:

                        return _j

                return None



            def _palm_nodes(_side, _source=True):

                _hand = source_map.get("hand_" + _side) if _source else target_map.get("hand_" + _side)

                if _source:

                    _prefix = "L_" if _side == "l" else "R_"

                    return {

                        "hand": _hand,

                        "thumb": _find_named_joint(_hand, [_prefix + "Thumb1", _prefix + "Thumb2"]),

                        "index": _find_named_joint(_hand, [_prefix + "Index1", _prefix + "Index2"]),

                        "middle": _find_named_joint(_hand, [_prefix + "Middle1", _prefix + "Middle2"]),

                        "ring": _find_named_joint(_hand, [_prefix + "Ring1", _prefix + "Ring2"]),

                        "pinky": _find_named_joint(_hand, [_prefix + "Pinky1", _prefix + "Pinky2"]),

                    }

                _suffix = "_" + _side

                return {

                    "hand": _hand,

                    "thumb": _find_named_joint(_hand, ["thumb_01" + _suffix, "thumb_02" + _suffix]),

                    "index": _find_named_joint(_hand, ["index_01" + _suffix, "index_02" + _suffix]),

                    "middle": _find_named_joint(_hand, ["middle_01" + _suffix, "middle_02" + _suffix]),

                    "ring": _find_named_joint(_hand, ["ring_01" + _suffix, "ring_02" + _suffix]),

                    "pinky": _find_named_joint(_hand, ["pinky_01" + _suffix, "pinky_02" + _suffix]),

                }



            def _world_point_to_joint_local_vec(_joint, _world_point):

                _loc = None

                try:

                    _loc = self._create_driver_locator("ALPHA_PalmLocalAxisProbe_LOC")

                    cmds.xform(_loc, worldSpace=True, translation=_world_point)

                    cmds.parent(_loc, _joint)

                    _t = cmds.getAttr(_loc + ".translate")[0]

                    return (float(_t[0]), float(_t[1]), float(_t[2]))

                except Exception:

                    return (0.0, 0.0, 0.0)

                finally:

                    try:

                        if _loc and safe_cmds_exists(_loc):

                            cmds.delete(_loc)

                    except Exception:

                        pass



            def _source_palm_frame(_side):

                _nodes = _palm_nodes(_side, True)

                _hand = _nodes.get("hand")

                if not (_hand and safe_cmds_exists(_hand)):

                    return None

                _hp = get_world_position(_hand)

                _bases = []

                for _k in ("index", "middle", "ring", "pinky"):

                    _n = _nodes.get(_k)

                    if _n and safe_cmds_exists(_n):

                        _bases.append(get_world_position(_n))

                if not _bases:

                    return None

                _center = (sum(p[0] for p in _bases)/len(_bases), sum(p[1] for p in _bases)/len(_bases), sum(p[2] for p in _bases)/len(_bases))

                _fwd = self._v_norm(self._v_sub(_center, _hp), fallback=(0.0, 0.0, -1.0))

                _idx = get_world_position(_nodes["index"]) if _nodes.get("index") and safe_cmds_exists(_nodes.get("index")) else None

                _pky = get_world_position(_nodes["pinky"]) if _nodes.get("pinky") and safe_cmds_exists(_nodes.get("pinky")) else None

                if _idx and _pky:

                    _side_vec = self._v_norm(self._v_sub(_idx, _pky), fallback=(1.0, 0.0, 0.0))

                else:

                    _side_vec = (1.0, 0.0, 0.0)

                _up = self._v_norm(self._v_cross(_side_vec, _fwd), fallback=(0.0, 1.0, 0.0))

                                                                                                                  

                _thumb = _nodes.get("thumb")

                if _thumb and safe_cmds_exists(_thumb):

                    _thumb_dir = self._v_norm(self._v_sub(get_world_position(_thumb), _hp), fallback=_up)

                    if self._v_dot(_up, _thumb_dir) < 0.0:

                        _up = self._v_mul(_up, -1.0)

                _up = self._v_norm(self._v_sub(_up, self._v_mul(_fwd, self._v_dot(_up, _fwd))), fallback=(0.0, 1.0, 0.0))

                return _fwd, _up



            def _target_hand_local_axes(_side):

                _nodes = _palm_nodes(_side, False)

                _hand = _nodes.get("hand")

                if not (_hand and safe_cmds_exists(_hand)):

                    return None

                _middle = _nodes.get("middle") or _nodes.get("index") or _nodes.get("ring")

                if not (_middle and safe_cmds_exists(_middle)):

                    return None

                _aim = self._v_norm(_world_point_to_joint_local_vec(_hand, get_world_position(_middle)), fallback=(1.0, 0.0, 0.0))

                _idx = _nodes.get("index")

                _pky = _nodes.get("pinky")

                _thumb = _nodes.get("thumb")

                if _idx and _pky and safe_cmds_exists(_idx) and safe_cmds_exists(_pky):

                    _idx_l = _world_point_to_joint_local_vec(_hand, get_world_position(_idx))

                    _pky_l = _world_point_to_joint_local_vec(_hand, get_world_position(_pky))

                    _side_l = self._v_norm(self._v_sub(_idx_l, _pky_l), fallback=(0.0, 1.0, 0.0))

                    _up = self._v_norm(self._v_cross(_side_l, _aim), fallback=(0.0, 1.0, 0.0))

                                                                                                          

                                                                                                               

                                                                                                             

                                                                                                                

                                                                                             

                    if _thumb and safe_cmds_exists(_thumb):

                        _thumb_l = _world_point_to_joint_local_vec(_hand, get_world_position(_thumb))

                        _thumb_l = self._v_norm(_thumb_l, fallback=_up)

                        if self._v_dot(_up, _thumb_l) < 0.0:

                            _up = self._v_mul(_up, -1.0)

                elif _thumb and safe_cmds_exists(_thumb):

                    _up = _safe_local_up_vector(_aim, _world_point_to_joint_local_vec(_hand, get_world_position(_thumb)))

                else:

                    _up = _safe_local_up_vector(_aim, (0.0, 1.0, 0.0))

                return _aim, _up



            def _clamp_dir_to_cone(_direction, _axis, _max_deg):

                _d = self._v_norm(_direction, fallback=(0.0, 0.0, -1.0))

                _a = self._v_norm(_axis, fallback=_d)

                _ang = _safe_angle(_a, _d)

                if _ang <= _max_deg:

                    return _d, False, _ang

                _orth = self._v_sub(_d, self._v_mul(_a, self._v_dot(_d, _a)))

                if self._v_len(_orth) <= 1.0e-5:

                    _orth = self._v_cross(_a, (0.0, 1.0, 0.0))

                    if self._v_len(_orth) <= 1.0e-5:

                        _orth = self._v_cross(_a, (1.0, 0.0, 0.0))

                _orth = self._v_norm(_orth, fallback=(0.0, 1.0, 0.0))

                _rad = math.radians(float(_max_deg))

                _out = self._v_add(self._v_mul(_a, math.cos(_rad)), self._v_mul(_orth, math.sin(_rad)))

                return self._v_norm(_out, fallback=_d), True, _ang



            _hand_axis = {"l": _target_hand_local_axes("l"), "r": _target_hand_local_axes("r")}

            _aim_locs = {}

            _up_locs = {}

            _palm_temp_nodes = []

            _palm_constraints = []

            _prev_fwd = {"l": None, "r": None}

            _prev_up = {"l": None, "r": None}

            for _side, _start_c, _mid_c, _end_c in sides:

                _hand = target_map.get(_end_c)

                if _hand_axis.get(_side) and _hand and safe_cmds_exists(_hand):

                    _aim_locs[_side] = self._create_driver_locator("ALPHA_V3_%s_PalmAim_LOC" % _side)

                    _up_locs[_side] = self._create_driver_locator("ALPHA_V3_%s_PalmUp_LOC" % _side)

                    _palm_temp_nodes.extend([_aim_locs[_side], _up_locs[_side]])



            if _aim_locs:

                for _frame in frames:

                    try:

                        cmds.currentTime(_frame, edit=True, update=True)

                    except Exception:

                        pass

                    _src_basis_now = _basis_from_map(source_map)

                    _tgt_basis_now = _basis_from_map(target_map)

                    for _side, _start_c, _mid_c, _end_c in sides:

                        if _side not in _aim_locs:

                            continue

                        _hand = target_map.get(_end_c)

                        _lower = target_map.get(_mid_c)

                        if not (_hand and _lower and safe_cmds_exists(_hand) and safe_cmds_exists(_lower)):

                            continue

                        _hand_pos = get_world_position(_hand)

                        _forearm_dir = self._v_norm(self._v_sub(_hand_pos, get_world_position(_lower)), fallback=(0.0, 0.0, -1.0))



                                                                                                                  

                                                                                                                     

                                                                                                                     

                                                                                                                     

                        _use_source_frame = bool(getattr(self.config, "alpha_v3_auto_palm_use_source_frame", False))

                        _strict_source_hand_dir = bool(getattr(self.config, "alpha_v3_strict_source_hand_direction_match", False)) and _use_source_frame

                        if _use_source_frame:

                            _src_pf = _source_palm_frame(_side)

                            if not _src_pf:

                                continue

                            _src_fwd, _src_up = _src_pf

                            _src_fwd_l = _maybe_invert_forward(_dir_to_local(_src_fwd, _src_basis_now))

                            _src_up_l = _maybe_invert_forward(_dir_to_local(_src_up, _src_basis_now))

                            _desired_fwd = self._v_norm(_dir_to_world(_src_fwd_l, _tgt_basis_now), fallback=_forearm_dir)

                            _desired_up = self._v_norm(_dir_to_world(_src_up_l, _tgt_basis_now), fallback=_tgt_basis_now[1])

                        else:

                            _desired_fwd = _forearm_dir

                            _desired_up = _tgt_basis_now[1]



                                                                                                

                                                                                                                  

                                                                                                      

                                                                                                                   

                                                                                         

                        _pose_class_upper = str(alpha_v3_pose_class).upper()

                        _is_clasp_contact = ("CLASP" in _pose_class_upper) or ("HAND_CONTACT" in _pose_class_upper)

                        _body_down = self._v_norm(self._v_mul(_tgt_basis_now[1], -1.0), fallback=(0.0, -1.0, 0.0))

                        _body_front = self._v_norm(_tgt_basis_now[2], fallback=(0.0, 0.0, 1.0))



                        if (not _strict_source_hand_dir) and _is_clasp_contact:

                            _other_key = "hand_r" if _side == "l" else "hand_l"

                            _other_hand = target_map.get(_other_key)

                            if _other_hand and safe_cmds_exists(_other_hand):

                                _pair_vec = self._v_sub(get_world_position(_other_hand), _hand_pos)

                                if self._v_len(_pair_vec) > 0.25:

                                    _pair_dir = self._v_norm(_pair_vec, fallback=_desired_fwd)

                                                                                                              

                                    if self._v_dot(_desired_fwd, _pair_dir) < 0.0:

                                        _desired_fwd = self._v_mul(_desired_fwd, -1.0)

                                    _desired_fwd = self._v_norm(self._v_add(self._v_mul(_pair_dir, 0.78), self._v_mul(_desired_fwd, 0.22)), fallback=_pair_dir)

                                                                                                             

                                                                                                            

                            _desired_up = self._v_norm(self._v_add(self._v_mul(_body_down, 0.72), self._v_mul(_body_front, 0.28)), fallback=_body_down)



                        elif ((not _strict_source_hand_dir) and str(alpha_v3_pose_class).upper() == "LOW_OR_LAP_HANDS" and

                                bool(getattr(self.config, "alpha_v3_lap_palm_force_body_down_normal", True))):

                            _bd_blend = max(0.0, min(1.0, float(getattr(self.config, "alpha_v3_lap_palm_body_down_blend", 1.0) or 1.0)))

                                                                                                         

                            _knee_key = "calf_" + _side

                            _foot_key = "foot_" + _side

                            _lap_dir = None

                            _knee_node = target_map.get(_knee_key)

                            _foot_node = target_map.get(_foot_key)

                            _lap_pts = []

                            for _lap_node in (_knee_node, _foot_node):

                                if _lap_node and safe_cmds_exists(_lap_node):

                                    _lap_pts.append(get_world_position(_lap_node))

                            if _lap_pts:

                                _lap_target = (sum(p[0] for p in _lap_pts)/len(_lap_pts), sum(p[1] for p in _lap_pts)/len(_lap_pts), sum(p[2] for p in _lap_pts)/len(_lap_pts))

                                _lap_vec = self._v_sub(_lap_target, _hand_pos)

                                if self._v_len(_lap_vec) > 0.25:

                                    _lap_dir = self._v_norm(_lap_vec, fallback=None)

                            if _lap_dir:

                                _desired_fwd = self._v_norm(self._v_add(self._v_mul(_lap_dir, 0.72), self._v_mul(_desired_fwd, 0.28)), fallback=_lap_dir)

                                                                                                                     

                                                                                                                   

                            if self._v_dot(_desired_up, _body_down) < self._v_dot(self._v_mul(_desired_up, -1.0), _body_down):

                                _desired_up = self._v_mul(_desired_up, -1.0)

                            _desired_up = self._v_norm(self._v_add(self._v_mul(_desired_up, 1.0 - _bd_blend), self._v_mul(_body_down, _bd_blend)), fallback=_body_down)



                        if (not _strict_source_hand_dir) and bool(getattr(self.config, "alpha_v3_enable_wrist_anatomy_guard", True)):

                            _desired_fwd, _did_clamp, _raw_ang = _clamp_dir_to_cone(_desired_fwd, _forearm_dir, _max_wrist_angle)

                            if _did_clamp:

                                auto_palm_clamps += 1

                        _desired_up = self._v_sub(_desired_up, self._v_mul(_desired_fwd, self._v_dot(_desired_up, _desired_fwd)))

                        if self._v_len(_desired_up) <= 1.0e-5:

                            _desired_up = self._v_cross(_desired_fwd, _forearm_dir)

                        _desired_up = self._v_norm(_desired_up, fallback=(0.0, 1.0, 0.0))

                        if _temporal and _prev_fwd[_side] is not None:

                            if self._v_dot(_desired_fwd, _prev_fwd[_side]) < -0.20:

                                _desired_fwd = _prev_fwd[_side]

                                _desired_up = _prev_up[_side] or _desired_up

                                auto_palm_temporal_holds += 1

                            elif _prev_up[_side] is not None and self._v_dot(_desired_up, _prev_up[_side]) < -0.35:

                                _desired_up = self._v_mul(_desired_up, -1.0)

                                auto_palm_temporal_holds += 1

                        _prev_fwd[_side] = _desired_fwd

                        _prev_up[_side] = _desired_up

                        self._set_and_key_locator_pos(_aim_locs[_side], self._v_add(_hand_pos, self._v_mul(_desired_fwd, 12.0)), _frame)

                        self._set_and_key_locator_pos(_up_locs[_side], self._v_add(_hand_pos, self._v_mul(_desired_up, 12.0)), _frame)

                for _side, _start_c, _mid_c, _end_c in sides:

                    _hand = target_map.get(_end_c)

                    _axes = _hand_axis.get(_side)

                    if not (_hand and _axes and _side in _aim_locs and _side in _up_locs and safe_cmds_exists(_hand)):

                        continue

                    try:

                        _aim_axis, _up_axis = _axes

                        _palm_constraints.append(cmds.aimConstraint(_aim_locs[_side], _hand, maintainOffset=False, aimVector=_aim_axis, upVector=_up_axis, worldUpType="object", worldUpObject=_up_locs[_side])[0])

                        auto_palm_constraints += 1

                    except Exception as _palm_con_exc:

                        self.log("ALPHA_V3_AUTO_PALM_FRAME WARNING: could not constrain %s hand: %s" % (_side, _palm_con_exc))

                if _palm_constraints:

                    _hand_nodes = [target_map.get("hand_l"), target_map.get("hand_r")]

                    _hand_nodes = [h for h in _hand_nodes if h and safe_cmds_exists(h)]

                    _bake = self._manual_sample_solved_joint_animation(_hand_nodes, frames, translate_key_nodes=set(), temp_nodes=_palm_constraints + _palm_temp_nodes, label="alpha_v3_auto_palm_frame")

                    auto_palm_keys = int(_bake.get("manual_bake_keyed_rotate_samples", 0) or 0) * 3



                                                                                                                     

                                                                                                                

                                                                                                           

                                                                                                            

                    if _restore_unsafe:

                        _strict_max = _max_wrist_angle

                        def _target_main_finger_forward(_side_v):

                            _nodes_v = _palm_nodes(_side_v, False)

                            _hand_v = _nodes_v.get("hand")

                            if not (_hand_v and safe_cmds_exists(_hand_v)):

                                return None

                            _hp_v = get_world_position(_hand_v)

                            _pts_v = []

                            for _k_v in ("index", "middle", "ring"):

                                _n_v = _nodes_v.get(_k_v)

                                if _n_v and safe_cmds_exists(_n_v):

                                    _pts_v.append(get_world_position(_n_v))

                            if not _pts_v:

                                return None

                            _center_v = (sum(p[0] for p in _pts_v)/len(_pts_v), sum(p[1] for p in _pts_v)/len(_pts_v), sum(p[2] for p in _pts_v)/len(_pts_v))

                            return self._v_norm(self._v_sub(_center_v, _hp_v), fallback=(0.0, 0.0, -1.0))



                        for _frame_v in frames:

                            try:

                                cmds.currentTime(_frame_v, edit=True, update=True)

                            except Exception:

                                pass

                            for _side_v, _start_c_v, _mid_c_v, _end_c_v in sides:

                                _hand_v = target_map.get(_end_c_v)

                                _lower_v = target_map.get(_mid_c_v)

                                if not (_hand_v and _lower_v and safe_cmds_exists(_hand_v) and safe_cmds_exists(_lower_v)):

                                    continue

                                _ff_v = _target_main_finger_forward(_side_v)

                                if not _ff_v:

                                    continue

                                _forearm_v = self._v_norm(self._v_sub(get_world_position(_hand_v), get_world_position(_lower_v)), fallback=_ff_v)

                                _angle_v = _safe_angle(_forearm_v, _ff_v)

                                _unsafe_v = _angle_v > _strict_max

                                if _unsafe_v:

                                    auto_palm_unsafe_frames += 1

                                    _bak_v = auto_palm_hik_backup.get(_side_v, {}).get(_frame_v)

                                    if _bak_v:

                                        try:

                                            cmds.setAttr(_hand_v + ".rotate", _bak_v[0], _bak_v[1], _bak_v[2])

                                            cmds.setKeyframe(_hand_v, attribute=ROTATE_ATTRS, time=_frame_v)

                                            auto_palm_hik_restores += 1

                                        except Exception:

                                            pass

                else:

                    for _n in _palm_temp_nodes:

                        try:

                            if safe_cmds_exists(_n):

                                cmds.delete(_n)

                        except Exception:

                            pass

                                                                                                  

                                                                                                       

                                                                                               

            post_palm_finger_finish_keys = 0

            try:

                _post_class = str(alpha_v3_pose_class).upper()

                _post_finger_ok = bool(getattr(self.config, "alpha_v3_enable_post_palm_finger_finish", True)) and (("CLASP" in _post_class) or ("HAND_CONTACT" in _post_class))

                if _post_finger_ok:

                    _post_blend = max(0.0, min(1.0, float(getattr(self.config, "alpha_v3_post_palm_finger_finish_blend", 0.42) or 0.42)))

                    _curl_by_idx = {

                        1: float(getattr(self.config, "alpha_v3_post_palm_finger_finish_curl_mcp", 22.0) or 22.0),

                        2: float(getattr(self.config, "alpha_v3_post_palm_finger_finish_curl_pip", 28.0) or 28.0),

                        3: float(getattr(self.config, "alpha_v3_post_palm_finger_finish_curl_dip", 10.0) or 10.0),

                    }



                    def _post_target_finger_nodes(_side_pf):

                        _hand_pf = target_map.get("hand_" + _side_pf)

                        if not (_hand_pf and safe_cmds_exists(_hand_pf)):

                            return []

                        try:

                            _desc_pf = cmds.listRelatives(_hand_pf, allDescendents=True, type="joint", fullPath=True) or []

                        except Exception:

                            _desc_pf = []

                        _by_short_pf = {short_name(_n).lower(): _n for _n in _desc_pf if _n and safe_cmds_exists(_n)}

                        _out_pf = []

                        for _finger_pf in ("index", "middle", "ring", "pinky"):

                            for _idx_pf in (1, 2, 3):

                                _name_pf = "%s_%02d_%s" % (_finger_pf, _idx_pf, _side_pf)

                                _node_pf = _by_short_pf.get(_name_pf)

                                if _node_pf and safe_cmds_exists(_node_pf):

                                    _out_pf.append((_node_pf, _finger_pf, _idx_pf, _side_pf))

                        return _out_pf



                    _finish_nodes = _post_target_finger_nodes("l") + _post_target_finger_nodes("r")

                    for _frame_pf in frames:

                        try:

                            cmds.currentTime(_frame_pf, edit=True, update=True)

                        except Exception:

                            pass

                        for _node_pf, _finger_pf, _idx_pf, _side_pf in _finish_nodes:

                            try:

                                _rot_pf = cmds.getAttr(_node_pf + ".rotate")[0]

                                _curl_pf = _curl_by_idx.get(int(_idx_pf), 0.0) * _post_blend

                                                                                                               

                                                                                           

                                cmds.setAttr(_node_pf + ".rotate", float(_rot_pf[0]), float(_rot_pf[1]), float(_rot_pf[2]) + _curl_pf)

                                cmds.setKeyframe(_node_pf, attribute="rotateZ", time=_frame_pf)

                                post_palm_finger_finish_keys += 1

                            except Exception:

                                pass

                    self.log("ALPHA_V3_POST_PALM_FINGER_FINISH: class=%s enabled=True mainNodes=%d blend=%.2f keys=%d correctiveHelpersTouched=False" % (alpha_v3_pose_class, len(_finish_nodes), _post_blend, post_palm_finger_finish_keys))

                else:

                    self.log("ALPHA_V3_POST_PALM_FINGER_FINISH: class=%s enabled=False reason=not_close_clasp_contact" % alpha_v3_pose_class)

            except Exception as _post_finger_exc:

                self.log("ALPHA_V3_POST_PALM_FINGER_FINISH WARNING: %s" % _post_finger_exc)



                                                                                                       

                                                                                                             

            try:

                for _diag_frame in sorted(set([frames[0], frames[len(frames)//2], frames[-1]])) if frames else []:

                    cmds.currentTime(_diag_frame, edit=True, update=True)

                    _tgt_basis_diag = _basis_from_map(target_map)

                    for _side_diag, _start_c_diag, _mid_c_diag, _end_c_diag in sides:

                        _hand_diag = target_map.get(_end_c_diag)

                        _lower_diag = target_map.get(_mid_c_diag)

                        if not (_hand_diag and _lower_diag and safe_cmds_exists(_hand_diag) and safe_cmds_exists(_lower_diag)):

                            continue

                        _rot_diag = cmds.getAttr(_hand_diag + ".rotate")[0]

                        _nodes_diag = _palm_nodes(_side_diag, False)

                        _hp_diag = get_world_position(_hand_diag)

                        _pts_diag = []

                        for _k_diag in ("index", "middle", "ring"):

                            _n_diag = _nodes_diag.get(_k_diag)

                            if _n_diag and safe_cmds_exists(_n_diag):

                                _pts_diag.append(get_world_position(_n_diag))

                        _finger_dir_diag = (0.0, 0.0, -1.0)

                        if _pts_diag:

                            _center_diag = (sum(p[0] for p in _pts_diag)/len(_pts_diag), sum(p[1] for p in _pts_diag)/len(_pts_diag), sum(p[2] for p in _pts_diag)/len(_pts_diag))

                            _finger_dir_diag = self._v_norm(self._v_sub(_center_diag, _hp_diag), fallback=_finger_dir_diag)

                        _forearm_diag = self._v_norm(self._v_sub(_hp_diag, get_world_position(_lower_diag)), fallback=_finger_dir_diag)

                        _body_down_diag = self._v_norm(self._v_mul(_tgt_basis_diag[1], -1.0), fallback=(0.0, -1.0, 0.0))

                        self.log("ALPHA_V3_POST_PALM_ROTATION_FINAL f=%.2f side=%s handRot=%s wristLocal=%s fingerVsForearm=%.1f fingerVsBodyDown=%.1f lapPalmBodyDown=%s" % (_diag_frame, _side_diag, _fmt3(_rot_diag), _fmt3(_to_local(_hp_diag, _tgt_basis_diag)), _safe_angle(_finger_dir_diag, _forearm_diag), _safe_angle(_finger_dir_diag, _body_down_diag), str(bool(getattr(self.config, "alpha_v3_lap_palm_force_body_down_normal", True)))))

            except Exception as _post_palm_diag_exc:

                self.log("ALPHA_V3_POST_PALM_ROTATION_FINAL WARNING: %s" % _post_palm_diag_exc)



            if bool(getattr(self.config, "alpha_v3_auto_palm_use_source_frame", False)):

                self.log("ALPHA_V3_SOURCE_PALM_ROTATION_SOLVER: class=%s enabled=True sourcePalmFrame=True constraints=%d handRotateKeys=%d anatomyGuard=%s temporalHolds=%d restoredToHIK=%d allowedClasses=%s lapPalmBodyDown=%s bodyDownBlend=%.2f customEulerOffsets=False wristLocationAlreadySolved=True" % (alpha_v3_pose_class, auto_palm_constraints, auto_palm_keys, str(bool(getattr(self.config, "alpha_v3_enable_wrist_anatomy_guard", False))), auto_palm_temporal_holds, auto_palm_hik_restores, ",".join(sorted(_auto_classes)) if _auto_classes else "<all>", str(bool(getattr(self.config, "alpha_v3_lap_palm_force_body_down_normal", True))), float(getattr(self.config, "alpha_v3_lap_palm_body_down_blend", 1.0) or 1.0)))

                if bool(getattr(self.config, "alpha_v3_strict_source_hand_direction_match", False)):

                    self.log("ALPHA_V3_1_6_LEFT_PALM_NORMAL_FLIP_FIX: enabled=True sourcePalmForwardAndThumbSideNormalDriveHandOnly=True targetThumbSideUpAxis=True wristLocationPreserved=True fingersUntouched=True claspLapOverridesSkipped=True anatomyClampSkipped=True")

                    try:

                        _audit_frames_after = sorted(set([frames[0], frames[len(frames)//2], frames[-1]])) if frames else []

                        for _af2 in _audit_frames_after:

                            cmds.currentTime(_af2, edit=True, update=True)

                            _src_basis_2 = _basis_from_map(source_map)

                            _tgt_basis_2 = _basis_from_map(target_map)

                            for _side_2 in ("l", "r"):

                                _src_f2 = _audit_hand_frame(_side_2, True, _src_basis_2)

                                _tgt_f2 = _audit_hand_frame(_side_2, False, _tgt_basis_2)

                                if not (_src_f2 and _tgt_f2):

                                    continue

                                _mapped_fwd_2, _src_fwd_l2 = _audit_map_source_dir_to_target_world(_src_f2["fwdW"], _src_basis_2, _tgt_basis_2)

                                _mapped_norm_2, _src_norm_l2 = _audit_map_source_dir_to_target_world(_src_f2["normalW"], _src_basis_2, _tgt_basis_2)

                                _mapped_side_2, _src_side_l2 = _audit_map_source_dir_to_target_world(_src_f2["sideW"], _src_basis_2, _tgt_basis_2)

                                _fwd_ang2, _fwd_flip2, _fwd_inv2 = _audit_bool_flip(_mapped_fwd_2, _tgt_f2["fwdW"])

                                _norm_ang2, _norm_flip2, _norm_inv2 = _audit_bool_flip(_mapped_norm_2, _tgt_f2["normalW"])

                                _side_ang2, _side_flip2, _side_inv2 = _audit_bool_flip(_mapped_side_2, _tgt_f2["sideW"])

                                _verdict2 = "OK"

                                if max(_fwd_ang2, _norm_ang2, _side_ang2) >= 70.0:

                                    _verdict2 = "BAD_DIRECTION"

                                elif max(_fwd_ang2, _norm_ang2, _side_ang2) >= 45.0:

                                    _verdict2 = "WARN_DIRECTION"

                                self.log("ALPHA_HAND_DIRECTION_AUDIT_AFTER_FIX FINAL f=%.2f side=%s verdict=%s palmFwd=%.1f/flip%.1f palmNormal=%.1f/flip%.1f handSide=%.1f/flip%.1f invertedCandidates(fwd=%s normal=%s side=%s) srcLocal fwd=%s normal=%s side=%s tgtLocal fwd=%s normal=%s side=%s srcRot=%s tgtRot=%s" % (_af2, _side_2, _verdict2, _fwd_ang2, _fwd_flip2, _norm_ang2, _norm_flip2, _side_ang2, _side_flip2, str(_fwd_inv2), str(_norm_inv2), str(_side_inv2), _fmt3(_src_fwd_l2), _fmt3(_src_norm_l2), _fmt3(_src_side_l2), _fmt3(_tgt_f2["fwdL"]), _fmt3(_tgt_f2["normalL"]), _fmt3(_tgt_f2["sideL"]), _fmt3(_src_f2["rot"]), _fmt3(_tgt_f2["rot"])))

                        self.log("ALPHA_HAND_DIRECTION_AUDIT_AFTER_FIX SUMMARY: source hand direction match should drive palmFwd/palmNormal/handSide under warning range. If this still warns, the issue is target finger landmark selection, not wrist location.")

                    except Exception as _audit_after_exc:

                        self.log("ALPHA_HAND_DIRECTION_AUDIT_AFTER_FIX WARNING: %s" % _audit_after_exc)

            else:

                self.log("ALPHA_V3_NEUTRAL_WRIST_SOLVER: class=%s enabled=True sourcePalmFrame=%s neutralHumanWrist=%s constraints=%d handRotateKeys=%d anatomyGuard=%s limitScale=%.2f maxForwardAngle=%.1f clamps=%d temporalHolds=%d unsafeFrames=%d restoredToHIK=%d allowedClasses=%s customEulerOffsets=False" % (alpha_v3_pose_class, str(bool(getattr(self.config, "alpha_v3_auto_palm_use_source_frame", False))), str(not bool(getattr(self.config, "alpha_v3_auto_palm_use_source_frame", False))), auto_palm_constraints, auto_palm_keys, str(bool(getattr(self.config, "alpha_v3_enable_wrist_anatomy_guard", True))), _limit_scale, _max_wrist_angle, auto_palm_clamps, auto_palm_temporal_holds, auto_palm_unsafe_frames, auto_palm_hik_restores, ",".join(sorted(_auto_classes)) if _auto_classes else "<all>"))

        elif bool(getattr(self.config, "alpha_v3_enable_auto_palm_frame_solver", False)):

            self.log("ALPHA_V3_AUTO_PALM_FRAME: skipped for class=%s allowed=%s" % (alpha_v3_pose_class, ",".join(sorted(_auto_classes)) if _auto_classes else "<all>"))



        finger_keys = 0

        if bool(getattr(self.config, "humanik_source_guided_arm_ik_key_fingers_to_rest", True)):

            finger_nodes = []

            for side in ("l", "r"):

                hand_node = target_map.get("hand_%s" % side)

                if not hand_node or not safe_cmds_exists(hand_node):

                    continue

                try:

                    descendants = cmds.listRelatives(hand_node, allDescendents=True, type="joint", fullPath=True) or []

                except Exception:

                    descendants = []

                for n in descendants:

                    sn = short_name(n).lower()

                    if any(tok in sn for tok in ("thumb", "index", "middle", "ring", "pinky", "finger", "metacarpal")):

                        finger_nodes.append(n)

            finger_nodes = list(dict.fromkeys(finger_nodes))

            for frame in frames:

                cmds.currentTime(frame, edit=True, update=False)

                for n in finger_nodes:

                    try:

                        cmds.setKeyframe(n, attribute=ROTATE_ATTRS, time=frame)

                        finger_keys += 3

                    except Exception:

                        pass

            if finger_nodes:

                self.log("HumanIK source-guided arm IK: stabilized finger/corrective joints=%d finger_keys=%d" % (len(finger_nodes), finger_keys))



        curves_after = count_anim_curves_on_nodes(target_joints_to_bake)

        stats.update({

            "humanik_source_guided_arm_ik_enabled": True,

            "humanik_source_guided_arm_ik_frames": len(frames),

            "humanik_source_guided_arm_ik_corrections": correction_count,

            "humanik_source_guided_arm_ik_side_corrections": side_corrections,

            "humanik_source_guided_arm_ik_max_wrist_delta": max_wrist_delta,

            "humanik_source_guided_arm_ik_max_reach_clamp": max_reach_clamp,

            "humanik_source_guided_arm_ik_ik_handles": len(ik_handles),

            "humanik_source_guided_arm_ik_driver_keyed_channels": keyed_driver_channels,

            "humanik_source_guided_arm_ik_pair_convergence_enabled": pair_convergence,

            "humanik_source_guided_arm_ik_pair_convergence_frames": pair_convergence_frames,

            "humanik_source_guided_arm_ik_pair_convergence_total_pull": pair_convergence_total_pull,

            "humanik_source_guided_arm_ik_pair_convergence_max_pull": pair_convergence_max_pull,

            "humanik_source_guided_arm_ik_pair_convergence_max_source_distance": pair_convergence_max_source_distance,

            "humanik_source_guided_arm_ik_restored_hand_keys": restored_hand_keys,

            "humanik_source_guided_arm_ik_bake_hand_rotation": bake_hand_rotation,

            "humanik_source_guided_arm_ik_source_palm_delta_enabled": source_palm_delta if 'source_palm_delta' in locals() else False,

            "humanik_source_guided_arm_ik_source_palm_delta_keys": source_palm_delta_keys if 'source_palm_delta_keys' in locals() else 0,

            "humanik_source_guided_arm_ik_include_clavicle_chain": include_clavicle_chain,

            "humanik_source_guided_arm_ik_finger_keys": finger_keys,

            "humanik_source_guided_arm_ik_source_finger_transfer_pairs": len(source_finger_transfer_pairs) if 'source_finger_transfer_pairs' in locals() else 0,

            "humanik_source_guided_arm_ik_source_finger_transfer_keys": source_finger_transfer_keys if 'source_finger_transfer_keys' in locals() else 0,

            "humanik_source_guided_arm_ik_corrective_finger_stabilize_keys": corrective_finger_stabilize_keys if 'corrective_finger_stabilize_keys' in locals() else 0,

            "humanik_source_guided_arm_ik_target_anim_curves": curves_after,

            "humanik_source_guided_arm_ik_manual_bake": bake_stats,

        })

        self.log(

            "HumanIK Option1 v2.29.0 arm IK finished: frames=%d corrections=%d pair_frames=%d pair_max_pull=%.3f side_corrections=%d ik_handles=%d restored_hand_keys=%d finger_keys=%d target_anim_curves=%d"

            % (len(frames), correction_count, pair_convergence_frames, pair_convergence_max_pull, side_corrections, len(ik_handles), restored_hand_keys, finger_keys, curves_after)

        )

        return stats





    def _post_override_humanik_arm_rotations_from_source(

        self,

        source_anim_map: Dict[str, str],

        target_map: Dict[str, str],

        source_rest_local_matrices: Dict[str, Any],

        target_rest_local_matrices: Dict[str, Any],

        target_rest_translates: Dict[str, Tuple[float, float, float]],

        target_joints_to_bake: List[str],

        start: float,

        end: float,

        source_rest_positions: Optional[Dict[str, Tuple[float, float, float]]] = None,

        target_rest_positions: Optional[Dict[str, Tuple[float, float, float]]] = None,

        target_rest_local_rotations: Optional[Dict[str, Tuple[float, float, float]]] = None,

    ) -> Dict[str, Any]:

        stats: Dict[str, Any] = {

            "humanik_arm_rotation_override_enabled": False,

            "humanik_arm_rotation_override_frames": 0,

            "humanik_arm_rotation_override_keys": 0,

        }

        if not bool(getattr(self.config, "humanik_post_override_arms_from_source", True)):

            self.log("HumanIK arm rotation override skipped: disabled.")

            return stats



        include_clavicles = bool(getattr(self.config, "humanik_arm_override_include_clavicles", True))

        include_hands = bool(getattr(self.config, "humanik_arm_override_include_hands", True))



        arm_canonicals: List[str] = []

        for side in ("l", "r"):

            if include_clavicles:

                arm_canonicals.append("clavicle_%s" % side)

            arm_canonicals.extend(["upperarm_%s" % side, "lowerarm_%s" % side])

            if include_hands:

                arm_canonicals.append("hand_%s" % side)



        valid: List[str] = []

        missing: List[str] = []

        for c in arm_canonicals:

            src = source_anim_map.get(c)

            tgt = target_map.get(c)

            if src and tgt and safe_cmds_exists(src) and safe_cmds_exists(tgt) and source_rest_local_matrices.get(c) is not None and target_rest_local_matrices.get(c) is not None:

                valid.append(c)

            else:

                missing.append(c)



        if len(valid) < 4:

            self.log("HumanIK arm rotation override skipped: too few valid arm joints. valid=%s missing=%s" % (valid, missing))

            return stats



        frames = self._build_sample_frames(start, end)

        if not frames:

            return stats



        keyed = 0

        nodes = set()

        max_source_delta = 0.0

        sample_lines: List[str] = []

        self.log(

            "HumanIK v1.4.7 ARM-ROTATION-OVERRIDE: overriding arm local rotations from source rest deltas. joints=%d frames=%d include_clavicles=%s include_hands=%s"

            % (len(valid), len(frames), include_clavicles, include_hands)

        )



        for frame in frames:

            cmds.currentTime(frame, edit=True, update=True)

            try:

                cmds.refresh(force=True)

            except Exception:

                pass

            for c in valid:

                src = source_anim_map[c]

                tgt = target_map[c]

                try:

                    src_rest_m = source_rest_local_matrices[c]

                    tgt_rest_m = target_rest_local_matrices[c]

                    src_curr_m = self._matrix_from_node_local(src)

                                                                                                    

                    delta_m = src_rest_m.inverse() * src_curr_m

                    out_m = tgt_rest_m * delta_m

                    keep_translate = target_rest_translates.get(c) or self._get_vec(tgt, TRANSLATE_ATTRS)

                    self._apply_local_matrix_to_joint(tgt, out_m, keep_translate=keep_translate)

                    cmds.setKeyframe(tgt, attribute=ROTATE_ATTRS, time=frame)

                    keyed += 3

                    nodes.add(tgt)

                    if frame in (frames[0], frames[len(frames)//2], frames[-1]) and c in ("upperarm_l", "lowerarm_l", "hand_l", "upperarm_r", "lowerarm_r", "hand_r"):

                        try:

                            src_rot = tuple(round(float(v), 3) for v in cmds.getAttr(src + ".rotate")[0])

                            tgt_rot = tuple(round(float(v), 3) for v in cmds.getAttr(tgt + ".rotate")[0])

                            sample_lines.append("f=%.2f %s srcRot=%s outRot=%s" % (frame, c, src_rot, tgt_rot))

                        except Exception:

                            pass

                    try:

                                                                                                         

                        src_rest_list = self._matrix_to_list(src_rest_m)

                        src_curr_list = self._matrix_to_list(src_curr_m)

                        max_source_delta = max(max_source_delta, sum(abs(src_curr_list[i] - src_rest_list[i]) for i in range(16)))

                    except Exception:

                        pass

                except Exception as exc:

                    self.log("HumanIK arm rotation override WARNING: failed %s at frame %.3f: %s" % (c, frame, exc))



                                                                                                         

                                                                                                        

                                                                                                           

        finger_keys = 0

        if bool(getattr(self.config, "humanik_arm_override_key_fingers_to_rest", True)):

            finger_nodes = []

            for side in ("l", "r"):

                hand_node = target_map.get("hand_%s" % side)

                if not hand_node or not safe_cmds_exists(hand_node):

                    continue

                try:

                    descendants = cmds.listRelatives(hand_node, allDescendents=True, type="joint", fullPath=True) or []

                except Exception:

                    descendants = []

                for n in descendants:

                    sn = short_name(n).lower()

                    if any(tok in sn for tok in ("thumb", "index", "middle", "ring", "pinky", "finger", "metacarpal")):

                        finger_nodes.append(n)

            finger_nodes = list(dict.fromkeys(finger_nodes))

            for frame in frames:

                cmds.currentTime(frame, edit=True, update=False)

                for n in finger_nodes:

                    try:

                        cmds.setKeyframe(n, attribute=ROTATE_ATTRS, time=frame)

                        finger_keys += 3

                    except Exception:

                        pass

            if finger_nodes:

                self.log("HumanIK arm rotation override: stabilized finger/corrective joints=%d finger_keys=%d" % (len(finger_nodes), finger_keys))



        for line in sample_lines[:12]:

            self.log("HumanIK arm rotation override sample: %s" % line)



        curves_after = count_anim_curves_on_nodes(target_joints_to_bake)

        stats.update({

            "humanik_arm_rotation_override_enabled": True,

            "humanik_arm_rotation_override_frames": len(frames),

            "humanik_arm_rotation_override_joint_count": len(valid),

            "humanik_arm_rotation_override_keys": keyed,

            "humanik_arm_rotation_override_finger_keys": finger_keys,

            "humanik_arm_rotation_override_max_source_delta": max_source_delta,

            "humanik_arm_rotation_override_target_anim_curves": curves_after,

        })

        self.log(

            "HumanIK arm rotation override finished: joints=%d frames=%d rotate_keys=%d finger_keys=%d target_anim_curves=%d max_source_delta=%.3f"

            % (len(valid), len(frames), keyed, finger_keys, curves_after, max_source_delta)

        )

        return stats





    def _post_correct_humanik_hands_to_leg_front(

        self,

        source_map: Dict[str, str],

        target_map: Dict[str, str],

        target_joints_to_bake: List[str],

        start: float,

        end: float,

        source_rest_positions: Optional[Dict[str, Tuple[float, float, float]]] = None,

        target_rest_positions: Optional[Dict[str, Tuple[float, float, float]]] = None,

        target_rest_local_rotations: Optional[Dict[str, Tuple[float, float, float]]] = None,

    ) -> Dict[str, Any]:

        stats: Dict[str, Any] = {

            "humanik_hand_front_enabled": False,

            "humanik_hand_front_frames": 0,

            "humanik_hand_front_corrections": 0,

        }

        if not bool(getattr(self.config, "humanik_post_correct_hands_to_leg_front", True)):

            self.log("HumanIK hand-front correction skipped: disabled.")

            return stats



        required = ["pelvis", "spine_03", "thigh_l", "thigh_r", "calf_l", "calf_r", "foot_l", "foot_r"]

        missing = [c for c in required if c not in source_map or c not in target_map]

        if missing:

            self.log("HumanIK hand-front correction skipped: missing basis joints: %s" % ", ".join(missing))

            return stats



        sides = [

            ("l", "upperarm_l", "lowerarm_l", "hand_l"),

            ("r", "upperarm_r", "lowerarm_r", "hand_r"),

        ]

        sides = [x for x in sides if all(c in source_map and c in target_map for c in x[1:4])]

        if not sides:

            self.log("HumanIK hand-front correction skipped: no complete arm chains mapped.")

            return stats



        frames = self._build_sample_frames(start, end)

        if not frames:

            return stats



        strength = max(0.0, min(1.0, float(getattr(self.config, "humanik_hand_front_strength", 0.85) or 0.0)))

        side_strength = max(0.0, min(1.0, float(getattr(self.config, "humanik_hand_front_side_strength", 0.20) or 0.0)))

        up_strength = max(0.0, min(1.0, float(getattr(self.config, "humanik_hand_front_up_strength", 0.20) or 0.0)))

        max_pull = max(0.0, float(getattr(self.config, "humanik_hand_front_max_pull_units", 55.0) or 0.0))

        reach_limit = max(0.1, min(1.2, float(getattr(self.config, "humanik_hand_front_reach_limit", 0.95) or 0.95)))

        min_knee_fraction = max(0.0, min(1.0, float(getattr(self.config, "humanik_hand_front_min_knee_fraction", 0.38) or 0.38)))

        same_side_min_units = max(0.0, float(getattr(self.config, "humanik_hand_front_same_side_lock_min_units", 8.0) or 0.0))



        def _leg_front_basis(map_dict: Dict[str, str]):

            pelvis = self._node_world_position_safe(map_dict.get("pelvis"))

            lhip = self._node_world_position_safe(map_dict.get("thigh_l"), pelvis)

            rhip = self._node_world_position_safe(map_dict.get("thigh_r"), pelvis)

            upper = self._node_world_position_safe(map_dict.get("spine_03"), self._node_world_position_safe(map_dict.get("head"), pelvis))

            up = self._v_norm(self._v_sub(upper, pelvis), (0.0, 1.0, 0.0))

            anatomical_right = self._v_norm(self._v_sub(rhip, lhip), (1.0, 0.0, 0.0))



            leg_points = []

            for c in ("calf_l", "calf_r", "foot_l", "foot_r"):

                n = map_dict.get(c)

                if n and safe_cmds_exists(n):

                    leg_points.append(get_world_position(n))

            if leg_points:

                avg = (sum(p[0] for p in leg_points) / len(leg_points), sum(p[1] for p in leg_points) / len(leg_points), sum(p[2] for p in leg_points) / len(leg_points))

                front_raw = self._v_sub(avg, pelvis)

            else:

                front_raw = self._v_cross(anatomical_right, up)

                                                                                          

            front = self._v_sub(front_raw, self._v_mul(up, self._v_dot(front_raw, up)))

            if self._v_len(front) <= 1e-4:

                front = self._v_cross(anatomical_right, up)

            front = self._v_norm(front, (0.0, 0.0, 1.0))



                                  

                                                                                           

                                                                                              

                                                                                               

                                                                                          

                                          

            right_projected = self._v_sub(anatomical_right, self._v_mul(up, self._v_dot(anatomical_right, up)))

            right_projected = self._v_sub(right_projected, self._v_mul(front, self._v_dot(right_projected, front)))

            if self._v_len(right_projected) <= 1e-4:

                right_projected = self._v_cross(up, front)

            right = self._v_norm(right_projected, anatomical_right)

            up2 = self._v_norm(self._v_cross(front, right), up)

            return right, up2, front, pelvis



        def _basis_to_local(world_pos, basis, origin):

            return self._basis_world_to_local(self._v_sub(world_pos, origin), basis)



        def _basis_to_world(local, basis, origin):

            return self._v_add(origin, self._basis_local_to_world(local, basis))



        def _chain_len(a, b, c):

            pa = self._node_world_position_safe(a)

            pb = self._node_world_position_safe(b, pa)

            pc = self._node_world_position_safe(c, pb)

            return max(self._v_len(self._v_sub(pb, pa)) + self._v_len(self._v_sub(pc, pb)), 1.0)



        temp_nodes: List[str] = []

        constraints: List[str] = []

        ik_handles: List[str] = []

        end_locs: Dict[str, str] = {}

        pole_locs: Dict[str, str] = {}

        chain_lengths: Dict[str, float] = {}



        for side, start_c, mid_c, end_c in sides:

            label = "front_hand_%s" % side

            end_locs[label] = self._make_temp_locator("ALPHA_HIKHandFront_%s_END_LOC" % side, self._node_world_position_safe(target_map.get(end_c)))

            pole_locs[label] = self._make_temp_locator("ALPHA_HIKHandFront_%s_POLE_LOC" % side, self._node_world_position_safe(target_map.get(mid_c)))

            temp_nodes.extend([end_locs[label], pole_locs[label]])

            chain_lengths[label] = _chain_len(target_map.get(start_c), target_map.get(mid_c), target_map.get(end_c))



        corrections = 0

        side_corrections = 0

        front_corrections = 0

        max_front_error = 0.0

        max_side_error = 0.0

        keyed_driver_channels = 0

        self.log(

            "HumanIK hand-front correction: sides=%d frames=%d strength=%.2f side=%.2f up=%.2f max_pull=%.2f reach=%.2f knee_fraction=%.2f same_side_min=%.2f"

            % (len(sides), len(frames), strength, side_strength, up_strength, max_pull, reach_limit, min_knee_fraction, same_side_min_units)

        )



        for frame in frames:

            cmds.currentTime(frame, edit=True, update=True)

            try:

                cmds.refresh(force=True)

            except Exception:

                pass



            src_right, src_up, src_front, src_pelvis = _leg_front_basis(source_map)

            tgt_right, tgt_up, tgt_front, tgt_pelvis = _leg_front_basis(target_map)

            src_basis = (src_right, src_up, src_front)

            tgt_basis = (tgt_right, tgt_up, tgt_front)



                                                                                                    

                                                                                                  

                                                                               

            knee_front_values = []

            for c in ("calf_l", "calf_r", "foot_l", "foot_r"):

                try:

                    knee_front_values.append(_basis_to_local(get_world_position(target_map[c]), tgt_basis, tgt_pelvis)[2])

                except Exception:

                    pass

            positive_leg_front = max([v for v in knee_front_values if v > 0.0] or [0.0])

            min_front = positive_leg_front * min_knee_fraction



                                                                                         

            if frame in (frames[0], frames[len(frames)//2], frames[-1]):

                hand_front_values = []

                hand_side_values = []

                shoulder_side_values = []

                for _side, _start_c, _mid_c, _end_c in sides:

                    try:

                        hand_l_sample = _basis_to_local(get_world_position(target_map[_end_c]), tgt_basis, tgt_pelvis)

                        shoulder_l_sample = _basis_to_local(get_world_position(target_map[_start_c]), tgt_basis, tgt_pelvis)

                        hand_front_values.append(hand_l_sample[2])

                        hand_side_values.append(hand_l_sample[0])

                        shoulder_side_values.append(shoulder_l_sample[0])

                    except Exception:

                        pass

                if hand_front_values:

                    self.log(

                        "HumanIK hand-front sample f=%.2f leg_front=%.3f min_front=%.3f hand_front_min=%.3f hand_front_max=%.3f hand_side=%s shoulder_side=%s"

                        % (frame, positive_leg_front, min_front, min(hand_front_values), max(hand_front_values), [round(v,3) for v in hand_side_values], [round(v,3) for v in shoulder_side_values])

                    )



            for side, start_c, mid_c, end_c in sides:

                label = "front_hand_%s" % side

                src_hand_l = _basis_to_local(get_world_position(source_map[end_c]), src_basis, src_pelvis)

                src_elbow_l = _basis_to_local(get_world_position(source_map[mid_c]), src_basis, src_pelvis)

                tgt_hand = get_world_position(target_map[end_c])

                tgt_elbow = get_world_position(target_map[mid_c])

                tgt_shoulder = get_world_position(target_map[start_c])

                tgt_hip = get_world_position(target_map.get("thigh_%s" % side, target_map.get("pelvis")))

                tgt_hand_l = _basis_to_local(tgt_hand, tgt_basis, tgt_pelvis)

                tgt_elbow_l = _basis_to_local(tgt_elbow, tgt_basis, tgt_pelvis)

                tgt_shoulder_l = _basis_to_local(tgt_shoulder, tgt_basis, tgt_pelvis)

                tgt_hip_l = _basis_to_local(tgt_hip, tgt_basis, tgt_pelvis)



                                             

                                                                                                   

                                                                                                    

                                                                                                     

                                                                                                        

                                                                       

                side_source_values = [tgt_shoulder_l[0], tgt_hip_l[0], tgt_elbow_l[0]]

                side_sign = 1.0

                for _v in side_source_values:

                    if abs(_v) > 0.25:

                        side_sign = 1.0 if _v >= 0.0 else -1.0

                        break



                current_same_side = tgt_hand_l[0] * side_sign

                target_side_width = max(abs(tgt_shoulder_l[0]), abs(tgt_hip_l[0]), same_side_min_units, 1.0)

                min_side_abs = max(

                    same_side_min_units,

                    abs(tgt_shoulder_l[0]) * 0.45,

                    abs(tgt_hip_l[0]) * 0.55,

                )



                                                                                                         

                                                                                             

                src_shoulder_l = _basis_to_local(get_world_position(source_map[start_c]), src_basis, src_pelvis)

                src_hip_l = _basis_to_local(get_world_position(source_map.get("thigh_%s" % side, source_map.get("pelvis"))), src_basis, src_pelvis)

                src_width = max(abs(src_shoulder_l[0]), abs(src_hip_l[0]), 1.0)

                src_side_ratio = max(0.25, min(1.20, abs(src_hand_l[0]) / src_width))

                desired_side_abs = max(min_side_abs, min(target_side_width * 1.15, target_side_width * src_side_ratio))



                                                                                                    

                                                                                                      

                if current_same_side > desired_side_abs:

                    desired_side_abs = current_same_side



                desired_side = side_sign * desired_side_abs

                side_error = desired_side - tgt_hand_l[0]

                max_side_error = max(max_side_error, abs(side_error))



                                                                                                           

                                                                                                            

                desired_front = max(src_hand_l[2], min_front)

                front_error = desired_front - tgt_hand_l[2]

                max_front_error = max(max_front_error, abs(front_error))



                needs_front_fix = front_error > 0.75

                needs_side_fix = abs(side_error) > 0.75



                                                                                                    

                                                                     

                if not needs_front_fix and not needs_side_fix:

                    desired_world = tgt_hand

                else:

                    desired_local = (

                        tgt_hand_l[0] + side_error * max(0.65, side_strength),

                        tgt_hand_l[1] + (src_hand_l[1] - tgt_hand_l[1]) * up_strength,

                        tgt_hand_l[2] + max(front_error, 0.0) * strength,

                    )

                    desired_world = _basis_to_world(desired_local, tgt_basis, tgt_pelvis)



                                                                  

                    shoulder_to_desired = self._v_sub(desired_world, tgt_shoulder)

                    desired_len = self._v_len(shoulder_to_desired)

                    max_reach = chain_lengths[label] * reach_limit

                    if desired_len > max_reach:

                        desired_world = self._v_add(tgt_shoulder, self._v_mul(self._v_norm(shoulder_to_desired), max_reach))



                                                                       

                    delta = self._v_sub(desired_world, tgt_hand)

                    delta_len = self._v_len(delta)

                    if max_pull > 0.0 and delta_len > max_pull:

                        desired_world = self._v_add(tgt_hand, self._v_mul(self._v_norm(delta), max_pull))

                    corrections += 1

                    if needs_front_fix:

                        front_corrections += 1

                    if needs_side_fix:

                        side_corrections += 1



                self._set_and_key_locator_pos(end_locs[label], desired_world, frame)

                keyed_driver_channels += 3



                                                                                                     

                                                                                                 

                elbow_same_side = tgt_elbow_l[0] * side_sign

                elbow_side_abs = max(elbow_same_side, min_side_abs * 0.75)

                desired_elbow_l = (

                    side_sign * elbow_side_abs,

                    tgt_elbow_l[1] + (src_elbow_l[1] - tgt_elbow_l[1]) * up_strength,

                    max(tgt_elbow_l[2], min_front * 0.35),

                )

                desired_elbow = _basis_to_world(desired_elbow_l, tgt_basis, tgt_pelvis)

                pole_target = self._make_pole_position(tgt_shoulder, desired_elbow, desired_world, fallback_axis=tgt_front, scale=1.0)

                pole_target = self._v_add(tgt_elbow, self._v_mul(self._v_sub(pole_target, tgt_elbow), 0.50))

                self._set_and_key_locator_pos(pole_locs[label], pole_target, frame)

                keyed_driver_channels += 3



        for side, start_c, mid_c, end_c in sides:

            label = "front_hand_%s" % side

            handle = self._create_ik_handle_safe("ALPHA_HIKHandFront_%s_IKH" % side, target_map.get(start_c), target_map.get(end_c))

            if not handle:

                continue

            temp_nodes.append(handle)

            ik_handles.append(handle)

            try:

                constraints.append(cmds.pointConstraint(end_locs[label], handle, maintainOffset=False)[0])

            except Exception as exc:

                self.log("HumanIK hand-front WARNING: could not pointConstraint %s: %s" % (label, exc))

            try:

                constraints.append(cmds.poleVectorConstraint(pole_locs[label], handle)[0])

            except Exception as exc:

                self.log("HumanIK hand-front WARNING: could not poleVectorConstraint %s: %s" % (label, exc))



        translate_key_nodes = set()

        for c in ("root", "pelvis"):

            n = target_map.get(c)

            if n and safe_cmds_exists(n):

                translate_key_nodes.add(n)



        if corrections == 0 and (max_front_error > 5.0 or max_side_error > 5.0):

            self.log(

                "HumanIK hand-front WARNING: max_front_error is high but corrections are 0. This usually means the basis/threshold still needs review."

            )

        self.log(

            "HumanIK hand-front correction: corrections=%d front_corrections=%d side_corrections=%d max_front_error=%.3f max_side_error=%.3f constraints=%d ik_handles=%d. Baking target hierarchy..."

            % (corrections, front_corrections, side_corrections, max_front_error, max_side_error, len(constraints), len(ik_handles))

        )

        bake_stats = self._manual_sample_solved_joint_animation(

            target_joints_to_bake,

            frames,

            translate_key_nodes=translate_key_nodes,

            temp_nodes=constraints + temp_nodes,

            label="humanik_hand_front",

        )

        curves_after = count_anim_curves_on_nodes(target_joints_to_bake)

        stats.update({

            "humanik_hand_front_enabled": True,

            "humanik_hand_front_frames": len(frames),

            "humanik_hand_front_corrections": corrections,

            "humanik_hand_front_max_error": max_front_error,

            "humanik_hand_front_max_side_error": max_side_error,

            "humanik_hand_front_front_corrections": front_corrections,

            "humanik_hand_front_side_corrections": side_corrections,

            "humanik_hand_front_ik_handles": len(ik_handles),

            "humanik_hand_front_driver_keyed_channels": keyed_driver_channels,

            "humanik_hand_front_target_anim_curves": curves_after,

            "humanik_hand_front_manual_bake": bake_stats,

        })

        self.log(

            "HumanIK hand-front correction finished: frames=%d corrections=%d front_corrections=%d side_corrections=%d ik_handles=%d target_anim_curves=%d"

            % (len(frames), corrections, front_corrections, side_corrections, len(ik_handles), curves_after)

        )

        return stats



    def _post_match_humanik_hands(

        self,

        source_map: Dict[str, str],

        target_map: Dict[str, str],

        source_rest_map: Dict[str, str],

        target_rest_positions: Dict[str, Tuple[float, float, float]],

        target_joints_to_bake: List[str],

        start: float,

        end: float,

    ) -> Dict[str, Any]:

        stats: Dict[str, Any] = {

            "humanik_post_match_hands_enabled": False,

            "humanik_post_match_hands_frames": 0,

        }

        if not bool(getattr(self.config, "humanik_post_match_hands", True)):

            self.log("HumanIK hand match skipped: disabled.")

            return stats



        required_basis = ["pelvis", "spine_03", "thigh_l", "thigh_r"]

        missing_basis = [c for c in required_basis if c not in source_map or c not in target_map]

        if missing_basis:

            self.log("HumanIK hand match skipped: missing body basis joints: %s" % ", ".join(missing_basis))

            return stats



        sides = [

            ("l", "upperarm_l", "lowerarm_l", "hand_l"),

            ("r", "upperarm_r", "lowerarm_r", "hand_r"),

        ]

        sides = [x for x in sides if all(c in source_map and c in target_map for c in x[1:4])]

        if not sides:

            self.log("HumanIK hand match skipped: no complete arm chains mapped.")

            return stats



        frames = self._build_sample_frames(start, end)

        if not frames:

            return stats



                                                          

        source_rest_positions: Dict[str, Tuple[float, float, float]] = {}

        for c, n in (source_rest_map or {}).items():

            if n and safe_cmds_exists(n):

                try:

                    source_rest_positions[c] = get_world_position(n)

                except Exception:

                    pass

        scale_ratio = 1.0

        if "pelvis" in source_rest_positions and "head" in source_rest_positions and "pelvis" in target_rest_positions and "head" in target_rest_positions:

            src_h = max(self._v_len(self._v_sub(source_rest_positions["head"], source_rest_positions["pelvis"])), 1.0)

            tgt_h = max(self._v_len(self._v_sub(target_rest_positions["head"], target_rest_positions["pelvis"])), 1.0)

            scale_ratio = tgt_h / src_h



        strength = max(0.0, min(1.0, float(getattr(self.config, "humanik_hand_match_strength", 0.70) or 0.0)))

        pole_strength = max(0.0, min(1.0, float(getattr(self.config, "humanik_hand_match_pole_strength", 0.65) or 0.0)))

        max_pull = max(0.0, float(getattr(self.config, "humanik_hand_match_max_pull_units", 45.0) or 0.0))

        reach_limit = max(0.1, min(1.2, float(getattr(self.config, "humanik_hand_match_reach_limit", 0.96) or 0.96)))

        stabilize_fingers = bool(getattr(self.config, "humanik_hand_match_key_fingers_to_rest", True))



        def _basis_from_current(map_dict: Dict[str, str]):

            pelvis = self._node_world_position_safe(map_dict.get("pelvis"))

            left_hip = self._node_world_position_safe(map_dict.get("thigh_l"), pelvis)

            right_hip = self._node_world_position_safe(map_dict.get("thigh_r"), pelvis)

            upper = self._node_world_position_safe(map_dict.get("spine_03"), self._node_world_position_safe(map_dict.get("head"), pelvis))

            return self._basis_from_positions(pelvis, left_hip, right_hip, upper)



        def _chain_len(start_j, mid_j, end_j):

            a = self._node_world_position_safe(start_j)

            b = self._node_world_position_safe(mid_j, a)

            c = self._node_world_position_safe(end_j, b)

            return max(self._v_len(self._v_sub(b, a)) + self._v_len(self._v_sub(c, b)), 1.0)



        temp_nodes: List[str] = []

        constraints: List[str] = []

        ik_handles: List[str] = []

        end_locs: Dict[str, str] = {}

        pole_locs: Dict[str, str] = {}

        chain_lengths: Dict[str, float] = {}



        for side, start_c, mid_c, end_c in sides:

            label = "hand_%s" % side

            end_locs[label] = self._make_temp_locator("ALPHA_HIKHandMatch_%s_END_LOC" % side, self._node_world_position_safe(target_map.get(end_c)))

            pole_locs[label] = self._make_temp_locator("ALPHA_HIKHandMatch_%s_POLE_LOC" % side, self._node_world_position_safe(target_map.get(mid_c)))

            temp_nodes.extend([end_locs[label], pole_locs[label]])

            chain_lengths[label] = _chain_len(target_map.get(start_c), target_map.get(mid_c), target_map.get(end_c))



        keyed_driver_channels = 0

        self.log(

            "HumanIK hand match: sides=%d frames=%d scale_ratio=%.4f strength=%.2f pole=%.2f max_pull=%.2f reach=%.2f"

            % (len(sides), len(frames), scale_ratio, strength, pole_strength, max_pull, reach_limit)

        )



        for frame in frames:

            cmds.currentTime(frame, edit=True, update=True)

            try:

                cmds.refresh(force=True)

            except Exception:

                pass

            src_pelvis = get_world_position(source_map["pelvis"])

            tgt_pelvis = get_world_position(target_map["pelvis"])

            src_basis = _basis_from_current(source_map)

            tgt_basis = _basis_from_current(target_map)



            for side, start_c, mid_c, end_c in sides:

                label = "hand_%s" % side

                src_hand = get_world_position(source_map[end_c])

                src_elbow = get_world_position(source_map[mid_c])

                tgt_shoulder = get_world_position(target_map[start_c])

                tgt_elbow_current = get_world_position(target_map[mid_c])

                tgt_hand_current = get_world_position(target_map[end_c])



                                                                                             

                src_hand_local = self._basis_world_to_local(self._v_sub(src_hand, src_pelvis), src_basis)

                desired_hand = self._v_add(tgt_pelvis, self._v_mul(self._basis_local_to_world(src_hand_local, tgt_basis), scale_ratio))



                                                                                                 

                shoulder_to_desired = self._v_sub(desired_hand, tgt_shoulder)

                desired_len = self._v_len(shoulder_to_desired)

                max_reach = chain_lengths[label] * reach_limit

                if desired_len > max_reach:

                    desired_hand = self._v_add(tgt_shoulder, self._v_mul(self._v_norm(shoulder_to_desired), max_reach))



                                                                                 

                delta = self._v_sub(desired_hand, tgt_hand_current)

                delta_len = self._v_len(delta)

                if max_pull > 0.0 and delta_len > max_pull:

                    delta = self._v_mul(self._v_norm(delta), max_pull)

                desired_hand = self._v_add(tgt_hand_current, self._v_mul(delta, strength))

                self._set_and_key_locator_pos(end_locs[label], desired_hand, frame)

                keyed_driver_channels += 3



                                                                                                    

                src_elbow_local = self._basis_world_to_local(self._v_sub(src_elbow, src_pelvis), src_basis)

                desired_elbow = self._v_add(tgt_pelvis, self._v_mul(self._basis_local_to_world(src_elbow_local, tgt_basis), scale_ratio))

                pole_target = self._make_pole_position(tgt_shoulder, desired_elbow, desired_hand, fallback_axis=(0.0, 0.0, 1.0), scale=max(scale_ratio, 0.1))

                pole_target = self._v_add(tgt_elbow_current, self._v_mul(self._v_sub(pole_target, tgt_elbow_current), pole_strength))

                self._set_and_key_locator_pos(pole_locs[label], pole_target, frame)

                keyed_driver_channels += 3



        for side, start_c, mid_c, end_c in sides:

            label = "hand_%s" % side

            handle = self._create_ik_handle_safe("ALPHA_HIKHandMatch_%s_IKH" % side, target_map.get(start_c), target_map.get(end_c))

            if not handle:

                continue

            temp_nodes.append(handle)

            ik_handles.append(handle)

            try:

                constraints.append(cmds.pointConstraint(end_locs[label], handle, maintainOffset=False)[0])

            except Exception as exc:

                self.log("HumanIK hand match WARNING: could not pointConstraint %s: %s" % (label, exc))

            try:

                constraints.append(cmds.poleVectorConstraint(pole_locs[label], handle)[0])

            except Exception as exc:

                self.log("HumanIK hand match WARNING: could not poleVectorConstraint %s: %s" % (label, exc))



        translate_key_nodes = set()

        for c in ("root", "pelvis"):

            n = target_map.get(c)

            if n and safe_cmds_exists(n):

                translate_key_nodes.add(n)



                                                                                                

        self.log(

            "HumanIK hand match: constraints=%d ik_handles=%d. Manually baking target hierarchy after hand solve..."

            % (len(constraints), len(ik_handles))

        )

        bake_stats = self._manual_sample_solved_joint_animation(

            target_joints_to_bake,

            frames,

            translate_key_nodes=translate_key_nodes,

            temp_nodes=constraints + temp_nodes,

            label="humanik_hand_match",

        )



                                                                                                

                                                                                                   

                                                                                                       

        finger_key_count = 0

        if stabilize_fingers:

            finger_tokens = ("thumb", "index", "middle", "ring", "pinky")

            finger_joints = [j for j in target_joints_to_bake if any(tok in short_name(j).lower() for tok in finger_tokens)]

            if finger_joints:

                rest_values = {}

                cmds.currentTime(start, edit=True, update=True)

                for j in finger_joints:

                    try:

                        rest_values[j] = tuple(cmds.getAttr(j + ".rotate")[0])

                    except Exception:

                        pass

                for frame in frames:

                    cmds.currentTime(frame, edit=True, update=True)

                    for j, rot in rest_values.items():

                        try:

                            cmds.setAttr(j + ".rotate", float(rot[0]), float(rot[1]), float(rot[2]))

                            cmds.setKeyframe(j, attribute=ROTATE_ATTRS, time=frame)

                            finger_key_count += 3

                        except Exception:

                            pass



        curves_after = count_anim_curves_on_nodes(target_joints_to_bake)

        stats.update({

            "humanik_post_match_hands_enabled": True,

            "humanik_post_match_hands_frames": len(frames),

            "humanik_post_match_hands_sides": len(sides),

            "humanik_post_match_hands_driver_keyed_channels": keyed_driver_channels,

            "humanik_post_match_hands_ik_handles": len(ik_handles),

            "humanik_post_match_hands_finger_key_count": finger_key_count,

            "humanik_post_match_hands_target_anim_curves": curves_after,

            "humanik_post_match_hands_manual_bake": bake_stats,

        })

        self.log(

            "HumanIK hand match finished: sides=%d ik_handles=%d driver_keys=%d finger_keys=%d target_anim_curves=%d"

            % (len(sides), len(ik_handles), keyed_driver_channels, finger_key_count, curves_after)

        )

        return stats



    def _post_refine_humanik_limbs(

        self,

        source_map: Dict[str, str],

        target_map: Dict[str, str],

        source_rest_map: Dict[str, str],

        target_rest_positions: Dict[str, Tuple[float, float, float]],

        target_joints_to_bake: List[str],

        start: float,

        end: float,

    ) -> Dict[str, Any]:

        stats: Dict[str, Any] = {

            "humanik_post_refine_enabled": False,

            "humanik_post_refine_frames": 0,

        }

        if not bool(getattr(self.config, "humanik_post_refine_limbs", False)):

            self.log("HumanIK limb refine skipped: disabled. This is the stable default; v1.2.4 refinement over-pulled this skeleton pair.")

            return stats



        required_basis = ["pelvis", "spine_03", "thigh_l", "thigh_r"]

        missing_basis = [c for c in required_basis if c not in source_map or c not in target_map]

        if missing_basis:

            self.log("HumanIK limb refine skipped: missing body basis joints: %s" % ", ".join(missing_basis))

            return stats



        frames = self._build_sample_frames(start, end)

        if not frames:

            return stats



                                                                                             

                                                                    

        source_rest_positions: Dict[str, Tuple[float, float, float]] = {}

        for c, n in (source_rest_map or {}).items():

            if n and safe_cmds_exists(n):

                try:

                    source_rest_positions[c] = get_world_position(n)

                except Exception:

                    pass

        scale_ratio = 1.0

        if "pelvis" in source_rest_positions and "head" in source_rest_positions and "pelvis" in target_rest_positions and "head" in target_rest_positions:

            src_h = max(self._v_len(self._v_sub(source_rest_positions["head"], source_rest_positions["pelvis"])), 1.0)

            tgt_h = max(self._v_len(self._v_sub(target_rest_positions["head"], target_rest_positions["pelvis"])), 1.0)

            scale_ratio = tgt_h / src_h



        overall_strength = max(0.0, min(1.0, float(getattr(self.config, "humanik_post_refine_strength", 0.90) or 0.0)))

        arm_strength = overall_strength * max(0.0, min(1.0, float(getattr(self.config, "humanik_post_refine_arm_strength", 0.85) or 0.0)))

        leg_strength = overall_strength * max(0.0, min(1.0, float(getattr(self.config, "humanik_post_refine_leg_strength", 1.00) or 0.0)))

        pole_strength = overall_strength * max(0.0, min(1.0, float(getattr(self.config, "humanik_post_refine_pole_strength", 1.00) or 0.0)))

        refine_hands = bool(getattr(self.config, "humanik_post_refine_hands", True))

        refine_feet = bool(getattr(self.config, "humanik_post_refine_feet", True))

        refine_poles = bool(getattr(self.config, "humanik_post_refine_poles", True))



        limb_specs: List[Tuple[str, str, str, str, float]] = []

        if refine_feet:

            limb_specs.extend([

                ("leg_l", "thigh_l", "calf_l", "foot_l", leg_strength),

                ("leg_r", "thigh_r", "calf_r", "foot_r", leg_strength),

            ])

        if refine_hands:

            limb_specs.extend([

                ("arm_l", "upperarm_l", "lowerarm_l", "hand_l", arm_strength),

                ("arm_r", "upperarm_r", "lowerarm_r", "hand_r", arm_strength),

            ])

        limb_specs = [x for x in limb_specs if all(c in source_map and c in target_map for c in x[1:4])]

        if not limb_specs:

            self.log("HumanIK limb refine skipped: no complete arm/leg chains were mapped.")

            return stats



        def _basis_from_current(map_dict: Dict[str, str]):

            pelvis = self._node_world_position_safe(map_dict.get("pelvis"))

            left_hip = self._node_world_position_safe(map_dict.get("thigh_l"), pelvis)

            right_hip = self._node_world_position_safe(map_dict.get("thigh_r"), pelvis)

            upper = self._node_world_position_safe(map_dict.get("spine_03"), self._node_world_position_safe(map_dict.get("head"), pelvis))

            return self._basis_from_positions(pelvis, left_hip, right_hip, upper)



        def _mapped_source_point(canonical: str, src_basis, tgt_basis, src_pelvis, tgt_pelvis, strength: float):

            src_node = source_map.get(canonical)

            tgt_node = target_map.get(canonical)

            if not (src_node and tgt_node and safe_cmds_exists(src_node) and safe_cmds_exists(tgt_node)):

                return None

            src_p = get_world_position(src_node)

            tgt_current = get_world_position(tgt_node)

            src_rel = self._v_sub(src_p, src_pelvis)

            src_local = self._basis_world_to_local(src_rel, src_basis)

            mapped_rel = self._basis_local_to_world(src_local, tgt_basis)

            desired = self._v_add(tgt_pelvis, self._v_mul(mapped_rel, scale_ratio))

                                                                                               

                                                                 

            return self._v_add(tgt_current, self._v_mul(self._v_sub(desired, tgt_current), strength))



        temp_nodes: List[str] = []

        constraints: List[str] = []

        ik_handles: List[str] = []

        end_locs: Dict[str, str] = {}

        pole_locs: Dict[str, str] = {}



        for label, _start_c, _mid_c, end_c, _strength in limb_specs:

            loc = self._make_temp_locator("ALPHA_HIKRefine_%s_END_LOC" % label, self._node_world_position_safe(target_map.get(end_c)))

            end_locs[label] = loc

            temp_nodes.append(loc)

            pole = self._make_temp_locator("ALPHA_HIKRefine_%s_POLE_LOC" % label, self._node_world_position_safe(target_map.get(_mid_c)))

            pole_locs[label] = pole

            temp_nodes.append(pole)



        keyed_driver_channels = 0

        self.log(

            "HumanIK limb refine: chains=%d frames=%d scale_ratio=%.4f overall=%.2f arms=%.2f legs=%.2f poles=%.2f"

            % (len(limb_specs), len(frames), scale_ratio, overall_strength, arm_strength, leg_strength, pole_strength)

        )



        for frame in frames:

            cmds.currentTime(frame, edit=True, update=True)

            try:

                cmds.refresh(force=True)

            except Exception:

                pass

            src_pelvis = get_world_position(source_map["pelvis"])

            tgt_pelvis = get_world_position(target_map["pelvis"])

            src_basis = _basis_from_current(source_map)

            tgt_basis = _basis_from_current(target_map)



                                                                                                 

            desired_cache: Dict[str, Tuple[float, float, float]] = {}

            for _label, start_c, mid_c, end_c, strength in limb_specs:

                for c in (start_c, mid_c, end_c):

                    if c not in desired_cache:

                        desired = _mapped_source_point(c, src_basis, tgt_basis, src_pelvis, tgt_pelvis, 1.0)

                        if desired is not None:

                            desired_cache[c] = desired

                end_desired = _mapped_source_point(end_c, src_basis, tgt_basis, src_pelvis, tgt_pelvis, strength)

                if end_desired is not None:

                    self._set_and_key_locator_pos(end_locs[_label], end_desired, frame)

                    keyed_driver_channels += 3



                if refine_poles and start_c in desired_cache and mid_c in desired_cache and end_c in desired_cache:

                    pole_target = self._make_pole_position(

                        desired_cache[start_c], desired_cache[mid_c], desired_cache[end_c],

                        fallback_axis=(0.0, 0.0, 1.0), scale=max(scale_ratio, 0.1)

                    )

                    current_pole = self._node_world_position_safe(target_map.get(mid_c), desired_cache[mid_c])

                    pole_target = self._v_add(current_pole, self._v_mul(self._v_sub(pole_target, current_pole), pole_strength))

                    self._set_and_key_locator_pos(pole_locs[_label], pole_target, frame)

                    keyed_driver_channels += 3



                                                                                                 

        for label, start_c, mid_c, end_c, _strength in limb_specs:

            start_t = target_map.get(start_c)

            end_t = target_map.get(end_c)

            handle = self._create_ik_handle_safe("ALPHA_HIKRefine_%s_IKH" % label, start_t, end_t)

            if not handle:

                continue

            temp_nodes.append(handle)

            ik_handles.append(handle)

            try:

                constraints.append(cmds.pointConstraint(end_locs[label], handle, maintainOffset=False)[0])

            except Exception as exc:

                self.log("HumanIK limb refine WARNING: could not pointConstraint %s IK handle: %s" % (label, exc))

            if refine_poles:

                try:

                    constraints.append(cmds.poleVectorConstraint(pole_locs[label], handle)[0])

                except Exception as exc:

                    self.log("HumanIK limb refine WARNING: could not poleVectorConstraint %s: %s" % (label, exc))



        translate_key_nodes = set()

        for c in ("root", "pelvis"):

            n = target_map.get(c)

            if n and safe_cmds_exists(n):

                translate_key_nodes.add(n)



        self.log(

            "HumanIK limb refine: constraints=%d ik_handles=%d. Manually baking refined target pose on %d joints..."

            % (len(constraints), len(ik_handles), len(target_joints_to_bake))

        )

        bake_stats = self._manual_sample_solved_joint_animation(

            target_joints_to_bake,

            frames,

            translate_key_nodes=translate_key_nodes,

            temp_nodes=constraints + temp_nodes,

            label="humanik_limb_refine",

        )

        curves_after = count_anim_curves_on_nodes(target_joints_to_bake)

        stats.update({

            "humanik_post_refine_enabled": True,

            "humanik_post_refine_frames": len(frames),

            "humanik_post_refine_scale_ratio": scale_ratio,

            "humanik_post_refine_chain_count": len(limb_specs),

            "humanik_post_refine_ik_handle_count": len(ik_handles),

            "humanik_post_refine_driver_keyed_channels": keyed_driver_channels,

            "humanik_post_refine_target_anim_curves": curves_after,

        })

        stats.update({"humanik_post_refine_manual_bake": bake_stats})

        self.log(

            "HumanIK limb refine finished: chains=%d ik_handles=%d driver_keys=%d target_anim_curves=%d"

            % (len(limb_specs), len(ik_handles), keyed_driver_channels, curves_after)

        )

        return stats



    def _find_hik_slot_joint_by_short_name(self, joints: Iterable[str], names: Iterable[str]) -> Optional[str]:

        wanted = [str(n) for n in names if n]

        for name in wanted:

            for node in joints or []:

                try:

                    if safe_cmds_exists(node) and short_name(node) == name:

                        return node

                except Exception:

                    pass

                                                                                   

        for name in wanted:

            try:

                hits = cmds.ls(name, type="joint", long=True) or []

                if hits:

                    return hits[0]

            except Exception:

                pass

        return None



    def _apply_humanik_smplh_femalestd_slot_overrides(

        self,

        source_map: Dict[str, str],

        target_map: Dict[str, str],

        source_joints: Iterable[str],

        target_joints: Iterable[str],

    ) -> Dict[str, Any]:

        stats: Dict[str, Any] = {"humanik_compressed_spine_slots_enabled": False}

        if not bool(getattr(self.config, "humanik_use_compressed_femalestd_spine_slots", True)):

            return stats

        src_s1 = self._find_hik_slot_joint_by_short_name(source_joints, ["Spine1"])

        src_s2 = self._find_hik_slot_joint_by_short_name(source_joints, ["Spine2"])

        src_s3 = self._find_hik_slot_joint_by_short_name(source_joints, ["Spine3"])

        tgt_s1 = self._find_hik_slot_joint_by_short_name(target_joints, ["spine_01"])

        tgt_s3 = self._find_hik_slot_joint_by_short_name(target_joints, ["spine_03"])

        tgt_s5 = self._find_hik_slot_joint_by_short_name(target_joints, ["spine_05"])

        changed = []

        if src_s1:

            source_map["spine_01"] = src_s1; changed.append("source spine_01=Spine1")

        if src_s2:

            source_map["spine_02"] = src_s2; changed.append("source spine_02=Spine2")

        if src_s3:

            source_map["spine_03"] = src_s3; changed.append("source spine_03=Spine3")

        if tgt_s1:

            target_map["spine_01"] = tgt_s1; changed.append("target spine_01=spine_01")

        if tgt_s3:

            target_map["spine_02"] = tgt_s3; changed.append("target spine_02=spine_03")

        if tgt_s5:

            target_map["spine_03"] = tgt_s5; changed.append("target spine_03=spine_05")

        stats.update({

            "humanik_compressed_spine_slots_enabled": True,

            "humanik_compressed_spine_slots": changed,

            "humanik_target_spine_slots": {

                "spine_01": short_name(target_map.get("spine_01", "")),

                "spine_02": short_name(target_map.get("spine_02", "")),

                "spine_03": short_name(target_map.get("spine_03", "")),

            },

        })

        self.log("HumanIK v1.3.0 slot fix: compressed FemaleStd spine slots -> %s" % stats["humanik_target_spine_slots"])

        return stats



    def _retarget_with_humanik_batch(

        self,

        source_joints: List[str],

        target_joints: List[str],

        start: float,

        end: float,

        source_rest_joints: Optional[List[str]] = None,

    ) -> Dict[str, Any]:

        require_maya()

        stats: Dict[str, Any] = {"retarget_method": "humanik_batch"}

        pairs = self.mapping.build_source_target_pairs(source_joints, target_joints)

        if len(pairs) < len(HIK_REQUIRED_CANONICAL):

            raise RuntimeError("HumanIK requires a full humanoid mapping; resolved only %d source-target pairs." % len(pairs))



        live_source_map = self._hik_build_canonical_map(source_joints, pairs, 0)

        target_map = self._hik_build_canonical_map(target_joints, pairs, 1)



                                                                                           

                                                                                             

                                                                                            

                                                                              

        use_rest_character_source = bool(getattr(self.config, "humanik_use_rest_characterized_source", True)) and bool(source_rest_joints)

        if use_rest_character_source:

            rest_pairs_for_source = self.mapping.build_source_target_pairs(source_rest_joints or [], target_joints)

            if len(rest_pairs_for_source) >= len(HIK_REQUIRED_CANONICAL):

                source_map = self._hik_build_canonical_map(source_rest_joints or [], rest_pairs_for_source, 0)

                source_hik_joints_for_slots = list(source_rest_joints or [])

                self.log("HumanIK v1.3.0: using rest-characterized source duplicate for HIK definition. live_source_pairs=%d rest_source_pairs=%d" % (len(pairs), len(rest_pairs_for_source)))

            else:

                source_map = live_source_map

                source_hik_joints_for_slots = list(source_joints or [])

                use_rest_character_source = False

                self.log("HumanIK v1.3.0 WARNING: rest-character source requested but only %d rest pairs resolved; falling back to live source characterization." % len(rest_pairs_for_source))

        else:

            source_map = live_source_map

            source_hik_joints_for_slots = list(source_joints or [])



        source_rest_map = self.mapping.build_canonical_map(source_rest_joints or []) if source_rest_joints else {}

        if "root" not in source_rest_map and "pelvis" in source_rest_map:

            try:

                parent = cmds.listRelatives(source_rest_map["pelvis"], parent=True, fullPath=True) or []

                if parent:

                    source_rest_map["root"] = parent[0]

            except Exception:

                pass

        target_rest_positions = {}

        for _canon, _node in target_map.items():

            if _node and safe_cmds_exists(_node):

                try:

                    target_rest_positions[_canon] = get_world_position(_node)

                except Exception:

                    pass



                                                                                             

                                                                                         

                                                                                                 

        source_hik_rest_positions = {}

        for _canon, _node in source_map.items():

            if _node and safe_cmds_exists(_node):

                try:

                    source_hik_rest_positions[_canon] = get_world_position(_node)

                except Exception:

                    pass



                                                                                                  

                                                                                                       

                                                               

        humanik_arm_canonicals = [

            "clavicle_l", "upperarm_l", "lowerarm_l", "hand_l",

            "clavicle_r", "upperarm_r", "lowerarm_r", "hand_r",

        ]

        source_hik_rest_local_matrices = {}

        source_hik_rest_local_rotations = {}

        target_rest_local_matrices = {}

        target_rest_local_translates = {}

        target_rest_local_rotations = {}

        for _canon in humanik_arm_canonicals:

            _src_node = source_map.get(_canon)

            _tgt_node = target_map.get(_canon)

            if _src_node and safe_cmds_exists(_src_node):

                try:

                    source_hik_rest_local_matrices[_canon] = self._matrix_from_node_local(_src_node)

                    source_hik_rest_local_rotations[_canon] = self._get_vec(_src_node, ROTATE_ATTRS)

                except Exception:

                    pass

            if _tgt_node and safe_cmds_exists(_tgt_node):

                try:

                    target_rest_local_matrices[_canon] = self._matrix_from_node_local(_tgt_node)

                    target_rest_local_translates[_canon] = self._get_vec(_tgt_node, TRANSLATE_ATTRS)

                    target_rest_local_rotations[_canon] = self._get_vec(_tgt_node, ROTATE_ATTRS)

                except Exception:

                    pass

        self.log("HumanIK Option1 v2.29.0 FULL-ARM USER CLASP TEMPLATE: lower body/root/legs stay from clean HIK; reference clasp template OFF; tiny HIK-clavicle guard ON; source-palm delta OFF; target-basis palm/finger clasp lock ON.")

        stats.update(self._apply_humanik_smplh_femalestd_slot_overrides(source_map, target_map, source_hik_joints_for_slots, target_joints))

        stats["humanik_source_map_preview"] = {k: short_name(v) for k, v in source_map.items() if k in HIK_BONE_IDS}

        stats["humanik_live_source_map_preview"] = {k: short_name(v) for k, v in live_source_map.items() if k in HIK_BONE_IDS}

        stats["humanik_target_map_preview"] = {k: short_name(v) for k, v in target_map.items() if k in HIK_BONE_IDS}

        self.log("HumanIK: live source slots preview: %s" % "; ".join(["%s=%s" % (k, short_name(v)) for k, v in sorted(live_source_map.items()) if k in HIK_BONE_IDS]))

        self.log("HumanIK: HIK source definition slots preview: %s" % "; ".join(["%s=%s" % (k, short_name(v)) for k, v in sorted(source_map.items()) if k in HIK_BONE_IDS]))

        self.log("HumanIK: target slots preview: %s" % "; ".join(["%s=%s" % (k, short_name(v)) for k, v in sorted(target_map.items()) if k in HIK_BONE_IDS]))



        self._hik_source_required_scripts()

        source_char = self._hik_create_character("ALPHA_Source_HIK")

        target_char = self._hik_create_character("ALPHA_Target_HIK")

        stats.update(self._hik_assign_character_definition(source_char, source_map, "source"))

                                                                                                          

                                                                                                   

        stats.update(self._pre_calibrate_target_hik_arm_reference_pose(target_map))

        if bool(getattr(self.config, "humanik_pre_calibrate_target_arm_reference_pose", False)) and not bool(getattr(self.config, "humanik_apply_inverse_reference_pose_offset_to_arms", False)):

            self.log("HumanIK Option1 v2.8.0 WARNING: target arm reference pre-calibration is enabled without inverse conversion. This is diagnostic only and can export arms in the wrong target bind basis.")

                                                                                                     

                                                                                        

        target_hik_reference_local_matrices = {}

        for _canon in humanik_arm_canonicals:

            _tgt_node = target_map.get(_canon)

            if _tgt_node and safe_cmds_exists(_tgt_node):

                try:

                    target_hik_reference_local_matrices[_canon] = self._matrix_from_node_local(_tgt_node)

                except Exception:

                    pass

        stats.update(self._hik_assign_character_definition(target_char, target_map, "target"))



        if use_rest_character_source and bool(getattr(self.config, "humanik_copy_live_animation_to_rest_source", True)):

            stats.update(self._hik_copy_live_source_animation_to_rest_character_source(live_source_map, source_map, start, end))



                                                                                             

        cmds.currentTime(start, edit=True)

        self._hik_set_target_source(target_char, source_char)

        for f in (start, min(end, start + 1.0), end):

            try:

                cmds.currentTime(f, edit=True)

                cmds.refresh(force=True)

            except Exception:

                pass

        target_root = target_map.get("root") or get_root_joints(target_joints)[0]

        target_bake_joints = get_hierarchy(target_root, node_type="joint") if target_root else target_joints

        curves_before = count_anim_curves_on_nodes(target_bake_joints)

        curves_after = self._hik_bake_target(target_char, target_bake_joints, start, end)

        stats["humanik_target_curves_before_bake"] = curves_before

        stats["humanik_target_curves_after_bake"] = curves_after

        stats.update(self._post_align_humanik_target_root(source_map, target_map, start, end))

        stats.update(self._post_apply_inverse_hik_reference_pose_offset_to_arms(target_map, target_bake_joints, start, end, target_rest_local_matrices, target_hik_reference_local_matrices, target_rest_local_translates))

        stats.update(self._post_apply_humanik_matrix_arm_transfer_from_source(source_map, target_map, target_bake_joints, start, end, source_hik_rest_local_matrices, target_rest_local_matrices, target_rest_local_translates))

        stats.update(self._post_solve_humanik_arms_from_source_positions(source_map, target_map, target_bake_joints, start, end, source_hik_rest_positions, target_rest_positions, target_rest_local_rotations, source_hik_rest_local_rotations))

        stats.update(self._post_override_humanik_arm_rotations_from_source(source_map, target_map, source_hik_rest_local_matrices, target_rest_local_matrices, target_rest_local_translates, target_bake_joints, start, end))

        stats.update(self._post_correct_humanik_hands_to_leg_front(source_map, target_map, target_bake_joints, start, end))

        stats.update(self._post_match_humanik_hands(source_map, target_map, source_rest_map, target_rest_positions, target_bake_joints, start, end))

        if bool(getattr(self.config, "humanik_post_refine_limbs", False)):

            stats.update(self._post_refine_humanik_limbs(source_map, target_map, source_rest_map, target_rest_positions, target_bake_joints, start, end))

        curves_after = count_anim_curves_on_nodes(target_bake_joints)

        stats["humanik_target_curves_after_post_align"] = curves_after

        stats["mapped_joint_count"] = len(pairs)

        stats["baked_target_joint_count"] = len(target_bake_joints)

        if curves_after <= curves_before and curves_after < 20:

            raise RuntimeError("HumanIK bake produced too few target animation curves (%d). Retarget not trusted." % curves_after)

        return stats





                                                                        

                                                 

                                                                        



    def _build_sample_frames(self, start: float, end: float) -> List[float]:

        sample_by = max(float(self.config.bake_sample_by or 1.0), 0.001)

        frames: List[float] = []

        frame = float(start)

        while frame <= float(end) + 0.0001:

            frames.append(round(frame, 6))

            frame += sample_by

        if frames and frames[-1] < float(end):

            frames.append(float(end))

        if not frames:

            frames = [float(start)]

        return frames



    def _world_euler_delta_rotation(self, rest_rot, current_rot, target_rest_rot):

                                                                                              

        return tuple(float(target_rest_rot[i]) + angular_delta(float(rest_rot[i]), float(current_rot[i])) for i in range(3))



    def _retarget_with_world_euler_delta_constraints(

        self,

        source_joints: List[str],

        target_joints: List[str],

        start: float,

        end: float,

        source_rest_joints: Optional[List[str]] = None,

    ) -> Dict[str, Any]:

        require_maya()

        stats: Dict[str, Any] = {}

        pairs = self.mapping.build_source_target_pairs(source_joints, target_joints)

        rest_pairs = self.mapping.build_source_target_pairs(source_rest_joints or [], target_joints) if source_rest_joints else {}



        stats["retarget_method"] = "world_euler_delta_constraints"

        stats["mapped_joint_count"] = len(pairs)

        stats["source_rest_mapped_joint_count"] = len(rest_pairs)

        stats["retarget_copy_pelvis_translation"] = bool(self.config.retarget_copy_pelvis_translation)

        stats["retarget_translation_scale"] = float(self.config.retarget_translation_scale)



        if len(pairs) < 8:

            raise RuntimeError("Too few mapped joints for retargeting (%d). Check mapping JSON / skeleton names." % len(pairs))

        if self.config.require_source_rest_for_matrix_delta and len(rest_pairs) < 8:

            raise RuntimeError(

                "Source Skeleton File / rest T-pose is required for world_euler_delta_constraints, but only %d rest joints mapped. "

                "Set Source Skeleton File to smplh_Tpose.fbx or click Apply SMPL-H -> FemaleStd Safe Defaults."

                % len(rest_pairs)

            )



        cmds.currentTime(start, edit=True)

        source_rest_rot: Dict[str, Tuple[float, float, float]] = {}

        source_rest_pos: Dict[str, Tuple[float, float, float]] = {}

        target_rest_rot: Dict[str, Tuple[float, float, float]] = {}

        target_rest_pos: Dict[str, Tuple[float, float, float]] = {}



        for canonical, (src, tgt) in pairs.items():

            if not (safe_cmds_exists(src) and safe_cmds_exists(tgt)):

                continue

            unlock_transform_attrs(tgt)

            set_rotate_order(tgt, self.config.retarget_rotate_order)

            target_rest_rot[canonical] = get_world_rotation(tgt)

            target_rest_pos[canonical] = get_world_position(tgt)

            rest_src = rest_pairs.get(canonical, (None, None))[0] if rest_pairs else None

            if rest_src and safe_cmds_exists(rest_src):

                source_rest_rot[canonical] = get_world_rotation(rest_src)

                source_rest_pos[canonical] = get_world_position(rest_src)

            else:

                source_rest_rot[canonical] = get_world_rotation(src)

                source_rest_pos[canonical] = get_world_position(src)



        frames = self._build_sample_frames(start, end)

        driver_group = cmds.group(empty=True, name="ALPHA_WorldEuler_Drivers_GRP")

        drivers: Dict[str, str] = {}

        keyed_driver_channels = 0

        source_start_delta_degrees_sum = 0.0

        driver_start_delta_degrees_sum = 0.0



        self.log("World-euler-delta retarget: building %d driver locators from %.2f to %.2f (%d samples)." % (len(pairs), start, end, len(frames)))



        for canonical in DEFAULT_RETARGET_CANONICAL_ORDER:

            if canonical not in pairs:

                continue

            if canonical not in source_rest_rot or canonical not in target_rest_rot:

                continue

            loc = self._create_driver_locator("ALPHA_wedrv_%s" % canonical)

            try:

                cmds.parent(loc, driver_group)

            except Exception:

                pass

            drivers[canonical] = loc



        for frame_index, frame in enumerate(frames):

            cmds.currentTime(frame, edit=True)

            for canonical, loc in drivers.items():

                src, tgt = pairs[canonical]

                if not (safe_cmds_exists(src) and safe_cmds_exists(tgt)):

                    continue

                src_curr_rot = get_world_rotation(src)

                src_curr_pos = get_world_position(src)

                out_rot = self._world_euler_delta_rotation(source_rest_rot[canonical], src_curr_rot, target_rest_rot[canonical])

                out_pos = target_rest_pos[canonical]

                if canonical == "pelvis" and self.config.retarget_copy_pelvis_translation:

                    scale = float(self.config.retarget_translation_scale or 1.0)

                    rest_pos = source_rest_pos.get(canonical, src_curr_pos)

                    tgt_rest_pos = target_rest_pos.get(canonical, (0.0, 0.0, 0.0))

                    out_pos = tuple(float(tgt_rest_pos[i]) + (float(src_curr_pos[i]) - float(rest_pos[i])) * scale for i in range(3))

                try:

                    cmds.xform(loc, worldSpace=True, translation=out_pos)

                    cmds.xform(loc, worldSpace=True, rotation=out_rot)

                    cmds.setKeyframe(loc, attribute=ROTATE_ATTRS + TRANSLATE_ATTRS, time=frame)

                    keyed_driver_channels += 6

                except Exception as exc:

                    self.log("World-euler driver key failed for %s at frame %.3f: %s" % (canonical, frame, exc))

                if frame_index == 0:

                    s_delta = sum(abs(angular_delta(source_rest_rot[canonical][i], src_curr_rot[i])) for i in range(3))

                    d_delta = sum(abs(angular_delta(target_rest_rot[canonical][i], out_rot[i])) for i in range(3))

                    source_start_delta_degrees_sum += s_delta

                    driver_start_delta_degrees_sum += d_delta



        constraints = []

        target_joint_set = []

        for canonical in DEFAULT_RETARGET_CANONICAL_ORDER:

            if canonical not in drivers or canonical not in pairs:

                continue

            loc = drivers[canonical]

            _src, tgt = pairs[canonical]

            if not safe_cmds_exists(tgt):

                continue

            unlock_transform_attrs(tgt)

            target_joint_set.append(tgt)

            try:

                if canonical == "pelvis" and self.config.retarget_copy_pelvis_translation:

                    constraints.extend(cmds.parentConstraint(loc, tgt, maintainOffset=False) or [])

                else:

                    constraints.extend(cmds.orientConstraint(loc, tgt, maintainOffset=False) or [])

            except Exception as exc:

                self.log("World-euler driver constraint failed for %s -> %s: %s" % (loc, tgt, exc))



        target_joint_set = sorted(set(target_joint_set))

        if not target_joint_set:

            try:

                cmds.delete(driver_group)

            except Exception:

                pass

            raise RuntimeError("No target joints were driven. Retarget failed.")



        self.log("World-euler-delta retarget: baking %d target joints..." % len(target_joint_set))

        cmds.bakeResults(

            target_joint_set,

            time=(start, end),

            simulation=True,

            sampleBy=max(float(self.config.bake_sample_by or 1.0), 0.001),

            disableImplicitControl=True,

            preserveOutsideKeys=False,

            sparseAnimCurveBake=False,

            removeBakedAttributeFromLayer=False,

            removeBakedAnimFromLayer=False,

            bakeOnOverrideLayer=False,

            minimizeRotation=True,

            controlPoints=False,

            shape=False,

        )



        if constraints:

            try:

                cmds.delete(constraints)

            except Exception:

                pass

        try:

            cmds.delete(driver_group)

        except Exception:

            pass



        self._apply_mapping_offsets(pairs)

        anim_curve_count = count_anim_curves_on_nodes(target_joint_set)

        target_pose_delta_degrees_sum = 0.0

        cmds.currentTime(start, edit=True)

        for canonical, (_src, tgt) in pairs.items():

            if canonical in target_rest_rot and safe_cmds_exists(tgt):

                now_rot = get_world_rotation(tgt)

                target_pose_delta_degrees_sum += sum(abs(angular_delta(target_rest_rot[canonical][i], now_rot[i])) for i in range(3))



        stats["baked_target_joint_count"] = len(target_joint_set)

        stats["driver_locator_count"] = len(drivers)

        stats["constraint_count"] = len(constraints)

        stats["keyed_driver_channels"] = keyed_driver_channels

        stats["target_anim_curve_count_after_retarget"] = anim_curve_count

        stats["source_start_euler_pose_delta_degrees_sum"] = source_start_delta_degrees_sum

        stats["driver_start_euler_pose_delta_degrees_sum"] = driver_start_delta_degrees_sum

        stats["target_start_pose_delta_degrees_sum"] = target_pose_delta_degrees_sum



        if self.config.fail_if_no_target_animation and anim_curve_count <= 0:

            raise RuntimeError("World-euler-delta retarget produced no animation curves on the target skeleton. Export cancelled.")

        if self.config.fail_if_no_target_animation and source_start_delta_degrees_sum > 5.0 and target_pose_delta_degrees_sum < 2.0:

            raise RuntimeError(

                "Source pose is different from rest, but target stayed near A-pose after world_euler_delta_constraints. "

                "This means the source/target mapping or imported source animation data is not being resolved correctly."

            )

        return stats



                                                                        

                                                        

                                                                        



    @staticmethod

    def _matrix_from_node_world(node: str):

        try:

            import maya.api.OpenMaya as om

        except Exception as exc:

            raise RuntimeError("maya.api.OpenMaya is required for rest_world_delta_constraints retargeting: %s" % exc)

        values = cmds.xform(node, query=True, worldSpace=True, matrix=True)

        return om.MMatrix(values)



    def _make_world_output_matrix(self, source_rest_world, source_current_world, target_rest_world):

        order = (self.config.matrix_delta_order or "target_rest_delta").strip().lower()

        if order in {"delta_target_rest", "current_rest_inv", "current_x_rest_inv", "current*rest_inv"}:

            delta = source_current_world * source_rest_world.inverse()

            return delta * target_rest_world

                                                                                                 

        delta = source_rest_world.inverse() * source_current_world

        return target_rest_world * delta



    def _create_driver_locator(self, name: str) -> str:

        loc = cmds.spaceLocator(name=name)[0]

        for attr in ROTATE_ATTRS + TRANSLATE_ATTRS:

            full = "%s.%s" % (loc, attr)

            try:

                cmds.setAttr(full, lock=False, keyable=True, channelBox=True)

            except Exception:

                pass

        return loc





                                                                        

                                                          

                                                                        



    def _capture_local_transform_state(self, nodes: List[str]) -> Dict[str, Dict[str, Tuple[float, float, float]]]:

        state: Dict[str, Dict[str, Tuple[float, float, float]]] = {}

        for node in nodes or []:

            if not safe_cmds_exists(node):

                continue

            state[node] = {

                "t": self._get_vec(node, TRANSLATE_ATTRS),

                "r": self._get_vec(node, ROTATE_ATTRS),

                "s": self._get_vec(node, SCALE_ATTRS),

            }

        return state



    def _restore_local_transform_state(self, state: Dict[str, Dict[str, Tuple[float, float, float]]]) -> None:

        for node, values in (state or {}).items():

            if not safe_cmds_exists(node):

                continue

            unlock_transform_attrs(node)

            try:

                self._set_vec(node, TRANSLATE_ATTRS, values.get("t", (0.0, 0.0, 0.0)))

                self._set_vec(node, ROTATE_ATTRS, values.get("r", (0.0, 0.0, 0.0)))

                self._set_vec(node, SCALE_ATTRS, values.get("s", (1.0, 1.0, 1.0)))

            except Exception:

                pass



    def _make_world_output_matrix_for_order(self, order: str, source_rest_world, source_current_world, target_rest_world):

        order = (order or "target_rest_delta").strip().lower()

        if order == "delta_target_rest":

            return (source_current_world * source_rest_world.inverse()) * target_rest_world

        if order == "source_delta_target_rest":

            return (source_rest_world.inverse() * source_current_world) * target_rest_world

        if order == "target_rest_current_delta":

            return target_rest_world * (source_current_world * source_rest_world.inverse())

                                      

        return target_rest_world * (source_rest_world.inverse() * source_current_world)



    def _apply_world_matrix_to_joint(self, joint: str, matrix_obj, keep_local_translate: Optional[Tuple[float, float, float]] = None) -> None:

        unlock_transform_attrs(joint)

        cmds.xform(joint, worldSpace=True, matrix=self._matrix_to_list(matrix_obj))

        if keep_local_translate is not None:

            self._set_vec(joint, TRANSLATE_ATTRS, keep_local_translate)



    def validate_target_pose_sanity(

        self,

        source_joints: List[str],

        target_joints: List[str],

        frame: float,

        label: str = "retarget",

    ) -> Dict[str, Any]:

        stats: Dict[str, Any] = {"pose_sanity_label": label}

        pairs = self.mapping.build_source_target_pairs(source_joints, target_joints)

        required = ["pelvis", "head"]

        if not all(k in pairs for k in required):

            stats["pose_sanity"] = "skipped_missing_pelvis_or_head"

            return stats

        cmds.currentTime(frame, edit=True)

        src_pelvis, tgt_pelvis = pairs["pelvis"]

        src_head, tgt_head = pairs["head"]

        if not all(safe_cmds_exists(n) for n in [src_pelvis, tgt_pelvis, src_head, tgt_head]):

            stats["pose_sanity"] = "skipped_missing_nodes"

            return stats

        src_head_y = get_world_position(src_head)[1] - get_world_position(src_pelvis)[1]

        tgt_head_y = get_world_position(tgt_head)[1] - get_world_position(tgt_pelvis)[1]

        stats["source_head_minus_pelvis_y"] = float(src_head_y)

        stats["target_head_minus_pelvis_y"] = float(tgt_head_y)



                                                                                     

        if abs(src_head_y) > 1.0 and abs(tgt_head_y) > 1.0 and (src_head_y * tgt_head_y) < 0.0:

            raise RuntimeError(

                "%s failed pose sanity: source head/pelvis vertical direction is %.3f but target is %.3f. "

                "This is the upside-down/broken retarget case, so this method is rejected."

                % (label, src_head_y, tgt_head_y)

            )



                                                                                            

        for side in ("l", "r"):

            foot_key = "foot_%s" % side

            if foot_key not in pairs:

                continue

            src_foot, tgt_foot = pairs[foot_key]

            if not (safe_cmds_exists(src_foot) and safe_cmds_exists(tgt_foot)):

                continue

            src_foot_y = get_world_position(src_foot)[1] - get_world_position(src_pelvis)[1]

            tgt_foot_y = get_world_position(tgt_foot)[1] - get_world_position(tgt_pelvis)[1]

            stats["source_%s_minus_pelvis_y" % foot_key] = float(src_foot_y)

            stats["target_%s_minus_pelvis_y" % foot_key] = float(tgt_foot_y)

            if src_foot_y < -1.0 and tgt_foot_y > abs(src_head_y) * 0.75:

                raise RuntimeError(

                    "%s failed pose sanity: target %s is above the upper body. Retarget method rejected."

                    % (label, foot_key)

                )

        stats["pose_sanity"] = "ok"

        return stats



    def _score_current_target_pose(self, pairs: Dict[str, Tuple[str, str]], target_rest_positions: Dict[str, Tuple[float, float, float]]) -> float:

        score = 0.0

        try:

            if "pelvis" in pairs and "head" in pairs:

                src_pelvis, tgt_pelvis = pairs["pelvis"]

                src_head, tgt_head = pairs["head"]

                src_head_y = get_world_position(src_head)[1] - get_world_position(src_pelvis)[1]

                tgt_head_y = get_world_position(tgt_head)[1] - get_world_position(tgt_pelvis)[1]

                if abs(src_head_y) > 1.0 and abs(tgt_head_y) > 1.0 and (src_head_y * tgt_head_y) < 0.0:

                    score -= 100000.0

                else:

                    score += 1000.0

                score += clamp(abs(tgt_head_y), 0.0, 250.0)

            pose_delta = 0.0

            for canonical, (_src, tgt) in pairs.items():

                if canonical not in target_rest_positions or not safe_cmds_exists(tgt):

                    continue

                pose_delta += vector_len(vector_sub(get_world_position(tgt), target_rest_positions[canonical]))

                                                                            

            score += clamp(pose_delta, 0.0, 1000.0)

            if pose_delta > 10000.0:

                score -= 10000.0

        except Exception:

            score -= 1000.0

        return score





                                                                        

                                                                       

                                                                        



    @staticmethod

    def _v_add(a, b):

        return (float(a[0]) + float(b[0]), float(a[1]) + float(b[1]), float(a[2]) + float(b[2]))



    @staticmethod

    def _v_sub(a, b):

        return (float(a[0]) - float(b[0]), float(a[1]) - float(b[1]), float(a[2]) - float(b[2]))



    @staticmethod

    def _v_mul(v, s):

        return (float(v[0]) * float(s), float(v[1]) * float(s), float(v[2]) * float(s))



    @staticmethod

    def _v_dot(a, b):

        return float(a[0]) * float(b[0]) + float(a[1]) * float(b[1]) + float(a[2]) * float(b[2])



    @staticmethod

    def _v_cross(a, b):

        return (

            float(a[1]) * float(b[2]) - float(a[2]) * float(b[1]),

            float(a[2]) * float(b[0]) - float(a[0]) * float(b[2]),

            float(a[0]) * float(b[1]) - float(a[1]) * float(b[0]),

        )



    @classmethod

    def _v_len(cls, v):

        return math.sqrt(cls._v_dot(v, v))



    @classmethod

    def _v_norm(cls, v, fallback=(1.0, 0.0, 0.0)):

        length = cls._v_len(v)

        if length <= 1e-8:

            return fallback

        return (float(v[0]) / length, float(v[1]) / length, float(v[2]) / length)



    @classmethod

    def _basis_from_positions(cls, pelvis, left_hip, right_hip, upper_body):

        right = cls._v_norm(cls._v_sub(right_hip, left_hip), (1.0, 0.0, 0.0))

        up = cls._v_norm(cls._v_sub(upper_body, pelvis), (0.0, 1.0, 0.0))

        forward = cls._v_norm(cls._v_cross(right, up), (0.0, 0.0, 1.0))

                                                                      

        up = cls._v_norm(cls._v_cross(forward, right), up)

        return right, up, forward



    @classmethod

    def _basis_world_to_local(cls, vector, basis):

        right, up, forward = basis

        return (cls._v_dot(vector, right), cls._v_dot(vector, up), cls._v_dot(vector, forward))



    @classmethod

    def _basis_local_to_world(cls, local, basis):

        right, up, forward = basis

        return cls._v_add(cls._v_add(cls._v_mul(right, local[0]), cls._v_mul(up, local[1])), cls._v_mul(forward, local[2]))



    def _make_temp_locator(self, name: str, position=(0.0, 0.0, 0.0)) -> str:

        loc = cmds.spaceLocator(name=name)[0]

        unlock_transform_attrs(loc)

        cmds.xform(loc, worldSpace=True, translation=position)

        return loc



    def _node_world_position_safe(self, node: str, default=(0.0, 0.0, 0.0)):

        if not node or not safe_cmds_exists(node):

            return default

        try:

            return get_world_position(node)

        except Exception:

            return default



    def _find_pair_node(self, pairs: Dict[str, Tuple[str, str]], canonical: str, source: bool = True) -> Optional[str]:

        if canonical not in pairs:

            return None

        return pairs[canonical][0 if source else 1]



    def _set_and_key_locator_pos(self, loc: str, pos, frame: float) -> None:

        cmds.currentTime(frame, edit=True)

        cmds.xform(loc, worldSpace=True, translation=(float(pos[0]), float(pos[1]), float(pos[2])))

        cmds.setKeyframe(loc, attribute=TRANSLATE_ATTRS, time=frame)



    def _make_pole_position(self, start_pos, mid_pos, end_pos, fallback_axis=(0.0, 0.0, 1.0), scale=1.0):

        center = self._v_mul(self._v_add(start_pos, end_pos), 0.5)

        pole_dir = self._v_sub(mid_pos, center)

        if self._v_len(pole_dir) <= 1e-4:

            pole_dir = fallback_axis

        pole_dir = self._v_norm(pole_dir, fallback_axis)

        limb_len = max(self._v_len(self._v_sub(start_pos, mid_pos)) + self._v_len(self._v_sub(mid_pos, end_pos)), 1.0)

        return self._v_add(mid_pos, self._v_mul(pole_dir, limb_len * 0.65 * float(scale)))



    def _create_ik_handle_safe(self, name: str, start_joint: str, end_joint: str) -> Optional[str]:

        if not (safe_cmds_exists(start_joint) and safe_cmds_exists(end_joint)):

            return None

        try:

            handle, effector = cmds.ikHandle(name=name, startJoint=start_joint, endEffector=end_joint, solver="ikRPsolver")

            return handle

        except Exception as exc:

            self.log("WARNING: Could not create IK handle %s (%s -> %s): %s" % (name, start_joint, end_joint, exc))

            return None





    def _manual_sample_solved_joint_animation(

        self,

        joints: List[str],

        frames: List[float],

        translate_key_nodes: Optional[set] = None,

        temp_nodes: Optional[List[str]] = None,

        label: str = "manual_solver",

    ) -> Dict[str, Any]:

        require_maya()

        translate_key_nodes = translate_key_nodes or set()

        temp_nodes = temp_nodes or []

        valid_joints = [j for j in joints if safe_cmds_exists(j)]

        if not valid_joints:

            raise RuntimeError("%s manual bake has no valid target joints." % label)



                                                                                        

        for j in valid_joints:

            unlock_transform_attrs(j)



        samples: Dict[float, Dict[str, Dict[str, Tuple[float, float, float]]]] = {}

        keyed_rotate_nodes = 0

        keyed_translate_nodes = 0

        for frame in frames:

            cmds.currentTime(frame, edit=True, update=True)

            frame_data: Dict[str, Dict[str, Tuple[float, float, float]]] = {}

            for j in valid_joints:

                try:

                    rot = cmds.getAttr(j + ".rotate")[0]

                except Exception:

                    rot = (0.0, 0.0, 0.0)

                node_data: Dict[str, Tuple[float, float, float]] = {"rotate": (float(rot[0]), float(rot[1]), float(rot[2]))}

                if j in translate_key_nodes:

                    try:

                        tr = cmds.getAttr(j + ".translate")[0]

                    except Exception:

                        tr = (0.0, 0.0, 0.0)

                    node_data["translate"] = (float(tr[0]), float(tr[1]), float(tr[2]))

                frame_data[j] = node_data

            samples[float(frame)] = frame_data



                                                                                                    

        for n in temp_nodes:

            try:

                if safe_cmds_exists(n):

                    cmds.delete(n)

            except Exception:

                pass



                                                                                           

        try:

            cmds.cutKey(valid_joints, time=(frames[0], frames[-1]), attribute=ROTATE_ATTRS + TRANSLATE_ATTRS, option="keys")

        except Exception:

            pass



        for frame in frames:

            cmds.currentTime(frame, edit=True, update=True)

            frame_data = samples.get(float(frame), {})

            for j in valid_joints:

                data = frame_data.get(j)

                if not data:

                    continue

                r = data.get("rotate", (0.0, 0.0, 0.0))

                for attr, value in zip(ROTATE_ATTRS, r):

                    try:

                        cmds.setAttr(j + "." + attr, float(value))

                        cmds.setKeyframe(j, attribute=attr, time=frame)

                    except Exception:

                        pass

                keyed_rotate_nodes += 1

                if j in translate_key_nodes and "translate" in data:

                    t = data["translate"]

                    for attr, value in zip(TRANSLATE_ATTRS, t):

                        try:

                            cmds.setAttr(j + "." + attr, float(value))

                            cmds.setKeyframe(j, attribute=attr, time=frame)

                        except Exception:

                            pass

                    keyed_translate_nodes += 1



        try:

            cmds.filterCurve()

        except Exception:

            pass



        curve_count = count_anim_curves_on_nodes(valid_joints)

        self.log(

            "%s manual bake: sampled_frames=%d keyed_rotate_samples=%d keyed_translate_samples=%d anim_curves=%d"

            % (label, len(frames), keyed_rotate_nodes, keyed_translate_nodes, curve_count)

        )

        return {

            "manual_bake_sampled_frame_count": len(frames),

            "manual_bake_valid_joint_count": len(valid_joints),

            "manual_bake_keyed_rotate_samples": keyed_rotate_nodes,

            "manual_bake_keyed_translate_samples": keyed_translate_nodes,

            "anim_curve_count_after_manual_bake": curve_count,

        }



    def _retarget_with_positional_ik_solver(

        self,

        source_joints: List[str],

        target_joints: List[str],

        start: float,

        end: float,

        source_rest_joints: Optional[List[str]] = None,

    ) -> Dict[str, Any]:

        require_maya()

        stats: Dict[str, Any] = {"retarget_method": "positional_ik_solver"}

        pairs = self.mapping.build_source_target_pairs(source_joints, target_joints)

        rest_pairs = self.mapping.build_source_target_pairs(source_rest_joints or [], target_joints) if source_rest_joints else {}

        stats["mapped_joint_count"] = len(pairs)

        stats["source_rest_mapped_joint_count"] = len(rest_pairs)



        required = ["pelvis", "spine_03", "head", "thigh_l", "calf_l", "foot_l", "thigh_r", "calf_r", "foot_r", "upperarm_l", "lowerarm_l", "hand_l", "upperarm_r", "lowerarm_r", "hand_r"]

        missing = [c for c in required if c not in pairs]

        missing_rest = [c for c in ["pelvis", "head", "thigh_l", "thigh_r", "spine_03"] if c not in rest_pairs]

        if missing:

            raise RuntimeError("positional_ik_solver missing mapped joints: %s" % ", ".join(missing))

        if missing_rest:

            raise RuntimeError("positional_ik_solver requires source rest/T-pose mappings. Missing: %s" % ", ".join(missing_rest))



        frames = self._build_sample_frames(start, end)

        target_joint_set = sorted(set(target_joints))

        for j in target_joint_set:

            if safe_cmds_exists(j):

                unlock_transform_attrs(j)

                set_rotate_order(j, self.config.retarget_rotate_order)



                                                                          

        cmds.currentTime(start, edit=True)

        target_rest_pos: Dict[str, Tuple[float, float, float]] = {}

        source_rest_pos: Dict[str, Tuple[float, float, float]] = {}

        for canonical, (_src, tgt) in pairs.items():

            if safe_cmds_exists(tgt):

                target_rest_pos[canonical] = self._node_world_position_safe(tgt)

        for canonical, (src_rest, _tgt) in rest_pairs.items():

            if safe_cmds_exists(src_rest):

                source_rest_pos[canonical] = self._node_world_position_safe(src_rest)



        def psrc(c):

            return self._node_world_position_safe(pairs[c][0])

        def prest(c):

            return source_rest_pos[c]

        def ptgt(c):

            return target_rest_pos[c]



                                                                                                            

        src_rest_basis = self._basis_from_positions(prest("pelvis"), prest("thigh_l"), prest("thigh_r"), prest("spine_03"))

        tgt_rest_basis = self._basis_from_positions(ptgt("pelvis"), ptgt("thigh_l"), ptgt("thigh_r"), ptgt("spine_03"))

        src_height = max(self._v_len(self._v_sub(prest("head"), prest("pelvis"))), 1.0)

        tgt_height = max(self._v_len(self._v_sub(ptgt("head"), ptgt("pelvis"))), 1.0)

        scale_ratio = tgt_height / src_height

        stats["position_retarget_scale_ratio"] = scale_ratio



                                

        temp_nodes: List[str] = []

        locs: Dict[str, str] = {}

        driver_canons = [

            "pelvis", "spine_01", "spine_02", "spine_03", "neck_01", "head",

            "clavicle_l", "upperarm_l", "lowerarm_l", "hand_l",

            "clavicle_r", "upperarm_r", "lowerarm_r", "hand_r",

            "thigh_l", "calf_l", "foot_l", "thigh_r", "calf_r", "foot_r",

        ]

        for c in driver_canons:

            if c in pairs and c in target_rest_pos:

                locs[c] = self._make_temp_locator("ALPHA_posIK_%s_LOC" % c, target_rest_pos[c])

                temp_nodes.append(locs[c])



                                                                                            

                                  

         

                                

                                                                                                 

                                                                                                

                                                                                                

                                                                                                 

                                  

                                                         

                                                                                           

                                                                                                 

                                                                                               

                                                                                      

        keyed_locs = 0

        pelvis_scale = float(getattr(self.config, "retarget_pelvis_translation_scale", getattr(self.config, "retarget_translation_scale", 1.0)) or 1.0)

        use_body_basis = True



        self.log(

            "Positional-IK retarget: building world-delta rest-pose drivers for %d frames, scale_ratio=%.4f, anchor=source_rest_to_target_rest, pelvis_scale=%.3f."

            % (len(frames), scale_ratio, pelvis_scale)

        )



        def retarget_world_delta(canonical, animated_pos):

            src_rest = source_rest_pos.get(canonical)

            tgt_rest = target_rest_pos.get(canonical)

            if src_rest is None or tgt_rest is None:

                return None

            world_delta = self._v_sub(animated_pos, src_rest)

            scale = scale_ratio * (pelvis_scale if canonical == "pelvis" else 1.0)

            if use_body_basis:

                                                                                              

                                                                                            

                                                  

                local_delta = self._basis_world_to_local(world_delta, src_rest_basis)

                mapped_delta = self._basis_local_to_world(local_delta, tgt_rest_basis)

            else:

                mapped_delta = world_delta

            return self._v_add(tgt_rest, self._v_mul(mapped_delta, scale))



        for frame in frames:

            cmds.currentTime(frame, edit=True)

            for c, loc in locs.items():

                if c not in pairs:

                    continue

                desired = retarget_world_delta(c, psrc(c))

                if desired is None:

                    continue

                self._set_and_key_locator_pos(loc, desired, frame)

                keyed_locs += 3



        constraints: List[str] = []

        ik_handles: List[str] = []



                                                                                                       

                                                                              

        if "pelvis" in locs and "pelvis" in pairs:

            try:

                con = cmds.pointConstraint(locs["pelvis"], pairs["pelvis"][1], maintainOffset=False)[0]

                constraints.append(con)

            except Exception as exc:

                self.log("WARNING: Could not pointConstraint pelvis: %s" % exc)



                                                                                                          

        limb_specs = [

            ("leg_l", "thigh_l", "calf_l", "foot_l"),

            ("leg_r", "thigh_r", "calf_r", "foot_r"),

            ("arm_l", "upperarm_l", "lowerarm_l", "hand_l"),

            ("arm_r", "upperarm_r", "lowerarm_r", "hand_r"),

        ]

        for label, start_c, mid_c, end_c in limb_specs:

            if not all(c in pairs for c in [start_c, mid_c, end_c]):

                continue

            start_t = pairs[start_c][1]

            end_t = pairs[end_c][1]

            handle = self._create_ik_handle_safe("ALPHA_posIK_%s_IKH" % label, start_t, end_t)

            if not handle:

                continue

            temp_nodes.append(handle)

            ik_handles.append(handle)

                                   

            if end_c in locs:

                try:

                    constraints.append(cmds.pointConstraint(locs[end_c], handle, maintainOffset=False)[0])

                except Exception as exc:

                    self.log("WARNING: Could not pointConstraint IK handle %s: %s" % (label, exc))

                                                                                                 

                                                                   

            pole_loc = self._make_temp_locator("ALPHA_posIK_%s_POLE_LOC" % label, target_rest_pos.get(mid_c, (0, 0, 0)))

            temp_nodes.append(pole_loc)

            for frame in frames:

                cmds.currentTime(frame, edit=True)

                sp = self._node_world_position_safe(locs.get(start_c, ""), target_rest_pos.get(start_c, (0, 0, 0))) if start_c in locs else target_rest_pos.get(start_c, (0, 0, 0))

                mp = self._node_world_position_safe(locs.get(mid_c, ""), target_rest_pos.get(mid_c, (0, 0, 0))) if mid_c in locs else target_rest_pos.get(mid_c, (0, 0, 0))

                ep = self._node_world_position_safe(locs.get(end_c, ""), target_rest_pos.get(end_c, (0, 0, 0))) if end_c in locs else target_rest_pos.get(end_c, (0, 0, 0))

                pole = self._make_pole_position(sp, mp, ep, scale=max(scale_ratio, 0.1))

                self._set_and_key_locator_pos(pole_loc, pole, frame)

            try:

                constraints.append(cmds.poleVectorConstraint(pole_loc, handle)[0])

            except Exception as exc:

                self.log("WARNING: Could not poleVectorConstraint %s: %s" % (label, exc))



                                                                                                    

        aim_specs = [("spine_01", "spine_02"), ("spine_02", "spine_03"), ("spine_03", "neck_01"), ("neck_01", "head")]

        for parent_c, child_c in aim_specs:

            if parent_c not in pairs or child_c not in locs:

                continue

            parent_t = pairs[parent_c][1]

                                                                                                        

            aim_vec = (1.0, 0.0, 0.0)

            if child_c in pairs and safe_cmds_exists(pairs[child_c][1]):

                try:

                    child_t = pairs[child_c][1]

                    child_local_t = cmds.xform(child_t, query=True, objectSpace=True, translation=True)

                    aim_vec = self._v_norm(child_local_t, (1.0, 0.0, 0.0))

                except Exception:

                    pass

            try:

                con = cmds.aimConstraint(locs[child_c], parent_t, maintainOffset=True, aimVector=aim_vec, upVector=(0, 1, 0), worldUpType="scene")[0]

                constraints.append(con)

            except Exception as exc:

                self.log("WARNING: Could not aimConstraint %s -> %s: %s" % (parent_c, child_c, exc))



        self.log("Positional-IK retarget: constraints=%d ik_handles=%d. Manually sampling solved target pose on %d joints..." % (len(constraints), len(ik_handles), len(target_joint_set)))



                                                                                              

                                                                                             

                                                                                              

                                                                                                 

                                                                                                  

        translate_key_nodes = set()

        if "pelvis" in pairs:

            translate_key_nodes.add(pairs["pelvis"][1])

            parent = cmds.listRelatives(pairs["pelvis"][1], parent=True, type="joint") or []

            if parent:

                translate_key_nodes.add(parent[0])

        manual_bake_stats = self._manual_sample_solved_joint_animation(

            target_joint_set,

            frames,

            translate_key_nodes=translate_key_nodes,

            temp_nodes=constraints + temp_nodes,

            label="positional_ik_solver",

        )



        self._apply_mapping_offsets(pairs)

        anim_curve_count = count_anim_curves_on_nodes(target_joint_set)

        if anim_curve_count <= 0 and manual_bake_stats.get("anim_curve_count_after_manual_bake", 0) > 0:

            anim_curve_count = int(manual_bake_stats.get("anim_curve_count_after_manual_bake", 0))

        sanity = self.validate_target_pose_sanity(source_joints, target_joints, start, label="positional_ik_solver")

        stats.update({

            "positional_ik_driver_locator_count": len(locs),

            "positional_ik_keyed_locator_channels": keyed_locs,

            "positional_ik_handle_count": len(ik_handles),

            "constraint_count": len(constraints),

            "baked_target_joint_count": len(target_joint_set),

            "target_anim_curve_count_after_retarget": anim_curve_count,

        })

        stats.update(manual_bake_stats)

        stats.update(sanity)

        if self.config.fail_if_no_target_animation and anim_curve_count <= 0:

            raise RuntimeError("positional_ik_solver produced no animation curves on the target skeleton. Export cancelled.")

        return stats



    def _retarget_with_hierarchical_world_matrix(

        self,

        source_joints: List[str],

        target_joints: List[str],

        start: float,

        end: float,

        source_rest_joints: Optional[List[str]] = None,

    ) -> Dict[str, Any]:

        require_maya()

        stats: Dict[str, Any] = {"retarget_method": "positional_ik_solver"}

        pairs = self.mapping.build_source_target_pairs(source_joints, target_joints)

        rest_pairs = self.mapping.build_source_target_pairs(source_rest_joints or [], target_joints) if source_rest_joints else {}

        stats["mapped_joint_count"] = len(pairs)

        stats["source_rest_mapped_joint_count"] = len(rest_pairs)

        if len(pairs) < 8:

            raise RuntimeError("Too few mapped joints for hierarchical_world_matrix (%d). Check mapping JSON." % len(pairs))

        if len(rest_pairs) < 8:

            raise RuntimeError("Source rest/T-pose skeleton is required for hierarchical_world_matrix. Only %d rest joints mapped." % len(rest_pairs))



        cmds.currentTime(start, edit=True)

        target_joint_set: List[str] = []

        target_rest_world: Dict[str, Any] = {}

        source_rest_world: Dict[str, Any] = {}

        target_rest_translate: Dict[str, Tuple[float, float, float]] = {}

        target_rest_positions: Dict[str, Tuple[float, float, float]] = {}



        for canonical in DEFAULT_RETARGET_CANONICAL_ORDER:

            if canonical not in pairs:

                continue

            src, tgt = pairs[canonical]

            rest_src = rest_pairs.get(canonical, (None, None))[0]

            if not (safe_cmds_exists(src) and safe_cmds_exists(tgt) and rest_src and safe_cmds_exists(rest_src)):

                continue

            unlock_transform_attrs(tgt)

            set_rotate_order(tgt, self.config.retarget_rotate_order)

            target_joint_set.append(tgt)

            target_rest_world[canonical] = self._matrix_from_node_world(tgt)

            source_rest_world[canonical] = self._matrix_from_node_world(rest_src)

            target_rest_translate[canonical] = self._get_vec(tgt, TRANSLATE_ATTRS)

            target_rest_positions[canonical] = get_world_position(tgt)



        target_joint_set = sorted(set(target_joint_set))

        if not target_joint_set:

            raise RuntimeError("hierarchical_world_matrix has no target joints to drive.")



        candidate_orders = [

            (self.config.matrix_delta_order or "target_rest_delta").strip().lower(),

            "target_rest_delta",

            "delta_target_rest",

            "source_delta_target_rest",

            "target_rest_current_delta",

        ]

                                        

        candidate_orders = list(dict.fromkeys([x for x in candidate_orders if x]))

        original_state = self._capture_local_transform_state(target_joint_set)

        best_order = candidate_orders[0]

        best_score = -10**18

        order_scores: Dict[str, float] = {}



        self.log("Hierarchical-world-matrix retarget: scoring matrix orders at frame %.2f..." % float(start))

        for order in candidate_orders:

            self._restore_local_transform_state(original_state)

            cmds.currentTime(start, edit=True)

            try:

                for canonical in DEFAULT_RETARGET_CANONICAL_ORDER:

                    if canonical not in pairs or canonical not in source_rest_world or canonical not in target_rest_world:

                        continue

                    src, tgt = pairs[canonical]

                    if not (safe_cmds_exists(src) and safe_cmds_exists(tgt)):

                        continue

                    out_m = self._make_world_output_matrix_for_order(order, source_rest_world[canonical], self._matrix_from_node_world(src), target_rest_world[canonical])

                    keep_tr = None if (canonical == "pelvis" and self.config.retarget_copy_pelvis_translation) else target_rest_translate.get(canonical)

                    self._apply_world_matrix_to_joint(tgt, out_m, keep_local_translate=keep_tr)

                score = self._score_current_target_pose(pairs, target_rest_positions)

            except Exception as exc:

                score = -10**12

                self.log("  Matrix order %s scoring error: %s" % (order, exc))

            order_scores[order] = float(score)

            self.log("  Matrix order score: %s = %.3f" % (order, score))

            if score > best_score:

                best_score = score

                best_order = order

        self._restore_local_transform_state(original_state)

        self.log("Hierarchical-world-matrix retarget: selected order=%s score=%.3f" % (best_order, best_score))



        frames = self._build_sample_frames(start, end)

        keyed = 0

        pelvis_translation_keys = 0

        self.log("Hierarchical-world-matrix retarget: writing %d mapped joints from %.2f to %.2f (%d samples)." % (len(target_joint_set), start, end, len(frames)))

        for frame in frames:

            cmds.currentTime(frame, edit=True)

            for canonical in DEFAULT_RETARGET_CANONICAL_ORDER:

                if canonical not in pairs or canonical not in source_rest_world or canonical not in target_rest_world:

                    continue

                src, tgt = pairs[canonical]

                if not (safe_cmds_exists(src) and safe_cmds_exists(tgt)):

                    continue

                out_m = self._make_world_output_matrix_for_order(best_order, source_rest_world[canonical], self._matrix_from_node_world(src), target_rest_world[canonical])

                keep_tr = None if (canonical == "pelvis" and self.config.retarget_copy_pelvis_translation) else target_rest_translate.get(canonical)

                self._apply_world_matrix_to_joint(tgt, out_m, keep_local_translate=keep_tr)

                try:

                    cmds.setKeyframe(tgt, attribute=ROTATE_ATTRS + TRANSLATE_ATTRS, time=frame)

                    keyed += 6

                    if canonical == "pelvis" and self.config.retarget_copy_pelvis_translation:

                        pelvis_translation_keys += 3

                except Exception as exc:

                    self.log("Could not key hierarchical matrix result for %s/%s at %.3f: %s" % (canonical, tgt, frame, exc))



        cmds.bakeResults(

            target_joint_set,

            time=(start, end),

            simulation=True,

            sampleBy=max(float(self.config.bake_sample_by or 1.0), 0.001),

            disableImplicitControl=True,

            preserveOutsideKeys=False,

            sparseAnimCurveBake=False,

            removeBakedAttributeFromLayer=False,

            removeBakedAnimFromLayer=False,

            bakeOnOverrideLayer=False,

            minimizeRotation=True,

            controlPoints=False,

            shape=False,

        )

        self._apply_mapping_offsets(pairs)

        sanity = self.validate_target_pose_sanity(source_joints, target_joints, start, label="hierarchical_world_matrix")

        anim_curve_count = count_anim_curves_on_nodes(target_joint_set)

        stats.update({

            "hierarchical_selected_order": best_order,

            "hierarchical_order_scores": order_scores,

            "baked_target_joint_count": len(target_joint_set),

            "direct_keys_written": keyed,

            "pelvis_translation_keys_written": pelvis_translation_keys,

            "target_anim_curve_count_after_retarget": anim_curve_count,

        })

        stats.update(sanity)

        if self.config.fail_if_no_target_animation and anim_curve_count <= 0:

            raise RuntimeError("hierarchical_world_matrix produced no animation curves on the target skeleton. Export cancelled.")

        return stats



    def _retarget_with_rest_world_delta_constraints(

        self,

        source_joints: List[str],

        target_joints: List[str],

        start: float,

        end: float,

        source_rest_joints: Optional[List[str]] = None,

    ) -> Dict[str, Any]:

        require_maya()

        stats: Dict[str, Any] = {}

        pairs = self.mapping.build_source_target_pairs(source_joints, target_joints)

        rest_pairs = self.mapping.build_source_target_pairs(source_rest_joints or [], target_joints) if source_rest_joints else {}



        stats["retarget_method"] = "rest_world_delta_constraints"

        stats["mapped_joint_count"] = len(pairs)

        stats["source_rest_mapped_joint_count"] = len(rest_pairs)

        stats["matrix_delta_order"] = self.config.matrix_delta_order

        stats["retarget_copy_pelvis_translation"] = bool(self.config.retarget_copy_pelvis_translation)

        stats["retarget_translation_scale"] = float(self.config.retarget_translation_scale)



        if len(pairs) < 8:

            raise RuntimeError("Too few mapped joints for retargeting (%d). Check mapping JSON / skeleton names." % len(pairs))

        if self.config.require_source_rest_for_matrix_delta and len(rest_pairs) < 8:

            raise RuntimeError(

                "Source Skeleton File / rest T-pose is required for rest_world_delta_constraints, but only %d rest joints mapped. "

                "Set Source Skeleton File to smplh_Tpose.fbx or click Apply SMPL-H -> FemaleStd Safe Defaults."

                % len(rest_pairs)

            )



        cmds.currentTime(start, edit=True)

        target_rest_world: Dict[str, Any] = {}

        source_rest_world: Dict[str, Any] = {}

        target_rest_translate: Dict[str, Tuple[float, float, float]] = {}

        source_rest_translate: Dict[str, Tuple[float, float, float]] = {}



        for canonical, (src, tgt) in pairs.items():

            if not (safe_cmds_exists(src) and safe_cmds_exists(tgt)):

                continue

            unlock_transform_attrs(tgt)

            set_rotate_order(tgt, self.config.retarget_rotate_order)

            target_rest_world[canonical] = self._matrix_from_node_world(tgt)

            target_rest_translate[canonical] = self._get_vec(tgt, TRANSLATE_ATTRS)

            rest_src = rest_pairs.get(canonical, (None, None))[0] if rest_pairs else None

            if rest_src and safe_cmds_exists(rest_src):

                source_rest_world[canonical] = self._matrix_from_node_world(rest_src)

                source_rest_translate[canonical] = self._get_vec(rest_src, TRANSLATE_ATTRS)

            else:

                source_rest_world[canonical] = self._matrix_from_node_world(src)

                source_rest_translate[canonical] = self._get_vec(src, TRANSLATE_ATTRS)



        frames = []

        sample_by = max(float(self.config.bake_sample_by or 1.0), 0.001)

        frame = float(start)

        while frame <= float(end) + 0.0001:

            frames.append(round(frame, 6))

            frame += sample_by

        if frames and frames[-1] < float(end):

            frames.append(float(end))

        if not frames:

            frames = [float(start)]



        driver_group = cmds.group(empty=True, name="ALPHA_Retarget_Drivers_GRP")

        drivers: Dict[str, str] = {}

        source_start_pose_delta_sum = 0.0

        driver_start_pose_delta_sum = 0.0

        keyed_driver_channels = 0



        self.log("Rest-world-delta retarget: building %d driver locators from %.2f to %.2f (%d samples)." % (len(pairs), start, end, len(frames)))



        for canonical in DEFAULT_RETARGET_CANONICAL_ORDER:

            if canonical not in pairs:

                continue

            if canonical not in source_rest_world or canonical not in target_rest_world:

                continue

            loc = self._create_driver_locator("ALPHA_drv_%s" % canonical)

            try:

                cmds.parent(loc, driver_group)

            except Exception:

                pass

            drivers[canonical] = loc



        for frame_index, frame in enumerate(frames):

            cmds.currentTime(frame, edit=True)

            for canonical, loc in drivers.items():

                src, tgt = pairs[canonical]

                if not (safe_cmds_exists(src) and safe_cmds_exists(tgt)):

                    continue

                src_rest_m = source_rest_world.get(canonical)

                tgt_rest_m = target_rest_world.get(canonical)

                if src_rest_m is None or tgt_rest_m is None:

                    continue

                src_curr_m = self._matrix_from_node_world(src)

                out_m = self._make_world_output_matrix(src_rest_m, src_curr_m, tgt_rest_m)

                try:

                    cmds.xform(loc, worldSpace=True, matrix=self._matrix_to_list(out_m))

                except Exception:

                                                                                                                

                    continue

                try:

                    cmds.setKeyframe(loc, attribute=ROTATE_ATTRS + TRANSLATE_ATTRS, time=frame)

                    keyed_driver_channels += 6

                except Exception:

                    pass

                if frame_index == 0:

                    src_rest_list = self._matrix_to_list(src_rest_m)

                    src_curr_list = self._matrix_to_list(src_curr_m)

                    out_list = self._matrix_to_list(out_m)

                    tgt_rest_list = self._matrix_to_list(tgt_rest_m)

                    source_start_pose_delta_sum += sum(abs(src_curr_list[i] - src_rest_list[i]) for i in range(16))

                    driver_start_pose_delta_sum += sum(abs(out_list[i] - tgt_rest_list[i]) for i in range(16))



        constraints = []

        target_joint_set = []

        for canonical in DEFAULT_RETARGET_CANONICAL_ORDER:

            if canonical not in drivers or canonical not in pairs:

                continue

            loc = drivers[canonical]

            _src, tgt = pairs[canonical]

            if not safe_cmds_exists(tgt):

                continue

            unlock_transform_attrs(tgt)

            target_joint_set.append(tgt)

            try:

                if canonical == "pelvis" and self.config.retarget_copy_pelvis_translation:

                    constraints.extend(cmds.parentConstraint(loc, tgt, maintainOffset=False) or [])

                elif canonical == "root" and self.config.retarget_use_point_constraint_for_root:

                    constraints.extend(cmds.parentConstraint(loc, tgt, maintainOffset=False) or [])

                else:

                    constraints.extend(cmds.orientConstraint(loc, tgt, maintainOffset=False) or [])

            except Exception as exc:

                self.log("Driver constraint failed for %s -> %s: %s" % (loc, tgt, exc))



        target_joint_set = sorted(set(target_joint_set))

        if not target_joint_set:

            try:

                cmds.delete(driver_group)

            except Exception:

                pass

            raise RuntimeError("No target joints were driven. Retarget failed.")



        self.log("Rest-world-delta retarget: baking %d target joints..." % len(target_joint_set))

        cmds.bakeResults(

            target_joint_set,

            time=(start, end),

            simulation=True,

            sampleBy=sample_by,

            disableImplicitControl=True,

            preserveOutsideKeys=False,

            sparseAnimCurveBake=False,

            removeBakedAttributeFromLayer=False,

            removeBakedAnimFromLayer=False,

            bakeOnOverrideLayer=False,

            minimizeRotation=True,

            controlPoints=False,

            shape=False,

        )



        if constraints:

            try:

                cmds.delete(constraints)

            except Exception:

                pass

        try:

            cmds.delete(driver_group)

        except Exception:

            pass



        self._apply_mapping_offsets(pairs)

        anim_curve_count = count_anim_curves_on_nodes(target_joint_set)

        stats["baked_target_joint_count"] = len(target_joint_set)

        stats["driver_locator_count"] = len(drivers)

        stats["constraint_count"] = len(constraints)

        stats["keyed_driver_channels"] = keyed_driver_channels

        stats["target_anim_curve_count_after_retarget"] = anim_curve_count

        stats["source_start_matrix_pose_delta_sum"] = source_start_pose_delta_sum

        stats["driver_start_matrix_pose_delta_sum"] = driver_start_pose_delta_sum

        if self.config.fail_if_no_target_animation and anim_curve_count <= 0:

            raise RuntimeError("Rest-world-delta retarget produced no animation curves on the target skeleton. Export cancelled.")

        if self.config.fail_if_no_target_animation and source_start_pose_delta_sum > 1.0 and driver_start_pose_delta_sum < 1.0:

            raise RuntimeError(

                "Source first frame is different from rest, but the generated target drivers stayed near target rest. "

                "Switch Delta Order to delta_target_rest and test one file again."

            )

        return stats



                                                                        

                                                  

                                                                        





    @staticmethod

    def _matrix_from_node_local(node: str):

        try:

            import maya.api.OpenMaya as om

        except Exception as exc:

            raise RuntimeError("maya.api.OpenMaya is required for local_matrix_delta retargeting: %s" % exc)

        values = cmds.xform(node, query=True, objectSpace=True, matrix=True)

        return om.MMatrix(values)



    @staticmethod

    def _matrix_to_list(matrix_obj) -> List[float]:

        return [float(matrix_obj.getElement(r, c)) for r in range(4) for c in range(4)]



    def _apply_local_matrix_to_joint(self, joint: str, matrix_obj, keep_translate: Optional[Tuple[float, float, float]] = None) -> None:

        unlock_transform_attrs(joint)

        cmds.xform(joint, objectSpace=True, matrix=self._matrix_to_list(matrix_obj))

        if keep_translate is not None:

            self._set_vec(joint, TRANSLATE_ATTRS, keep_translate)



    def _make_matrix_delta(self, rest_matrix, current_matrix):

        order = (self.config.matrix_delta_order or "rest_inv_current").strip().lower()

        if order in {"current_rest_inv", "current_x_rest_inv", "current*rest_inv"}:

            return current_matrix * rest_matrix.inverse()

                                                                              

        return rest_matrix.inverse() * current_matrix



    def _retarget_with_local_matrix_delta(

        self,

        source_joints: List[str],

        target_joints: List[str],

        start: float,

        end: float,

        source_rest_joints: Optional[List[str]] = None,

    ) -> Dict[str, Any]:

        require_maya()

        stats: Dict[str, Any] = {}

        pairs = self.mapping.build_source_target_pairs(source_joints, target_joints)

        rest_pairs = self.mapping.build_source_target_pairs(source_rest_joints or [], target_joints) if source_rest_joints else {}



        stats["retarget_method"] = "local_matrix_delta"

        stats["mapped_joint_count"] = len(pairs)

        stats["source_rest_mapped_joint_count"] = len(rest_pairs)

        stats["matrix_delta_order"] = self.config.matrix_delta_order

        stats["retarget_copy_pelvis_translation"] = bool(self.config.retarget_copy_pelvis_translation)

        stats["retarget_translation_scale"] = float(self.config.retarget_translation_scale)



        if len(pairs) < 8:

            raise RuntimeError("Too few mapped joints for retargeting (%d). Check mapping JSON / skeleton names." % len(pairs))

        if self.config.require_source_rest_for_matrix_delta and len(rest_pairs) < 8:

            raise RuntimeError(

                "Source Skeleton File / rest T-pose is required for local_matrix_delta, but only %d rest joints mapped. "

                "Set Source Skeleton File to smplh_Tpose.fbx, or keep Auto Find Source Rest File enabled. "

                "Without a real rest pose, a sitting first frame will be treated as neutral and the target can stay in A-pose."

                % len(rest_pairs)

            )



        cmds.currentTime(start, edit=True)

        target_rest_matrix: Dict[str, Any] = {}

        target_rest_rotate: Dict[str, Tuple[float, float, float]] = {}

        target_rest_translate: Dict[str, Tuple[float, float, float]] = {}

        source_rest_matrix: Dict[str, Any] = {}

        source_rest_translate: Dict[str, Tuple[float, float, float]] = {}



        for canonical, (src, tgt) in pairs.items():

            if not (safe_cmds_exists(src) and safe_cmds_exists(tgt)):

                continue

            unlock_transform_attrs(tgt)

            set_rotate_order(tgt, self.config.retarget_rotate_order)

            target_rest_matrix[canonical] = self._matrix_from_node_local(tgt)

            target_rest_rotate[canonical] = self._get_vec(tgt, ROTATE_ATTRS)

            target_rest_translate[canonical] = self._get_vec(tgt, TRANSLATE_ATTRS)



            rest_src = rest_pairs.get(canonical, (None, None))[0] if rest_pairs else None

            if rest_src and safe_cmds_exists(rest_src):

                source_rest_matrix[canonical] = self._matrix_from_node_local(rest_src)

                source_rest_translate[canonical] = self._get_vec(rest_src, TRANSLATE_ATTRS)

            else:

                                                                                                              

                source_rest_matrix[canonical] = self._matrix_from_node_local(src)

                source_rest_translate[canonical] = self._get_vec(src, TRANSLATE_ATTRS)



        frames = []

        sample_by = max(float(self.config.bake_sample_by or 1.0), 0.001)

        frame = float(start)

        while frame <= float(end) + 0.0001:

            frames.append(round(frame, 6))

            frame += sample_by

        if frames and frames[-1] < float(end):

            frames.append(float(end))

        if not frames:

            frames = [float(start)]



        keyed = 0

        keyed_nodes = set()

        pelvis_translation_keys = 0

        source_start_pose_delta_sum = 0.0

        target_start_pose_delta_sum = 0.0

        self.log("Local-matrix retarget: writing keys on %d mapped joints from %.2f to %.2f (%d samples)." % (len(pairs), start, end, len(frames)))



        for frame_index, frame in enumerate(frames):

            cmds.currentTime(frame, edit=True)

            for canonical in DEFAULT_RETARGET_CANONICAL_ORDER:

                if canonical not in pairs:

                    continue

                src, tgt = pairs[canonical]

                if not (safe_cmds_exists(src) and safe_cmds_exists(tgt)):

                    continue

                src_rest_m = source_rest_matrix.get(canonical)

                tgt_rest_m = target_rest_matrix.get(canonical)

                if src_rest_m is None or tgt_rest_m is None:

                    continue

                src_curr_m = self._matrix_from_node_local(src)

                delta_m = self._make_matrix_delta(src_rest_m, src_curr_m)

                out_m = tgt_rest_m * delta_m



                keep_translate = target_rest_translate.get(canonical)

                if canonical == "pelvis" and self.config.retarget_copy_pelvis_translation:

                    keep_translate = None

                self._apply_local_matrix_to_joint(tgt, out_m, keep_translate=keep_translate)



                if canonical == "pelvis" and self.config.retarget_copy_pelvis_translation:

                    src_tr = self._get_vec(src, TRANSLATE_ATTRS)

                    src_rest_tr = source_rest_translate.get(canonical, (0.0, 0.0, 0.0))

                    tgt_rest_tr = target_rest_translate.get(canonical, (0.0, 0.0, 0.0))

                    scale = float(self.config.retarget_translation_scale or 1.0)

                    out_tr = tuple(tgt_rest_tr[i] + (src_tr[i] - src_rest_tr[i]) * scale for i in range(3))

                    self._set_vec(tgt, TRANSLATE_ATTRS, out_tr)



                try:

                    cmds.setKeyframe(tgt, attribute=ROTATE_ATTRS + TRANSLATE_ATTRS, time=frame)

                    keyed += 6

                    if canonical == "pelvis" and self.config.retarget_copy_pelvis_translation:

                        pelvis_translation_keys += 3

                    keyed_nodes.add(tgt)

                except Exception as exc:

                    self.log("Could not key matrix-retarget result for %s (%s): %s" % (canonical, tgt, exc))



                if frame_index == 0:

                                                                                                                

                                                                                          

                    src_rot_now = self._get_vec(src, ROTATE_ATTRS)

                                                                                                      

                    src_rest_list = self._matrix_to_list(src_rest_m)

                    src_curr_list = self._matrix_to_list(src_curr_m)

                    src_matrix_diff = sum(abs(src_curr_list[i] - src_rest_list[i]) for i in range(16))

                    source_start_pose_delta_sum += src_matrix_diff

                    tgt_rot_now = self._get_vec(tgt, ROTATE_ATTRS)

                    tgt_rest_rot = target_rest_rotate.get(canonical, (0.0, 0.0, 0.0))

                    target_start_pose_delta_sum += sum(abs(self._angle_delta_degrees(tgt_rest_rot[i], tgt_rot_now[i])) for i in range(3))



        target_joint_set = sorted(keyed_nodes)

        if not target_joint_set:

            raise RuntimeError("Local-matrix retarget wrote no target keys. Check mapping/source animation.")



        cmds.bakeResults(

            target_joint_set,

            time=(start, end),

            simulation=True,

            sampleBy=sample_by,

            disableImplicitControl=True,

            preserveOutsideKeys=False,

            sparseAnimCurveBake=False,

            removeBakedAttributeFromLayer=False,

            removeBakedAnimFromLayer=False,

            bakeOnOverrideLayer=False,

            minimizeRotation=True,

            controlPoints=False,

            shape=False,

        )

        self._apply_mapping_offsets(pairs)



        anim_curve_count = count_anim_curves_on_nodes(target_joint_set)

        stats["baked_target_joint_count"] = len(target_joint_set)

        stats["direct_keys_written"] = keyed

        stats["pelvis_translation_keys_written"] = pelvis_translation_keys

        stats["target_anim_curve_count_after_retarget"] = anim_curve_count

        stats["source_start_matrix_pose_delta_sum"] = source_start_pose_delta_sum

        stats["target_start_pose_delta_degrees_sum"] = target_start_pose_delta_sum

        if self.config.fail_if_no_target_animation and anim_curve_count <= 0:

            raise RuntimeError("Local-matrix retarget produced no animation curves on the target skeleton. Export cancelled.")

        if self.config.fail_if_no_target_animation and source_start_pose_delta_sum > 1.0 and target_start_pose_delta_sum < 1.0:

            raise RuntimeError(

                "Source first frame is visibly different from rest, but target stayed almost unchanged. "

                "This usually means the wrong Source Skeleton File was used, the mapping JSON is wrong, or matrix_delta_order must be switched. "

                "Try matrix_delta_order=current_rest_inv once if the default rest_inv_current does not work."

            )

        return stats



                                                                        

                                                                   

                                                                        

    @staticmethod

    def _angle_delta_degrees(rest_value: float, current_value: float) -> float:

        delta = float(current_value) - float(rest_value)

        while delta > 180.0:

            delta -= 360.0

        while delta < -180.0:

            delta += 360.0

        return delta



    @staticmethod

    def _get_vec(node: str, attrs: List[str]) -> Tuple[float, float, float]:

        values = []

        for attr in attrs:

            try:

                values.append(float(cmds.getAttr("%s.%s" % (node, attr))))

            except Exception:

                values.append(0.0)

        return values[0], values[1], values[2]



    @staticmethod

    def _set_vec(node: str, attrs: List[str], values: Iterable[float]) -> None:

        for attr, value in zip(attrs, values):

            full = "%s.%s" % (node, attr)

            if not cmds.objExists(full):

                continue

            try:

                if cmds.getAttr(full, lock=True):

                    cmds.setAttr(full, lock=False)

            except Exception:

                pass

            try:

                cmds.setAttr(full, float(value))

            except Exception:

                pass



    def _remap_rotation_delta(self, canonical: str, delta_xyz: Tuple[float, float, float]) -> Tuple[float, float, float]:

        data = self.mapping.axis_remap.get(canonical) or {}

        order = data.get("order") or data.get("axes") or ["x", "y", "z"]

        sign = data.get("sign") or data.get("signs") or [1, 1, 1]

        axis_values = {"x": delta_xyz[0], "y": delta_xyz[1], "z": delta_xyz[2]}

        out = []

        for i in range(3):

            axis = str(order[i] if i < len(order) else ["x", "y", "z"][i]).lower().replace("rotate", "")[:1]

            sgn = float(sign[i]) if i < len(sign) else 1.0

            out.append(axis_values.get(axis, 0.0) * sgn)

        return out[0], out[1], out[2]



    def _retarget_with_local_euler_delta(

        self,

        source_joints: List[str],

        target_joints: List[str],

        start: float,

        end: float,

        source_rest_joints: Optional[List[str]] = None,

    ) -> Dict[str, Any]:

        require_maya()

        stats: Dict[str, Any] = {}

        pairs = self.mapping.build_source_target_pairs(source_joints, target_joints)

        rest_pairs = self.mapping.build_source_target_pairs(source_rest_joints or [], target_joints) if source_rest_joints else {}



        stats["retarget_method"] = "local_euler_delta"

        stats["mapped_joint_count"] = len(pairs)

        stats["source_rest_mapped_joint_count"] = len(rest_pairs)

        stats["retarget_copy_pelvis_translation"] = bool(self.config.retarget_copy_pelvis_translation)

        stats["retarget_translation_scale"] = float(self.config.retarget_translation_scale)



        if len(pairs) < 8:

            raise RuntimeError("Too few mapped joints for retargeting (%d). Check mapping JSON / skeleton names." % len(pairs))



                                                                                             

        cmds.currentTime(start, edit=True)

        target_rest_rotate: Dict[str, Tuple[float, float, float]] = {}

        target_rest_translate: Dict[str, Tuple[float, float, float]] = {}

        source_rest_rotate: Dict[str, Tuple[float, float, float]] = {}

        source_rest_translate: Dict[str, Tuple[float, float, float]] = {}



        for canonical, (src, tgt) in pairs.items():

            if not (safe_cmds_exists(src) and safe_cmds_exists(tgt)):

                continue

            unlock_transform_attrs(tgt)

            set_rotate_order(tgt, self.config.retarget_rotate_order)

            target_rest_rotate[canonical] = self._get_vec(tgt, ROTATE_ATTRS)

            target_rest_translate[canonical] = self._get_vec(tgt, TRANSLATE_ATTRS)



                                                                                                     

            rest_src = rest_pairs.get(canonical, (None, None))[0] if rest_pairs else None

            if rest_src and safe_cmds_exists(rest_src):

                source_rest_rotate[canonical] = self._get_vec(rest_src, ROTATE_ATTRS)

                source_rest_translate[canonical] = self._get_vec(rest_src, TRANSLATE_ATTRS)

            else:

                                                                                                        

                                                                     

                source_rest_rotate[canonical] = self._get_vec(src, ROTATE_ATTRS)

                source_rest_translate[canonical] = self._get_vec(src, TRANSLATE_ATTRS)



        if not source_rest_joints:

            self.log("WARNING: Source Skeleton File was not used. Local-delta retarget is using the first animation frame as source rest pose.")

        elif len(rest_pairs) < 8:

            self.log("WARNING: Source Skeleton File was imported, but only %d rest joints mapped. Check Source Skeleton File and Mapping JSON." % len(rest_pairs))



        frames = []

        sample_by = max(float(self.config.bake_sample_by or 1.0), 0.001)

        frame = float(start)

        while frame <= float(end) + 0.0001:

            frames.append(round(frame, 6))

            frame += sample_by

        if frames and frames[-1] < float(end):

            frames.append(float(end))

        if not frames:

            frames = [float(start)]



        keyed = 0

        keyed_nodes = set()

        pelvis_translation_keys = 0

        self.log("Local-delta retarget: writing keys on %d mapped joints from %.2f to %.2f (%d samples)." % (len(pairs), start, end, len(frames)))



        for frame in frames:

            cmds.currentTime(frame, edit=True)

            for canonical in DEFAULT_RETARGET_CANONICAL_ORDER:

                if canonical not in pairs:

                    continue

                src, tgt = pairs[canonical]

                if not (safe_cmds_exists(src) and safe_cmds_exists(tgt)):

                    continue

                src_rot = self._get_vec(src, ROTATE_ATTRS)

                src_rest_rot = source_rest_rotate.get(canonical, (0.0, 0.0, 0.0))

                tgt_rest_rot = target_rest_rotate.get(canonical, (0.0, 0.0, 0.0))

                delta = tuple(self._angle_delta_degrees(a, b) for a, b in zip(src_rest_rot, src_rot))

                delta = self._remap_rotation_delta(canonical, delta)

                out_rot = tuple(tgt_rest_rot[i] + delta[i] for i in range(3))

                self._set_vec(tgt, ROTATE_ATTRS, out_rot)

                try:

                    cmds.setKeyframe(tgt, attribute=ROTATE_ATTRS, time=frame)

                    keyed += 3

                    keyed_nodes.add(tgt)

                except Exception as exc:

                    self.log("Could not key rotation for %s (%s): %s" % (canonical, tgt, exc))



                if canonical == "pelvis" and self.config.retarget_copy_pelvis_translation:

                    src_tr = self._get_vec(src, TRANSLATE_ATTRS)

                    src_rest_tr = source_rest_translate.get(canonical, (0.0, 0.0, 0.0))

                    tgt_rest_tr = target_rest_translate.get(canonical, (0.0, 0.0, 0.0))

                    scale = float(self.config.retarget_translation_scale or 1.0)

                    out_tr = tuple(tgt_rest_tr[i] + (src_tr[i] - src_rest_tr[i]) * scale for i in range(3))

                    self._set_vec(tgt, TRANSLATE_ATTRS, out_tr)

                    try:

                        cmds.setKeyframe(tgt, attribute=TRANSLATE_ATTRS, time=frame)

                        keyed += 3

                        pelvis_translation_keys += 3

                        keyed_nodes.add(tgt)

                    except Exception as exc:

                        self.log("Could not key pelvis translation for %s: %s" % (tgt, exc))



                                                                                                        

        target_joint_set = sorted(keyed_nodes)

        if not target_joint_set:

            raise RuntimeError("Local-delta retarget wrote no target keys. Check mapping/source animation.")

        cmds.bakeResults(

            target_joint_set,

            time=(start, end),

            simulation=True,

            sampleBy=sample_by,

            disableImplicitControl=True,

            preserveOutsideKeys=False,

            sparseAnimCurveBake=False,

            removeBakedAttributeFromLayer=False,

            removeBakedAnimFromLayer=False,

            bakeOnOverrideLayer=False,

            minimizeRotation=True,

            controlPoints=False,

            shape=False,

        )

        self._apply_mapping_offsets(pairs)



        anim_curve_count = count_anim_curves_on_nodes(target_joint_set)

        stats["baked_target_joint_count"] = len(target_joint_set)

        stats["direct_keys_written"] = keyed

        stats["pelvis_translation_keys_written"] = pelvis_translation_keys

        stats["target_anim_curve_count_after_retarget"] = anim_curve_count

        if self.config.fail_if_no_target_animation and anim_curve_count <= 0:

            raise RuntimeError("Retarget produced no animation curves on the target skeleton. Export cancelled.")

        return stats



                                                                        

                                                                     

                                                                        



    def _retarget_with_constraints(self, source_joints: List[str], target_joints: List[str], start: float, end: float) -> Dict[str, Any]:

        require_maya()

        stats: Dict[str, Any] = {}

        pairs = self.mapping.build_source_target_pairs(source_joints, target_joints)

        stats["retarget_method"] = "constraints"

        stats["mapped_joint_count"] = len(pairs)

        stats["retarget_maintain_offset"] = bool(self.config.retarget_maintain_offset)

        stats["retarget_use_point_constraint_for_root"] = bool(self.config.retarget_use_point_constraint_for_root)

        stats["retarget_use_point_constraint_for_pelvis"] = bool(self.config.retarget_use_point_constraint_for_pelvis)

        if not self.config.retarget_maintain_offset:

            self.log("WARNING: Maintain Constraint Offset is OFF. This is unsafe for SMPL-H -> FemaleStd and can rotate the body sideways.")

        if len(pairs) < 8:

            raise RuntimeError("Too few mapped joints for retargeting (%d). Check mapping JSON / skeleton names." % len(pairs))



        constraints = []

        target_joint_set = []



        for canonical in DEFAULT_RETARGET_CANONICAL_ORDER:

            if canonical not in pairs:

                continue

            src, tgt = pairs[canonical]

            if not (safe_cmds_exists(src) and safe_cmds_exists(tgt)):

                continue

            unlock_transform_attrs(tgt)

            set_rotate_order(tgt, self.config.retarget_rotate_order)

            target_joint_set.append(tgt)



            try:

                if canonical == "root" and self.config.retarget_use_point_constraint_for_root:

                    constraints.extend(cmds.parentConstraint(src, tgt, maintainOffset=self.config.retarget_maintain_offset) or [])

                elif canonical == "pelvis" and self.config.retarget_use_point_constraint_for_pelvis:

                    constraints.extend(cmds.pointConstraint(src, tgt, maintainOffset=self.config.retarget_maintain_offset) or [])

                    constraints.extend(cmds.orientConstraint(src, tgt, maintainOffset=self.config.retarget_maintain_offset) or [])

                else:

                    constraints.extend(cmds.orientConstraint(src, tgt, maintainOffset=self.config.retarget_maintain_offset) or [])

            except Exception as exc:

                self.log("Constraint failed for %s: %s -> %s: %s" % (canonical, src, tgt, exc))



        target_joint_set = sorted(set(target_joint_set))

        if not target_joint_set:

            raise RuntimeError("No target joints were constrained. Retarget failed.")



        self.log("Constraint retarget: baking %d target joints from %.2f to %.2f..." % (len(target_joint_set), start, end))

        cmds.bakeResults(

            target_joint_set,

            time=(start, end),

            simulation=True,

            sampleBy=float(self.config.bake_sample_by),

            disableImplicitControl=True,

            preserveOutsideKeys=False,

            sparseAnimCurveBake=False,

            removeBakedAttributeFromLayer=False,

            removeBakedAnimFromLayer=False,

            bakeOnOverrideLayer=False,

            minimizeRotation=True,

            controlPoints=False,

            shape=False,

        )



        if constraints:

            try:

                cmds.delete(constraints)

            except Exception:

                pass



        self._apply_mapping_offsets(pairs)



        anim_curve_count = count_anim_curves_on_nodes(target_joint_set)

        stats["baked_target_joint_count"] = len(target_joint_set)

        stats["constraint_count"] = len(constraints)

        stats["target_anim_curve_count_after_retarget"] = anim_curve_count

        if self.config.fail_if_no_target_animation and anim_curve_count <= 0:

            raise RuntimeError("Constraint retarget produced no animation curves on the target skeleton. Export cancelled.")

        return stats



    def _retarget_with_direct_constraints_no_offset(self, source_joints: List[str], target_joints: List[str], start: float, end: float) -> Dict[str, Any]:

        require_maya()

        stats: Dict[str, Any] = {}

        pairs = self.mapping.build_source_target_pairs(source_joints, target_joints)

        stats["retarget_method"] = "direct_constraints_no_offset"

        stats["mapped_joint_count"] = len(pairs)

        stats["maintain_offset"] = False

        if len(pairs) < 8:

            raise RuntimeError("Too few mapped joints for direct fallback retargeting (%d). Check mapping JSON / skeleton names." % len(pairs))



        cmds.currentTime(start, edit=True)

        target_rest_rot = {}

        for canonical, (_src, tgt) in pairs.items():

            if safe_cmds_exists(tgt):

                try:

                    target_rest_rot[canonical] = get_world_rotation(tgt)

                    unlock_transform_attrs(tgt)

                    set_rotate_order(tgt, self.config.retarget_rotate_order)

                except Exception:

                    pass



        constraints = []

        target_joint_set = []

        preview = []

        for canonical in DEFAULT_RETARGET_CANONICAL_ORDER:

            if canonical not in pairs:

                continue

            src, tgt = pairs[canonical]

            if not (safe_cmds_exists(src) and safe_cmds_exists(tgt)):

                continue

            try:

                if canonical == "pelvis":

                    constraints.extend(cmds.parentConstraint(src, tgt, maintainOffset=False) or [])

                else:

                    constraints.extend(cmds.orientConstraint(src, tgt, maintainOffset=False) or [])

                target_joint_set.append(tgt)

                if len(preview) < 12:

                    preview.append("%s:%s->%s" % (canonical, short_name(src), short_name(tgt)))

            except Exception as exc:

                self.log("Direct no-offset constraint failed for %s -> %s: %s" % (short_name(src), short_name(tgt), exc))



        target_joint_set = sorted(set(target_joint_set))

        self.log("Direct no-offset fallback pairs: %s" % "; ".join(preview))

        self.log("Direct no-offset fallback: constraints=%d, target joints=%d, bake range %.2f-%.2f" % (len(constraints), len(target_joint_set), start, end))

        if not target_joint_set:

            raise RuntimeError("No target joints were driven by direct no-offset fallback.")



        cmds.bakeResults(

            target_joint_set,

            time=(start, end),

            simulation=True,

            sampleBy=max(float(self.config.bake_sample_by or 1.0), 0.001),

            disableImplicitControl=True,

            preserveOutsideKeys=False,

            sparseAnimCurveBake=False,

            removeBakedAttributeFromLayer=False,

            removeBakedAnimFromLayer=False,

            bakeOnOverrideLayer=False,

            minimizeRotation=True,

            controlPoints=False,

            shape=False,

        )

        if constraints:

            try:

                cmds.delete(constraints)

            except Exception:

                pass



        anim_curve_count = count_anim_curves_on_nodes(target_joint_set)

        target_pose_delta_degrees_sum = 0.0

        cmds.currentTime(start, edit=True)

        for canonical, (_src, tgt) in pairs.items():

            if canonical in target_rest_rot and safe_cmds_exists(tgt):

                try:

                    now_rot = get_world_rotation(tgt)

                    target_pose_delta_degrees_sum += sum(abs(angular_delta(target_rest_rot[canonical][i], now_rot[i])) for i in range(3))

                except Exception:

                    pass



        stats["baked_target_joint_count"] = len(target_joint_set)

        stats["constraint_count"] = len(constraints)

        stats["target_anim_curve_count_after_retarget"] = anim_curve_count

        stats["target_start_pose_delta_degrees_sum"] = target_pose_delta_degrees_sum

        self.log("Direct no-offset fallback result: target_anim_curves=%d, target_start_pose_delta_sum=%.3f" % (anim_curve_count, target_pose_delta_degrees_sum))



        if self.config.fail_if_no_target_animation and anim_curve_count <= 0:

            raise RuntimeError("Direct no-offset fallback produced no animation curves on target skeleton.")

        if self.config.fail_if_no_target_animation and target_pose_delta_degrees_sum < 1.0:

            raise RuntimeError("Direct no-offset fallback baked keys, but target still appears near A-pose. Source animation may not have been imported as animated/posed joints.")

        return stats



    def _apply_mapping_offsets(self, pairs: Dict[str, Tuple[str, str]]) -> None:

        offsets = self.mapping.offsets or {}

        if not offsets:

            return

        for canonical, (_, target) in pairs.items():

            offset_data = offsets.get(canonical) or offsets.get(short_name(target))

            if not offset_data:

                continue

            rotate = offset_data.get("rotate") or offset_data.get("rotation")

            if rotate and len(rotate) >= 3:

                for attr, amount in zip(ROTATE_ATTRS, rotate[:3]):

                    curves = cmds.listConnections("%s.%s" % (target, attr), source=True, destination=False, type="animCurve") or []

                    for curve in curves:

                        add_value_to_curve(curve, float(amount))





def add_value_to_curve(curve: str, amount: float) -> int:

    times, values = get_curve_key_data(curve)

    for t, v in zip(times, values):

        set_curve_value(curve, t, v + amount)

    return len(times)





                                                                               

                 

                                                                               



class BatchProcessor:

    def __init__(self, config: ToolConfig, log_callback=None, progress_callback=None):

        self.config = config

        self.log_callback = log_callback

        self.progress_callback = progress_callback

                                                                                

                                                                                 

        search_dirs = [

            os.path.dirname(normalize_path(config.mapping_json)) if config.mapping_json else "",

            script_directory(),

            os.path.join(script_directory(), "Presets"),

            os.path.join(script_directory(), "Presets", "SMPLH_FemaleStd"),

        ]

        resolved_mapping = resolve_real_mapping_json(config.mapping_json, search_dirs, log_callback=self.log)

        if resolved_mapping != normalize_path(config.mapping_json or ""):

            config.mapping_json = resolved_mapping

        if config.mapping_json and not is_real_joint_mapping_json(config.mapping_json):

            raise RuntimeError(

                "Invalid Joint Mapping JSON. You selected a config/preset JSON instead of the real joint mapping. "

                "Use Presets/SMPLH_FemaleStd/smplh_to_femalestd_body_mapping.json. Current value: %s" % config.mapping_json

            )

        mapping_data = load_json_file(config.mapping_json) if config.mapping_json else {}

        self.mapping = JointMapping(mapping_data)

        if config.mapping_json:

            self.log("Using Joint Mapping JSON: %s" % config.mapping_json)

        self.scanner = AnimationScanner(config, self.mapping, log_callback=self.log)

        self.corrector = AnimationCorrector(config, self.mapping, log_callback=self.log)

        self.retargeter = AnimationRetargeter(config, self.mapping, log_callback=self.log)

        self.npz_importer = NPZImporter(config, self.mapping, log_callback=self.log)

        self._resolve_packaged_preset_paths()

        self.results: List[ScanResult] = []



    def _resolve_packaged_preset_paths(self) -> None:

        if not getattr(self.config, "auto_find_source_rest_file", True):

            return

        if self.config.source_skeleton_file and os.path.isfile(normalize_path(self.config.source_skeleton_file)):

            return

        mapping_dir = normalize_path(os.path.dirname(self.config.mapping_json)) if self.config.mapping_json else ""

        target_dir = normalize_path(os.path.dirname(self.config.target_skeleton_file)) if self.config.target_skeleton_file else ""

        input_dir = normalize_path(self.config.input_folder)

        input_parent = normalize_path(os.path.dirname(input_dir)) if input_dir else ""

        tool_dir = script_directory()

        names = []

        source_name = self.mapping.mapping_data.get("source_file") if isinstance(self.mapping.mapping_data, dict) else ""

        if source_name:

            names.append(os.path.basename(str(source_name)))

            names.append(str(source_name))

        names.extend(["smplh_Tpose.fbx", "SMPLH_Tpose.fbx", "smplh_tpose.fbx"])

        search_dirs = [mapping_dir, tool_dir, os.path.join(tool_dir, "Presets"), os.path.join(tool_dir, "Presets", "SMPLH_FemaleStd"),

                       os.path.join(tool_dir, "Presets", "SMPLH"), target_dir, input_parent]

        found = find_existing_file_by_names(names, search_dirs)

        if found:

            self.config.source_skeleton_file = found

            self.log("Auto-found Source Skeleton File / rest pose: %s" % found)



    def log(self, message: str) -> None:

        text = "[%s] %s" % (datetime.datetime.now().strftime("%H:%M:%S"), message)

        if self.log_callback:

            self.log_callback(text)

        else:

            print(text)



    def progress(self, index: int, total: int, label: str) -> None:

        if self.progress_callback:

            self.progress_callback(index, total, label)



    def collect_files(self) -> List[str]:

        input_folder = normalize_path(self.config.input_folder)

        if not os.path.isdir(input_folder):

            raise RuntimeError("Input folder does not exist: %s" % input_folder)

        allowed_exts = set()

        if self.config.include_fbx:

            allowed_exts.update(SUPPORTED_FBX_EXTENSIONS)

        if self.config.include_npz:

            allowed_exts.update(SUPPORTED_NPZ_EXTENSIONS)

        if not allowed_exts:

            raise RuntimeError("No input file types are enabled.")

        files = []

        if self.config.recursive_scan:

            for root, _, filenames in os.walk(input_folder):

                for filename in filenames:

                    if os.path.splitext(filename)[1].lower() in allowed_exts:

                        files.append(normalize_path(os.path.join(root, filename)))

        else:

            for filename in os.listdir(input_folder):

                path = os.path.join(input_folder, filename)

                if os.path.isfile(path) and os.path.splitext(filename)[1].lower() in allowed_exts:

                    files.append(normalize_path(path))

        files.sort()

        if self.config.max_files and self.config.max_files > 0:

            files = files[:self.config.max_files]

        return files



    def run(self) -> List[ScanResult]:

        require_maya()

        self.validate_config()

        files = self.collect_files()

        if not files:

            self.log("No files found.")

            return []

        self.log("Found %d file(s)." % len(files))

        self.log("Run mode: scan_only=%s, retarget_enabled=%s, export_enabled=%s, skip_bad_files_before_retarget=%s" % (

            bool(self.config.scan_only), bool(self.config.retarget_enabled), bool(self.config.export_enabled), bool(getattr(self.config, "skip_bad_files_before_retarget", False))

        ))

        self.log("Input Folder: %s" % normalize_path(self.config.input_folder))

        self.log("Output Folder: %s" % normalize_path(self.config.output_folder))

        self.log("Target Skeleton File: %s" % normalize_path(self.config.target_skeleton_file))

        self.log("Source Rest Skeleton File: %s" % normalize_path(self.config.source_skeleton_file))

        self.log("Joint Mapping JSON: %s" % normalize_path(self.config.mapping_json))

        ensure_dir(self.config.output_folder)

        ensure_dir(self.config.report_folder)

        if self.config.copy_bad_files:

            ensure_dir(self.config.bad_folder)

        if self.config.copy_good_files:

            ensure_dir(self.config.good_folder)



        self.results = []

        start_all = time.time()

        self._start_maya_progress(len(files))

        try:

            for index, file_path in enumerate(files, 1):

                self.progress(index, len(files), os.path.basename(file_path))

                self._update_maya_progress(index, len(files), file_path)

                result = self.process_file(file_path)

                self.results.append(result)

                self.log("%s -> %s (%d issue(s))" % (os.path.basename(file_path), result.status, len(result.issues)))

                                                       

                try:

                    cmds.refresh(force=True)

                except Exception:

                    pass

                try:

                    import maya.utils as maya_utils

                    maya_utils.processIdleEvents()

                except Exception:

                    pass

        finally:

            self._end_maya_progress()



        total_time = time.time() - start_all

        self.log("Batch finished in %.2f seconds." % total_time)

        writer = ReportWriter(self.config.report_folder)

        report_paths = writer.write(self.results, self.config)

        self.log("Reports written:")

        for key, path in report_paths.items():

            self.log("  %s: %s" % (key, path))

        return self.results



    def validate_config(self) -> None:

        if not self.config.input_folder:

            raise RuntimeError("Input Folder is required.")

        if not self.config.report_folder:

            raise RuntimeError("Report Folder is required.")

                                                                                   

                                                                                

        if self.config.mapping_json:

            search_dirs = [

                os.path.dirname(normalize_path(self.config.mapping_json)),

                script_directory(),

                os.path.join(script_directory(), "Presets"),

                os.path.join(script_directory(), "Presets", "SMPLH_FemaleStd"),

            ]

            self.config.mapping_json = resolve_real_mapping_json(self.config.mapping_json, search_dirs, log_callback=self.log)

            if not is_real_joint_mapping_json(self.config.mapping_json):

                raise RuntimeError(

                    "Invalid Joint Mapping JSON. Do NOT select the safe_config JSON here. "

                    "Select smplh_to_femalestd_body_mapping.json. Current value: %s" % self.config.mapping_json

                )

        if self.config.retarget_enabled and not self.config.scan_only:

            if not self.config.target_skeleton_file:

                raise RuntimeError("Target Skeleton File is required for retarget/export mode.")

            if not os.path.isfile(normalize_path(self.config.target_skeleton_file)):

                raise RuntimeError("Target Skeleton File does not exist: %s" % self.config.target_skeleton_file)

        if self.config.include_npz and self.config.retarget_enabled:

                                                                                             

            if self.config.source_skeleton_file and not os.path.isfile(normalize_path(self.config.source_skeleton_file)):

                raise RuntimeError("Source Skeleton File does not exist: %s" % self.config.source_skeleton_file)

        method = (self.config.retarget_method or "").strip().lower()

        rest_required_methods = {"humanik_batch", "humanik", "maya_hik", "hik_batch", "positional_ik_solver", "ik_pose_solver", "directional_ik", "world_euler_delta_constraints", "world_euler_delta", "local_matrix_delta", "matrix", "matrix_delta", "rest_world_delta_constraints", "world_delta", "rest_world"}

        if self.config.retarget_enabled and method in rest_required_methods:

            if self.config.retarget_use_source_rest_file and self.config.require_source_rest_for_matrix_delta:

                if not self.config.source_skeleton_file or not os.path.isfile(normalize_path(self.config.source_skeleton_file)):

                    raise RuntimeError(

                        "%s requires a real Source Skeleton File/rest T-pose. "

                        "Set Source Skeleton File to smplh_Tpose.fbx or click Apply SMPL-H -> FemaleStd Safe Defaults. "

                        "Using the first animation frame as rest is not allowed for this preset because it can keep sitting/action clips in target A-pose."

                        % method

                    )



    def process_file(self, file_path: str) -> ScanResult:

        result = ScanResult(file_path=normalize_path(file_path), started_at=now_iso())

        start_time = time.time()

        ext = os.path.splitext(file_path)[1].lower()

        result.source_type = ext.lstrip(".").upper()



        try:

            if self.config.dry_run:

                result.status = STATUS_SKIPPED

                result.add_issue("DRY_RUN", SEVERITY_INFO, "Dry run enabled. File was not imported or processed.")

                return result



            reset_scene()

            if self.config.force_frame_rate:

                set_scene_frame_rate(self.config.target_frame_rate, self.log_callback)

            result.stats["maya_time_unit"] = get_scene_time_unit()

            result.stats["target_frame_rate"] = float(self.config.target_frame_rate)

            if ext == ".fbx":

                self._process_fbx(file_path, result)

            elif ext == ".npz":

                self._process_npz(file_path, result)

            else:

                result.status = STATUS_SKIPPED

                result.add_issue("UNSUPPORTED_FILE", SEVERITY_ERROR, "Unsupported file extension: %s" % ext)

        except Exception as exc:

            result.status = STATUS_FAILED

            result.add_issue("PROCESS_FAILED", SEVERITY_FATAL, "%s\n%s" % (exc, traceback.format_exc()))

        finally:

            result.finished_at = now_iso()

            result.duration_seconds = time.time() - start_time

            self._sort_file_if_needed(result)

        return result



    def _run_retarget_with_fallbacks(

        self,

        source_joints: List[str],

        target_joints: List[str],

        start: float,

        end: float,

        source_rest_joints: Optional[List[str]] = None,

    ) -> Dict[str, Any]:

        primary = (self.config.retarget_method or "humanik_batch").strip().lower()

        methods = [primary]

        if getattr(self.config, "auto_retarget_fallback", True):

                                                                                                     

                                                                              

            for m in ["humanik_batch", "positional_ik_solver", "hierarchical_world_matrix", "world_euler_delta_constraints", "rest_world_delta_constraints", "constraints", "direct_constraints_no_offset", "local_matrix_delta"]:

                if m not in methods:

                    methods.append(m)

        errors = []

        original_method = self.config.retarget_method

        for method in methods:

            try:

                self.config.retarget_method = method

                self.retargeter.config.retarget_method = method

                self.log("Trying retarget method: %s" % method)

                stats = self.retargeter.retarget_current_scene(source_joints, target_joints, start, end, source_rest_joints=source_rest_joints)

                                                                                                  

                try:

                    sanity = self.retargeter.validate_target_pose_sanity(source_joints, target_joints, start, label=method)

                    stats.update(sanity)

                except Exception as sanity_exc:

                    raise RuntimeError(str(sanity_exc))

                stats["retarget_method_used"] = method

                if errors:

                    stats["retarget_fallback_errors"] = errors

                self.log("Retarget method succeeded: %s" % method)

                return stats

            except Exception as exc:

                msg = "%s failed: %s" % (method, exc)

                errors.append(msg)

                self.log("WARNING: " + msg)

        self.config.retarget_method = original_method

        self.retargeter.config.retarget_method = original_method

        raise RuntimeError("All retarget methods failed. Last errors:\n%s" % "\n".join(errors))



    def _process_fbx(self, file_path: str, result: ScanResult) -> None:

        self.log("---- FBX BEGIN: %s ----" % os.path.basename(file_path))

        self.log("FULL_PIPELINE_GUARD: scan_only=%s retarget_enabled=%s export_enabled=%s skip_bad=%s" % (

            bool(self.config.scan_only), bool(self.config.retarget_enabled), bool(self.config.export_enabled), bool(getattr(self.config, "skip_bad_files_before_retarget", False))

        ))



        if self.config.scan_only or not self.config.retarget_enabled:

            self.log("SCAN_ONLY_PATH: importing source FBX only; no retarget/export will be attempted.")

            import_animation_fbx(file_path, namespace="SRC")

            source_joints = get_all_joints()

            self.log("SCAN_ONLY_PATH: imported source joints=%d" % len(source_joints))

            self.scanner.scan_scene(result, source_joints)

            return



                                                                                                              

        self.config.scan_only = False

        self.config.retarget_enabled = True

        if not hasattr(self.config, "skip_bad_files_before_retarget"):

            self.config.skip_bad_files_before_retarget = False



                                    

        self.log("STAGE 1/8: Import target skeleton: %s" % normalize_path(self.config.target_skeleton_file))

        target_nodes = import_maya_or_fbx(self.config.target_skeleton_file, namespace="TGT")

        target_joints = get_all_joints()

        target_roots_before = get_root_joints(target_joints)

        result.stats["target_imported_node_count"] = len(target_nodes)

        result.stats["target_joint_count"] = len(target_joints)

        result.stats["target_root_joints"] = [short_name(x) for x in target_roots_before]

        self.log("STAGE 1 OK: target nodes=%d joints=%d roots=%s" % (len(target_nodes), len(target_joints), ", ".join([short_name(x) for x in target_roots_before[:5]])))

        if not target_joints:

            raise RuntimeError("Target skeleton imported but no joints were found.")



                                                

                                                                                           

                                                                                        

        source_rest_joints: List[str] = []

        source_rest_live_joints: List[str] = []

        if (self.config.retarget_use_source_rest_file and self.config.source_skeleton_file

                and os.path.isfile(normalize_path(self.config.source_skeleton_file))):

            self.log("STAGE 2/8: Import source rest skeleton: %s" % normalize_path(self.config.source_skeleton_file))

            before_rest = set(cmds.ls(type="joint", long=True) or [])

            rest_nodes = import_maya_or_fbx(self.config.source_skeleton_file, namespace="SRCREST")

            after_rest = set(cmds.ls(type="joint", long=True) or [])

            source_rest_live_joints = sorted(after_rest - before_rest)

                                                                                                            

            if not source_rest_live_joints:

                source_rest_live_joints = [j for j in get_all_joints() if j not in set(target_joints)]

                self.log("STAGE 2 WARNING: rest namespace-delta was empty; fallback live rest joints=%d" % len(source_rest_live_joints))

            source_rest_joints = duplicate_rest_reference_joints(source_rest_live_joints, namespace="SRCREST_REF", log_callback=self.log)

            result.stats["source_rest_imported_node_count"] = len(rest_nodes)

            result.stats["source_rest_live_joint_count"] = len(source_rest_live_joints)

            result.stats["source_rest_reference_joint_count"] = len(source_rest_joints)

            self.log("STAGE 2 OK: source rest nodes=%d live_joints=%d protected_rest_joints=%d" % (len(rest_nodes), len(source_rest_live_joints), len(source_rest_joints)))

        else:

            self.log("STAGE 2 WARNING: no Source Skeleton File/rest T-pose was imported. Some retarget modes will fail.")



                                     

        self.log("STAGE 3/8: Import source animation FBX: %s" % normalize_path(file_path))

        before = set(cmds.ls(type="joint", long=True) or [])

        before_curve_count = len(get_scene_anim_curves())

        source_nodes = import_animation_fbx(file_path, namespace="SRC")

        after = set(cmds.ls(type="joint", long=True) or [])

        after_curve_count = len(get_scene_anim_curves())

        source_joints = sorted(after - before)

        source_resolution_mode = "new_imported_joints"



        if not source_joints and source_rest_live_joints:

                                                                                                   

                                                                                    

            source_joints = [j for j in source_rest_live_joints if safe_cmds_exists(j)]

            source_resolution_mode = "animation_applied_to_source_rest_live_joints"

            self.log("STAGE 3 INFO: no new source joints were created; using live source rest skeleton as animated source joints=%d" % len(source_joints))



        if not source_joints:

            exclude = set(target_joints) | set(source_rest_joints) | set(source_rest_live_joints)

            source_joints = [j for j in get_all_joints() if j not in exclude]

            source_resolution_mode = "scene_fallback_excluding_target_and_rest"

            self.log("STAGE 3 WARNING: namespace-delta source joints were empty; fallback source joints=%d" % len(source_joints))



        if not source_joints:

            raise RuntimeError("Source animation imported but no source joints were found. This FBX may be animation-only and did not bind to the source rest skeleton, or Maya FBX import settings are rejecting the take.")



        keyed_source_joints = count_keyed_transform_joints(source_joints)

        result.stats["source_imported_node_count"] = len(source_nodes)

        result.stats["source_joint_count"] = len(source_joints)

        result.stats["source_joint_resolution_mode"] = source_resolution_mode

        result.stats["source_keyed_joint_count"] = keyed_source_joints

        result.stats["scene_anim_curves_before_source_import"] = before_curve_count

        result.stats["scene_anim_curves_after_source_import"] = after_curve_count

        result.stats["source_joint_preview"] = [short_name(x) for x in source_joints[:30]]

        self.log("STAGE 3 OK: mode=%s source_nodes=%d joints=%d keyed_joints=%d scene_curves_before=%d after=%d first_joints=%s" % (source_resolution_mode, len(source_nodes), len(source_joints), keyed_source_joints, before_curve_count, after_curve_count, ", ".join([short_name(x) for x in source_joints[:12]])))

        if keyed_source_joints == 0 and after_curve_count <= before_curve_count:

            self.log("STAGE 3 WARNING: source joints resolved, but no transform animation curves were detected after FBX import. Retarget will still run using current pose/timeline, but the source FBX may contain no baked joint animation.")



                                                                                         

        self.log("STAGE 4/8: Scan source animation. Scan result is diagnostic; Full Batch continues unless Skip Bad is ON.")

        self.scanner.scan_scene(result, source_joints)

        result.stats["source_anim_curve_count"] = count_anim_curves_on_nodes(source_joints)

        result.stats["scene_anim_curve_count_after_source_import"] = len(get_scene_anim_curves())

        self.log("STAGE 4 OK: scan_status=%s issues=%d source_anim_curves=%d scene_anim_curves=%d" % (

            result.status, len(result.issues), result.stats["source_anim_curve_count"], result.stats["scene_anim_curve_count_after_source_import"]

        ))

        for issue in result.issues[:12]:

            self.log("  SCAN_ISSUE: %s %s - %s" % (issue.severity, issue.code, issue.message))

        if result.status == STATUS_BAD and bool(getattr(self.config, "skip_bad_files_before_retarget", False)):

            self.log("STOP_REASON: Skip Bad Files Before Retarget is ON and scan_status=BAD. No retarget/export for this file.")

            return

        if result.status == STATUS_BAD:

            self.log("CONTINUE_AFTER_BAD_SCAN: skip_bad=False, so retarget/export WILL continue.")



                                                

        self.log("STAGE 5/8: Resolve retarget joint mapping.")

        pairs_debug = self.mapping.build_source_target_pairs(source_joints, target_joints)

        rest_pairs_debug = self.mapping.build_source_target_pairs(source_rest_joints or [], target_joints) if source_rest_joints else {}

        result.stats["resolved_source_target_pair_count"] = len(pairs_debug)

        result.stats["resolved_rest_target_pair_count"] = len(rest_pairs_debug)

        self.log("STAGE 5 OK: source_target_pairs=%d rest_target_pairs=%d target_joints=%d" % (len(pairs_debug), len(rest_pairs_debug), len(target_joints)))

        if len(pairs_debug) < 8:

            self.log("MAPPING_FAILURE_DEBUG: too few source animation mapping pairs.")

            self.log("  Source first joints: %s" % ", ".join([short_name(x) for x in source_joints[:40]]))

            self.log("  Target first joints: %s" % ", ".join([short_name(x) for x in target_joints[:40]]))

            raise RuntimeError("Too few source-target mapping pairs (%d). Retarget cannot continue." % len(pairs_debug))

        preview_pairs = []

        for k in list(pairs_debug.keys())[:18]:

            preview_pairs.append("%s:%s->%s" % (k, short_name(pairs_debug[k][0]), short_name(pairs_debug[k][1])))

        self.log("  Pair preview: %s" % "; ".join(preview_pairs))



                                                                                                        

        self.log("STAGE 6/8: Resolve frame range.")

        source_curves = []

        for j in source_joints:

            source_curves.extend(get_connected_anim_curves(j))

        start, end = get_anim_time_range(source_curves or None)

        if end < start:

            start, end = end, start

        if abs(end - start) < 0.001:

                                                                            

            end = start + 1.0

            self.log("STAGE 6 WARNING: source has near-zero frame range; baking a 1-frame pose from %.2f to %.2f." % (start, end))

        set_timeline(start, end)

        result.stats["retarget_start_frame"] = start

        result.stats["retarget_end_frame"] = end

        result.stats["retarget_frame_count_estimate"] = max(1, int(round(end - start + 1)))

        self.log("STAGE 6 OK: frame_range=%.3f -> %.3f, source_curves=%d" % (start, end, len(source_curves)))



                                     

                                                                                                   

                                                                                                 

                                                                              

        try:

            self.config.humanik_source_guided_arm_ik_current_source_file_path = normalize_path(file_path)

        except Exception:

            pass

        self.log("STAGE 7/8: Retarget target skeleton. Primary method=%s auto_fallback=%s" % (self.config.retarget_method, bool(getattr(self.config, "auto_retarget_fallback", True))))

        retarget_stats = self._run_retarget_with_fallbacks(source_joints, target_joints, start, end, source_rest_joints)

        result.stats.update(retarget_stats)

        self.log("STAGE 7 OK: method=%s mapped=%s target_anim_curves=%s target_pose_delta=%s" % (

            retarget_stats.get("retarget_method_used", retarget_stats.get("retarget_method")),

            retarget_stats.get("mapped_joint_count"),

            retarget_stats.get("target_anim_curve_count_after_retarget"),

            retarget_stats.get("target_start_pose_delta_degrees_sum")

        ))



        if self.config.correction_enabled:

            self.log("STAGE 7B: Applying correction passes.")

            correction_stats = self.corrector.apply_all(target_joints, start, end)

            result.stats.update(correction_stats)

            self.log("STAGE 7B OK: correction stats keys=%d" % len(correction_stats))

        else:

            self.log("STAGE 7B SKIPPED: Correction Enabled is OFF.")



                    

        self.log("STAGE 8/8: Export. export_enabled=%s" % bool(self.config.export_enabled))

        if self.config.export_enabled:

            if self.config.delete_source_after_bake:

                result.stats["deleted_source_hierarchy_roots"] = delete_hierarchy_roots_for_joints(source_joints + source_rest_joints, log_callback=self.log)

                result.stats["deleted_source_namespace_nodes"] = delete_namespace_nodes(["SRC", "SRCREST"], log_callback=self.log)

            output_path = relative_output_path(file_path, self.config.input_folder, self.config.output_folder, extension=".fbx")

            if not self.config.preserve_folder_structure:

                output_path = normalize_path(os.path.join(self.config.output_folder, os.path.splitext(os.path.basename(file_path))[0] + ".fbx"))

            result.output_path = output_path

            ensure_dir(os.path.dirname(output_path))

            if os.path.exists(output_path) and not self.config.overwrite_outputs:

                result.add_issue("OUTPUT_EXISTS", SEVERITY_ERROR, "Output exists and overwrite is disabled.")

                self.log("STOP_REASON: Output exists and overwrite is disabled: %s" % output_path)

                return

            roots = target_roots_before or get_root_joints(target_joints)

            root = roots[0] if roots else target_joints[0]

            target_export_joints = get_hierarchy(root, node_type="joint")

            if not target_export_joints:

                target_export_joints = list(target_joints)

            if self.config.export_force_key_target_joints:

                forced_keys = force_key_transform_nodes(target_export_joints, start, end)

                result.stats["forced_export_keys"] = forced_keys

                self.log("STAGE 8: forced export keys=%d on target joints=%d" % (forced_keys, len(target_export_joints)))

            export_nodes = select_export_nodes_for_target(root, include_meshes=self.config.export_include_target_meshes)

            result.stats["export_selected_node_count"] = len(export_nodes)

            result.stats["export_anim_curve_count"] = count_anim_curves_on_nodes(target_export_joints)

            self.log("STAGE 8: Export path: %s" % output_path)

            self.log("STAGE 8: Export root=%s selected_nodes=%d target_anim_curves=%d" % (short_name(root), len(export_nodes), result.stats["export_anim_curve_count"]))

            if not export_nodes:

                raise RuntimeError("No export nodes were selected for target root: %s" % root)

            export_fbx_selected(output_path, start, end, selected_only=self.config.export_selected_target_only)

            self.log("STAGE 8: FBX export command finished: %s" % output_path)

            if self.config.export_validate_file:

                result.stats["export_file_size_bytes"] = os.path.getsize(output_path) if os.path.isfile(output_path) else 0

                self.log("STAGE 8: exported file size=%d bytes" % result.stats["export_file_size_bytes"])

                if result.stats["export_file_size_bytes"] < 2048:

                    raise RuntimeError("Exported FBX is too small and probably invalid: %s" % output_path)

        else:

            self.log("STAGE 8 SKIPPED: Export Enabled is OFF.")

        self.log("---- FBX END: %s ----" % os.path.basename(file_path))



    def _process_npz(self, file_path: str, result: ScanResult) -> None:

        if not NUMPY_AVAILABLE:

            result.status = STATUS_SKIPPED

            result.add_issue("NPZ_NUMPY_MISSING", SEVERITY_ERROR,

                             "NumPy is unavailable in Maya Python. NPZ file skipped.")

            return

        if self.config.scan_only or not self.config.retarget_enabled:

                                  

            data = _np.load(normalize_path(file_path), allow_pickle=True)

            result.stats["npz_keys"] = list(data.keys())

            result.stats["npz_shapes"] = {key: list(data[key].shape) for key in data.keys() if hasattr(data[key], "shape")}

            result.status = STATUS_GOOD

            return



        import_maya_or_fbx(self.config.target_skeleton_file, namespace="TGT")

        target_joints = get_all_joints()

        target_roots_before = get_root_joints(target_joints)

        if not target_joints:

            raise RuntimeError("Target skeleton imported but no joints were found.")



        before = set(cmds.ls(type="joint", long=True) or [])

        source_joints, (start, end) = self.npz_importer.import_npz_to_source_skeleton(file_path)

        after = set(cmds.ls(type="joint", long=True) or [])

        source_joints = sorted(after - before) or source_joints

        self.scanner.scan_scene(result, source_joints)

        if result.status == STATUS_BAD and self.config.skip_bad_files_before_retarget:

            self.log("Skipping BAD NPZ before retarget because Skip Bad Files Before Retarget is enabled: %s" % file_path)

            return

        set_timeline(start, end)

        result.stats.update(self.retargeter.retarget_current_scene(source_joints, target_joints, start, end, source_rest_joints=None))

        if self.config.correction_enabled:

            result.stats.update(self.corrector.apply_all(target_joints, start, end))

        if self.config.export_enabled:

            self.log("Export enabled. Preparing FBX export...")

            if self.config.delete_source_after_bake:

                result.stats["deleted_source_hierarchy_roots"] = delete_hierarchy_roots_for_joints(source_joints, log_callback=self.log)

                result.stats["deleted_source_namespace_nodes"] = delete_namespace_nodes(["SRC", "SRCREST"], log_callback=self.log)

            output_path = relative_output_path(file_path, self.config.input_folder, self.config.output_folder, extension=".fbx")

            if not self.config.preserve_folder_structure:

                output_path = normalize_path(os.path.join(self.config.output_folder, os.path.splitext(os.path.basename(file_path))[0] + ".fbx"))

            result.output_path = output_path

            roots = target_roots_before or get_root_joints(target_joints)

            root = roots[0] if roots else target_joints[0]

            target_export_joints = get_hierarchy(root, node_type="joint")

            if self.config.export_force_key_target_joints:

                forced_keys = force_key_transform_nodes(target_export_joints, start, end)

                result.stats["forced_export_keys"] = forced_keys

            export_nodes = select_export_nodes_for_target(root, include_meshes=self.config.export_include_target_meshes)

            result.stats["export_selected_node_count"] = len(export_nodes)

            result.stats["export_anim_curve_count"] = count_anim_curves_on_nodes(target_export_joints)

            self.log("Export path: %s" % output_path)

            self.log("Export root: %s, selected nodes=%d, target anim curves=%d" % (short_name(root), len(export_nodes), result.stats["export_anim_curve_count"]))

            if not export_nodes:

                raise RuntimeError("No export nodes were selected for target root: %s" % root)

            export_fbx_selected(output_path, start, end, selected_only=self.config.export_selected_target_only)

            self.log("FBX export command finished: %s" % output_path)

            if self.config.export_validate_file:

                result.stats["export_file_size_bytes"] = os.path.getsize(output_path) if os.path.isfile(output_path) else 0

                if result.stats["export_file_size_bytes"] < 2048:

                    raise RuntimeError("Exported FBX is too small and probably invalid: %s" % output_path)



    def _sort_file_if_needed(self, result: ScanResult) -> None:

        if not result.file_path or not os.path.isfile(result.file_path):

            return

        try:

            if result.status in {STATUS_BAD, STATUS_FAILED, STATUS_NEEDS_FIX} and self.config.copy_bad_files and self.config.bad_folder:

                self._copy_or_move_to_folder(result.file_path, self.config.bad_folder)

            elif result.status == STATUS_GOOD and self.config.copy_good_files and self.config.good_folder:

                self._copy_or_move_to_folder(result.file_path, self.config.good_folder)

        except Exception as exc:

            result.add_issue("SORT_FAILED", SEVERITY_WARNING, "Could not copy/move file: %s" % exc)



    def _copy_or_move_to_folder(self, source_path: str, folder: str) -> str:

        ensure_dir(folder)

        if self.config.preserve_folder_structure:

            try:

                rel = os.path.relpath(source_path, self.config.input_folder)

            except Exception:

                rel = os.path.basename(source_path)

            dest = normalize_path(os.path.join(folder, rel))

        else:

            dest = normalize_path(os.path.join(folder, os.path.basename(source_path)))

        ensure_dir(os.path.dirname(dest))

        if os.path.exists(dest) and self.config.overwrite_outputs:

            os.remove(dest)

        if self.config.sort_originals_instead_of_copy:

            shutil.move(source_path, dest)

        else:

            shutil.copy2(source_path, dest)

        return dest



    def _start_maya_progress(self, total: int) -> None:

                                                                             

                                                                                 

                                                             

        return



    def _update_maya_progress(self, index: int, total: int, file_path: str) -> None:

                                                                         

        return



    def _end_maya_progress(self) -> None:

        return





                                                                               

                                

                                                                               



def create_example_mapping_json(path: str) -> str:

    data = {

        "description": "Target joint -> Source joint/canonical mapping. Edit this per client skeleton.",

        "recommended_maya_tool_settings": {

            "force_frame_rate": True,

            "target_frame_rate": 30.0,

            "retarget_method": "humanik_batch",

            "retarget_use_source_rest_file": True,

            "retarget_copy_pelvis_translation": True,

            "retarget_translation_scale": 1.0,

            "retarget_maintain_offset": True,

            "retarget_use_point_constraint_for_root": False,

            "retarget_use_point_constraint_for_pelvis": True,

            "delete_source_after_bake": True,

            "fail_if_no_target_animation": True,

            "validate_required_bones": False,

            "correction_enabled": False

        },

        "joints": {

            "root": "root",

            "pelvis": "pelvis",

            "spine_01": "spine_01",

            "spine_02": "spine_02",

            "spine_03": "spine_03",

            "neck_01": "neck_01",

            "neck_02": "neck_02",

            "head": "head",

            "clavicle_l": "clavicle_l",

            "upperarm_l": "upperarm_l",

            "lowerarm_l": "lowerarm_l",

            "hand_l": "hand_l",

            "clavicle_r": "clavicle_r",

            "upperarm_r": "upperarm_r",

            "lowerarm_r": "lowerarm_r",

            "hand_r": "hand_r",

            "thigh_l": "thigh_l",

            "calf_l": "calf_l",

            "foot_l": "foot_l",

            "thigh_r": "thigh_r",

            "calf_r": "calf_r",

            "foot_r": "foot_r"

        },

        "aliases": {

            "custom_source_upperarm_l": ["YourSourceLeftArmName"],

            "custom_target_upperarm_l": ["YourTargetLeftArmName"]

        },

        "offsets": {

            "upperarm_l": {"rotate": [0, 0, 0]},

            "upperarm_r": {"rotate": [0, 0, 0]},

            "neck_01": {"rotate": [0, 0, 0]}

        }

    }

    save_json_file(path, data)

    return path





def create_example_npz_schema_json(path: str) -> str:

    data = {

        "description": "Example NPZ schema. NPZ has no universal animation standard; edit this to match the client's file.",

        "joint_names_key": "joint_names",

        "local_euler_key": "local_euler",

        "poses_key": "poses",

        "root_translation_key": "root_translation",

        "rotation_format": "euler",

        "degrees": True,

        "start_frame": 1,

        "fps": 30,

        "joint_names": []

    }

    save_json_file(path, data)

    return path





                                                                               

    

                                                                               





class ALPHABatchAnimationToolUI:

    WIN = WINDOW_NAME

    def __init__(self):

        require_maya()

        self.config = self.load_config_silent()

        self.translations_zh_cn = load_chinese_translations()

        if self.config.ui_language not in (LANGUAGE_ENGLISH, LANGUAGE_CHINESE_SIMPLIFIED):

            self.config.ui_language = LANGUAGE_ENGLISH

        self.controls: Dict[str, str] = {}

        self.log_field = None

        self.progress_text = None

        self.progress_bar = None

        self.cancel_requested = False

        self._log_lines: List[str] = []



    def tr(self, key: str, fallback: str) -> str:

        if getattr(self.config, "ui_language", LANGUAGE_ENGLISH) == LANGUAGE_CHINESE_SIMPLIFIED:

            return self.translations_zh_cn.get(key, fallback)

        return fallback



    def change_language(self, language: str) -> None:

        if language not in (LANGUAGE_ENGLISH, LANGUAGE_CHINESE_SIMPLIFIED):

            language = LANGUAGE_ENGLISH

        try:

            cfg = self.read_ui_config() if self.controls else self.config

        except Exception:

            cfg = self.config

        cfg.ui_language = language

        self.config = cfg

        try:

            save_json_file(config_default_path(), cfg.to_dict())

        except Exception:

            pass

        self.show()



    def show(self) -> None:

        self.controls = {}

        self.translations_zh_cn = load_chinese_translations()

        if cmds.window(self.WIN, exists=True):

            cmds.deleteUI(self.WIN)

        window = cmds.window(self.WIN, title=self.tr("scanner.window_title", "ALPHA Scanning"), sizeable=True, widthHeight=(720, 820))

        main = cmds.columnLayout(adjustableColumn=True, rowSpacing=6)

        cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnWidth2=(220, 220))

        cmds.button(label=u"切换到中文", command=lambda *_: self.change_language(LANGUAGE_CHINESE_SIMPLIFIED), height=28)

        cmds.button(label="Change Language to English", command=lambda *_: self.change_language(LANGUAGE_ENGLISH), height=28)

        cmds.setParent("..")

        cmds.separator(height=8, style="in")

        scroll = cmds.scrollLayout(childResizable=True, height=610)

        body = cmds.columnLayout(adjustableColumn=True, rowSpacing=8)

        self._build_paths_section(body)

        self._build_batch_section(body)

        self._build_validation_section(body)

        self._build_buttons_section(body)

        cmds.setParent(main)

        cmds.frameLayout(label=self.tr("section.progress", "Progress"), collapsable=False, marginWidth=8, marginHeight=6)

        cmds.columnLayout(adjustableColumn=True, rowSpacing=4)

        self.progress_text = cmds.text(label="0/0 | 0.00%", align="left", height=22)

        self.progress_bar = cmds.progressBar(maxValue=1000, progress=0, height=18)

        cmds.setParent("..")

        cmds.setParent("..")

        self.log_field = cmds.scrollField(editable=False, wordWrap=False, height=160, text="")

        cmds.showWindow(window)

        self.log(self.tr("log.scanner_loaded", "Scanning is ready."))



    def _build_paths_section(self, parent) -> None:

        cmds.frameLayout(label=self.tr("section.paths", "Paths"), collapsable=True, collapse=False, marginWidth=8, marginHeight=8, parent=parent)

        cmds.columnLayout(adjustableColumn=True, rowSpacing=4)

        self._path_row("input_folder", "Input Folder", folder=True)

        self._path_row("report_folder", "Report Folder", folder=True)

        self._path_row("bad_folder", "Bad / Needs Fix Folder", folder=True)

        self._path_row("good_folder", "Good Folder", folder=True)

        self._path_row("source_skeleton_file", "Source Skeleton File", folder=False, file_filter="FBX/Maya Files (*.fbx *.ma *.mb)")

        self._path_row("mapping_json", "Joint Mapping JSON", folder=False, file_filter="JSON Files (*.json)")

        self._path_row("npz_schema_json", "NPZ Schema JSON", folder=False, file_filter="JSON Files (*.json)")

        cmds.setParent("..")

        cmds.setParent("..")



    def _build_batch_section(self, parent) -> None:

        cmds.frameLayout(label=self.tr("section.batch", "Batch Options"), collapsable=True, collapse=False, marginWidth=8, marginHeight=8, parent=parent)

        cmds.columnLayout(adjustableColumn=True, rowSpacing=4)

        for key, label in [

            ("include_fbx", "Include FBX"),

            ("include_npz", "Include NPZ"),

            ("recursive_scan", "Recursive Scan"),

            ("copy_bad_files", "Copy Bad / Needs Fix Files"),

            ("copy_good_files", "Copy Good Files"),

            ("preserve_folder_structure", "Preserve Folder Structure"),

            ("overwrite_outputs", "Overwrite Existing Copies"),

            ("sort_originals_instead_of_copy", "Move Original Files Instead Of Copy"),

            ("dry_run", "Dry Run"),

        ]:

            self._check(key, label)

        self._int("max_files", "Max Files (0 = all)", min_value=0)

        self._check("force_frame_rate", "Force Frame Rate")

        self._float("target_frame_rate", "Target Frame Rate", min_value=1.0)

        self._int("sample_every_n_frames", "Validation Sample Every N Frames", min_value=1)

        cmds.setParent("..")

        cmds.setParent("..")



    def _build_validation_section(self, parent) -> None:

        cmds.frameLayout(label=self.tr("section.validation", "Scanning Rules"), collapsable=True, collapse=False, marginWidth=8, marginHeight=8, parent=parent)

        cmds.columnLayout(adjustableColumn=True, rowSpacing=4)

        self._text("required_canonical_bones", "Required Canonical Bones")

        for key, label in [

            ("validate_required_bones", "Validate Required Bones"),

            ("validate_empty_clip", "Validate Empty / Corrupted Clip"),

            ("validate_animation_length", "Validate Animation Length"),

            ("validate_scale", "Validate Scale Values"),

            ("validate_extreme_rotation", "Validate Extreme Local Rotations"),

            ("validate_rotation_spikes", "Validate Rotation Spikes"),

            ("validate_translation_spikes", "Validate Translation Spikes"),

            ("validate_root_motion", "Validate Root Motion Offset"),

            ("validate_shoulder_pose", "Validate Shoulder Pose"),

            ("validate_neck_pose", "Validate Neck Pose"),

            ("validate_arm_twist", "Validate Arm Twist"),

            ("validate_hand_flip", "Validate Hand / Wrist Flip"),

        ]:

            self._check(key, label)

        self._float("min_anim_length_frames", "Min Animation Length Frames", min_value=0.0)

        self._float("max_anim_length_frames", "Max Animation Length Frames", min_value=1.0)

        self._float("min_scale_value", "Min Scale Value", min_value=0.0)

        self._float("max_scale_value", "Max Scale Value", min_value=0.001)

        self._float("extreme_rotation_degrees", "Extreme Rotation Threshold Degrees", min_value=1.0)

        self._float("rotation_spike_degrees", "Rotation Spike Threshold Degrees", min_value=1.0)

        self._float("translation_spike_units", "Translation Spike Threshold Units", min_value=0.001)

        self._float("max_root_offset_units", "Max Root Offset Units", min_value=0.0)

        self._float("shoulder_raise_angle_degrees", "Shoulder Raise Sensitivity Degrees", min_value=1.0)

        self._float("neck_extreme_degrees", "Neck Extreme Threshold Degrees", min_value=1.0)

        self._float("arm_twist_degrees", "Arm Twist Threshold Degrees", min_value=1.0)

        self._float("hand_flip_degrees", "Hand Flip Threshold Degrees", min_value=1.0)

        cmds.setParent("..")

        cmds.setParent("..")



    def _build_buttons_section(self, parent) -> None:

        cmds.frameLayout(label=self.tr("section.actions", "Actions"), collapsable=True, collapse=False, marginWidth=8, marginHeight=8, parent=parent)

        cmds.columnLayout(adjustableColumn=True, rowSpacing=6)

        cmds.rowLayout(numberOfColumns=3, adjustableColumn=1, columnWidth3=(220, 180, 180))

        cmds.button(label=self.tr("button.run_scanning", "Run Scanning"), command=lambda *_: self.run_scan_only(), height=36)

        cmds.button(label=self.tr("button.stop_batch", "Stop"), command=lambda *_: self.request_cancel(), height=36)

        cmds.button(label=self.tr("button.open_report_folder", "Open Report Folder"), command=lambda *_: self.open_report_folder(), height=36)

        cmds.setParent("..")

        cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnWidth2=(220, 220))

        cmds.button(label=self.tr("button.save_config", "Save Settings"), command=lambda *_: self.save_config(), height=30)

        cmds.button(label=self.tr("button.load_config", "Load Settings"), command=lambda *_: self.load_config(), height=30)

        cmds.setParent("..")

        cmds.setParent("..")

        cmds.setParent("..")



    def _path_row(self, key: str, label: str, folder: bool, file_filter: str = "All Files (*.*)") -> None:

        cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnWidth3=(180, 430, 80))

        cmds.text(label=self.tr("label." + key, label), align="right")

        ctrl = cmds.textField(text=getattr(self.config, key))

        self.controls[key] = ctrl

        cmds.button(label=self.tr("button.browse", "Browse"), command=lambda *_args, k=key, f=folder, ff=file_filter: self.browse_path(k, f, ff))

        cmds.setParent("..")



    def _check(self, key: str, label: str) -> None:

        ctrl = cmds.checkBox(label=self.tr("label." + key, label), value=bool(getattr(self.config, key)))

        self.controls[key] = ctrl



    def _int(self, key: str, label: str, min_value: int = 0) -> None:

        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=(280, 140))

        cmds.text(label=self.tr("label." + key, label), align="right")

        ctrl = cmds.intField(value=int(getattr(self.config, key)), minValue=min_value)

        self.controls[key] = ctrl

        cmds.setParent("..")



    def _float(self, key: str, label: str, min_value: float = -999999.0, max_value: Optional[float] = None) -> None:

        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=(280, 140))

        cmds.text(label=self.tr("label." + key, label), align="right")

        kwargs = {"value": float(getattr(self.config, key)), "minValue": min_value}

        if max_value is not None:

            kwargs["maxValue"] = max_value

        ctrl = cmds.floatField(**kwargs)

        self.controls[key] = ctrl

        cmds.setParent("..")



    def _text(self, key: str, label: str) -> None:

        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=(280, 430))

        cmds.text(label=self.tr("label." + key, label), align="right")

        ctrl = cmds.textField(text=str(getattr(self.config, key)))

        self.controls[key] = ctrl

        cmds.setParent("..")



    def browse_path(self, key: str, folder: bool, file_filter: str) -> None:

        if folder:

            result = cmds.fileDialog2(fileMode=3, dialogStyle=2, caption="%s %s" % (self.tr("dialog.select", "Select"), key))

        else:

            result = cmds.fileDialog2(fileMode=1, dialogStyle=2, fileFilter=file_filter, caption="%s %s" % (self.tr("dialog.select", "Select"), key))

        if result:

            cmds.textField(self.controls[key], edit=True, text=normalize_path(result[0]))



    def read_ui_config(self) -> ToolConfig:

        data = self.config.to_dict()

        for key, ctrl in self.controls.items():

            if not hasattr(self.config, key):

                continue

            value = getattr(self.config, key)

            if isinstance(value, bool):

                data[key] = bool(cmds.checkBox(ctrl, query=True, value=True))

            elif isinstance(value, int) and not isinstance(value, bool):

                data[key] = int(cmds.intField(ctrl, query=True, value=True))

            elif isinstance(value, float):

                data[key] = float(cmds.floatField(ctrl, query=True, value=True))

            else:

                data[key] = normalize_path(cmds.textField(ctrl, query=True, text=True)) if "folder" in key or "file" in key or key.endswith("json") else cmds.textField(ctrl, query=True, text=True)

        self.config = ToolConfig.from_dict(data)

        return self.config



    def apply_config_to_ui(self, config: ToolConfig) -> None:

        self.config = config

        for key, ctrl in self.controls.items():

            if not hasattr(self.config, key):

                continue

            value = getattr(self.config, key)

            if isinstance(value, bool):

                cmds.checkBox(ctrl, edit=True, value=bool(value))

            elif isinstance(value, int) and not isinstance(value, bool):

                cmds.intField(ctrl, edit=True, value=int(value))

            elif isinstance(value, float):

                cmds.floatField(ctrl, edit=True, value=float(value))

            else:

                cmds.textField(ctrl, edit=True, text=str(value))



    def run_scan_only(self) -> None:

        cfg = self.read_ui_config()

        cfg.scan_only = True

        cfg.retarget_enabled = False

        cfg.export_enabled = False

        cfg.correction_enabled = False

        cfg.skip_bad_files_before_retarget = False

        cfg.auto_retarget_fallback = False

        self._run_with_config(cfg)



    def _run_with_config(self, cfg: ToolConfig) -> None:

        self.cancel_requested = False

        self.clear_log()

        self.set_progress(0, 0, self.tr("progress.starting", "Starting"))

        self.log(self.tr("log.scanning_started", "Scanning started."))

        processor = BatchProcessor(cfg, log_callback=self.log, progress_callback=self.set_progress)

        try:

            processor.run()

            self.log(self.tr("log.done", "Done."))

        except KeyboardInterrupt:

            self.log(self.tr("log.cancelled", "Cancelled by user."))

        except Exception as exc:

            self.log("ERROR: %s" % exc)

            self.log(traceback.format_exc())



    def save_config(self) -> None:

        cfg = self.read_ui_config()

        path = config_default_path()

        save_json_file(path, cfg.to_dict())

        self.log("Settings saved: %s" % path)



    def load_config_silent(self) -> ToolConfig:

        path = config_default_path()

        if os.path.isfile(path):

            try:

                return ToolConfig.from_dict(load_json_file(path))

            except Exception:

                pass

        return ToolConfig()



    def load_config(self) -> None:

        path = config_default_path()

        if not os.path.isfile(path):

            self.log("No saved settings found: %s" % path)

            return

        cfg = ToolConfig.from_dict(load_json_file(path))

        self.apply_config_to_ui(cfg)

        self.log("Settings loaded: %s" % path)



    def request_cancel(self) -> None:

        self.cancel_requested = True

        self.log(self.tr("log.cancel_requested", "Stop requested. The batch will stop after the current file."))



    def open_report_folder(self) -> None:

        cfg = self.read_ui_config()

        folder = cfg.report_folder

        if not folder:

            self.log("Report folder is empty.")

            return

        folder = ensure_dir(folder)

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



    def set_progress(self, index: int, total: int, label: str) -> None:

        if self.cancel_requested:

            raise KeyboardInterrupt("Batch cancelled by user.")

        safe_total = max(int(total), 0)

        safe_index = max(int(index), 0)

        percent = 0.0 if safe_total <= 0 else clamp((float(safe_index) / float(safe_total)) * 100.0, 0.0, 100.0)

        clean_label = os.path.basename(label) if label else ""

        if self.progress_text:

            cmds.text(self.progress_text, edit=True, label="%d/%d | %.2f%% | %s" % (safe_index, safe_total, percent, clean_label))

        if self.progress_bar:

            cmds.progressBar(self.progress_bar, edit=True, progress=int(percent * 10.0))

        try:

            cmds.refresh(force=True)

        except Exception:

            pass



    def log(self, message: str) -> None:

        print(message)

        self._log_lines.append(str(message))

        if len(self._log_lines) > MAX_UI_LOG_LINES:

            self._log_lines = self._log_lines[-MAX_UI_LOG_LINES:]

        if self.log_field:

            text = "\n".join(self._log_lines) + "\n"

            cmds.scrollField(self.log_field, edit=True, text=text)

            for kwargs in ({"insertionPosition": len(text)}, {"scrollToBottom": True}):

                try:

                    cmds.scrollField(self.log_field, edit=True, **kwargs)

                    break

                except Exception:

                    pass



    def clear_log(self) -> None:

        self._log_lines = []

        if self.log_field:

            cmds.scrollField(self.log_field, edit=True, text="")

        if self.progress_bar:

            cmds.progressBar(self.progress_bar, edit=True, progress=0)



class ALPHALauncherUI:

    WIN = "ALPHAToolLauncherWindow"

    def __init__(self):

        require_maya()

        self.config = self.load_config_silent()

        self.translations_zh_cn = load_chinese_translations()

        if self.config.ui_language not in (LANGUAGE_ENGLISH, LANGUAGE_CHINESE_SIMPLIFIED):

            self.config.ui_language = LANGUAGE_ENGLISH



    def tr(self, key: str, fallback: str) -> str:

        if getattr(self.config, "ui_language", LANGUAGE_ENGLISH) == LANGUAGE_CHINESE_SIMPLIFIED:

            return self.translations_zh_cn.get(key, fallback)

        return fallback



    def load_config_silent(self) -> ToolConfig:

        path = config_default_path()

        if os.path.isfile(path):

            try:

                return ToolConfig.from_dict(load_json_file(path))

            except Exception:

                pass

        return ToolConfig()



    def save_language(self) -> None:

        try:

            data = self.config.to_dict()

            save_json_file(config_default_path(), data)

        except Exception:

            pass



    def change_language(self, language: str) -> None:

        if language not in (LANGUAGE_ENGLISH, LANGUAGE_CHINESE_SIMPLIFIED):

            language = LANGUAGE_ENGLISH

        self.config.ui_language = language

        self.save_language()

        self.show()



    def show(self) -> None:

        self.translations_zh_cn = load_chinese_translations()

        if cmds.window(self.WIN, exists=True):

            cmds.deleteUI(self.WIN)

        if cmds.window(WINDOW_NAME, exists=True):

            cmds.deleteUI(WINDOW_NAME)

        window = cmds.window(self.WIN, title=self.tr("launcher.title", "ALPHA Animation Tool"), sizeable=False, widthHeight=(360, 210))

        cmds.columnLayout(adjustableColumn=True, rowSpacing=10)

        cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnWidth2=(170, 170))

        cmds.button(label=u"切换到中文", command=lambda *_: self.change_language(LANGUAGE_CHINESE_SIMPLIFIED), height=28)

        cmds.button(label="Change Language to English", command=lambda *_: self.change_language(LANGUAGE_ENGLISH), height=28)

        cmds.setParent("..")

        cmds.separator(height=8, style="in")

        cmds.button(label=self.tr("launcher.retarget", "Retarget"), height=58, command=lambda *_: self.open_retarget())

        cmds.button(label=self.tr("launcher.scanning", "Scanning"), height=58, command=lambda *_: self.open_scanning())

        cmds.showWindow(window)



    def open_scanning(self) -> None:

        if cmds.window(self.WIN, exists=True):

            cmds.deleteUI(self.WIN)

        ui = ALPHABatchAnimationToolUI()

        ui.show()



    def open_retarget(self) -> None:

        if cmds.window(self.WIN, exists=True):

            cmds.deleteUI(self.WIN)

        tool_dir = script_directory()

        if tool_dir not in sys.path:

            sys.path.append(tool_dir)

        import importlib

        import ALPHAOption1CalibrationTest as retargeting

        importlib.reload(retargeting)

        retargeting.show()



_UI_INSTANCE: Optional[ALPHALauncherUI] = None





def show() -> ALPHALauncherUI:

    global _UI_INSTANCE

    require_maya()

    _UI_INSTANCE = ALPHALauncherUI()

    _UI_INSTANCE.show()

    return _UI_INSTANCE





def show_scanning() -> ALPHABatchAnimationToolUI:

    require_maya()

    ui = ALPHABatchAnimationToolUI()

    ui.show()

    return ui





def run_batch_from_config(config_path: str) -> List[ScanResult]:

    require_maya()

    cfg = ToolConfig.from_dict(load_json_file(config_path))

    processor = BatchProcessor(cfg)

    return processor.run()





if __name__ == "__main__":

    if MAYA_AVAILABLE:

        show()

    else:

        print("This script is intended to run inside Autodesk Maya 2024 Python.")

