"""
Settings panel for Movie Translate UI
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional
import json


class SettingsPanel(ctk.CTkToplevel):
    """Settings dialog for Movie Translate"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("设置")
        self.geometry("800x600")
        self.transient(parent)
        self.grab_set()
        
        # Settings data
        self.settings_data = self._load_settings()
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create tabs
        self._create_general_tab()
        self._create_api_tab()
        self._create_services_tab()
        self._create_advanced_tab()
        
        # Bottom buttons
        self._create_bottom_buttons()
        
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
    
    def _create_general_tab(self):
        """Create general settings tab"""
        general_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(general_frame, text="常规")
        
        # Language settings
        lang_frame = ctk.CTkFrame(general_frame)
        lang_frame.pack(fill="x", padx=20, pady=10)
        
        lang_label = ctk.CTkLabel(
            lang_frame,
            text="界面语言",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        lang_label.pack(anchor="w", padx=10, pady=5)
        
        self.ui_lang_var = tk.StringVar(value=self.settings_data.get('ui_language', 'zh'))
        lang_combo = ctk.CTkComboBox(
            lang_frame,
            variable=self.ui_lang_var,
            values=["zh", "en"],
            width=200
        )
        lang_combo.pack(anchor="w", padx=10, pady=5)
        
        # Theme settings
        theme_frame = ctk.CTkFrame(general_frame)
        theme_frame.pack(fill="x", padx=20, pady=10)
        
        theme_label = ctk.CTkLabel(
            theme_frame,
            text="主题",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        theme_label.pack(anchor="w", padx=10, pady=5)
        
        self.theme_var = tk.StringVar(value=self.settings_data.get('theme', 'System'))
        theme_combo = ctk.CTkComboBox(
            theme_frame,
            variable=self.theme_var,
            values=["System", "Light", "Dark"],
            width=200
        )
        theme_combo.pack(anchor="w", padx=10, pady=5)
        
        # File settings
        file_frame = ctk.CTkFrame(general_frame)
        file_frame.pack(fill="x", padx=20, pady=10)
        
        file_label = ctk.CTkLabel(
            file_frame,
            text="文件设置",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        file_label.pack(anchor="w", padx=10, pady=5)
        
        # Temp directory
        temp_frame = ctk.CTkFrame(file_frame)
        temp_frame.pack(fill="x", padx=10, pady=5)
        
        temp_label = ctk.CTkLabel(temp_frame, text="临时文件目录:")
        temp_label.pack(side="left", padx=5)
        
        self.temp_dir_var = tk.StringVar(value=self.settings_data.get('temp_dir', ''))
        temp_entry = ctk.CTkEntry(temp_frame, variable=self.temp_dir_var, width=300)
        temp_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        temp_browse_btn = ctk.CTkButton(
            temp_frame,
            text="浏览",
            command=self._browse_temp_dir,
            width=60
        )
        temp_browse_btn.pack(side="left", padx=5)
        
        # Output directory
        output_frame = ctk.CTkFrame(file_frame)
        output_frame.pack(fill="x", padx=10, pady=5)
        
        output_label = ctk.CTkLabel(output_frame, text="输出文件目录:")
        output_label.pack(side="left", padx=5)
        
        self.output_dir_var = tk.StringVar(value=self.settings_data.get('output_dir', ''))
        output_entry = ctk.CTkEntry(output_frame, variable=self.output_dir_var, width=300)
        output_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        output_browse_btn = ctk.CTkButton(
            output_frame,
            text="浏览",
            command=self._browse_output_dir,
            width=60
        )
        output_browse_btn.pack(side="left", padx=5)
        
        # Auto-save
        self.auto_save_var = tk.BooleanVar(value=self.settings_data.get('auto_save', True))
        auto_save_check = ctk.CTkCheckBox(
            file_frame,
            text="自动保存项目",
            variable=self.auto_save_var
        )
        auto_save_check.pack(anchor="w", padx=10, pady=5)
    
    def _create_api_tab(self):
        """Create API settings tab"""
        api_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(api_frame, text="API设置")
        
        # API Keys section
        keys_frame = ctk.CTkFrame(api_frame)
        keys_frame.pack(fill="x", padx=20, pady=10)
        
        keys_label = ctk.CTkLabel(
            keys_frame,
            text="API密钥",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        keys_label.pack(anchor="w", padx=10, pady=5)
        
        # DeepSeek API
        deepseek_frame = ctk.CTkFrame(keys_frame)
        deepseek_frame.pack(fill="x", padx=10, pady=5)
        
        deepseek_label = ctk.CTkLabel(deepseek_frame, text="DeepSeek API Key:")
        deepseek_label.pack(side="left", padx=5)
        
        self.deepseek_key_var = tk.StringVar(value=self.settings_data.get('deepseek_api_key', ''))
        deepseek_entry = ctk.CTkEntry(
            deepseek_frame,
            variable=self.deepseek_key_var,
            width=400,
            show="*"
        )
        deepseek_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # GLM API
        glm_frame = ctk.CTkFrame(keys_frame)
        glm_frame.pack(fill="x", padx=10, pady=5)
        
        glm_label = ctk.CTkLabel(glm_frame, text="GLM API Key:")
        glm_label.pack(side="left", padx=5)
        
        self.glm_key_var = tk.StringVar(value=self.settings_data.get('glm_api_key', ''))
        glm_entry = ctk.CTkEntry(
            glm_frame,
            variable=self.glm_key_var,
            width=400,
            show="*"
        )
        glm_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Baidu API
        baidu_frame = ctk.CTkFrame(keys_frame)
        baidu_frame.pack(fill="x", padx=10, pady=5)
        
        baidu_label = ctk.CTkLabel(baidu_frame, text="百度 App ID:")
        baidu_label.pack(side="left", padx=5)
        
        self.baidu_app_id_var = tk.StringVar(value=self.settings_data.get('baidu_app_id', ''))
        baidu_entry = ctk.CTkEntry(
            baidu_frame,
            variable=self.baidu_app_id_var,
            width=200
        )
        baidu_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        baidu_api_frame = ctk.CTkFrame(keys_frame)
        baidu_api_frame.pack(fill="x", padx=10, pady=5)
        
        baidu_api_label = ctk.CTkLabel(baidu_api_frame, text="百度 API Key:")
        baidu_api_label.pack(side="left", padx=5)
        
        self.baidu_api_key_var = tk.StringVar(value=self.settings_data.get('baidu_api_key', ''))
        baidu_api_entry = ctk.CTkEntry(
            baidu_api_frame,
            variable=self.baidu_api_key_var,
            width=200,
            show="*"
        )
        baidu_api_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        baidu_secret_frame = ctk.CTkFrame(keys_frame)
        baidu_secret_frame.pack(fill="x", padx=10, pady=5)
        
        baidu_secret_label = ctk.CTkLabel(baidu_secret_frame, text="百度 Secret Key:")
        baidu_secret_label.pack(side="left", padx=5)
        
        self.baidu_secret_key_var = tk.StringVar(value=self.settings_data.get('baidu_secret_key', ''))
        baidu_secret_entry = ctk.CTkEntry(
            baidu_secret_frame,
            variable=self.baidu_secret_key_var,
            width=200,
            show="*"
        )
        baidu_secret_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # MiniMax API
        minimax_frame = ctk.CTkFrame(keys_frame)
        minimax_frame.pack(fill="x", padx=10, pady=5)
        
        minimax_label = ctk.CTkLabel(minimax_frame, text="MiniMax API Key:")
        minimax_label.pack(side="left", padx=5)
        
        self.minimax_key_var = tk.StringVar(value=self.settings_data.get('minimax_api_key', ''))
        minimax_entry = ctk.CTkEntry(
            minimax_frame,
            variable=self.minimax_key_var,
            width=400,
            show="*"
        )
        minimax_entry.pack(side="left", padx=5, fill="x", expand=True)
    
    def _create_services_tab(self):
        """Create services settings tab"""
        services_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(services_frame, text="服务设置")
        
        # Translation service
        trans_frame = ctk.CTkFrame(services_frame)
        trans_frame.pack(fill="x", padx=20, pady=10)
        
        trans_label = ctk.CTkLabel(
            trans_frame,
            text="翻译服务",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        trans_label.pack(anchor="w", padx=10, pady=5)
        
        self.trans_service_var = tk.StringVar(value=self.settings_data.get('translation_service', 'deepseek'))
        trans_combo = ctk.CTkComboBox(
            trans_frame,
            variable=self.trans_service_var,
            values=["deepseek", "glm"],
            width=200
        )
        trans_combo.pack(anchor="w", padx=10, pady=5)
        
        # Speech recognition service
        speech_frame = ctk.CTkFrame(services_frame)
        speech_frame.pack(fill="x", padx=20, pady=10)
        
        speech_label = ctk.CTkLabel(
            speech_frame,
            text="语音识别服务",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        speech_label.pack(anchor="w", padx=10, pady=5)
        
        self.speech_service_var = tk.StringVar(value=self.settings_data.get('speech_service', 'baidu'))
        speech_combo = ctk.CTkComboBox(
            speech_frame,
            variable=self.speech_service_var,
            values=["baidu", "sensevoice"],
            width=200
        )
        speech_combo.pack(anchor="w", padx=10, pady=5)
        
        # Voice cloning service
        voice_frame = ctk.CTkFrame(services_frame)
        voice_frame.pack(fill="x", padx=20, pady=10)
        
        voice_label = ctk.CTkLabel(
            voice_frame,
            text="声音克隆服务",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        voice_label.pack(anchor="w", padx=10, pady=5)
        
        self.voice_service_var = tk.StringVar(value=self.settings_data.get('voice_service', 'f5_tts'))
        voice_combo = ctk.CTkComboBox(
            voice_frame,
            variable=self.voice_service_var,
            values=["f5_tts", "minimax"],
            width=200
        )
        voice_combo.pack(anchor="w", padx=10, pady=5)
        
        # Processing settings
        proc_frame = ctk.CTkFrame(services_frame)
        proc_frame.pack(fill="x", padx=20, pady=10)
        
        proc_label = ctk.CTkLabel(
            proc_frame,
            text="处理设置",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        proc_label.pack(anchor="w", padx=10, pady=5)
        
        # Batch size
        batch_frame = ctk.CTkFrame(proc_frame)
        batch_frame.pack(fill="x", padx=10, pady=5)
        
        batch_label = ctk.CTkLabel(batch_frame, text="批处理大小:")
        batch_label.pack(side="left", padx=5)
        
        self.batch_size_var = tk.IntVar(value=self.settings_data.get('batch_size', 5))
        batch_spin = ctk.CTkSpinBox(
            batch_frame,
            variable=self.batch_size_var,
            width=100,
            from_value=1,
            to=20
        )
        batch_spin.pack(side="left", padx=5)
        
        # Max workers
        workers_frame = ctk.CTkFrame(proc_frame)
        workers_frame.pack(fill="x", padx=10, pady=5)
        
        workers_label = ctk.CTkLabel(workers_frame, text="最大并发数:")
        workers_label.pack(side="left", padx=5)
        
        self.max_workers_var = tk.IntVar(value=self.settings_data.get('max_workers', 4))
        workers_spin = ctk.CTkSpinBox(
            workers_frame,
            variable=self.max_workers_var,
            width=100,
            from_value=1,
            to=16
        )
        workers_spin.pack(side="left", padx=5)
    
    def _create_advanced_tab(self):
        """Create advanced settings tab"""
        advanced_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(advanced_frame, text="高级")
        
        # Performance settings
        perf_frame = ctk.CTkFrame(advanced_frame)
        perf_frame.pack(fill="x", padx=20, pady=10)
        
        perf_label = ctk.CTkLabel(
            perf_frame,
            text="性能设置",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        perf_label.pack(anchor="w", padx=10, pady=5)
        
        # Cache settings
        self.cache_var = tk.BooleanVar(value=self.settings_data.get('enable_cache', True))
        cache_check = ctk.CTkCheckBox(
            perf_frame,
            text="启用缓存",
            variable=self.cache_var
        )
        cache_check.pack(anchor="w", padx=10, pady=5)
        
        # GPU acceleration
        self.gpu_var = tk.BooleanVar(value=self.settings_data.get('enable_gpu', False))
        gpu_check = ctk.CTkCheckBox(
            perf_frame,
            text="启用GPU加速",
            variable=self.gpu_var
        )
        gpu_check.pack(anchor="w", padx=10, pady=5)
        
        # Logging settings
        log_frame = ctk.CTkFrame(advanced_frame)
        log_frame.pack(fill="x", padx=20, pady=10)
        
        log_label = ctk.CTkLabel(
            log_frame,
            text="日志设置",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        log_label.pack(anchor="w", padx=10, pady=5)
        
        # Log level
        level_frame = ctk.CTkFrame(log_frame)
        level_frame.pack(fill="x", padx=10, pady=5)
        
        level_label = ctk.CTkLabel(level_frame, text="日志级别:")
        level_label.pack(side="left", padx=5)
        
        self.log_level_var = tk.StringVar(value=self.settings_data.get('log_level', 'INFO'))
        level_combo = ctk.CTkComboBox(
            level_frame,
            variable=self.log_level_var,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            width=150
        )
        level_combo.pack(side="left", padx=5)
        
        # Debug mode
        self.debug_var = tk.BooleanVar(value=self.settings_data.get('debug_mode', False))
        debug_check = ctk.CTkCheckBox(
            log_frame,
            text="调试模式",
            variable=self.debug_var
        )
        debug_check.pack(anchor="w", padx=10, pady=5)
        
        # Reset button
        reset_btn = ctk.CTkButton(
            advanced_frame,
            text="重置设置",
            command=self._reset_settings,
            width=120
        )
        reset_btn.pack(anchor="w", padx=10, pady=10)
    
    def _create_bottom_buttons(self):
        """Create bottom action buttons"""
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        # Test connection button
        test_btn = ctk.CTkButton(
            button_frame,
            text="测试连接",
            command=self._test_connection,
            width=120
        )
        test_btn.pack(side="left", padx=5)
        
        # Apply button
        apply_btn = ctk.CTkButton(
            button_frame,
            text="应用",
            command=self._apply_settings,
            width=120
        )
        apply_btn.pack(side="right", padx=5)
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="取消",
            command=self.destroy,
            width=120
        )
        cancel_btn.pack(side="right", padx=5)
    
    def _browse_temp_dir(self):
        """Browse for temp directory"""
        from tkinter import filedialog
        directory = filedialog.askdirectory(title="选择临时文件目录")
        if directory:
            self.temp_dir_var.set(directory)
    
    def _browse_output_dir(self):
        """Browse for output directory"""
        from tkinter import filedialog
        directory = filedialog.askdirectory(title="选择输出文件目录")
        if directory:
            self.output_dir_var.set(directory)
    
    def _test_connection(self):
        """Test API connections"""
        # Mock test - in real implementation, test actual APIs
        messagebox.showinfo("连接测试", "API连接测试功能正在开发中")
    
    def _apply_settings(self):
        """Apply settings and save"""
        # Collect settings
        new_settings = {
            'ui_language': self.ui_lang_var.get(),
            'theme': self.theme_var.get(),
            'temp_dir': self.temp_dir_var.get(),
            'output_dir': self.output_dir_var.get(),
            'auto_save': self.auto_save_var.get(),
            'deepseek_api_key': self.deepseek_key_var.get(),
            'glm_api_key': self.glm_key_var.get(),
            'baidu_app_id': self.baidu_app_id_var.get(),
            'baidu_api_key': self.baidu_api_key_var.get(),
            'baidu_secret_key': self.baidu_secret_key_var.get(),
            'minimax_api_key': self.minimax_key_var.get(),
            'translation_service': self.trans_service_var.get(),
            'speech_service': self.speech_service_var.get(),
            'voice_service': self.voice_service_var.get(),
            'batch_size': self.batch_size_var.get(),
            'max_workers': self.max_workers_var.get(),
            'enable_cache': self.cache_var.get(),
            'enable_gpu': self.gpu_var.get(),
            'log_level': self.log_level_var.get(),
            'debug_mode': self.debug_var.get()
        }
        
        # Save settings
        self._save_settings(new_settings)
        
        # Apply theme
        ctk.set_appearance_mode(self.theme_var.get())
        
        messagebox.showinfo("成功", "设置已保存")
        self.destroy()
    
    def _reset_settings(self):
        """Reset settings to defaults"""
        result = messagebox.askyesno("确认", "确定要重置所有设置吗？")
        if result:
            self.settings_data = self._get_default_settings()
            self._load_settings_to_ui()
            messagebox.showinfo("成功", "设置已重置")
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file or return defaults"""
        try:
            settings_file = Path("settings.json")
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        
        return self._get_default_settings()
    
    def _save_settings(self, settings: Dict[str, Any]):
        """Save settings to file"""
        try:
            with open("settings.json", 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败: {e}")
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default settings"""
        return {
            'ui_language': 'zh',
            'theme': 'System',
            'temp_dir': '',
            'output_dir': '',
            'auto_save': True,
            'deepseek_api_key': '',
            'glm_api_key': '',
            'baidu_app_id': '',
            'baidu_api_key': '',
            'baidu_secret_key': '',
            'minimax_api_key': '',
            'translation_service': 'deepseek',
            'speech_service': 'baidu',
            'voice_service': 'f5_tts',
            'batch_size': 5,
            'max_workers': 4,
            'enable_cache': True,
            'enable_gpu': False,
            'log_level': 'INFO',
            'debug_mode': False
        }
    
    def _load_settings_to_ui(self):
        """Load settings data to UI components"""
        self.ui_lang_var.set(self.settings_data.get('ui_language', 'zh'))
        self.theme_var.set(self.settings_data.get('theme', 'System'))
        self.temp_dir_var.set(self.settings_data.get('temp_dir', ''))
        self.output_dir_var.set(self.settings_data.get('output_dir', ''))
        self.auto_save_var.set(self.settings_data.get('auto_save', True))
        self.deepseek_key_var.set(self.settings_data.get('deepseek_api_key', ''))
        self.glm_key_var.set(self.settings_data.get('glm_api_key', ''))
        self.baidu_app_id_var.set(self.settings_data.get('baidu_app_id', ''))
        self.baidu_api_key_var.set(self.settings_data.get('baidu_api_key', ''))
        self.baidu_secret_key_var.set(self.settings_data.get('baidu_secret_key', ''))
        self.minimax_key_var.set(self.settings_data.get('minimax_api_key', ''))
        self.trans_service_var.set(self.settings_data.get('translation_service', 'deepseek'))
        self.speech_service_var.set(self.settings_data.get('speech_service', 'baidu'))
        self.voice_service_var.set(self.settings_data.get('voice_service', 'f5_tts'))
        self.batch_size_var.set(self.settings_data.get('batch_size', 5))
        self.max_workers_var.set(self.settings_data.get('max_workers', 4))
        self.cache_var.set(self.settings_data.get('enable_cache', True))
        self.gpu_var.set(self.settings_data.get('enable_gpu', False))
        self.log_level_var.set(self.settings_data.get('log_level', 'INFO'))
        self.debug_var.set(self.settings_data.get('debug_mode', False))