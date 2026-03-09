# SPDX-License-Identifier: MIT
# Copyright (c) 2026 AYSTBA
# https://github.com/AYSTBA
import threading
import time
from datetime import datetime
from .utils import do_full_backup

class ScheduledBackup:
    def __init__(self, app):
        self.app = app
        self.timer_thread = None
        self.running = False
        self.interval_minutes = 30
        self.last_backup_time = None

    def start(self, interval_minutes):
        if self.running:
            return False
        self.interval_minutes = interval_minutes
        self.running = True
        self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self.timer_thread.start()
        return True
        #mix in(hahaha)
    def stop(self):
        self.running = False
        if self.timer_thread:
            self.timer_thread.join(timeout=1)
        return True

    def _timer_loop(self):
        while self.running:
            for _ in range(self.interval_minutes * 60):
                if not self.running:
                    return
                time.sleep(1)
            self._auto_backup()

    def _auto_backup(self):
        if not self.app.gui.selected_save.get() or not self.app.gui.save_root.get():
            return
        
        selected_items = [name for name, var in self.app.gui.check_vars.items() if var.get()]
        if not selected_items:
            selected_items = ["地图存档"]
        
        mc_root = self.app.gui.current_mc_root.get()
        ver = self.app.gui.selected_version.get()
        selected_save = self.app.gui.selected_save.get()
        save_root = self.app.gui.save_root.get()
        time_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        zip_name = f"自动备份_{time_str}.zip"
        target_zip = self.app.get_backup_path(ver, selected_save, zip_name)
        #so easy
        
        success, failed = do_full_backup(
            src_root=mc_root,
            save_root=save_root,
            target_zip=target_zip,
            selected_items=selected_items,
            selected_save=selected_save
        )
        
        self.last_backup_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.app.root.after(0, self.app.refresh_backup_history)
        self.app.root.after(0, lambda: self.app.gui.schedule_status_label.config(
            text=f"定时备份：运行中 | 间隔：{self.interval_minutes}分钟 | 上次备份：{self.last_backup_time}",
            foreground="green"
        ))