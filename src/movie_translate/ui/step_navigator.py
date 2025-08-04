"""
Step navigator component for Movie Translate UI
"""

import customtkinter as ctk
from typing import List, Dict, Any, Callable, Optional


class StepNavigator(ctk.CTkFrame):
    """Step navigation component"""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.current_step = 0
        self.step_buttons = []
        self.step_labels = []
        
        # Define steps
        self.steps = [
            {
                'id': 'file_import',
                'name': '文件导入',
                'description': '导入视频文件',
                'icon': '📁'
            },
            {
                'id': 'character_manager',
                'name': '角色管理',
                'description': '管理配音角色',
                'icon': '👥'
            },
            {
                'id': 'speech_recognition',
                'name': '语音识别',
                'description': '识别语音内容',
                'icon': '🎤'
            },
            {
                'id': 'translation',
                'name': '翻译处理',
                'description': '翻译文本内容',
                'icon': '🌐'
            },
            {
                'id': 'voice_cloning',
                'name': '声音克隆',
                'description': '生成配音声音',
                'icon': '🎭'
            },
            {
                'id': 'video_synthesis',
                'name': '视频合成',
                'description': '合成最终视频',
                'icon': '🎬'
            }
        ]
        
        self._create_ui()
    
    def _create_ui(self):
        """Create step navigator UI"""
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="处理步骤",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=10, pady=(10, 20))
        
        # Create step items
        for i, step in enumerate(self.steps):
            self._create_step_item(i, step)
    
    def _create_step_item(self, index: int, step: Dict[str, Any]):
        """Create individual step item"""
        # Step frame
        step_frame = ctk.CTkFrame(self)
        step_frame.grid(row=index + 1, column=0, padx=5, pady=2, sticky="ew")
        step_frame.grid_columnconfigure(1, weight=1)
        
        # Step button
        btn = ctk.CTkButton(
            step_frame,
            text=step['icon'],
            width=40,
            height=40,
            font=ctk.CTkFont(size=16),
            command=lambda idx=index: self._on_step_click(idx)
        )
        btn.grid(row=0, column=0, padx=5, pady=5)
        
        # Step info
        info_frame = ctk.CTkFrame(step_frame, fg_color="transparent")
        info_frame.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        info_frame.grid_columnconfigure(0, weight=1)
        
        # Step name
        name_label = ctk.CTkLabel(
            info_frame,
            text=step['name'],
            font=ctk.CTkFont(size=12, weight="bold")
        )
        name_label.grid(row=0, column=0, sticky="w")
        
        # Step description
        desc_label = ctk.CTkLabel(
            info_frame,
            text=step['description'],
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        desc_label.grid(row=1, column=0, sticky="w")
        
        # Status indicator
        status_label = ctk.CTkLabel(
            step_frame,
            text="○",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        status_label.grid(row=0, column=2, padx=5, pady=5)
        
        # Store references
        self.step_buttons.append(btn)
        self.step_labels.append({
            'name': name_label,
            'description': desc_label,
            'status': status_label
        })
        
        # Set initial state
        self._update_step_state(index, 'pending')
    
    def _on_step_click(self, step_index: int):
        """Handle step button click"""
        if step_index <= self.current_step:
            self.app._navigate_to_step(step_index)
    
    def _update_step_state(self, step_index: int, state: str):
        """Update step visual state"""
        if step_index >= len(self.step_labels):
            return
        
        label_info = self.step_labels[step_index]
        button = self.step_buttons[step_index]
        
        if state == 'completed':
            # Completed step
            button.configure(fg_color="green", hover_color="darkgreen")
            label_info['status'].configure(text="✓", text_color="green")
            label_info['name'].configure(text_color="green")
        elif state == 'current':
            # Current step
            button.configure(fg_color="blue", hover_color="darkblue")
            label_info['status'].configure(text="●", text_color="blue")
            label_info['name'].configure(text_color="blue")
        elif state == 'pending':
            # Pending step
            button.configure(fg_color="gray", hover_color="darkgray", state="disabled")
            label_info['status'].configure(text="○", text_color="gray")
            label_info['name'].configure(text_color="gray")
        elif state == 'error':
            # Error step
            button.configure(fg_color="red", hover_color="darkred")
            label_info['status'].configure(text="✗", text_color="red")
            label_info['name'].configure(text_color="red")
        elif state == 'available':
            # Available step (can be clicked)
            button.configure(fg_color="lightblue", hover_color="blue", state="normal")
            label_info['status'].configure(text="○", text_color="lightblue")
            label_info['name'].configure(text_color="black")
    
    def set_current_step(self, step_index: int):
        """Set current step and update UI"""
        if step_index < 0 or step_index >= len(self.steps):
            return
        
        self.current_step = step_index
        
        # Update all step states
        for i in range(len(self.steps)):
            if i < step_index:
                self._update_step_state(i, 'completed')
            elif i == step_index:
                self._update_step_state(i, 'current')
            elif i == step_index + 1:
                self._update_step_state(i, 'available')
            else:
                self._update_step_state(i, 'pending')
    
    def set_step_error(self, step_index: int):
        """Mark step as having error"""
        if step_index < len(self.step_labels):
            self._update_step_state(step_index, 'error')
    
    def set_step_completed(self, step_index: int):
        """Mark step as completed"""
        if step_index < len(self.step_labels):
            self._update_step_state(step_index, 'completed')
    
    def enable_step(self, step_index: int):
        """Enable a step for navigation"""
        if step_index < len(self.step_labels):
            self._update_step_state(step_index, 'available')
    
    def disable_step(self, step_index: int):
        """Disable a step"""
        if step_index < len(self.step_labels):
            self._update_step_state(step_index, 'pending')
    
    def get_step_info(self, step_index: int) -> Optional[Dict[str, Any]]:
        """Get step information"""
        if 0 <= step_index < len(self.steps):
            return self.steps[step_index]
        return None
    
    def get_current_step_id(self) -> str:
        """Get current step ID"""
        if 0 <= self.current_step < len(self.steps):
            return self.steps[self.current_step]['id']
        return ""
    
    def reset_all_steps(self):
        """Reset all steps to pending state"""
        self.current_step = 0
        for i in range(len(self.steps)):
            self._update_step_state(i, 'pending')
        self._update_step_state(0, 'current')
    
    def update_step_progress(self, step_index: int, progress: float):
        """Update step progress (0.0 to 1.0)"""
        if step_index < len(self.step_labels):
            # Update description with progress
            step = self.steps[step_index]
            progress_text = f"{step['description']} ({progress:.0%})"
            self.step_labels[step_index]['description'].configure(text=progress_text)
    
    def set_step_description(self, step_index: int, description: str):
        """Set custom description for a step"""
        if step_index < len(self.step_labels):
            self.step_labels[step_index]['description'].configure(text=description)
    
    def highlight_step(self, step_index: int):
        """Highlight a step temporarily"""
        if step_index < len(self.step_buttons):
            button = self.step_buttons[step_index]
            
            # Flash the button
            original_color = button.cget("fg_color")
            button.configure(fg_color="yellow")
            self.after(500, lambda: button.configure(fg_color=original_color))
    
    def get_next_step(self) -> Optional[int]:
        """Get next available step"""
        if self.current_step < len(self.steps) - 1:
            return self.current_step + 1
        return None
    
    def get_previous_step(self) -> Optional[int]:
        """Get previous available step"""
        if self.current_step > 0:
            return self.current_step - 1
        return None
    
    def can_navigate_to_step(self, step_index: int) -> bool:
        """Check if navigation to step is allowed"""
        return step_index <= self.current_step + 1 and step_index >= 0
    
    def set_step_callback(self, callback: Callable[[int], None]):
        """Set callback for step navigation"""
        self.step_callback = callback
    
    def refresh(self):
        """Refresh the navigator display"""
        self.set_current_step(self.current_step)