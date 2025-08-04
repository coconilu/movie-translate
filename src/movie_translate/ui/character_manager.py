"""
Character manager frame for Movie Translate UI
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Any, Optional
import asyncio


class CharacterManagerFrame(ctk.CTkFrame):
    """Character manager frame for step 2"""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.characters = []
        self.selected_character = None
        
        self._create_ui()
    
    def _create_ui(self):
        """Create character manager UI"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        header_frame.grid_columnconfigure(1, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="角色管理",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=15)
        
        description_label = ctk.CTkLabel(
            header_frame,
            text="识别和管理视频中的配音角色",
            font=ctk.CTkFont(size=12)
        )
        description_label.grid(row=0, column=1, padx=20, pady=15, sticky="w")
        
        # Main content area
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Left panel - Character list
        left_panel = ctk.CTkFrame(content_frame)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        left_panel.grid_rowconfigure(1, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)
        
        # Character list header
        list_header = ctk.CTkFrame(left_panel)
        list_header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        list_header.grid_columnconfigure(1, weight=1)
        
        list_title = ctk.CTkLabel(
            list_header,
            text="角色列表",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        list_title.grid(row=0, column=0, padx=10, pady=10)
        
        self.character_count_label = ctk.CTkLabel(
            list_header,
            text="共 0 个角色",
            font=ctk.CTkFont(size=12)
        )
        self.character_count_label.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        
        # Character list
        self.character_list_frame = ctk.CTkScrollableFrame(left_panel, height=300)
        self.character_list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.character_list_frame.grid_columnconfigure(0, weight=1)
        
        # Character list buttons
        list_buttons = ctk.CTkFrame(left_panel)
        list_buttons.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        
        self.detect_btn = ctk.CTkButton(
            list_buttons,
            text="自动识别",
            command=self._detect_characters,
            width=100
        )
        self.detect_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.add_character_btn = ctk.CTkButton(
            list_buttons,
            text="添加角色",
            command=self._add_character,
            width=100
        )
        self.add_character_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.merge_btn = ctk.CTkButton(
            list_buttons,
            text="合并角色",
            command=self._merge_characters,
            width=100,
            state="disabled"
        )
        self.merge_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Right panel - Character details
        right_panel = ctk.CTkFrame(content_frame)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
        right_panel.grid_rowconfigure(1, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)
        
        # Character details header
        details_header = ctk.CTkFrame(right_panel)
        details_header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        details_title = ctk.CTkLabel(
            details_header,
            text="角色详情",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        details_title.grid(row=0, column=0, padx=10, pady=10)
        
        # Character details
        self.details_frame = ctk.CTkFrame(right_panel)
        self.details_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.details_frame.grid_rowconfigure(10, weight=1)
        self.details_frame.grid_columnconfigure(1, weight=1)
        
        # Character ID
        id_label = ctk.CTkLabel(
            self.details_frame,
            text="角色ID:",
            font=ctk.CTkFont(size=12)
        )
        id_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.character_id_label = ctk.CTkLabel(
            self.details_frame,
            text="未选择角色",
            font=ctk.CTkFont(size=12)
        )
        self.character_id_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        # Character name
        name_label = ctk.CTkLabel(
            self.details_frame,
            text="角色名称:",
            font=ctk.CTkFont(size=12)
        )
        name_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.character_name_entry = ctk.CTkEntry(self.details_frame)
        self.character_name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.character_name_entry.bind("<KeyRelease>", self._on_name_changed)
        
        # Language
        lang_label = ctk.CTkLabel(
            self.details_frame,
            text="语言:",
            font=ctk.CTkFont(size=12)
        )
        lang_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.language_var = tk.StringVar(value="zh")
        self.language_combo = ctk.CTkComboBox(
            self.details_frame,
            variable=self.language_var,
            values=["zh", "en", "ja", "ko", "fr", "de", "es", "ru"]
        )
        self.language_combo.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        
        # Voice sample info
        voice_label = ctk.CTkLabel(
            self.details_frame,
            text="语音样本:",
            font=ctk.CTkFont(size=12)
        )
        voice_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        
        self.voice_sample_label = ctk.CTkLabel(
            self.details_frame,
            text="0 个语音样本",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.voice_sample_label.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        
        # Voice features
        features_label = ctk.CTkLabel(
            self.details_frame,
            text="声音特征:",
            font=ctk.CTkFont(size=12)
        )
        features_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        
        self.features_frame = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        self.features_frame.grid(row=5, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        self.features_frame.grid_columnconfigure(0, weight=1)
        
        # Preview section
        preview_label = ctk.CTkLabel(
            self.details_frame,
            text="预览:",
            font=ctk.CTkFont(size=12)
        )
        preview_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")
        
        self.preview_frame = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        self.preview_frame.grid(row=7, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        self.preview_frame.grid_columnconfigure(0, weight=1)
        
        # Character actions
        actions_frame = ctk.CTkFrame(self.details_frame)
        actions_frame.grid(row=8, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        self.play_sample_btn = ctk.CTkButton(
            actions_frame,
            text="播放样本",
            command=self._play_sample,
            width=100,
            state="disabled"
        )
        self.play_sample_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.record_sample_btn = ctk.CTkButton(
            actions_frame,
            text="录制样本",
            command=self._record_sample,
            width=100,
            state="disabled"
        )
        self.record_sample_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.delete_character_btn = ctk.CTkButton(
            actions_frame,
            text="删除角色",
            command=self._delete_character,
            width=100,
            state="disabled"
        )
        self.delete_character_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Save button
        self.save_btn = ctk.CTkButton(
            actions_frame,
            text="保存修改",
            command=self._save_character,
            width=100,
            state="disabled"
        )
        self.save_btn.grid(row=0, column=3, padx=5, pady=5)
        
        # Bottom action buttons
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=20)
        
        self.analyze_btn = ctk.CTkButton(
            bottom_frame,
            text="分析角色",
            command=self._analyze_characters,
            width=120
        )
        self.analyze_btn.grid(row=0, column=0, padx=10, pady=10)
        
        self.prev_btn = ctk.CTkButton(
            bottom_frame,
            text="上一步",
            command=self._prev_step,
            width=120
        )
        self.prev_btn.grid(row=0, column=1, padx=10, pady=10)
        
        self.next_btn = ctk.CTkButton(
            bottom_frame,
            text="下一步",
            command=self._next_step,
            width=120,
            state="disabled"
        )
        self.next_btn.grid(row=0, column=2, padx=10, pady=10)
    
    def _detect_characters(self):
        """Auto-detect characters from video"""
        if not self.app.current_project or not self.app.current_project.get('video_file'):
            messagebox.showerror("错误", "请先导入视频文件")
            return
        
        async def detect():
            try:
                self.app.show_progress("正在识别角色...")
                self.app.update_progress(0, "开始识别")
                
                # TODO: Implement character detection
                # For now, add some mock characters
                self.app.update_progress(30, "分析音频特征")
                await asyncio.sleep(1)
                
                self.app.update_progress(60, "识别声音模式")
                await asyncio.sleep(1)
                
                self.app.update_progress(90, "生成角色信息")
                await asyncio.sleep(1)
                
                # Add mock characters
                mock_characters = [
                    {'id': 'char_001', 'name': '角色1', 'language': 'zh', 'samples': 5},
                    {'id': 'char_002', 'name': '角色2', 'language': 'zh', 'samples': 3},
                    {'id': 'char_003', 'name': '角色3', 'language': 'zh', 'samples': 7}
                ]
                
                for char_data in mock_characters:
                    self._add_character_to_list(char_data)
                
                self.app.update_progress(100, "识别完成")
                self.app.hide_progress()
                
                messagebox.showinfo("成功", f"识别到 {len(mock_characters)} 个角色")
                self.next_btn.configure(state="normal")
                
            except Exception as e:
                self.app.hide_progress()
                messagebox.showerror("错误", f"识别失败: {e}")
        
        self.app.run_async(detect())
    
    def _add_character(self):
        """Add new character manually"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("添加角色")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        
        # Character name
        name_label = ctk.CTkLabel(dialog, text="角色名称:")
        name_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        name_entry = ctk.CTkEntry(dialog, width=300)
        name_entry.grid(row=0, column=1, padx=20, pady=10)
        
        # Language
        lang_label = ctk.CTkLabel(dialog, text="语言:")
        lang_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        lang_var = tk.StringVar(value="zh")
        lang_combo = ctk.CTkComboBox(dialog, width=150, variable=lang_var)
        lang_combo.grid(row=1, column=1, padx=20, pady=10, sticky="w")
        lang_combo.configure(values=["zh", "en", "ja", "ko", "fr", "de", "es", "ru"])
        
        # Description
        desc_label = ctk.CTkLabel(dialog, text="描述:")
        desc_label.grid(row=2, column=0, padx=20, pady=10, sticky="nw")
        
        desc_text = ctk.CTkTextbox(dialog, width=300, height=100)
        desc_text.grid(row=2, column=1, padx=20, pady=10)
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        def add_character():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("错误", "请输入角色名称")
                return
            
            character_data = {
                'id': f'char_{len(self.characters) + 1:03d}',
                'name': name,
                'language': lang_var.get(),
                'description': desc_text.get("1.0", "end-1c"),
                'samples': 0
            }
            
            self._add_character_to_list(character_data)
            dialog.destroy()
        
        add_btn = ctk.CTkButton(button_frame, text="添加", command=add_character)
        add_btn.grid(row=0, column=0, padx=10)
        
        cancel_btn = ctk.CTkButton(button_frame, text="取消", command=dialog.destroy)
        cancel_btn.grid(row=0, column=1, padx=10)
    
    def _add_character_to_list(self, character_data: Dict[str, Any]):
        """Add character to the list"""
        if character_data not in self.characters:
            self.characters.append(character_data)
            self._update_character_list()
    
    def _update_character_list(self):
        """Update character list display"""
        # Clear existing widgets
        for widget in self.character_list_frame.winfo_children():
            widget.destroy()
        
        # Add character items
        for i, character in enumerate(self.characters):
            char_frame = ctk.CTkFrame(self.character_list_frame)
            char_frame.grid(row=i, column=0, sticky="ew", padx=5, pady=2)
            char_frame.grid_columnconfigure(1, weight=1)
            
            # Select checkbox
            select_var = tk.BooleanVar()
            select_check = ctk.CTkCheckBox(
                char_frame,
                text="",
                variable=select_var,
                command=lambda c=character, v=select_var: self._on_character_selected(c, v.get())
            )
            select_check.grid(row=0, column=0, padx=5, pady=5)
            
            # Character info
            info_frame = ctk.CTkFrame(char_frame, fg_color="transparent")
            info_frame.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            info_frame.grid_columnconfigure(0, weight=1)
            
            name_label = ctk.CTkLabel(
                info_frame,
                text=character['name'],
                font=ctk.CTkFont(size=12, weight="bold")
            )
            name_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")
            
            info_label = ctk.CTkLabel(
                info_frame,
                text=f"ID: {character['id']} | 样本: {character.get('samples', 0)}",
                font=ctk.CTkFont(size=10),
                text_color="gray"
            )
            info_label.grid(row=1, column=0, padx=5, pady=2, sticky="w")
            
            # Actions
            actions_frame = ctk.CTkFrame(char_frame, fg_color="transparent")
            actions_frame.grid(row=0, column=2, padx=5, pady=5)
            
            edit_btn = ctk.CTkButton(
                actions_frame,
                text="编辑",
                command=lambda c=character: self._edit_character(c),
                width=60,
                height=25
            )
            edit_btn.grid(row=0, column=0, padx=2, pady=2)
            
            remove_btn = ctk.CTkButton(
                actions_frame,
                text="删除",
                command=lambda c=character: self._remove_character(c),
                width=60,
                height=25
            )
            remove_btn.grid(row=0, column=1, padx=2, pady=2)
        
        # Update count
        self.character_count_label.configure(text=f"共 {len(self.characters)} 个角色")
        
        # Update button states
        self.merge_btn.configure(state="normal" if len(self.characters) > 1 else "disabled")
    
    def _on_character_selected(self, character: Dict[str, Any], selected: bool):
        """Handle character selection"""
        if selected:
            self.selected_character = character
            self._show_character_details(character)
        else:
            self.selected_character = None
            self._clear_character_details()
    
    def _show_character_details(self, character: Dict[str, Any]):
        """Show character details"""
        self.character_id_label.configure(text=character['id'])
        self.character_name_entry.configure(state="normal")
        self.character_name_entry.delete(0, "end")
        self.character_name_entry.insert(0, character['name'])
        
        self.language_var.set(character.get('language', 'zh'))
        self.voice_sample_label.configure(text=f"{character.get('samples', 0)} 个语音样本")
        
        # Enable action buttons
        self.play_sample_btn.configure(state="normal")
        self.record_sample_btn.configure(state="normal")
        self.delete_character_btn.configure(state="normal")
        self.save_btn.configure(state="normal")
        
        # Show voice features
        self._show_voice_features(character)
    
    def _clear_character_details(self):
        """Clear character details"""
        self.character_id_label.configure(text="未选择角色")
        self.character_name_entry.configure(state="disabled")
        self.character_name_entry.delete(0, "end")
        
        self.voice_sample_label.configure(text="0 个语音样本")
        
        # Disable action buttons
        self.play_sample_btn.configure(state="disabled")
        self.record_sample_btn.configure(state="disabled")
        self.delete_character_btn.configure(state="disabled")
        self.save_btn.configure(state="disabled")
    
    def _show_voice_features(self, character: Dict[str, Any]):
        """Show voice features for character"""
        # Clear existing features
        for widget in self.features_frame.winfo_children():
            widget.destroy()
        
        # Show mock features
        features = character.get('voice_features', {})
        if features:
            for i, (key, value) in enumerate(features.items()):
                feature_label = ctk.CTkLabel(
                    self.features_frame,
                    text=f"{key}: {value:.2f}",
                    font=ctk.CTkFont(size=10)
                )
                feature_label.grid(row=i, column=0, padx=5, pady=2, sticky="w")
        else:
            no_features_label = ctk.CTkLabel(
                self.features_frame,
                text="暂无声音特征数据",
                font=ctk.CTkFont(size=10),
                text_color="gray"
            )
            no_features_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")
    
    def _on_name_changed(self, event=None):
        """Handle character name change"""
        if self.selected_character and self.character_name_entry.get().strip():
            self.save_btn.configure(state="normal")
        else:
            self.save_btn.configure(state="disabled")
    
    def _save_character(self):
        """Save character changes"""
        if not self.selected_character:
            return
        
        new_name = self.character_name_entry.get().strip()
        if not new_name:
            messagebox.showerror("错误", "角色名称不能为空")
            return
        
        # Update character data
        self.selected_character['name'] = new_name
        self.selected_character['language'] = self.language_var.get()
        
        # Update list
        self._update_character_list()
        
        messagebox.showinfo("成功", "角色信息已保存")
    
    def _edit_character(self, character: Dict[str, Any]):
        """Edit character"""
        self.selected_character = character
        self._show_character_details(character)
    
    def _remove_character(self, character: Dict[str, Any]):
        """Remove character"""
        result = messagebox.askyesno("确认", f"确定要删除角色 '{character['name']}' 吗？")
        if result:
            self.characters.remove(character)
            self._update_character_list()
            if self.selected_character == character:
                self._clear_character_details()
    
    def _delete_character(self):
        """Delete selected character"""
        if self.selected_character:
            self._remove_character(self.selected_character)
    
    def _merge_characters(self):
        """Merge selected characters"""
        selected_chars = [c for c in self.characters if c.get('selected', False)]
        if len(selected_chars) < 2:
            messagebox.showwarning("警告", "请选择至少两个角色进行合并")
            return
        
        # TODO: Implement character merging
        messagebox.showinfo("提示", "角色合并功能正在开发中")
    
    def _play_sample(self):
        """Play voice sample for selected character"""
        if not self.selected_character:
            return
        
        # TODO: Implement voice sample playback
        messagebox.showinfo("提示", "语音播放功能正在开发中")
    
    def _record_sample(self):
        """Record voice sample for selected character"""
        if not self.selected_character:
            return
        
        # TODO: Implement voice recording
        messagebox.showinfo("提示", "语音录制功能正在开发中")
    
    def _analyze_characters(self):
        """Analyze characters"""
        if not self.characters:
            messagebox.showwarning("警告", "请先添加角色")
            return
        
        async def analyze():
            try:
                self.app.show_progress("正在分析角色...")
                self.app.update_progress(0, "开始分析")
                
                # TODO: Implement character analysis
                self.app.update_progress(50, "分析声音特征")
                await asyncio.sleep(1)
                
                self.app.update_progress(100, "分析完成")
                self.app.hide_progress()
                
                messagebox.showinfo("成功", "角色分析完成")
                self.next_btn.configure(state="normal")
                
            except Exception as e:
                self.app.hide_progress()
                messagebox.showerror("错误", f"分析失败: {e}")
        
        self.app.run_async(analyze())
    
    def _prev_step(self):
        """Navigate to previous step"""
        self.app._navigate_to_step(0)
    
    def _next_step(self):
        """Navigate to next step"""
        if not self.characters:
            messagebox.showwarning("警告", "请先添加角色")
            return
        
        # Save character data to project
        if self.app.current_project:
            self.app.current_project['characters'] = self.characters
        
        self.app._navigate_to_step(2)
    
    def refresh(self):
        """Refresh the frame"""
        self._update_character_list()
    
    def get_characters(self) -> List[Dict[str, Any]]:
        """Get character list"""
        return self.characters.copy()
    
    def set_characters(self, characters: List[Dict[str, Any]]):
        """Set character list from project data"""
        self.characters = characters.copy()
        self._update_character_list()