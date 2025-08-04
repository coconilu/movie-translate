"""
Recovery dialog for Movie Translate UI
Handles recovery of interrupted work
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from movie_translate.core.interrupt_recovery import get_interrupt_recovery
from movie_translate.core import logger


class RecoveryDialog(ctk.CTkToplevel):
    """Recovery dialog for handling interrupted work"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("恢复工作")
        self.geometry("600x500")
        self.transient(parent)
        self.grab_set()
        
        self.recovery_data = None
        self.checkpoints = []
        
        # Create UI
        self._create_ui()
        
        # Load recovery data
        self._load_recovery_data()
        
        # Center the dialog
        self._center_window()
    
    def _center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_ui(self):
        """Create recovery dialog UI"""
        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="恢复未完成的工作",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Auto recovery tab
        self._create_auto_recovery_tab()
        
        # Checkpoints tab
        self._create_checkpoints_tab()
        
        # Buttons
        self._create_buttons()
    
    def _create_auto_recovery_tab(self):
        """Create auto recovery tab"""
        auto_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(auto_frame, text="自动恢复")
        
        # Recovery info
        self.info_frame = ctk.CTkFrame(auto_frame)
        self.info_frame.pack(fill="x", padx=20, pady=20)
        
        # Loading label
        self.loading_label = ctk.CTkLabel(
            self.info_frame,
            text="正在检查恢复数据...",
            font=ctk.CTkFont(size=12)
        )
        self.loading_label.pack(pady=20)
        
        # Recovery details (initially hidden)
        self.details_frame = ctk.CTkFrame(auto_frame)
        
        # Project info
        self.project_info_frame = ctk.CTkFrame(self.details_frame)
        self.project_info_frame.pack(fill="x", padx=20, pady=10)
        
        # Step progress
        self.steps_frame = ctk.CTkFrame(self.details_frame)
        self.steps_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    def _create_checkpoints_tab(self):
        """Create checkpoints tab"""
        checkpoints_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(checkpoints_frame, text="检查点")
        
        # Checkpoints list
        self.checkpoints_list_frame = ctk.CTkScrollableFrame(checkpoints_frame, height=300)
        self.checkpoints_list_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Loading label
        self.checkpoints_loading_label = ctk.CTkLabel(
            self.checkpoints_list_frame,
            text="正在加载检查点...",
            font=ctk.CTkFont(size=12)
        )
        self.checkpoints_loading_label.pack(pady=20)
    
    def _create_buttons(self):
        """Create action buttons"""
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Recover button
        self.recover_btn = ctk.CTkButton(
            button_frame,
            text="恢复工作",
            command=self._recover_work,
            width=120,
            state="disabled"
        )
        self.recover_btn.pack(side="left", padx=5)
        
        # Load checkpoint button
        self.load_checkpoint_btn = ctk.CTkButton(
            button_frame,
            text="加载检查点",
            command=self._load_selected_checkpoint,
            width=120,
            state="disabled"
        )
        self.load_checkpoint_btn.pack(side="left", padx=5)
        
        # Delete checkpoint button
        self.delete_checkpoint_btn = ctk.CTkButton(
            button_frame,
            text="删除检查点",
            command=self._delete_selected_checkpoint,
            width=120,
            state="disabled"
        )
        self.delete_checkpoint_btn.pack(side="left", padx=5)
        
        # New project button
        self.new_project_btn = ctk.CTkButton(
            button_frame,
            text="新建项目",
            command=self._new_project,
            width=120
        )
        self.new_project_btn.pack(side="right", padx=5)
        
        # Cancel button
        self.cancel_btn = ctk.CTkButton(
            button_frame,
            text="取消",
            command=self.destroy,
            width=120
        )
        self.cancel_btn.pack(side="right", padx=5)
    
    def _load_recovery_data(self):
        """Load recovery data"""
        try:
            interrupt_recovery = get_interrupt_recovery()
            
            # Check for auto recovery
            if interrupt_recovery.has_recovery_state():
                recovery_info = interrupt_recovery.get_recovery_info()
                
                if recovery_info['has_state']:
                    self.recovery_data = interrupt_recovery.load_state()
                    self._show_recovery_details(recovery_info)
                    self.recover_btn.configure(state="normal")
            
            # Load checkpoints
            self._load_checkpoints()
            
        except Exception as e:
            logger.error(f"Failed to load recovery data: {e}")
            self.loading_label.configure(text="无法加载恢复数据")
    
    def _show_recovery_details(self, recovery_info: Dict[str, Any]):
        """Show recovery details"""
        # Hide loading label
        self.loading_label.pack_forget()
        
        # Show details frame
        self.details_frame.pack(fill="both", expand=True)
        
        # Format timestamp
        timestamp = datetime.fromisoformat(recovery_info['timestamp'])
        time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        age_str = self._format_age(recovery_info['age'])
        
        # Create info labels
        info_text = f"发现未完成的工作\n"
        info_text += f"保存时间: {time_str}\n"
        info_text += f"年龄: {age_str}\n"
        info_text += f"版本: {recovery_info['version']}"
        
        info_label = ctk.CTkLabel(
            self.project_info_frame,
            text=info_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        info_label.pack(pady=10)
        
        # Show project details if available
        if self.recovery_data and 'project' in self.recovery_data:
            project_data = self.recovery_data['project']
            
            project_text = "项目信息:\n"
            if 'name' in project_data:
                project_text += f"项目名称: {project_data['name']}\n"
            if 'video_file' in project_data:
                project_text += f"视频文件: {project_data['video_file']}\n"
            if 'current_step' in project_data:
                project_text += f"当前步骤: {project_data['current_step']}"
            
            project_label = ctk.CTkLabel(
                self.project_info_frame,
                text=project_text,
                font=ctk.CTkFont(size=11),
                justify="left"
            )
            project_label.pack(pady=5)
        
        # Show step progress
        if self.recovery_data and 'steps' in self.recovery_data:
            steps_data = self.recovery_data['steps']
            
            steps_label = ctk.CTkLabel(
                self.steps_frame,
                text="步骤进度:",
                font=ctk.CTkFont(size=12, weight="bold")
            )
            steps_label.pack(pady=(10, 5))
            
            for step_id, step_info in steps_data.items():
                step_timestamp = datetime.fromisoformat(step_info['timestamp'])
                step_time_str = step_timestamp.strftime("%H:%M:%S")
                
                step_text = f"步骤 {step_id}: {step_time_str}"
                step_label = ctk.CTkLabel(
                    self.steps_frame,
                    text=step_text,
                    font=ctk.CTkFont(size=11)
                )
                step_label.pack(pady=2)
    
    def _load_checkpoints(self):
        """Load checkpoints"""
        try:
            interrupt_recovery = get_interrupt_recovery()
            self.checkpoints = interrupt_recovery.list_checkpoints()
            
            # Hide loading label
            self.checkpoints_loading_label.pack_forget()
            
            if self.checkpoints:
                self._display_checkpoints()
            else:
                no_checkpoints_label = ctk.CTkLabel(
                    self.checkpoints_list_frame,
                    text="没有可用的检查点",
                    font=ctk.CTkFont(size=12),
                    text_color="gray"
                )
                no_checkpoints_label.pack(pady=20)
                
        except Exception as e:
            logger.error(f"Failed to load checkpoints: {e}")
            self.checkpoints_loading_label.configure(text="无法加载检查点")
    
    def _display_checkpoints(self):
        """Display checkpoints list"""
        self.selected_checkpoint = None
        
        for i, checkpoint in enumerate(self.checkpoints):
            # Checkpoint frame
            checkpoint_frame = ctk.CTkFrame(self.checkpoints_list_frame)
            checkpoint_frame.pack(fill="x", padx=10, pady=5)
            
            # Radio button
            radio_var = tk.StringVar()
            radio_btn = ctk.CTkRadioButton(
                checkpoint_frame,
                text="",
                variable=radio_var,
                value=checkpoint['name'],
                command=lambda cp=checkpoint: self._select_checkpoint(cp)
            )
            radio_btn.pack(side="left", padx=10)
            
            # Checkpoint info
            info_frame = ctk.CTkFrame(checkpoint_frame, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, padx=10)
            
            # Name
            name_label = ctk.CTkLabel(
                info_frame,
                text=checkpoint['name'],
                font=ctk.CTkFont(size=12, weight="bold")
            )
            name_label.pack(anchor="w")
            
            # Timestamp
            timestamp = datetime.fromisoformat(checkpoint['timestamp'])
            time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            
            time_label = ctk.CTkLabel(
                info_frame,
                text=time_str,
                font=ctk.CTkFont(size=10),
                text_color="gray"
            )
            time_label.pack(anchor="w")
            
            # Version
            version_label = ctk.CTkLabel(
                info_frame,
                text=f"版本: {checkpoint['version']}",
                font=ctk.CTkFont(size=10),
                text_color="gray"
            )
            version_label.pack(anchor="w")
    
    def _select_checkpoint(self, checkpoint: Dict[str, Any]):
        """Select a checkpoint"""
        self.selected_checkpoint = checkpoint
        self.load_checkpoint_btn.configure(state="normal")
        self.delete_checkpoint_btn.configure(state="normal")
    
    def _format_age(self, age_seconds: float) -> str:
        """Format age in human readable format"""
        if age_seconds < 60:
            return f"{int(age_seconds)}秒前"
        elif age_seconds < 3600:
            return f"{int(age_seconds // 60)}分钟前"
        elif age_seconds < 86400:
            return f"{int(age_seconds // 3600)}小时前"
        else:
            return f"{int(age_seconds // 86400)}天前"
    
    def _recover_work(self):
        """Recover work from auto-save"""
        if not self.recovery_data:
            return
        
        try:
            # Confirm recovery
            result = messagebox.askyesno(
                "确认恢复",
                "确定要恢复未完成的工作吗？这将覆盖当前的项目状态。"
            )
            
            if not result:
                return
            
            # Load recovery data into parent
            if hasattr(self.parent, 'load_recovery_data'):
                self.parent.load_recovery_data(self.recovery_data)
            
            # Clear recovery state
            interrupt_recovery = get_interrupt_recovery()
            interrupt_recovery.clear_recovery_state()
            
            messagebox.showinfo("成功", "工作已恢复")
            self.destroy()
            
        except Exception as e:
            logger.error(f"Failed to recover work: {e}")
            messagebox.showerror("错误", f"恢复失败: {e}")
    
    def _load_selected_checkpoint(self):
        """Load selected checkpoint"""
        if not self.selected_checkpoint:
            return
        
        try:
            # Confirm loading
            result = messagebox.askyesno(
                "确认加载",
                f"确定要加载检查点 '{self.selected_checkpoint['name']}' 吗？这将覆盖当前的项目状态。"
            )
            
            if not result:
                return
            
            # Load checkpoint
            interrupt_recovery = get_interrupt_recovery()
            success = interrupt_recovery.load_checkpoint(self.selected_checkpoint['name'])
            
            if success:
                # Load recovery data into parent
                if hasattr(self.parent, 'load_recovery_data'):
                    self.parent.load_recovery_data(interrupt_recovery.current_state)
                
                messagebox.showinfo("成功", f"检查点 '{self.selected_checkpoint['name']}' 已加载")
                self.destroy()
            else:
                messagebox.showerror("错误", "加载检查点失败")
                
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            messagebox.showerror("错误", f"加载检查点失败: {e}")
    
    def _delete_selected_checkpoint(self):
        """Delete selected checkpoint"""
        if not self.selected_checkpoint:
            return
        
        try:
            # Confirm deletion
            result = messagebox.askyesno(
                "确认删除",
                f"确定要删除检查点 '{self.selected_checkpoint['name']}' 吗？此操作不可撤销。"
            )
            
            if not result:
                return
            
            # Delete checkpoint
            interrupt_recovery = get_interrupt_recovery()
            interrupt_recovery.delete_checkpoint(self.selected_checkpoint['name'])
            
            # Refresh checkpoints list
            self._load_checkpoints()
            
            messagebox.showinfo("成功", f"检查点 '{self.selected_checkpoint['name']}' 已删除")
            
        except Exception as e:
            logger.error(f"Failed to delete checkpoint: {e}")
            messagebox.showerror("错误", f"删除检查点失败: {e}")
    
    def _new_project(self):
        """Start new project (clear recovery)"""
        try:
            # Confirm new project
            result = messagebox.askyesno(
                "确认新建项目",
                "确定要新建项目吗？所有未完成的恢复数据将被清除。"
            )
            
            if not result:
                return
            
            # Clear recovery state
            interrupt_recovery = get_interrupt_recovery()
            interrupt_recovery.clear_recovery_state()
            
            # Close dialog
            self.destroy()
            
        except Exception as e:
            logger.error(f"Failed to clear recovery: {e}")
            messagebox.showerror("错误", f"清除恢复数据失败: {e}")


def show_recovery_dialog(parent):
    """Show recovery dialog"""
    dialog = RecoveryDialog(parent)
    dialog.wait_window()
    return dialog.recovery_data