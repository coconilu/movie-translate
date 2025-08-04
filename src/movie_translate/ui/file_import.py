"""
File import frame for Movie Translate UI
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Optional, Dict, Any, List
import asyncio


class FileImportFrame(ctk.CTkFrame):
    """File import frame for step 1"""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.video_file = None
        self.subtitle_file = None
        self.audio_files = []
        
        self._create_ui()
    
    def _create_ui(self):
        """Create file import UI"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        header_frame.grid_columnconfigure(1, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="文件导入",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=15)
        
        description_label = ctk.CTkLabel(
            header_frame,
            text="导入视频文件和相关资料，支持拖拽上传",
            font=ctk.CTkFont(size=12)
        )
        description_label.grid(row=0, column=1, padx=20, pady=15, sticky="w")
        
        # Main content area
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        content_frame.grid_rowconfigure(3, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Video file section
        video_frame = ctk.CTkFrame(content_frame)
        video_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        video_frame.grid_columnconfigure(1, weight=1)
        
        video_label = ctk.CTkLabel(
            video_frame,
            text="🎬 视频文件",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        video_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.video_path_label = ctk.CTkLabel(
            video_frame,
            text="未选择视频文件",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.video_path_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        self.video_browse_btn = ctk.CTkButton(
            video_frame,
            text="浏览",
            command=self._browse_video,
            width=80
        )
        self.video_browse_btn.grid(row=0, column=2, padx=10, pady=10)
        
        # Video info
        self.video_info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.video_info_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.video_info_frame.grid_columnconfigure(0, weight=1)
        
        # Subtitle file section
        subtitle_frame = ctk.CTkFrame(content_frame)
        subtitle_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        subtitle_frame.grid_columnconfigure(1, weight=1)
        
        subtitle_label = ctk.CTkLabel(
            subtitle_frame,
            text="📝 字幕文件 (可选)",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        subtitle_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.subtitle_path_label = ctk.CTkLabel(
            subtitle_frame,
            text="未选择字幕文件",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.subtitle_path_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        self.subtitle_browse_btn = ctk.CTkButton(
            subtitle_frame,
            text="浏览",
            command=self._browse_subtitle,
            width=80
        )
        self.subtitle_browse_btn.grid(row=0, column=2, padx=10, pady=10)
        
        self.subtitle_remove_btn = ctk.CTkButton(
            subtitle_frame,
            text="移除",
            command=self._remove_subtitle,
            width=80,
            state="disabled"
        )
        self.subtitle_remove_btn.grid(row=0, column=3, padx=10, pady=10)
        
        # Audio files section
        audio_frame = ctk.CTkFrame(content_frame)
        audio_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        audio_frame.grid_rowconfigure(1, weight=1)
        audio_frame.grid_columnconfigure(0, weight=1)
        
        audio_header_frame = ctk.CTkFrame(audio_frame, fg_color="transparent")
        audio_header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        audio_header_frame.grid_columnconfigure(1, weight=1)
        
        audio_label = ctk.CTkLabel(
            audio_header_frame,
            text="🎵 音频文件 (可选)",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        audio_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.audio_count_label = ctk.CTkLabel(
            audio_header_frame,
            text="已添加 0 个音频文件",
            font=ctk.CTkFont(size=12)
        )
        self.audio_count_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        self.audio_add_btn = ctk.CTkButton(
            audio_header_frame,
            text="添加音频",
            command=self._add_audio,
            width=80
        )
        self.audio_add_btn.grid(row=0, column=2, padx=10, pady=10)
        
        self.audio_clear_btn = ctk.CTkButton(
            audio_header_frame,
            text="清空",
            command=self._clear_audio,
            width=80,
            state="disabled"
        )
        self.audio_clear_btn.grid(row=0, column=3, padx=10, pady=10)
        
        # Audio files list
        self.audio_list_frame = ctk.CTkScrollableFrame(audio_frame, height=150)
        self.audio_list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.audio_list_frame.grid_columnconfigure(0, weight=1)
        
        # Import settings
        settings_frame = ctk.CTkFrame(content_frame)
        settings_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=10)
        settings_frame.grid_columnconfigure(1, weight=1)
        
        # Target language
        lang_label = ctk.CTkLabel(
            settings_frame,
            text="目标语言:",
            font=ctk.CTkFont(size=12)
        )
        lang_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.target_lang_var = tk.StringVar(value="zh")
        self.lang_combo = ctk.CTkComboBox(
            settings_frame,
            width=150,
            variable=self.target_lang_var,
            values=["zh", "en", "ja", "ko", "fr", "de", "es", "ru"]
        )
        self.lang_combo.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Auto-detect language
        self.auto_detect_var = tk.BooleanVar(value=True)
        self.auto_detect_check = ctk.CTkCheckBox(
            settings_frame,
            text="自动检测源语言",
            variable=self.auto_detect_var
        )
        self.auto_detect_check.grid(row=0, column=2, padx=10, pady=10)
        
        # Action buttons
        action_frame = ctk.CTkFrame(self)
        action_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=20)
        
        self.analyze_btn = ctk.CTkButton(
            action_frame,
            text="分析文件",
            command=self._analyze_files,
            width=120,
            state="disabled"
        )
        self.analyze_btn.grid(row=0, column=0, padx=10, pady=10)
        
        self.next_btn = ctk.CTkButton(
            action_frame,
            text="下一步",
            command=self._next_step,
            width=120,
            state="disabled"
        )
        self.next_btn.grid(row=0, column=1, padx=10, pady=10)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            action_frame,
            mode='determinate',
            length=300
        )
        self.progress_bar.grid(row=0, column=2, padx=10, pady=10)
        self.progress_bar['value'] = 0
        
        # Configure drag and drop
        self._setup_drag_drop()
    
    def _setup_drag_drop(self):
        """Setup drag and drop functionality"""
        # This is a basic implementation
        # For full drag and drop, you might need additional libraries
        self.bind("<Button-1>", self._on_drop_enter)
        self.bind("<B1-Motion>", self._on_drop_motion)
        self.bind("<ButtonRelease-1>", self._on_drop_release)
    
    def _on_drop_enter(self, event):
        """Handle drag enter"""
        self.configure(fg_color=("gray90", "gray20"))
    
    def _on_drop_motion(self, event):
        """Handle drag motion"""
        pass
    
    def _on_drop_release(self, event):
        """Handle drop release"""
        self.configure(fg_color=("gray95", "gray10"))
        # In a real implementation, you would handle file drops here
    
    def _browse_video(self):
        """Browse for video file"""
        file_path = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=[
                ("视频文件", "*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            self._set_video_file(file_path)
    
    def _browse_subtitle(self):
        """Browse for subtitle file"""
        file_path = filedialog.askopenfilename(
            title="选择字幕文件",
            filetypes=[
                ("字幕文件", "*.srt *.ass *.ssa *.sub"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            self._set_subtitle_file(file_path)
    
    def _add_audio(self):
        """Add audio file"""
        file_paths = filedialog.askopenfilenames(
            title="选择音频文件",
            filetypes=[
                ("音频文件", "*.wav *.mp3 *.flac *.aac *.ogg"),
                ("所有文件", "*.*")
            ]
        )
        
        for file_path in file_paths:
            self._add_audio_file(file_path)
    
    def _set_video_file(self, file_path: str):
        """Set video file and update UI"""
        self.video_file = Path(file_path)
        self.video_path_label.configure(
            text=self.video_file.name,
            text_color="black"
        )
        
        # Show video info
        self._show_video_info()
        
        # Enable analyze button
        self.analyze_btn.configure(state="normal")
        
        # Check if we can proceed
        self._check_can_proceed()
    
    def _set_subtitle_file(self, file_path: str):
        """Set subtitle file and update UI"""
        self.subtitle_file = Path(file_path)
        self.subtitle_path_label.configure(
            text=self.subtitle_file.name,
            text_color="black"
        )
        self.subtitle_remove_btn.configure(state="normal")
    
    def _remove_subtitle(self):
        """Remove subtitle file"""
        self.subtitle_file = None
        self.subtitle_path_label.configure(
            text="未选择字幕文件",
            text_color="gray"
        )
        self.subtitle_remove_btn.configure(state="disabled")
    
    def _add_audio_file(self, file_path: str):
        """Add audio file to list"""
        audio_path = Path(file_path)
        if audio_path not in self.audio_files:
            self.audio_files.append(audio_path)
            self._update_audio_list()
    
    def _remove_audio_file(self, audio_path: Path):
        """Remove audio file from list"""
        if audio_path in self.audio_files:
            self.audio_files.remove(audio_path)
            self._update_audio_list()
    
    def _clear_audio(self):
        """Clear all audio files"""
        self.audio_files.clear()
        self._update_audio_list()
    
    def _update_audio_list(self):
        """Update audio files list display"""
        # Clear existing widgets
        for widget in self.audio_list_frame.winfo_children():
            widget.destroy()
        
        # Add audio files
        for i, audio_file in enumerate(self.audio_files):
            audio_frame = ctk.CTkFrame(self.audio_list_frame)
            audio_frame.grid(row=i, column=0, sticky="ew", padx=5, pady=2)
            audio_frame.grid_columnconfigure(0, weight=1)
            
            # Audio file name
            name_label = ctk.CTkLabel(
                audio_frame,
                text=audio_file.name,
                font=ctk.CTkFont(size=11)
            )
            name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            
            # Remove button
            remove_btn = ctk.CTkButton(
                audio_frame,
                text="移除",
                command=lambda f=audio_file: self._remove_audio_file(f),
                width=60,
                height=25
            )
            remove_btn.grid(row=0, column=1, padx=5, pady=5)
        
        # Update count
        self.audio_count_label.configure(text=f"已添加 {len(self.audio_files)} 个音频文件")
        
        # Update clear button state
        self.audio_clear_btn.configure(state="normal" if self.audio_files else "disabled")
    
    def _show_video_info(self):
        """Show video file information"""
        if not self.video_file:
            return
        
        # Clear existing info
        for widget in self.video_info_frame.winfo_children():
            widget.destroy()
        
        # Show basic file info
        file_size = self.video_file.stat().st_size / (1024 * 1024)  # MB
        
        info_text = f"文件大小: {file_size:.1f} MB"
        
        info_label = ctk.CTkLabel(
            self.video_info_frame,
            text=info_text,
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        info_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    
    def _check_can_proceed(self):
        """Check if we can proceed to next step"""
        if self.video_file:
            self.next_btn.configure(state="normal")
        else:
            self.next_btn.configure(state="disabled")
    
    def _analyze_files(self):
        """Analyze imported files"""
        if not self.video_file:
            messagebox.showerror("错误", "请先选择视频文件")
            return
        
        async def analyze():
            try:
                self.app.show_progress("正在分析文件...")
                self.app.update_progress(0, "开始分析")
                
                # Analyze video file
                self.app.update_progress(20, "分析视频文件")
                # TODO: Implement video analysis
                
                # Analyze subtitle file if present
                if self.subtitle_file:
                    self.app.update_progress(40, "分析字幕文件")
                    # TODO: Implement subtitle analysis
                
                # Analyze audio files if present
                if self.audio_files:
                    self.app.update_progress(60, "分析音频文件")
                    # TODO: Implement audio analysis
                
                # Final analysis
                self.app.update_progress(80, "完成分析")
                # TODO: Implement final analysis
                
                self.app.update_progress(100, "分析完成")
                self.app.hide_progress()
                
                messagebox.showinfo("成功", "文件分析完成")
                
                # Enable next step
                self.next_btn.configure(state="normal")
                
            except Exception as e:
                self.app.hide_progress()
                messagebox.showerror("错误", f"分析失败: {e}")
        
        self.app.run_async(analyze())
    
    def _next_step(self):
        """Navigate to next step"""
        if not self.video_file:
            messagebox.showerror("错误", "请先选择视频文件")
            return
        
        # Save file information to project
        if self.app.current_project:
            self.app.current_project['video_file'] = str(self.video_file)
            if self.subtitle_file:
                self.app.current_project['subtitle_file'] = str(self.subtitle_file)
            if self.audio_files:
                self.app.current_project['audio_files'] = [str(f) for f in self.audio_files]
            self.app.current_project['target_language'] = self.target_lang_var.get()
            self.app.current_project['auto_detect_language'] = self.auto_detect_var.get()
        
        # Navigate to next step
        self.app._navigate_to_step(1)
    
    def refresh(self):
        """Refresh the frame"""
        self._check_can_proceed()
    
    def get_imported_files(self) -> Dict[str, Any]:
        """Get imported files information"""
        return {
            'video_file': str(self.video_file) if self.video_file else None,
            'subtitle_file': str(self.subtitle_file) if self.subtitle_file else None,
            'audio_files': [str(f) for f in self.audio_files],
            'target_language': self.target_lang_var.get(),
            'auto_detect_language': self.auto_detect_var.get()
        }
    
    def set_imported_files(self, files: Dict[str, Any]):
        """Set imported files from project data"""
        if files.get('video_file'):
            self._set_video_file(files['video_file'])
        
        if files.get('subtitle_file'):
            self._set_subtitle_file(files['subtitle_file'])
        
        if files.get('audio_files'):
            for audio_file in files['audio_files']:
                self._add_audio_file(audio_file)
        
        if files.get('target_language'):
            self.target_lang_var.set(files['target_language'])
        
        if files.get('auto_detect_language') is not None:
            self.auto_detect_var.set(files['auto_detect_language'])