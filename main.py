# SPDX-License-Identifier: MIT
# Copyright (c) 2026 AYSTBA
# https://github.com/AYSTBA
import tkinter as tk
from backend.utils import init_dpi_fix
from backend.app_logic import PCLGetAppLogic
from frontend.gui import PCLGetAppGUI
import sys
import os

# 获取打包后的临时目录路径
def resource_path(relative_path):
    """获取资源文件的绝对路径"""
    try:
        # PyInstaller 
        base_path = sys._MEIPASS
    except Exception:
        # 别不打包炸了
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
class PCLGetApp:
    def __init__(self, root):
        self.root = root
        self.app_logic = PCLGetAppLogic(self)
        self.gui = PCLGetAppGUI(root, self.app_logic)
    
    def get_backup_path(self, version, save_name, zip_name):
        return self.app_logic.get_backup_path(version, save_name, zip_name)
    
    def refresh_backup_history(self):
        self.gui.refresh_backup_history()

if __name__ == "__main__":
    init_dpi_fix()
    root = tk.Tk()
    app = PCLGetApp(root)
    root.mainloop()

#   风神巴巴托斯：代码如风，运行丝滑
#   岩神钟离：    结构稳固，坚如磐石
#   双神庇佑 —— 打包一次过，运行永不崩，存档永不丢
#   阿弥托福
