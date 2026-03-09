# SPDX-License-Identifier: MIT
# Copyright (c) 2026 AYSTBA
# https://github.com/AYSTBA
import os
import subprocess
from datetime import datetime
from tkinter import messagebox, simpledialog
from .utils import find_all_minecraft_folders, get_version_list, get_save_info, do_full_backup, do_restore_zip, BACKUP_FOLDER_NAME
from .scheduled_backup import ScheduledBackup

class PCLGetAppLogic:
    def __init__(self, app):
        self.app = app
        self.current_mc_root = None
        self.selected_version = None
        self.selected_save = None
        self.save_root = None
        self.save_type = None
        self.backup_name_map = {}
        self.scheduled_backup = ScheduledBackup(app)
        self.schedule_interval = 30
        self.backup_root = os.path.join(os.path.expanduser("~"), BACKUP_FOLDER_NAME)
        os.makedirs(self.backup_root, exist_ok=True)

    def get_backup_path(self, version, save_name, zip_name):
        return os.path.join(self.backup_root, version, save_name, zip_name)

    def refresh_mc_list(self):
        mc_list = find_all_minecraft_folders()
        if mc_list:
            return mc_list
        else:
            return ["未找到.minecraft文件夹"]

    def load_versions(self, mc_root):
        if not mc_root or not os.path.isdir(mc_root):
            return []
        versions_dir = os.path.join(mc_root, "versions")#fuck code
        if not os.path.isdir(versions_dir):
            return []
        return get_version_list(versions_dir)

    def load_saves(self, mc_root, version):
        saves, save_root, save_type = get_save_info(mc_root, version)
        self.save_root = save_root
        self.save_type = save_type
        return saves, save_root, save_type

    def refresh_backup_history(self, version, save_name):
        if not version or not save_name:
            return [], {}
        backup_dir = os.path.join(self.backup_root, version, save_name)
        if not os.path.isdir(backup_dir):
            return [], {}
        backup_list = []
        backup_map = {}
        for f in sorted(os.listdir(backup_dir), reverse=True):
            if f.endswith(".zip"):
                display = os.path.splitext(f)[0]
                backup_map[display] = os.path.join(backup_dir, f)
                backup_list.append(display)
        return backup_list, backup_map

    def do_backup(self, mc_root, version, save_name, save_root, selected_items, note=""):
        if not save_name or not save_root or not selected_items:
            return False, "请选存档+至少一项内容"
        time_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        zip_name = f"备份_{time_str}_{note}.zip"
        target = self.get_backup_path(version, save_name, zip_name)
        success, failed = do_full_backup(mc_root, save_root, target, selected_items, save_name)
        msg = f"成功：{', '.join(success)}\n"
        if failed:
            msg += f"失败：{', '.join(failed)}"
        return True, msg

    def do_restore(self, zip_path, mc_root, save_root):
        result = do_restore_zip(zip_path, mc_root, save_root)
        if result is True:
            return True, "回滚完成！已适配存档实际存储位置"
        else:
            return False, result

    def open_backup_location(self, backup_path):
        if backup_path and os.path.exists(backup_path):
            subprocess.Popen(f'explorer /select,"{backup_path}"')
            return True
        return False

    def delete_backup(self, backup_path):
        if not os.path.exists(backup_path):
            return False, "文件不存在"
        try:
            os.remove(backup_path)
            return True, "已删除"
        except Exception as e:
            return False, str(e)

    def start_schedule(self, interval, save_name):
        if not save_name:
            return False, "请先选择要备份的存档"
        if interval < 5:
            return False, "备份间隔不能少于5分钟"
        if self.scheduled_backup.start(interval):
            return True, f"定时备份已启动，每{interval}分钟自动备份一次"
        else:
            return False, "定时备份已经在运行"

    def stop_schedule(self):
        if self.scheduled_backup.stop():
            return True, "定时备份已停止"
        else:
            return False, "定时备份未运行"