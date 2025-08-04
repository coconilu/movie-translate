"""
Main UI application for Movie Translate
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import asyncio
import threading
from pathlib import Path
from typing import Optional, Dict, Any
import json

from ..core import logger, settings
from ..core.interrupt_recovery import get_interrupt_recovery
from ..api.client import APIClient, ProjectManager
from ..models import initialize_database
from .step_navigator import StepNavigator
from .file_import import FileImportFrame
from .character_manager import CharacterManagerFrame
from .settings_panel import SettingsPanel
from .progress_display import ProgressDisplay
from .recovery_dialog import show_recovery_dialog


class MovieTranslateApp(ctk.CTk):
    """Main application window for Movie Translate"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize database
        try:
            initialize_database()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            messagebox.showerror("数据库错误", f"数据库初始化失败: {e}")
        
        # Initialize API client
        self.api_client = APIClient()
        self.project_manager = ProjectManager(self.api_client)
        
        # Current project data
        self.current_project = None
        self.current_step = 0
        
        # Configure window
        self.title("Movie Translate - 电影翻译配音工具")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # Set appearance
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # Configure grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Create UI components
        self._create_sidebar()
        self._create_main_content()
        self._create_status_bar()
        
        # Initialize components
        self._initialize_components()
        
        # Setup async event loop
        self._setup_async_loop()
        
        # Start interrupt recovery
        self._start_interrupt_recovery()
        
        # Check for recovery data
        self._check_recovery()
        
        logger.info("Main UI application initialized")
    
    def _create_sidebar(self):
        """Create sidebar with navigation"""
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)
        
        # App title
        title_label = ctk.CTkLabel(
            self.sidebar,
            text="Movie Translate",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            self.sidebar,
            text="电影翻译配音工具",
            font=ctk.CTkFont(size=14)
        )
        subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 20))
        
        # Step navigator
        self.step_navigator = StepNavigator(self.sidebar, self)
        self.step_navigator.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        # Project info frame
        self.project_frame = ctk.CTkFrame(self.sidebar)
        self.project_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        
        project_label = ctk.CTkLabel(
            self.project_frame,
            text="项目信息",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        project_label.grid(row=0, column=0, padx=10, pady=(10, 5))
        
        self.project_name_label = ctk.CTkLabel(
            self.project_frame,
            text="未创建项目",
            font=ctk.CTkFont(size=12)
        )
        self.project_name_label.grid(row=1, column=0, padx=10, pady=5)
        
        self.project_status_label = ctk.CTkLabel(
            self.project_frame,
            text="状态: 就绪",
            font=ctk.CTkFont(size=12)
        )
        self.project_status_label.grid(row=2, column=0, padx=10, pady=5)
        
        # Quick actions frame
        actions_frame = ctk.CTkFrame(self.sidebar)
        actions_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        
        actions_label = ctk.CTkLabel(
            actions_frame,
            text="快速操作",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        actions_label.grid(row=0, column=0, padx=10, pady=(10, 5))
        
        self.new_project_btn = ctk.CTkButton(
            actions_frame,
            text="新建项目",
            command=self._new_project,
            width=200
        )
        self.new_project_btn.grid(row=1, column=0, padx=10, pady=5)
        
        self.open_project_btn = ctk.CTkButton(
            actions_frame,
            text="打开项目",
            command=self._open_project,
            width=200
        )
        self.open_project_btn.grid(row=2, column=0, padx=10, pady=5)
        
        self.save_project_btn = ctk.CTkButton(
            actions_frame,
            text="保存项目",
            command=self._save_project,
            width=200,
            state="disabled"
        )
        self.save_project_btn.grid(row=3, column=0, padx=10, pady=5)
        
        # Settings button
        self.settings_btn = ctk.CTkButton(
            self.sidebar,
            text="设置",
            command=self._open_settings,
            width=200
        )
        self.settings_btn.grid(row=5, column=0, padx=10, pady=5)
        
        # Recovery button
        self.recovery_btn = ctk.CTkButton(
            self.sidebar,
            text="恢复管理",
            command=self._open_recovery_dialog,
            width=200
        )
        self.recovery_btn.grid(row=6, column=0, padx=10, pady=5)
        
        # Export button
        self.export_btn = ctk.CTkButton(
            self.sidebar,
            text="导出视频",
            command=self._export_video,
            width=200,
            state="disabled"
        )
        self.export_btn.grid(row=6, column=0, padx=10, pady=5)
        
        # Help button
        self.help_btn = ctk.CTkButton(
            self.sidebar,
            text="帮助",
            command=self._show_help,
            width=200
        )
        self.help_btn.grid(row=7, column=0, padx=10, pady=5)
        
        # Version info
        version_label = ctk.CTkLabel(
            self.sidebar,
            text="v1.0.0",
            font=ctk.CTkFont(size=10)
        )
        version_label.grid(row=8, column=0, padx=10, pady=(20, 10))
    
    def _create_main_content(self):
        """Create main content area"""
        self.main_content = ctk.CTkFrame(self, corner_radius=0)
        self.main_content.grid(row=0, column=1, sticky="nsew")
        self.main_content.grid_rowconfigure(1, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)
        
        # Content header
        self.header_frame = ctk.CTkFrame(self.main_content, height=60)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_rowconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=1)
        
        self.step_title_label = ctk.CTkLabel(
            self.header_frame,
            text="欢迎使用 Movie Translate",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.step_title_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        self.step_description_label = ctk.CTkLabel(
            self.header_frame,
            text="请创建新项目或打开现有项目开始",
            font=ctk.CTkFont(size=14)
        )
        self.step_description_label.grid(row=0, column=1, padx=20, pady=15, sticky="w")
        
        # Content area
        self.content_frame = ctk.CTkFrame(self.main_content)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Progress display
        self.progress_display = ProgressDisplay(self.main_content)
        self.progress_display.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))
        self.progress_display.hide()
    
    def _create_status_bar(self):
        """Create status bar"""
        self.status_bar = ctk.CTkFrame(self, height=30)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.status_bar.grid_rowconfigure(0, weight=1)
        self.status_bar.grid_columnconfigure(1, weight=1)
        
        # Status text
        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="就绪",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Connection status
        self.connection_status_label = ctk.CTkLabel(
            self.status_bar,
            text="API: 未连接",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.connection_status_label.grid(row=0, column=1, padx=10, pady=5, sticky="e")
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            self.status_bar,
            mode='determinate',
            length=200
        )
        self.progress_bar.grid(row=0, column=2, padx=10, pady=5)
        self.progress_bar['value'] = 0
    
    def _initialize_components(self):
        """Initialize UI components"""
        # Initialize all frames
        self.frames = {}
        
        # Create frames for each step
        self.frames['file_import'] = FileImportFrame(self.content_frame, self)
        self.frames['character_manager'] = CharacterManagerFrame(self.content_frame, self)
        
        # Hide all frames initially
        for frame in self.frames.values():
            frame.grid_remove()
    
    def _setup_async_loop(self):
        """Setup async event loop for the application"""
        self.async_loop = asyncio.new_event_loop()
        
        def run_async_loop():
            asyncio.set_event_loop(self.async_loop)
            self.async_loop.run_forever()
        
        self.async_thread = threading.Thread(target=run_async_loop, daemon=True)
        self.async_thread.start()
        
        # Schedule connection check
        self.after(1000, self._check_api_connection)
    
    def _check_api_connection(self):
        """Check API connection status"""
        async def check_connection():
            try:
                await self.api_client.health_check()
                self._update_connection_status(True)
            except Exception as e:
                logger.warning(f"API connection failed: {e}")
                self._update_connection_status(False)
        
        self.run_async(check_connection())
        # Check every 30 seconds
        self.after(30000, self._check_api_connection)
    
    def _update_connection_status(self, connected: bool):
        """Update connection status display"""
        if connected:
            self.connection_status_label.configure(text="API: 已连接", text_color="green")
        else:
            self.connection_status_label.configure(text="API: 未连接", text_color="red")
    
    def run_async(self, coro):
        """Run async coroutine from main thread"""
        if not self.async_loop.is_running():
            return
        
        future = asyncio.run_coroutine_threadsafe(coro, self.async_loop)
        return future.result()
    
    def _new_project(self):
        """Create new project"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("新建项目")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        
        # Project name
        name_label = ctk.CTkLabel(dialog, text="项目名称:")
        name_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        name_entry = ctk.CTkEntry(dialog, width=300)
        name_entry.grid(row=0, column=1, padx=20, pady=10)
        
        # Video file
        video_label = ctk.CTkLabel(dialog, text="视频文件:")
        video_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        video_path = tk.StringVar()
        video_entry = ctk.CTkEntry(dialog, width=250, textvariable=video_path)
        video_entry.grid(row=1, column=1, padx=20, pady=10, sticky="w")
        
        def browse_video():
            file_path = filedialog.askopenfilename(
                title="选择视频文件",
                filetypes=[
                    ("视频文件", "*.mp4 *.avi *.mkv *.mov *.wmv"),
                    ("所有文件", "*.*")
                ]
            )
            if file_path:
                video_path.set(file_path)
        
        browse_btn = ctk.CTkButton(dialog, text="浏览", command=browse_video)
        browse_btn.grid(row=1, column=2, padx=10, pady=10)
        
        # Target language
        lang_label = ctk.CTkLabel(dialog, text="目标语言:")
        lang_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        
        lang_var = tk.StringVar(value="zh")
        lang_combo = ctk.CTkComboBox(dialog, width=150, variable=lang_var)
        lang_combo.grid(row=2, column=1, padx=20, pady=10, sticky="w")
        lang_combo.configure(values=["zh", "en", "ja", "ko", "fr", "de", "es", "ru"])
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        def create_project():
            project_name = name_entry.get().strip()
            video_file = video_path.get()
            target_lang = lang_var.get()
            
            if not project_name:
                messagebox.showerror("错误", "请输入项目名称")
                return
            
            if not video_file:
                messagebox.showerror("错误", "请选择视频文件")
                return
            
            async def create():
                try:
                    project = await self.project_manager.create_project(
                        name=project_name,
                        video_path=video_file,
                        target_language=target_lang
                    )
                    self.current_project = project
                    self._update_project_display()
                    self._navigate_to_step(0)
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("错误", f"创建项目失败: {e}")
            
            self.run_async(create())
        
        create_btn = ctk.CTkButton(button_frame, text="创建", command=create_project)
        create_btn.grid(row=0, column=0, padx=10)
        
        cancel_btn = ctk.CTkButton(button_frame, text="取消", command=dialog.destroy)
        cancel_btn.grid(row=0, column=1, padx=10)
    
    def _open_recovery_dialog(self):
        """Open recovery management dialog"""
        try:
            show_recovery_dialog(self)
        except Exception as e:
            logger.error(f"Failed to open recovery dialog: {e}")
            messagebox.showerror("错误", f"打开恢复对话框失败: {e}")
    
    def _open_project(self):
        """Open existing project"""
        file_path = filedialog.askopenfilename(
            title="打开项目",
            filetypes=[
                ("项目文件", "*.json"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            async def open_project():
                try:
                    project = await self.project_manager.load_project(file_path)
                    self.current_project = project
                    self._update_project_display()
                    self._navigate_to_step(0)
                except Exception as e:
                    messagebox.showerror("错误", f"打开项目失败: {e}")
            
            self.run_async(open_project())
    
    def _save_project(self):
        """Save current project"""
        if not self.current_project:
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存项目",
            defaultextension=".json",
            filetypes=[
                ("项目文件", "*.json"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            async def save_project():
                try:
                    await self.project_manager.save_project(file_path)
                    messagebox.showinfo("成功", "项目保存成功")
                except Exception as e:
                    messagebox.showerror("错误", f"保存项目失败: {e}")
            
            self.run_async(save_project())
    
    def _export_video(self):
        """Export final video"""
        if not self.current_project:
            messagebox.showwarning("警告", "请先创建或打开项目")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="导出视频",
            defaultextension=".mp4",
            filetypes=[
                ("MP4文件", "*.mp4"),
                ("AVI文件", "*.avi"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            async def export_video():
                try:
                    self.progress_display.show("正在导出视频...")
                    self.progress_display.update_progress(0, "开始导出")
                    
                    # Export video using API
                    result = await self.project_manager.export_video(file_path)
                    
                    self.progress_display.update_progress(100, "导出完成")
                    messagebox.showinfo("成功", f"视频导出成功: {file_path}")
                    
                    self.progress_display.hide()
                except Exception as e:
                    self.progress_display.hide()
                    messagebox.showerror("错误", f"导出视频失败: {e}")
            
            self.run_async(export_video())
    
    def _open_settings(self):
        """Open settings dialog"""
        settings_dialog = SettingsPanel(self)
        settings_dialog.grab_set()
    
    def _show_help(self):
        """Show help dialog"""
        help_text = """
Movie Translate 使用指南

1. 创建新项目：导入视频文件并设置翻译参数
2. 文件导入：上传视频和相关文件
3. 角色管理：识别和管理配音角色
4. 语音识别：自动识别视频中的语音
5. 翻译处理：翻译识别到的文本
6. 声音克隆：为角色生成配音
7. 视频合成：合成最终的视频文件

快捷键：
- Ctrl+N: 新建项目
- Ctrl+O: 打开项目
- Ctrl+S: 保存项目
- Ctrl+E: 导出视频

更多信息请访问：https://github.com/your-repo/movie-translate
        """
        
        messagebox.showinfo("帮助", help_text)
    
    def _update_project_display(self):
        """Update project information display"""
        if self.current_project:
            self.project_name_label.configure(text=self.current_project.get('name', '未知项目'))
            self.project_status_label.configure(text=f"状态: {self.current_project.get('status', '未知')}")
            self.save_project_btn.configure(state="normal")
            self.export_btn.configure(state="normal")
        else:
            self.project_name_label.configure(text="未创建项目")
            self.project_status_label.configure(text="状态: 就绪")
            self.save_project_btn.configure(state="disabled")
            self.export_btn.configure(state="disabled")
    
    def _navigate_to_step(self, step_index: int):
        """Navigate to specific step"""
        self.current_step = step_index
        
        # Hide all frames
        for frame in self.frames.values():
            frame.grid_remove()
        
        # Show current step frame
        step_frames = ['file_import', 'character_manager']
        if step_index < len(step_frames):
            current_frame = self.frames[step_frames[step_index]]
            current_frame.grid(row=0, column=0, sticky="nsew")
        
        # Update step navigator
        self.step_navigator.set_current_step(step_index)
        
        # Update header
        step_titles = [
            "文件导入",
            "角色管理",
            "语音识别",
            "翻译处理",
            "声音克隆",
            "视频合成"
        ]
        
        step_descriptions = [
            "导入视频文件和相关资料",
            "识别和管理配音角色",
            "自动识别视频中的语音内容",
            "翻译识别到的文本内容",
            "为角色生成克隆声音",
            "合成最终的视频文件"
        ]
        
        if step_index < len(step_titles):
            self.step_title_label.configure(text=f"步骤 {step_index + 1}: {step_titles[step_index]}")
            self.step_description_label.configure(text=step_descriptions[step_index])
    
    def set_status(self, text: str):
        """Set status bar text"""
        self.status_label.configure(text=text)
    
    def set_progress(self, value: int, maximum: int = 100):
        """Set progress bar value"""
        self.progress_bar['maximum'] = maximum
        self.progress_bar['value'] = value
    
    def show_progress(self, title: str, description: str = ""):
        """Show progress display"""
        self.progress_display.show(title, description)
    
    def update_progress(self, value: int, status: str = ""):
        """Update progress display"""
        self.progress_display.update_progress(value, status)
    
    def hide_progress(self):
        """Hide progress display"""
        self.progress_display.hide()
    
    def on_closing(self):
        """Handle application closing"""
        if self.current_project:
            result = messagebox.askyesnocancel(
                "保存项目",
                "是否保存当前项目？"
            )
            
            if result is True:  # Save
                self._save_project()
            elif result is None:  # Cancel
                return
        
        # Clean up
        if self.async_loop and self.async_loop.is_running():
            self.async_loop.call_soon_threadsafe(self.async_loop.stop)
        
        # Stop interrupt recovery
        self._stop_interrupt_recovery()
        
        # Save current state before closing
        self._save_current_state()
        
        self.destroy()
    
    def _check_recovery(self):
        """Check for recovery data on startup"""
        try:
            interrupt_recovery = get_interrupt_recovery()
            
            if interrupt_recovery.has_recovery_state():
                # Show recovery dialog
                recovery_data = show_recovery_dialog(self)
                
                if recovery_data:
                    self.load_recovery_data(recovery_data)
        except Exception as e:
            logger.error(f"Failed to check recovery: {e}")
    
    def load_recovery_data(self, recovery_data: Dict[str, Any]):
        """Load recovery data into application"""
        try:
            # Load project data
            if 'project' in recovery_data:
                self.current_project = recovery_data['project']
                self._update_project_display()
                
                # Load project data into frames
                if 'video_file' in self.current_project:
                    self.frames['file_import'].set_video_file(self.current_project['video_file'])
                
                if 'characters' in self.current_project:
                    self.frames['character_manager'].set_characters(self.current_project['characters'])
                
                if 'current_step' in self.current_project:
                    self._navigate_to_step(self.current_project['current_step'])
            
            # Load step data
            if 'steps' in recovery_data:
                for step_id, step_info in recovery_data['steps'].items():
                    step_index = int(step_id)
                    if step_index < len(self.frames):
                        frame_name = list(self.frames.keys())[step_index]
                        if hasattr(self.frames[frame_name], 'load_step_data'):
                            self.frames[frame_name].load_step_data(step_info['data'])
            
            logger.info("Recovery data loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load recovery data: {e}")
    
    def _save_current_state(self):
        """Save current application state for recovery"""
        try:
            interrupt_recovery = get_interrupt_recovery()
            
            # Save project state
            if self.current_project:
                interrupt_recovery.update_project_state(self.current_project)
            
            # Save step states
            for i, (frame_name, frame) in enumerate(self.frames.items()):
                if hasattr(frame, 'get_step_data'):
                    step_data = frame.get_step_data()
                    if step_data:
                        interrupt_recovery.update_step_state(i, step_data)
            
            logger.info("Current state saved for recovery")
            
        except Exception as e:
            logger.error(f"Failed to save current state: {e}")
    
    def create_checkpoint(self, checkpoint_name: str):
        """Create a named checkpoint"""
        try:
            # Save current state first
            self._save_current_state()
            
            # Create checkpoint
            interrupt_recovery = get_interrupt_recovery()
            interrupt_recovery.create_checkpoint(checkpoint_name)
            
            logger.info(f"Checkpoint '{checkpoint_name}' created")
            
        except Exception as e:
            logger.error(f"Failed to create checkpoint: {e}")
    
    def _start_interrupt_recovery(self):
        """Start interrupt recovery auto-save"""
        try:
            interrupt_recovery = get_interrupt_recovery()
            interrupt_recovery.start_auto_save()
            logger.info("Interrupt recovery auto-save started")
        except Exception as e:
            logger.error(f"Failed to start interrupt recovery: {e}")
    
    def _stop_interrupt_recovery(self):
        """Stop interrupt recovery auto-save"""
        try:
            interrupt_recovery = get_interrupt_recovery()
            interrupt_recovery.stop_auto_save()
            logger.info("Interrupt recovery auto-save stopped")
        except Exception as e:
            logger.error(f"Failed to stop interrupt recovery: {e}")


def main():
    """Main entry point for the application"""
    app = MovieTranslateApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()