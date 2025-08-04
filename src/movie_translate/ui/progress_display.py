"""
Progress display component for Movie Translate UI
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any, List
from datetime import datetime
import threading


class ProgressDisplay(ctk.CTkFrame):
    """Progress display component for showing operation progress"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color=("gray95", "gray10"))
        self.parent = parent
        self.current_operation = None
        self.start_time = None
        self.progress_tasks = []
        
        self._create_ui()
        self.hide()
    
    def _create_ui(self):
        """Create progress display UI"""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Main progress bar
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(1, weight=1)
        
        # Operation title
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Status text
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        # Progress percentage
        self.percent_label = ctk.CTkLabel(
            self.main_frame,
            text="0%",
            font=ctk.CTkFont(size=12)
        )
        self.percent_label.grid(row=0, column=2, padx=10, pady=5, sticky="e")
        
        # Main progress bar
        self.progress_bar = ctk.CTkProgressBar(self.main_frame)
        self.progress_bar.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
        self.progress_bar.set(0)
        
        # Subtasks frame
        self.subtasks_frame = ctk.CTkScrollableFrame(self, height=200)
        self.subtasks_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=5)
        self.subtasks_frame.grid_columnconfigure(1, weight=1)
        
        # Action buttons
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
        
        self.cancel_btn = ctk.CTkButton(
            self.actions_frame,
            text="取消",
            command=self._cancel_operation,
            width=80,
            state="disabled"
        )
        self.cancel_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.pause_btn = ctk.CTkButton(
            self.actions_frame,
            text="暂停",
            command=self._pause_operation,
            width=80,
            state="disabled"
        )
        self.pause_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.details_btn = ctk.CTkButton(
            self.actions_frame,
            text="详细信息",
            command=self._show_details,
            width=80
        )
        self.details_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Hide by default
        self.grid_remove()
    
    def show(self, title: str, description: str = ""):
        """Show progress display"""
        self.current_operation = {
            'title': title,
            'description': description,
            'start_time': datetime.now(),
            'progress': 0,
            'status': 'running',
            'paused': False,
            'cancelled': False
        }
        
        self.title_label.configure(text=title)
        self.status_label.configure(text=description or "准备中...")
        self.percent_label.configure(text="0%")
        self.progress_bar.set(0)
        
        # Enable buttons
        self.cancel_btn.configure(state="normal")
        self.pause_btn.configure(state="normal")
        
        # Show the frame
        self.grid()
        
        # Start time updates
        self._update_time_display()
    
    def hide(self):
        """Hide progress display"""
        self.grid_remove()
        self.current_operation = None
        self.progress_tasks.clear()
        
        # Clear subtasks
        for widget in self.subtasks_frame.winfo_children():
            widget.destroy()
    
    def update_progress(self, value: int, status: str = ""):
        """Update main progress"""
        if not self.current_operation:
            return
        
        # Clamp value between 0 and 100
        value = max(0, min(100, value))
        
        self.current_operation['progress'] = value
        self.progress_bar.set(value / 100)
        self.percent_label.configure(text=f"{value}%")
        
        if status:
            self.status_label.configure(text=status)
        
        # Check if completed
        if value >= 100:
            self._on_operation_completed()
    
    def add_subtask(self, task_id: str, title: str, weight: float = 1.0):
        """Add a subtask to track"""
        if not self.current_operation:
            return
        
        task = {
            'id': task_id,
            'title': title,
            'weight': weight,
            'progress': 0,
            'status': 'pending'
        }
        
        self.progress_tasks.append(task)
        self._create_subtask_ui(task)
    
    def update_subtask(self, task_id: str, progress: int, status: str = ""):
        """Update subtask progress"""
        if not self.current_operation:
            return
        
        # Find and update task
        for task in self.progress_tasks:
            if task['id'] == task_id:
                task['progress'] = max(0, min(100, progress))
                task['status'] = status or 'running'
                
                # Update UI
                self._update_subtask_ui(task)
                
                # Update overall progress
                self._update_overall_progress()
                break
    
    def complete_subtask(self, task_id: str):
        """Mark subtask as completed"""
        self.update_subtask(task_id, 100, "已完成")
    
    def fail_subtask(self, task_id: str, error: str = ""):
        """Mark subtask as failed"""
        self.update_subtask(task_id, 0, error or "失败")
    
    def _create_subtask_ui(self, task: Dict[str, Any]):
        """Create UI for a subtask"""
        row = len(self.progress_tasks) - 1
        
        # Task frame
        task_frame = ctk.CTkFrame(self.subtasks_frame, fg_color="transparent")
        task_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
        task_frame.grid_columnconfigure(1, weight=1)
        
        # Task status indicator
        status_label = ctk.CTkLabel(
            task_frame,
            text="○",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        status_label.grid(row=0, column=0, padx=5, pady=2)
        
        # Task title
        title_label = ctk.CTkLabel(
            task_frame,
            text=task['title'],
            font=ctk.CTkFont(size=11)
        )
        title_label.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        # Task progress
        progress_bar = ctk.CTkProgressBar(task_frame, width=100, height=8)
        progress_bar.grid(row=0, column=2, padx=5, pady=2)
        progress_bar.set(0)
        
        # Task percentage
        percent_label = ctk.CTkLabel(
            task_frame,
            text="0%",
            font=ctk.CTkFont(size=10)
        )
        percent_label.grid(row=0, column=3, padx=5, pady=2)
        
        # Store UI references
        task['ui'] = {
            'frame': task_frame,
            'status_label': status_label,
            'title_label': title_label,
            'progress_bar': progress_bar,
            'percent_label': percent_label
        }
    
    def _update_subtask_ui(self, task: Dict[str, Any]):
        """Update subtask UI"""
        if 'ui' not in task:
            return
        
        ui = task['ui']
        
        # Update progress bar
        ui['progress_bar'].set(task['progress'] / 100)
        ui['percent_label'].configure(text=f"{task['progress']}%")
        
        # Update status indicator
        if task['progress'] >= 100:
            ui['status_label'].configure(text="✓", text_color="green")
            ui['title_label'].configure(text_color="green")
        elif task['status'].startswith('失败') or task['status'].startswith('错误'):
            ui['status_label'].configure(text="✗", text_color="red")
            ui['title_label'].configure(text_color="red")
        elif task['status'] == 'running':
            ui['status_label'].configure(text="●", text_color="blue")
            ui['title_label'].configure(text_color="blue")
        else:
            ui['status_label'].configure(text="○", text_color="gray")
            ui['title_label'].configure(text_color="black")
        
        # Update title with status
        if task['status'] and task['status'] != 'running':
            ui['title_label'].configure(text=f"{task['title']} - {task['status']}")
    
    def _update_overall_progress(self):
        """Update overall progress based on subtasks"""
        if not self.progress_tasks:
            return
        
        total_weight = sum(task['weight'] for task in self.progress_tasks)
        weighted_progress = sum(task['progress'] * task['weight'] for task in self.progress_tasks)
        
        overall_progress = int(weighted_progress / total_weight) if total_weight > 0 else 0
        self.update_progress(overall_progress)
    
    def _update_time_display(self):
        """Update time display"""
        if not self.current_operation:
            return
        
        if self.current_operation['start_time']:
            elapsed = datetime.now() - self.current_operation['start_time']
            elapsed_str = str(elapsed).split('.')[0]  # Remove microseconds
            
            if self.current_operation['progress'] > 0:
                # Estimate remaining time
                total_estimated = elapsed.total_seconds() / (self.current_operation['progress'] / 100)
                remaining_seconds = total_estimated - elapsed.total_seconds()
                
                if remaining_seconds > 0:
                    remaining_str = f"剩余时间: {int(remaining_seconds // 60)}分{int(remaining_seconds % 60)}秒"
                    self.status_label.configure(text=f"{self.current_operation['description']} | {remaining_str}")
        
        # Schedule next update
        if self.current_operation and self.current_operation['status'] == 'running':
            self.after(1000, self._update_time_display)
    
    def _cancel_operation(self):
        """Cancel current operation"""
        if not self.current_operation:
            return
        
        result = tk.messagebox.askyesno("确认", "确定要取消当前操作吗？")
        if result:
            self.current_operation['cancelled'] = True
            self.current_operation['status'] = 'cancelled'
            self.status_label.configure(text="操作已取消")
            self.cancel_btn.configure(state="disabled")
            self.pause_btn.configure(state="disabled")
            
            # Notify parent
            if hasattr(self.parent, 'on_operation_cancelled'):
                self.parent.on_operation_cancelled()
    
    def _pause_operation(self):
        """Pause/resume current operation"""
        if not self.current_operation:
            return
        
        if self.current_operation['paused']:
            # Resume
            self.current_operation['paused'] = False
            self.pause_btn.configure(text="暂停")
            self.status_label.configure(text="操作已恢复")
            
            # Resume time updates
            self._update_time_display()
            
            # Notify parent
            if hasattr(self.parent, 'on_operation_resumed'):
                self.parent.on_operation_resumed()
        else:
            # Pause
            self.current_operation['paused'] = True
            self.pause_btn.configure(text="继续")
            self.status_label.configure(text="操作已暂停")
            
            # Notify parent
            if hasattr(self.parent, 'on_operation_paused'):
                self.parent.on_operation_paused()
    
    def _show_details(self):
        """Show detailed progress information"""
        if not self.current_operation:
            return
        
        details_window = ctk.CTkToplevel(self)
        details_window.title("操作详情")
        details_window.geometry("500x400")
        details_window.transient(self)
        details_window.grab_set()
        
        # Create details text
        details_text = ctk.CTkTextbox(details_window)
        details_text.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Add details
        details = f"操作: {self.current_operation['title']}\n"
        details += f"状态: {self.current_operation['status']}\n"
        details += f"进度: {self.current_operation['progress']}%\n"
        
        if self.current_operation['start_time']:
            elapsed = datetime.now() - self.current_operation['start_time']
            details += f"已用时间: {str(elapsed).split('.')[0]}\n"
        
        details += f"\n子任务 ({len(self.progress_tasks)}):\n"
        details += "-" * 40 + "\n"
        
        for task in self.progress_tasks:
            details += f"• {task['title']}: {task['progress']}% - {task['status']}\n"
        
        details_text.insert("1.0", details)
        details_text.configure(state="disabled")
        
        # Close button
        close_btn = ctk.CTkButton(
            details_window,
            text="关闭",
            command=details_window.destroy,
            width=80
        )
        close_btn.pack(pady=10)
    
    def _on_operation_completed(self):
        """Handle operation completion"""
        if not self.current_operation:
            return
        
        self.current_operation['status'] = 'completed'
        self.status_label.configure(text="操作完成")
        self.cancel_btn.configure(state="disabled")
        self.pause_btn.configure(state="disabled")
        
        # Notify parent
        if hasattr(self.parent, 'on_operation_completed'):
            self.parent.on_operation_completed()
    
    def is_cancelled(self) -> bool:
        """Check if operation was cancelled"""
        return self.current_operation and self.current_operation.get('cancelled', False)
    
    def is_paused(self) -> bool:
        """Check if operation is paused"""
        return self.current_operation and self.current_operation.get('paused', False)
    
    def get_progress(self) -> int:
        """Get current progress value"""
        return self.current_operation['progress'] if self.current_operation else 0
    
    def set_error(self, error_message: str):
        """Set error state"""
        if not self.current_operation:
            return
        
        self.current_operation['status'] = 'error'
        self.status_label.configure(text=f"错误: {error_message}")
        self.cancel_btn.configure(state="disabled")
        self.pause_btn.configure(state="disabled")
        
        # Change progress bar color to red
        self.progress_bar.configure(progress_color="red")
        
        # Notify parent
        if hasattr(self.parent, 'on_operation_error'):
            self.parent.on_operation_error(error_message)
    
    def reset(self):
        """Reset progress display"""
        self.hide()
        self.progress_bar.configure(progress_color="blue")  # Reset color