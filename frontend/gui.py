# SPDX-License-Identifier: MIT
# Copyright (c) 2026 AYSTBA
# https://github.com/AYSTBA
import os
import tkinter as tk
from tkinter import ttk, messagebox, Menu, simpledialog
from backend.utils import APP_NAME, FONT_NORMAL, FONT_BOLD, FONT_TITLE, FULL_BACKUP_MAP

class PCLGetAppGUI:
    def __init__(self, root, app_logic):
        self.root = root
        self.app_logic = app_logic
        self.root.title(APP_NAME)
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)

        self.style = ttk.Style()
        self.style.configure("TCheckbutton", font=FONT_NORMAL)
        self.style.configure("TCombobox", font=FONT_NORMAL)
        self.style.configure("TLabel", font=FONT_NORMAL)
        self.style.configure("TButton", font=FONT_NORMAL)
        self.style.configure("TLabelframe.Label", font=FONT_BOLD)

        self.current_mc_root = tk.StringVar()
        self.selected_version = tk.StringVar()
        self.selected_save = tk.StringVar()
        self.save_root = tk.StringVar()
        self.save_type = tk.StringVar()
        self.backup_name_map = {}

        self.schedule_interval = tk.IntVar(value=30)

        self.create_widgets()
        self.root.after(200, self.refresh_mc_list)

    def create_widgets(self):
        # -------------------------- 顶部 --------------------------
        top_frame = ttk.Frame(self.root, padding="15 10 15 10")
        top_frame.pack(fill=tk.X, anchor=tk.N)
        ttk.Label(top_frame, text="选择 .minecraft 实例：", font=FONT_BOLD).pack(side=tk.LEFT, padx=8)
        self.mc_combo = ttk.Combobox(top_frame, textvariable=self.current_mc_root, width=80, state="readonly")
        self.mc_combo.pack(side=tk.LEFT, padx=8)
        self.mc_combo.bind("<<ComboboxSelected>>", self.on_mc_selected)
        ttk.Button(top_frame, text="刷新列表", command=self.refresh_mc_list).pack(side=tk.LEFT, padx=15)

        # -------------------------- 定时备份 --------------------------
        schedule_frame = ttk.LabelFrame(self.root, text="定时备份", padding="10 5 10 5")#????????????fuck!!!!!
        schedule_frame.pack(fill=tk.X, padx=15, pady=5)
        
        self.schedule_status_label = ttk.Label(schedule_frame, text="定时备份：未启动", font=FONT_BOLD, foreground="gray")
        self.schedule_status_label.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(schedule_frame, text="备份间隔（分钟）：").pack(side=tk.LEFT, padx=5)
        self.interval_spinbox = ttk.Spinbox(schedule_frame, from_=5, to=1440, textvariable=self.schedule_interval, width=8)
        self.interval_spinbox.pack(side=tk.LEFT, padx=5)
        
        self.start_schedule_btn = ttk.Button(schedule_frame, text="启动定时备份", command=self.start_schedule)
        self.start_schedule_btn.pack(side=tk.LEFT, padx=10)
        self.stop_schedule_btn = ttk.Button(schedule_frame, text="停止定时备份", command=self.stop_schedule, state=tk.DISABLED)
        self.stop_schedule_btn.pack(side=tk.LEFT, padx=5)

        # -------------------------- 主体 --------------------------
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=5)
        main_frame.grid_rowconfigure(0, weight=1)

        # 左侧版本
        left_frame = ttk.Frame(main_frame, width=240)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=5)
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_propagate(False)
        ttk.Label(left_frame, text="游戏版本", font=FONT_TITLE).grid(row=0, column=0, pady=8)
        self.version_listbox = tk.Listbox(left_frame, font=FONT_NORMAL, exportselection=False)
        self.version_listbox.grid(row=1, column=0, sticky="nsew")
        self.version_listbox.bind("<<ListboxSelect>>", self.on_version_selected)

        # 右侧
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=8, pady=5)
        right_frame.grid_rowconfigure(4, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        # 存档
        save_frame = ttk.LabelFrame(right_frame, text="存档选择（自动适配版本隔离/全局共享）", padding="15 15 15 15")
        save_frame.grid(row=0, column=0, sticky="nsew", pady=10)
        save_frame.grid_columnconfigure(0, weight=1)
        
        self.save_type_label = ttk.Label(save_frame, text="存档类型：未检测", font=FONT_BOLD, foreground="blue")
        self.save_type_label.grid(row=0, column=0, sticky="w", pady=5)
        
        # ========== 关键修复 1：exportselection=False，失去焦点不取消选中 ==========
        self.save_listbox = tk.Listbox(save_frame, font=FONT_NORMAL, height=5, exportselection=False)
        self.save_listbox.grid(row=1, column=0, sticky="nsew")
        self.save_listbox.bind("<<ListboxSelect>>", self.on_save_selected)

        # 备份项
        backup_items_frame = ttk.LabelFrame(right_frame, text="可选备份内容（勾选即备份）", padding="15 15 15 15")
        backup_items_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        backup_items_frame.grid_columnconfigure(tuple(range(4)), weight=1)

        self.check_vars = {}
        self.check_buttons = []
        all_items = list(FULL_BACKUP_MAP.keys())
        row1_items = all_items[0:4]
        row2_items = all_items[4:8]
        row3_items = all_items[8:]

        for col, item_name in enumerate(row1_items):
            var = tk.BooleanVar()
            self.check_vars[item_name] = var
            cb = ttk.Checkbutton(
                backup_items_frame,
                text=item_name,
                variable=var,
                padding="10 5 10 5",
                state=tk.DISABLED,
                command=self.on_check_changed
            )
            cb.grid(row=0, column=col, padx=15, pady=5, sticky="n")
            self.check_buttons.append(cb)

        for col, item_name in enumerate(row2_items):
            var = tk.BooleanVar()
            self.check_vars[item_name] = var
            cb = ttk.Checkbutton(
                backup_items_frame,
                text=item_name,
                variable=var,
                padding="10 5 10 5",
                state=tk.DISABLED,
                command=self.on_check_changed
            )
            cb.grid(row=1, column=col, padx=15, pady=5, sticky="n")
            self.check_buttons.append(cb)

        for col, item_name in enumerate(row3_items):
            var = tk.BooleanVar()
            self.check_vars[item_name] = var
            cb = ttk.Checkbutton(
                backup_items_frame,
                text=item_name,
                variable=var,
                padding="10 5 10 5",
                state=tk.DISABLED,
                command=self.on_check_changed
            )
            cb.grid(row=2, column=col, padx=15, pady=5, sticky="n")
            self.check_buttons.append(cb)

        # 按钮
        btn_frame = ttk.Frame(right_frame)
        btn_frame.grid(row=2, column=0, sticky="nsew", pady=15)
        self.btn_backup = ttk.Button(btn_frame, text="开始备份", state=tk.DISABLED, command=self.do_backup)
        self.btn_backup.pack(side=tk.LEFT, padx=8, ipadx=25, ipady=6)
        self.btn_restore = ttk.Button(btn_frame, text="回滚选中备份", state=tk.DISABLED, command=self.do_restore)
        self.btn_restore.pack(side=tk.LEFT, padx=8, ipadx=25, ipady=6)
        self.btn_select_all = ttk.Button(btn_frame, text="全选/取消全选", command=self.toggle_select_all)
        self.btn_select_all.pack(side=tk.LEFT, padx=8, ipadx=20, ipady=6)

        # 备份历史
        history_frame = ttk.LabelFrame(right_frame, text="当前存档的备份历史", padding="15 15 15 15")
        history_frame.grid(row=3, column=0, sticky="nsew", pady=10)
        history_frame.grid_columnconfigure(0, weight=1)
        history_frame.grid_rowconfigure(0, weight=1)
        
        # ========== 关键修复 2：备份历史也加 exportselection=False ==========
        self.backup_history_list = tk.Listbox(history_frame, font=FONT_NORMAL, height=8, exportselection=False)
        self.backup_history_list.grid(row=0, column=0, sticky="nsew")
        self.backup_history_list.bind("<<ListboxSelect>>", self.on_backup_selected)
        self.backup_history_list.bind("<Button-3>", self.on_right_click_backup)

        # 右键菜单
        self.right_menu = Menu(self.root, tearoff=0, font=FONT_NORMAL)
        self.right_menu.add_command(label="打开文件所在位置", command=self.open_backup_location)
        self.right_menu.add_separator()
        self.right_menu.add_command(label="删除选中备份", command=self.delete_backup)

    # -------------------------- 定时 --------------------------
    def start_schedule(self):
        interval = self.schedule_interval.get()
        save_name = self.selected_save.get()
        success, msg = self.app_logic.start_schedule(interval, save_name)
        if success:
            self.start_schedule_btn.config(state=tk.DISABLED)
            self.stop_schedule_btn.config(state=tk.NORMAL)
            self.schedule_status_label.config(text=f"定时备份：启动中...", foreground="orange")
            messagebox.showinfo("成功", msg)
        else:
            messagebox.showwarning("提示", msg)

    def stop_schedule(self):
        success, msg = self.app_logic.stop_schedule()
        if success:
            self.start_schedule_btn.config(state=tk.NORMAL)
            self.stop_schedule_btn.config(state=tk.DISABLED)
            self.schedule_status_label.config(text=f"定时备份：已停止", foreground="red")
            messagebox.showinfo("成功", msg)

    # -------------------------- 逻辑 --------------------------
    def update_backup_btn_state(self):
        selected_items = [name for name, var in self.check_vars.items() if var.get()]
        if not self.selected_save.get() or not selected_items:
            self.btn_backup.config(state=tk.DISABLED)
        else:
            self.btn_backup.config(state=tk.NORMAL)

    def on_check_changed(self):
        self.update_backup_btn_state()

    def on_save_selected(self, event=None):
        # ========== 关键修复 3：不要因为失去焦点就清空 ==========
        sel = self.save_listbox.curselection()
        if not sel:
            # 如果没有选中，但之前已经有选中的存档，保持不变
            if not self.selected_save.get():
                self.btn_backup.config(state=tk.DISABLED)
            return
        
        # 只有真正选中了新存档，才更新
        new_save = self.save_listbox.get(sel[0])
        if new_save != self.selected_save.get():
            self.selected_save.set(new_save)
            self.backup_history_list.delete(0, tk.END)
            self.backup_name_map.clear()
            self.btn_restore.config(state=tk.DISABLED)
            self.refresh_backup_history()
        
        self.update_backup_btn_state()

    def set_check_state(self, state):
        for var in self.check_vars.values():
            var.set(False)
        for cb in self.check_buttons:
            cb.config(state=state)
        self.update_backup_btn_state()

    def toggle_select_all(self):
        all_checked = all(var.get() for var in self.check_vars.values())
        for var in self.check_vars.values():
            var.set(not all_checked)
        self.update_backup_btn_state()

    def refresh_mc_list(self):
        self.mc_combo.config(values=["正在搜索..."])
        self.root.update()
        mc_list = self.app_logic.refresh_mc_list()
        if mc_list and mc_list[0] != "未找到.minecraft文件夹":
            self.mc_combo.config(values=mc_list)
            self.mc_combo.current(0)
            self.on_mc_selected()
        else:
            self.mc_combo.config(values=mc_list)
            messagebox.showwarning("提示", "未找到.minecraft文件夹")

    def on_mc_selected(self, event=None):
        self.version_listbox.delete(0, tk.END)
        self.save_listbox.delete(0, tk.END)
        self.backup_history_list.delete(0, tk.END)
        self.backup_name_map.clear()
        self.set_check_state(tk.DISABLED)
        self.btn_restore.config(state=tk.DISABLED)
        self.save_type_label.config(text="存档类型：未检测")
        self.save_root.set("")
        self.save_type.set("")
        self.selected_save.set("")

        mc_root = self.current_mc_root.get()
        if not mc_root or mc_root == "未找到.minecraft文件夹":
            return

        versions = self.app_logic.load_versions(mc_root)
        for ver in versions:
            self.version_listbox.insert(tk.END, ver)
        #why？？？fuck code

    def on_version_selected(self, event=None):
        sel = self.version_listbox.curselection()
        if not sel:
            return
        self.save_listbox.delete(0, tk.END)
        self.backup_history_list.delete(0, tk.END)
        self.backup_name_map.clear()
        self.set_check_state(tk.NORMAL)
        self.btn_restore.config(state=tk.DISABLED)
        self.selected_save.set("")

        self.selected_version.set(self.version_listbox.get(sel[0]))
        self.load_save_list()

    def load_save_list(self):
        mc_root = self.current_mc_root.get()
        ver = self.selected_version.get()
        saves, save_root, save_type = self.app_logic.load_saves(mc_root, ver)
        self.save_root.set(save_root)
        self.save_type.set(save_type)
        self.save_type_label.config(text=f"存档类型：{save_type}")
        self.save_listbox.delete(0, tk.END)
        for s in saves:
            self.save_listbox.insert(tk.END, s)
        if not saves:
            self.save_type_label.config(text=f"存档类型：{save_type} - 无存档", foreground="red")

    def refresh_backup_history(self):
        ver = self.selected_version.get()
        save_name = self.selected_save.get()
        backup_list, backup_map = self.app_logic.refresh_backup_history(ver, save_name)
        self.backup_history_list.delete(0, tk.END)
        self.backup_name_map = backup_map
        for item in backup_list:
            self.backup_history_list.insert(tk.END, item)

    def on_backup_selected(self, event=None):
        if self.backup_history_list.curselection():
            self.btn_restore.config(state=tk.NORMAL)
        else:
            self.btn_restore.config(state=tk.DISABLED)

    def on_right_click_backup(self, event):
        idx = self.backup_history_list.nearest(event.y)
        if idx < 0 or idx >= self.backup_history_list.size():
            return
        self.backup_history_list.selection_clear(0, tk.END)
        self.backup_history_list.selection_set(idx)
        self.backup_history_list.activate(idx)
        self.on_backup_selected()
        self.right_menu.post(event.x_root, event.y_root)

    # -------------------------- 备份历史操作 --------------------------
    def open_backup_location(self):
        sel = self.backup_history_list.curselection()
        if not sel:
            return
        name = self.backup_history_list.get(sel[0])
        path = self.backup_name_map.get(name)
        self.app_logic.open_backup_location(path)

    def delete_backup(self):
        sel = self.backup_history_list.curselection()
        if not sel:
            return
        name = self.backup_history_list.get(sel[0])
        path = self.backup_name_map.get(name)
        if not messagebox.askyesno("确认", f"确定删除备份：\n{name}"):
            return
        success, msg = self.app_logic.delete_backup(path)
        if success:
            self.refresh_backup_history()
            messagebox.showinfo("成功", msg)
        else:
            messagebox.showerror("失败", msg)

    # -------------------------- 备份 / 回滚 --------------------------
    def do_backup(self):
        selected_items = [k for k, v in self.check_vars.items() if v.get()]
        save = self.selected_save.get()
        save_root = self.save_root.get()
        mc_root = self.current_mc_root.get()
        ver = self.selected_version.get()
        note = simpledialog.askstring("备注", "输入备注（可选）", parent=self.root) or ""
        success, msg = self.app_logic.do_backup(mc_root, ver, save, save_root, selected_items, note)
        if success:
            messagebox.showinfo("完成", msg)
            self.refresh_backup_history()
        else:
            messagebox.showwarning("提示", msg)

    def do_restore(self):
        sel = self.backup_history_list.curselection()
        if not sel:
            messagebox.showwarning("提示", "请先选中一个备份")
            return
        name = self.backup_history_list.get(sel[0])
        path = self.backup_name_map.get(name)
        if not path or not os.path.exists(path):
            messagebox.showerror("错误", "文件不存在")
            return
        if not messagebox.askyesno("确认回滚", "回滚会覆盖当前的对应文件，是否继续？"):
            return
        success, msg = self.app_logic.do_restore(path, self.current_mc_root.get(), self.save_root.get())
        if success:
            messagebox.showinfo("成功", msg)
        else:
            messagebox.showerror("回滚失败", msg)