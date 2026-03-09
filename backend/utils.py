# SPDX-License-Identifier: MIT
# Copyright (c) 2026 AYSTBA
# https://github.com/AYSTBA
import os
import shutil
import zipfile
import subprocess
from datetime import datetime

# =============================================================================
# 核心配置
# =============================================================================
APP_NAME = "PCL Get"
BACKUP_FOLDER_NAME = "PCL-Saves"
FONT_NORMAL = ("微软雅黑", 11)
FONT_BOLD = ("微软雅黑", 11, "bold")
FONT_TITLE = ("微软雅黑", 13, "bold")
# 全量备份项
FULL_BACKUP_MAP = {
    "地图存档": ["saves"],
    "游戏全局设置": ["options.txt", "optionsof.txt"],
    "模组配置文件": ["config"],
    "服务器列表": ["servers.dat"],
    "Mod文件": ["mods"],
    "资源包/材质包": ["resourcepacks"],
    "光影包": ["shaderpacks"],
    "世界数据包": ["datapacks"],
    "创世神蓝图": ["schematics", "WorldEdit"],
    "运行日志": ["logs"],
    "崩溃报告": ["crash-reports"]
}
# PCL高频搜索路径
SEARCH_PATHS = [
    os.path.expanduser("~"),
    os.path.join(os.path.expanduser("~"), "Desktop"),
    os.path.join(os.path.expanduser("~"), "Downloads"),
    "D:\\PCL2", "D:\\pcll2", "D:\\MC",
    "E:\\PCL2", "E:\\pcll2", "E:\\MC",
    "F:\\PCL2", "F:\\pcll2",
]

# =============================================================================
# 基础工具函数
# =============================================================================
def init_dpi_fix():
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(2)
    except:
        pass

def find_all_minecraft_folders():
    found = []
    official_path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", ".minecraft")
    if os.path.exists(official_path) and os.path.isdir(os.path.join(official_path, "versions")):
        found.append(official_path)
    for root_path in SEARCH_PATHS:
        if not os.path.exists(root_path):
            continue
        try:
            for base, dirs, _ in os.walk(root_path):
                if base.count(os.sep) - root_path.count(os.sep) > 2:
                    continue
                if ".minecraft" in dirs:
                    full_path = os.path.join(base, ".minecraft")
                    if os.path.isdir(os.path.join(full_path, "versions")) and full_path not in found:
                        found.append(full_path)
        except (PermissionError, OSError):
            continue
    return sorted(list(set(found)))

def get_version_list(versions_dir):
    if not os.path.exists(versions_dir):
        return []
    versions = [d for d in os.listdir(versions_dir) if os.path.isdir(os.path.join(versions_dir, d))]
    return sorted(versions)

def get_save_info(mc_root, version):
    version_saves = os.path.join(mc_root, "versions", version, "saves")
    global_saves = os.path.join(mc_root, "saves")
    
    if os.path.exists(version_saves) and len(os.listdir(version_saves)) > 0:
        saves = [d for d in os.listdir(version_saves) if os.path.isdir(os.path.join(version_saves, d))]
        save_root = version_saves
        save_type = "版本隔离"
    elif os.path.exists(global_saves) and len(os.listdir(global_saves)) > 0:
        saves = [d for d in os.listdir(global_saves) if os.path.isdir(os.path.join(global_saves, d))]
        save_root = global_saves
        save_type = "全局共享"
    else:
        saves = []
        save_root = ""
        save_type = "无存档"
    
    return sorted(saves), save_root, save_type

def do_full_backup(src_root, save_root, target_zip, selected_items, selected_save=None):
    success = []
    failed = []
    os.makedirs(os.path.dirname(target_zip), exist_ok=True)

    with zipfile.ZipFile(target_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for item in selected_items:
            item_found = False
            if item == "地图存档" and selected_save:
                save_full = os.path.join(save_root, selected_save)
                if not os.path.exists(save_full):
                    failed.append(f"地图存档（{selected_save}）")
                    continue
                for root, _, files in os.walk(save_full):
                    for file in files:
                        full_file = os.path.join(root, file)
                        rel_path = os.path.relpath(full_file, src_root)
                        zf.write(full_file, rel_path)
                success.append(f"地图存档（{selected_save}）")
                item_found = True
            else:
                paths_to_check = [
                    os.path.join(src_root, "versions", os.path.basename(os.path.dirname(save_root)), p) 
                    if "versions" in save_root else os.path.join(src_root, p) 
                    for p in FULL_BACKUP_MAP[item]
                ] + [os.path.join(src_root, p) for p in FULL_BACKUP_MAP[item]]
                
                for path in paths_to_check:
                    if not os.path.exists(path):
                        continue
                    item_found = True
                    if os.path.isdir(path):
                        for root, _, files in os.walk(path):
                            for file in files:
                                full_file = os.path.join(root, file)
                                rel_path = os.path.relpath(full_file, src_root)
                                zf.write(full_file, rel_path)
                    else:
                        rel_path = os.path.relpath(path, src_root)
                        zf.write(path, rel_path)
                    success.append(item)
                    break
            if not item_found:
                failed.append(item)
    return success, failed

def do_restore_zip(zip_path, target_mc_root, save_root):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(target_mc_root)
            
            if "versions" in save_root:
                save_name = os.path.basename(os.path.dirname(zip_path))
                src_save = os.path.join(target_mc_root, "saves", save_name)
                dst_save = os.path.join(save_root, save_name)
                if os.path.exists(src_save) and not os.path.exists(dst_save):
                    shutil.move(src_save, dst_save)
                    if os.path.exists(src_save):
                        shutil.rmtree(src_save)
        return True
    except Exception as e:
        return False, str(e)