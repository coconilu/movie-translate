# 技术方案 - 电影翻译系统

## 1. 系统架构设计

### 1.1 整体架构 - Python全栈桌面应用
```
┌─────────────────────────────────────────────────────────────────┐
│                        桌面应用层 (Desktop App)                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Python桌面应用 (CustomTkinter/PySide6)               │   │
│  │  • 主界面组件                                        │   │
│  │  • 文件拖拽上传                                        │   │
│  │  • 实时进度显示                                        │   │
│  │  • 角色管理界面                                        │   │
│  │  • 设置管理界面                                        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        本地服务层 (Local Service)                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  FastAPI本地服务器                                      │   │
│  │  • RESTful API (本地通信)                              │   │
│  │  • WebSocket实时通信                                    │   │
│  │  • 任务队列管理                                        │   │
│  │  • 进度状态同步                                        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        业务逻辑层 (Service)                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  核心服务模块                                           │   │
│  │  • 视频处理服务                                        │   │
│  │  • 语音识别服务                                        │   │
│  │  • 翻译服务                                            │   │
│  │  • 角色识别服务                                        │   │
│  │  • 声音克隆服务                                        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        数据存储层 (Local Storage)                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  本地存储                                               │   │
│  │  • SQLite (关系数据)                                   │   │
│  │  • 文件系统缓存                                        │   │
│  │  • 本地模型存储                                        │   │
│  │  • 配置文件管理                                        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        外部服务层 (External)                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  第三方API                                             │   │
│  │  • 语音识别API (SenseVoice, 百度语音)                 │   │
│  │  • 翻译API (DeepSeek, GLM-4.5)                        │   │
│  │  • 声音克隆API (本地模型)                             │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 本地服务架构
```
┌─────────────────────────────────────────────────────────────────┐
│                    桌面应用主进程                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Main Application (CustomTkinter/PySide6)               │   │
│  │  • UI事件处理                                          │   │
│  │  • 本地API调用                                         │   │
│  │  • 实时状态更新                                        │   │
│  │  • 文件操作管理                                        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    本地FastAPI服务                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Local FastAPI Server                                  │   │
│  │  • 路由: /api/v1/*                                   │   │
│  │  • 本地任务队列                                       │   │
│  │  • 文件系统管理                                       │   │
│  │  • 进度状态同步                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Media Service  │ │  Audio Service  │ │  Translation    │
│                 │ │                 │ │  Service        │
│ • 视频处理      │ │ • 音频提取      │ │ • 文本翻译      │
│ • 格式转换      │ │ • 音频处理      │ │ • 多语言支持    │
│ • 元数据提取    │ │ • 质量检测      │ │ • 术语库管理    │
└─────────────────┘ └─────────────────┘ └─────────────────┘
                    │           │           │
                    ▼           ▼           ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Character      │ │  Voice Clone    │ │  Cache Service  │
│  Service        │ │  Service        │ │                 │
│ • 角色识别      │ │ • 音色建模      │ │ • 本地文件缓存  │
│ • 性别识别      │ │ • 语音合成      │ │ • 断点续传      │
│ • 特征提取      │ │ • 质量优化      │ │ • 数据清理      │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## 2. 项目结构

### 2.1 目录结构 - Python桌面应用
```
movie-translate/
├── app/                        # 桌面应用主程序
│   ├── __init__.py
│   ├── main.py                 # 应用入口
│   ├── ui/                     # UI界面
│   │   ├── __init__.py
│   │   ├── main_window.py      # 主窗口
│   │   ├── components/         # UI组件
│   │   │   ├── __init__.py
│   │   │   ├── file_upload.py    # 文件上传组件
│   │   │   ├── progress_panel.py # 进度面板
│   │   │   ├── step_navigator.py # 步骤导航器
│   │   │   ├── character_manager.py # 角色管理器
│   │   │   ├── settings_panel.py # 设置面板
│   │   │   └── cache_manager.py # 缓存管理器
│   │   ├── dialogs/           # 对话框
│   │   │   ├── __init__.py
│   │   │   ├── error_dialog.py    # 错误对话框
│   │   │   ├── progress_dialog.py # 进度对话框
│   │   │   └── settings_dialog.py # 设置对话框
│   │   ├── styles/            # 样式配置
│   │   │   ├── __init__.py
│   │   │   ├── themes.py         # 主题配置
│   │   │   └── fonts.py          # 字体配置
│   │   └── utils/             # UI工具
│   │       ├── __init__.py
│   │       ├── file_dialog.py    # 文件对话框
│   │       └── message_box.py    # 消息框
│   ├── services/               # 本地API客户端
│   │   ├── __init__.py
│   │   ├── api_client.py       # API客户端
│   │   ├── websocket_client.py # WebSocket客户端
│   │   └── event_handler.py    # 事件处理器
│   ├── models/                 # 数据模型
│   │   ├── __init__.py
│   │   ├── process.py          # 处理状态模型
│   │   ├── character.py        # 角色模型
│   │   ├── settings.py         # 设置模型
│   │   └── cache.py            # 缓存模型
│   └── utils/                  # 应用工具
│       ├── __init__.py
│       ├── config.py           # 配置管理
│       ├── file_utils.py       # 文件工具
│       └── system_utils.py     # 系统工具
│
├── backend/                     # 本地后端服务
│   ├── __init__.py
│   ├── main.py                 # FastAPI服务入口
│   ├── config.py               # 服务配置
│   ├── api/                    # API路由
│   │   ├── __init__.py
│   │   ├── v1/                 # API版本1
│   │   │   ├── __init__.py
│   │   │   ├── video.py        # 视频相关API
│   │   │   ├── audio.py        # 音频相关API
│   │   │   ├── translation.py  # 翻译相关API
│   │   │   ├── character.py    # 角色相关API
│   │   │   ├── voice.py        # 声音相关API
│   │   │   ├── process.py      # 处理流程API
│   │   │   ├── cache.py        # 缓存管理API
│   │   │   └── system.py       # 系统状态API
│   │   └── websocket/          # WebSocket路由
│   │       ├── __init__.py
│   │       └── events.py       # 事件处理
│   ├── services/               # 业务逻辑
│   │   ├── __init__.py
│   │   ├── video_service.py
│   │   ├── audio_service.py
│   │   ├── translation_service.py
│   │   ├── character_service.py
│   │   ├── voice_service.py
│   │   ├── step_manager.py     # 步骤管理服务
│   │   ├── cache_manager.py    # 缓存管理服务
│   │   ├── interrupt_handler.py # 中断处理服务
│   │   └── process_orchestrator.py # 处理编排服务
│   ├── models/                 # 数据模型
│   │   ├── __init__.py
│   │   ├── video.py
│   │   ├── audio.py
│   │   ├── translation.py
│   │   ├── character.py
│   │   ├── process.py          # 处理流程模型
│   │   └── cache.py            # 缓存模型
│   ├── schemas/                # 数据模式
│   │   ├── __init__.py
│   │   ├── video.py
│   │   ├── audio.py
│   │   ├── translation.py
│   │   ├── character.py
│   │   ├── process.py
│   │   └── cache.py
│   ├── utils/                  # 工具函数
│   │   ├── __init__.py
│   │   ├── file_utils.py
│   │   ├── audio_utils.py
│   │   ├── video_utils.py
│   │   └── system_utils.py
│   ├── database/                # 数据库操作
│   │   ├── __init__.py
│   │   ├── connection.py       # 数据库连接
│   │   ├── migrations.py       # 数据库迁移
│   │   └── models.py           # 数据库模型
│   └── tests/                  # 测试文件
│       ├── __init__.py
│       ├── test_services/
│       └── test_api/
│
├── ml-services/                # 机器学习服务
│   ├── speech_recognition/     # 语音识别
│   │   ├── sense_voice/        # SenseVoice模型（本地）
│   │   └── baidu/              # 百度语音API
│   ├── translation/            # 翻译服务
│   │   ├── deepseek/           # DeepSeek模型
│   │   ├── glm/                # GLM模型
│   │   └── google/             # Google翻译
│   ├── voice_cloning/          # 声音克隆
│   │   ├── f5_tts/             # F5-TTS本地模型
│   │   │   ├── models/         # F5-TTS模型文件
│   │   │   ├── training/       # 模型训练脚本
│   │   │   ├── synthesis/      # 语音合成
│   │   │   └── optimization/    # 性能优化
│   │   ├── minimax/            # MiniMax Audio API
│   │   │   ├── api/            # API接口封装
│   │   │   ├── fallback/       # 容错机制
│   │   │   └── quality/         # 质量评估
│   │   ├── routing/            # 智能路由
│   │   ├── quality/             # 质量评估
│   │   └── cache/              # 缓存管理
│   └── character_analysis/     # 角色分析
│       ├── gender_detection/   # 性别检测
│       ├── voice_feature/      # 音色特征
│       └── clustering/         # 角色聚类
│
├── database/                   # 数据库相关
│   ├── migrations/             # 数据库迁移
│   ├── seeds/                  # 初始数据
│   └── schema.sql              # 数据库结构
│
├── storage/                    # 文件存储
│   ├── uploads/                # 上传文件
│   ├── cache/                  # 缓存文件
│   ├── models/                 # 模型文件
│   └── output/                 # 输出文件
│
├── config/                     # 配置文件
│   ├── development.py          # 开发环境配置
│   ├── production.py           # 生产环境配置
│   └── models.yaml             # 模型配置
│
├── docker/                     # Docker配置
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .env.example
│
├── docs/                       # 文档
│   ├── api/                    # API文档
│   ├── deployment/             # 部署文档
│   └── user_guide/             # 用户指南
│
├── scripts/                    # 脚本文件
│   ├── setup.py                # 安装脚本
│   ├── migrate.py              # 数据迁移脚本
│   └── backup.py               # 备份脚本
│
├── tests/                      # 测试
│   ├── unit/                   # 单元测试
│   ├── integration/            # 集成测试
│   └── e2e/                    # 端到端测试
│
├── .env.example               # 环境变量示例
├── .gitignore
├── README.md
└── docker-compose.yml
```

## 3. 技术选型

### 3.1 桌面应用技术栈
| 技术类别 | 选择 | 理由 |
|---------|------|------|
| **UI框架** | CustomTkinter / PySide6 | 现代化桌面UI框架，跨平台支持 |
| **备选方案** | PyQt6, Tkinter | 成熟稳定的桌面应用框架 |
| **图形渲染** | Canvas / QPainter | 高性能图形绘制 |
| **多线程** | threading / asyncio | 支持后台任务处理 |
| **文件拖拽** | tkinterdnd2 / PySide6拖拽 | 原生拖拽支持 |
| **系统托盘** | pystray | 系统托盘图标支持 |
| **打包工具** | PyInstaller / Nuitka | 将Python应用打包为可执行文件 |

### 3.2 本地服务技术栈
| 技术类别 | 选择 | 理由 |
|---------|------|------|
| **框架** | FastAPI | 高性能异步框架，自动生成API文档 |
| **ORM** | SQLAlchemy | 成熟的ORM，支持异步 |
| **数据库** | SQLite | 轻量级本地数据库，无需额外服务 |
| **文件存储** | 本地文件系统 | 简单可靠的文件存储 |
| **任务队列** | ThreadPoolExecutor | 本地任务队列管理 |
| **进程通信** | WebSocket / HTTP | 本地进程间通信 |
| **API文档** | OpenAPI 3.0 | 自动生成API文档 |
| **日志** | Loguru | 简单易用的日志库 |

### 3.3 机器学习技术栈
| 技术类别 | 选择 | 理由 |
|---------|------|------|
| **语音识别** | SenseVoice (阿里) | 中文优化，本地部署，5090显卡加速 |
| **翻译模型** | DeepSeek R1 | 高质量翻译，支持上下文 |
| **备选方案** | GLM-4.5 | 中文优化，专业术语 |
| **声音克隆** | F5-TTS (本地) / MiniMax Audio (云端) | F5-TTS本地部署高质量声音克隆，MiniMax Audio云端API备用方案 |
| **角色识别** | PyAnnote, VoiceID | 说话人识别和聚类 |
| **音频处理** | librosa, pydub | 音频分析和处理 |
| **深度学习框架** | PyTorch | 灵活的深度学习框架 |
| **GPU加速** | CUDA + cuDNN | GPU加速计算 |

### 3.4 桌面应用开发工具
| 技术类别 | 选择 | 理由 |
|---------|------|------|
| **打包工具** | PyInstaller | 将Python应用打包为可执行文件 |
| **安装程序** | Inno Setup (Windows) | Windows安装程序制作 |
| **图标制作** | GIMP / Inkscape | 图标和资源文件制作 |
| **版本管理** | Git | 版本控制 |
| **代码质量** | Black, isort, flake8 | 代码格式化和质量检查 |
| **测试** | pytest, pytest-qt | 完整的测试框架 |
| **调试工具** | pdb, VS Code调试器 | 代码调试 |

## 4. 核心模块设计

### 4.1 步骤管理模块
```python
# step_manager.py
class StepManager:
    def __init__(self):
        self.steps = [
            Step(name="文件导入", handler="file_import"),
            Step(name="音频处理", handler="audio_process"),
            Step(name="语音识别", handler="speech_recognition"),
            Step(name="翻译处理", handler="translation"),
            Step(name="角色识别", handler="character_recognition"),
            Step(name="配音生成", handler="voice_synthesis")
        ]
        self.current_step = 0
        self.step_states = {}
    
    async def execute_step(self, step_id: int, context: ProcessContext) -> StepResult:
        """执行指定步骤"""
        step = self.steps[step_id]
        handler = self.get_handler(step.handler)
        
        # 检查缓存
        cache_result = await self.cache_manager.get_step_cache(step_id, context)
        if cache_result:
            return cache_result
        
        # 执行步骤
        result = await handler.execute(context)
        
        # 保存缓存
        await self.cache_manager.save_step_cache(step_id, context, result)
        
        return result
    
    async def pause_step(self, step_id: int) -> bool:
        """暂停指定步骤"""
        # 实现暂停逻辑
        pass
    
    async def resume_step(self, step_id: int) -> bool:
        """恢复指定步骤"""
        # 实现恢复逻辑
        pass
    
    async def interrupt_step(self, step_id: int, save_progress: bool = True) -> bool:
        """中断指定步骤"""
        # 实现中断逻辑
        pass
```

### 4.2 缓存管理模块
```python
# cache_manager.py
class CacheManager:
    def __init__(self):
        self.cache_dir = "cache/"
        self.step_cache = {}
    
    async def save_step_cache(self, step_id: int, context: ProcessContext, result: StepResult):
        """保存步骤缓存"""
        cache_key = self._generate_cache_key(step_id, context)
        cache_path = os.path.join(self.cache_dir, f"step_{step_id}_{cache_key}")
        
        # 保存结果到缓存
        await self._save_to_cache(cache_path, result)
        
        # 更新缓存索引
        self.step_cache[cache_key] = {
            "step_id": step_id,
            "context": context,
            "cache_path": cache_path,
            "created_at": datetime.now(),
            "size": os.path.getsize(cache_path)
        }
    
    async def get_step_cache(self, step_id: int, context: ProcessContext) -> Optional[StepResult]:
        """获取步骤缓存"""
        cache_key = self._generate_cache_key(step_id, context)
        
        if cache_key in self.step_cache:
            cache_info = self.step_cache[cache_key]
            return await self._load_from_cache(cache_info["cache_path"])
        
        return None
    
    async def clear_step_cache(self, step_id: int, context: ProcessContext):
        """清理步骤缓存"""
        cache_key = self._generate_cache_key(step_id, context)
        
        if cache_key in self.step_cache:
            cache_info = self.step_cache[cache_key]
            os.remove(cache_info["cache_path"])
            del self.step_cache[cache_key]
    
    def get_cache_status(self) -> Dict[str, Any]:
        """获取缓存状态"""
        total_size = sum(info["size"] for info in self.step_cache.values())
        return {
            "total_steps": len(self.step_cache),
            "total_size": total_size,
            "cache_dir": self.cache_dir,
            "steps": list(self.step_cache.values())
        }
```

### 4.3 中断处理模块
```python
# interrupt_handler.py
class InterruptHandler:
    def __init__(self):
        self.interrupt_signals = {}
    
    async def handle_interrupt(self, step_id: int, interrupt_type: str, save_progress: bool = True):
        """处理中断信号"""
        if interrupt_type == "pause":
            await self._handle_pause(step_id)
        elif interrupt_type == "stop":
            await self._handle_stop(step_id, save_progress)
        elif interrupt_type == "skip":
            await self._handle_skip(step_id)
    
    async def _handle_pause(self, step_id: int):
        """处理暂停"""
        # 通知步骤暂停
        await self._notify_step_pause(step_id)
        
        # 保存当前状态
        await self._save_step_state(step_id, "paused")
    
    async def _handle_stop(self, step_id: int, save_progress: bool):
        """处理停止"""
        if save_progress:
            # 保存进度
            await self._save_step_progress(step_id)
        
        # 通知步骤停止
        await self._notify_step_stop(step_id)
        
        # 更新状态
        await self._save_step_state(step_id, "stopped")
    
    async def _handle_skip(self, step_id: int):
        """处理跳过"""
        # 通知步骤跳过
        await self._notify_step_skip(step_id)
        
        # 更新状态
        await self._save_step_state(step_id, "skipped")
    
    async def resume_from_interrupt(self, step_id: int) -> bool:
        """从中断恢复"""
        current_state = await self._get_step_state(step_id)
        
        if current_state in ["paused", "stopped"]:
            await self._notify_step_resume(step_id)
            await self._save_step_state(step_id, "running")
            return True
        
        return False
```

### 4.4 视频处理模块
```python
# video_service.py
class MediaService:
    def __init__(self):
        self.ffmpeg = FFmpeg()
        self.storage = FileStorage()
        self.cache_manager = CacheManager()
    
    async def process_media(self, file_path: str) -> MediaInfo:
        """处理媒体文件"""
        # 1. 识别文件类型（视频/音频）
        # 2. 验证文件格式
        # 3. 提取元数据
        # 4. 生成缩略图（仅视频）
        # 5. 转换格式（如果需要）
        # 6. 保存到存储
        pass
    
    async def extract_audio(self, video_path: str) -> str:
        """提取音频（仅视频文件）"""
        # 使用FFmpeg提取音频
        pass
    
    async def process_audio(self, audio_path: str) -> AudioInfo:
        """处理音频文件"""
        # 1. 验证音频格式
        # 2. 提取音频元数据
        # 3. 格式转换（如果需要）
        # 4. 质量检测
        pass
    
    async def generate_thumbnails(self, video_path: str) -> List[str]:
        """生成缩略图（仅视频文件）"""
        pass
```

### 4.2 语音识别模块
```python
# speech_recognition_service.py
class SpeechRecognitionService:
    def __init__(self):
        self.models = {
            'sense_voice': SenseVoiceModel(), # 本地SenseVoice模型
            'baidu': BaiduSpeechService()    # 云端API
        }
    
    async def transcribe(self, audio_path: str, model: str) -> SRTResult:
        """语音识别转字幕"""
        # 1. 验证模型选择
        if model not in self.models:
            raise ValueError(f"不支持的模型: {model}. 可用模型: {list(self.models.keys())}")
        
        # 2. 预处理音频
        processed_audio = await self._preprocess_audio(audio_path)
        
        # 3. 执行识别
        result = await self.models[model].transcribe(processed_audio)
        
        # 4. 生成SRT格式
        srt_result = await self._generate_srt(result)
        
        # 5. 保存结果
        await self._save_transcription_result(audio_path, srt_result)
        
        return srt_result
    
    async def detect_language(self, audio_path: str) -> str:
        """检测语言"""
        return await self.models['sense_voice'].detect_language(audio_path)
    
    def get_available_models(self) -> Dict[str, Dict[str, str]]:
        """获取可用模型列表"""
        return {
            'sense_voice': {
                'name': 'SenseVoice',
                'type': 'local',
                'description': '本地模型，中文优化，支持情感识别',
                'requires_gpu': True
            },
            'baidu': {
                'name': '百度语音',
                'type': 'cloud',
                'description': '云端API，中文优化，支持方言识别',
                'requires_api_key': True
            }
        }
```

### 4.2.1 SenseVoice模型集成
```python
# sense_voice_integration.py
class SenseVoiceModel:
    def __init__(self):
        self.model_name = "SenseVoiceSmall"
        self.model = None
        self.processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_cache = {}
        
    async def load_model(self):
        """加载SenseVoice模型"""
        if self.model is None:
            try:
                # 从Hugging Face加载SenseVoice模型
                self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                    "FunAudioLLM/SenseVoiceSmall"
                ).to(self.device)
                
                self.processor = AutoProcessor.from_pretrained(
                    "FunAudioLLM/SenseVoiceSmall"
                )
                
                # 启用半精度以节省显存
                if self.device == "cuda":
                    self.model = self.model.half()
                
                logger.info("SenseVoice模型加载成功")
                
            except Exception as e:
                logger.error(f"SenseVoice模型加载失败: {e}")
                raise ModelLoadError(f"SenseVoice模型加载失败: {e}")
    
    async def transcribe(self, audio_path: str) -> TranscriptionResult:
        """SenseVoice语音识别"""
        await self.load_model()
        
        try:
            # 1. 音频预处理
            audio_features = await self._preprocess_audio(audio_path)
            
            # 2. 生成输入特征
            input_features = self.processor(
                audio_features, 
                sampling_rate=16000, 
                return_tensors="pt"
            ).input_features.to(self.device)
            
            # 3. 执行识别（支持情感识别）
            with torch.no_grad():
                predicted_ids = self.model.generate(
                    input_features,
                    language="zh",  # 中文识别
                    task="transcribe",
                    temperature=0.0,
                    beam_size=5,
                    best_of=5,
                    patience=1.0,
                    length_penalty=1.0,
                    repetition_penalty=1.0,
                    no_repeat_ngram_size=3,
                    return_timestamps=True,  # 返回时间戳
                    return_token_timestamps=True  # 返回词级时间戳
                )
            
            # 4. 解码结果（包含情感信息）
            transcription = self.processor.batch_decode(
                predicted_ids, 
                skip_special_tokens=True
            )[0]
            
            # 5. 后处理
            cleaned_text = self._postprocess_transcription(transcription)
            
            # 6. 情感分析（SenseVoice特有功能）
            emotion_result = await self._analyze_emotion(audio_features)
            
            return TranscriptionResult(
                text=cleaned_text,
                language="zh",
                confidence=0.96,  # SenseVoice中文优化，置信度更高
                model_used="SenseVoiceSmall",
                processing_time=time.time(),
                emotion=emotion_result  # 包含情感信息
            )
            
        except Exception as e:
            logger.error(f"SenseVoice识别失败: {e}")
            raise TranscriptionError(f"语音识别失败: {e}")
    
    async def _preprocess_audio(self, audio_path: str) -> np.ndarray:
        """音频预处理"""
        try:
            # 1. 读取音频
            audio, sr = librosa.load(audio_path, sr=16000)
            
            # 2. 标准化音频
            audio = librosa.util.normalize(audio)
            
            # 3. 去除静音
            audio = self._remove_silence(audio)
            
            # 4. 音频增强
            audio = self._enhance_audio(audio)
            
            return audio
            
        except Exception as e:
            logger.error(f"音频预处理失败: {e}")
            raise
    
    def _remove_silence(self, audio: np.ndarray) -> np.ndarray:
        """去除静音"""
        # 使用librosa去除静音
        intervals = librosa.effects.split(
            audio, 
            top_db=20, 
            frame_length=2048, 
            hop_length=512
        )
        
        # 提取非静音片段
        non_silent_segments = []
        for start, end in intervals:
            non_silent_segments.append(audio[start:end])
        
        if non_silent_segments:
            return np.concatenate(non_silent_segments)
        else:
            return audio
    
    def _enhance_audio(self, audio: np.ndarray) -> np.ndarray:
        """音频增强"""
        try:
            # 1. 降噪
            if hasattr(self, 'denoiser'):
                audio = self.denoiser(audio, sr=16000)
            
            # 2. 音量标准化
            audio = librosa.util.normalize(audio)
            
            return audio
            
        except Exception as e:
            logger.warning(f"音频增强失败，使用原始音频: {e}")
            return audio
    
    def _postprocess_transcription(self, text: str) -> str:
        """转录结果后处理"""
        # 1. 去除多余空格
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 2. 修复标点符号
        text = self._fix_punctuation(text)
        
        # 3. 移除识别错误常见词
        text = self._remove_common_errors(text)
        
        return text
    
    def _fix_punctuation(self, text: str) -> str:
        """修复标点符号"""
        # 添加中文标点符号
        punctuation_map = {
            ',': '，',
            '.': '。',
            '?': '？',
            '!': '！',
            ':': '：',
            ';': '；',
            '"': '"',
            "'": '"'
        }
        
        for en, zh in punctuation_map.items():
            text = text.replace(en, zh)
        
        return text
    
    def _remove_common_errors(self, text: str) -> str:
        """移除常见识别错误"""
        # Whisper常见错误词汇映射
        error_map = {
            '字幕': '字幕',
            '感谢观看': '感谢观看',
            '请点赞': '请点赞',
            '订阅': '订阅',
        }
        
        # 这里可以根据实际使用情况添加更多错误修正
        return text
    
    async def _analyze_emotion(self, audio_features: np.ndarray) -> Dict[str, float]:
        """情感分析（SenseVoice特有功能）"""
        try:
            # 使用SenseVoice的情感识别能力
            emotion_features = self.model.extract_emotion_features(audio_features)
            
            # 分析情感分布
            emotions = {
                "neutral": emotion_features.get("neutral", 0.0),
                "happy": emotion_features.get("happy", 0.0),
                "sad": emotion_features.get("sad", 0.0),
                "angry": emotion_features.get("angry", 0.0),
                "excited": emotion_features.get("excited", 0.0)
            }
            
            # 归一化情感值
            total = sum(emotions.values())
            if total > 0:
                emotions = {k: v/total for k, v in emotions.items()}
            
            return emotions
            
        except Exception as e:
            logger.warning(f"情感分析失败，返回默认值: {e}")
            return {"neutral": 1.0}
```

### 4.2.2 SenseVoice性能优化
```python
# sense_voice_optimizer.py
class SenseVoiceOptimizer:
    def __init__(self):
        self.model_config = WhisperConfig()
        self.gpu_manager = GPUMemoryManager()
        self.batch_processor = BatchProcessor()
    
    async def optimize_for_inference(self):
        """推理性能优化"""
        if torch.cuda.is_available():
            # 1. 启用TensorRT加速（如果可用）
            if self._is_tensorrt_available():
                await self._enable_tensorrt()
            
            # 2. 启用半精度推理
            self.model = self.model.half()
            
            # 3. 启用Flash Attention
            if hasattr(self.model, 'config'):
                self.model.config.use_flash_attention = True
            
            # 4. 模型量化
            await self._quantize_model()
    
    async def batch_transcribe(self, audio_files: List[str]) -> List[TranscriptionResult]:
        """批量语音识别"""
        # 1. 音频文件分组
        batches = self._group_audio_files(audio_files, batch_size=4)
        
        # 2. 并行处理
        results = []
        for batch in batches:
            batch_results = await self._process_batch(batch)
            results.extend(batch_results)
        
        return results
    
    async def _process_batch(self, audio_files: List[str]) -> List[TranscriptionResult]:
        """处理音频批次"""
        try:
            # 1. 预处理所有音频
            audio_features = []
            for audio_path in audio_files:
                features = await self._preprocess_audio(audio_path)
                audio_features.append(features)
            
            # 2. 批量生成特征
            input_features = self.processor(
                audio_features, 
                sampling_rate=16000, 
                return_tensors="pt",
                padding=True
            ).input_features.to(self.device)
            
            # 3. 批量识别
            with torch.no_grad():
                predicted_ids = self.model.generate(
                    input_features,
                    language="zh",
                    task="transcribe",
                    **self._get_batch_generation_params()
                )
            
            # 4. 批量解码
            transcriptions = self.processor.batch_decode(
                predicted_ids, 
                skip_special_tokens=True
            )
            
            # 5. 处理结果
            results = []
            for i, transcription in enumerate(transcriptions):
                result = TranscriptionResult(
                    text=self._postprocess_transcription(transcription),
                    language="zh",
                    confidence=0.95,
                    model_used="whisper-large-v3",
                    audio_file=audio_files[i],
                    processing_time=time.time()
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"批量处理失败: {e}")
            raise
    
    def _get_batch_generation_params(self) -> Dict:
        """获取批量生成参数"""
        return {
            "temperature": 0.0,
            "beam_size": 5,
            "best_of": 5,
            "patience": 1.0,
            "length_penalty": 1.0,
            "repetition_penalty": 1.0,
            "no_repeat_ngram_size": 3,
            "num_beams": 5
        }
```

### 4.2.3 SenseVoice缓存管理
```python
# sense_voice_cache.py
class SenseVoiceCacheManager:
    def __init__(self):
        self.cache_db = SenseVoiceCacheDB()
        self.hash_generator = AudioHashGenerator()
        self.ttl = 86400 * 7  # 7天缓存
    
    async def get_cached_transcription(self, audio_path: str) -> Optional[TranscriptionResult]:
        """获取缓存的转录结果"""
        try:
            # 1. 生成音频哈希
            audio_hash = await self.hash_generator.generate_hash(audio_path)
            
            # 2. 查询缓存
            cached_result = await self.cache_db.get_cache(audio_hash)
            
            if cached_result:
                # 3. 更新访问时间
                await self.cache_db.update_access_time(audio_hash)
                
                return TranscriptionResult(
                    text=cached_result['text'],
                    language=cached_result['language'],
                    confidence=cached_result['confidence'],
                    model_used=cached_result['model_used'],
                    is_cached=True,
                    processing_time=0.0
                )
            
            return None
            
        except Exception as e:
            logger.error(f"获取缓存失败: {e}")
            return None
    
    async def save_transcription_cache(self, audio_path: str, result: TranscriptionResult):
        """保存转录缓存"""
        try:
            # 1. 生成音频哈希
            audio_hash = await self.hash_generator.generate_hash(audio_path)
            
            # 2. 保存缓存
            cache_data = {
                'audio_hash': audio_hash,
                'text': result.text,
                'language': result.language,
                'confidence': result.confidence,
                'model_used': result.model_used,
                'audio_path': audio_path,
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(seconds=self.ttl)
            }
            
            await self.cache_db.save_cache(audio_hash, cache_data)
            
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")
    
    async def cleanup_expired_cache(self):
        """清理过期缓存"""
        try:
            expired_count = await self.cache_db.delete_expired_cache()
            logger.info(f"清理了 {expired_count} 个过期缓存")
            
        except Exception as e:
            logger.error(f"清理缓存失败: {e}")
```

### 4.2.4 模型选择接口
```python
# model_selection.py
class ModelSelectionService:
    def __init__(self):
        self.speech_service = SpeechRecognitionService()
    
    def get_speech_recognition_models(self) -> Dict[str, Dict[str, str]]:
        """获取语音识别可用模型列表"""
        return self.speech_service.get_available_models()
    
    def validate_model_selection(self, model: str, model_type: str) -> bool:
        """验证模型选择是否有效"""
        if model_type == "speech_recognition":
            return model in self.speech_service.get_available_models()
        return False
    
    def get_model_requirements(self, model: str) -> Dict[str, Any]:
        """获取模型配置要求"""
        models = self.speech_service.get_available_models()
        if model in models:
            return models[model]
        return {}
```

### 4.3 翻译模块
```python
# translation_service.py
class TranslationService:
    def __init__(self):
        self.models = {
            'deepseek': DeepSeekModel(),
            'glm': GLMModel()
        }
        self.cache_manager = TranslationCacheManager()
        self.srt_processor = SRTProcessor()
    
    async def translate_srt(self, srt_path: str, target_lang: str = 'zh') -> str:
        """翻译SRT文件 - 本地预处理+线上翻译方案"""
        # 1. 解析SRT文件
        srt_data = await self.srt_processor.parse_srt(srt_path)
        
        # 2. 文本预处理
        processed_text = await self.srt_processor.preprocess_text(srt_data)
        
        # 3. 检查翻译缓存
        cached_result = await self.cache_manager.get_cached_translation(
            processed_text, target_lang
        )
        if cached_result:
            return cached_result
        
        # 4. 批量翻译处理
        translated_chunks = await self._batch_translate(
            processed_text, target_lang
        )
        
        # 5. 重新组装SRT格式
        result_srt = await self.srt_processor.assemble_srt(
            srt_data, translated_chunks
        )
        
        # 6. 保存翻译缓存
        await self.cache_manager.save_translation(
            processed_text, translated_chunks, target_lang
        )
        
        return result_srt
    
    async def _batch_translate(self, text_chunks: List[str], target_lang: str) -> List[str]:
        """批量翻译文本块"""
        # 1. 智能分段（考虑上下文连贯性）
        chunks = self._smart_chunking(text_chunks)
        
        # 2. 并发翻译控制
        tasks = []
        for chunk in chunks:
            task = self._translate_chunk(chunk, target_lang)
            tasks.append(task)
        
        # 3. 执行翻译（控制并发数）
        results = await self._concurrent_translate(tasks)
        
        return results
    
    async def _translate_chunk(self, chunk: str, target_lang: str) -> str:
        """翻译单个文本块"""
        # 1. 选择最优模型
        model = self._select_optimal_model(chunk, target_lang)
        
        # 2. 执行翻译
        result = await model.translate(chunk, target_lang)
        
        # 3. 后处理优化
        return self._post_process_translation(result)
    
    def resume_translation(self, srt_path: str, checkpoint_path: str) -> str:
        """断点续传翻译"""
        # 从检查点恢复翻译进度
        pass
```

### 4.4 SRT预处理模块
```python
# srt_processor.py
class SRTProcessor:
    def __init__(self):
        self.max_chunk_size = 2000  # 单次翻译最大字符数
        self.context_window = 3     # 上下文窗口大小
    
    async def parse_srt(self, srt_path: str) -> List[SRTEntry]:
        """解析SRT文件"""
        entries = []
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析SRT格式
        blocks = content.split('\n\n')
        for block in blocks:
            if block.strip():
                entry = self._parse_srt_block(block)
                entries.append(entry)
        
        return entries
    
    async def preprocess_text(self, srt_data: List[SRTEntry]) -> List[TextChunk]:
        """文本预处理"""
        # 1. 提取纯文本
        texts = [entry.text for entry in srt_data]
        
        # 2. 去重处理
        unique_texts = self._remove_duplicates(texts)
        
        # 3. 智能分段
        chunks = self._smart_chunking(unique_texts)
        
        # 4. 添加上下文信息
        enriched_chunks = self._add_context(chunks, srt_data)
        
        return enriched_chunks
    
    def _smart_chunking(self, texts: List[str]) -> List[TextChunk]:
        """智能分段"""
        chunks = []
        current_chunk = ""
        
        for text in texts:
            # 考虑句子完整性
            if len(current_chunk + text) <= self.max_chunk_size:
                current_chunk += text + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = text + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def assemble_srt(self, original_data: List[SRTEntry], 
                          translated_chunks: List[str]) -> str:
        """重新组装SRT格式"""
        # 将翻译结果映射回原始SRT结构
        result = []
        
        for i, entry in enumerate(original_data):
            translated_text = self._map_translation(entry.text, translated_chunks)
            srt_block = self._format_srt_entry(
                entry.index, entry.start_time, entry.end_time, translated_text
            )
            result.append(srt_block)
        
        return '\n\n'.join(result)
```

### 4.5 翻译缓存管理模块
```python
# translation_cache_manager.py
class TranslationCacheManager:
    def __init__(self):
        self.cache_db = TranslationCacheDB()
        self.hash_generator = TextHashGenerator()
    
    async def get_cached_translation(self, text_hash: str, target_lang: str) -> Optional[str]:
        """获取缓存的翻译结果"""
        cache_key = f"{text_hash}_{target_lang}"
        return await self.cache_db.get_cache(cache_key)
    
    async def save_translation(self, original_hash: str, translated_text: str, 
                            target_lang: str, metadata: Dict = None):
        """保存翻译缓存"""
        cache_key = f"{original_hash}_{target_lang}"
        cache_data = {
            'original_hash': original_hash,
            'translated_text': translated_text,
            'target_lang': target_lang,
            'created_at': datetime.now(),
            'metadata': metadata or {}
        }
        await self.cache_db.save_cache(cache_key, cache_data)
    
    async def create_checkpoint(self, srt_path: str, progress: Dict):
        """创建翻译检查点"""
        checkpoint_data = {
            'srt_path': srt_path,
            'progress': progress,
            'timestamp': datetime.now(),
            'translated_chunks': progress.get('translated_chunks', []),
            'current_position': progress.get('current_position', 0)
        }
        await self.cache_db.save_checkpoint(srt_path, checkpoint_data)
    
    async def load_checkpoint(self, srt_path: str) -> Optional[Dict]:
        """加载翻译检查点"""
        return await self.cache_db.get_checkpoint(srt_path)
    
    def generate_text_hash(self, text: str) -> str:
        """生成文本哈希值"""
        return self.hash_generator.generate_hash(text)
```

### 4.4 角色识别模块
```python
# character_service.py
class CharacterService:
    def __init__(self):
        self.voice_analyzer = VoiceAnalyzer()
        self.gender_detector = GenderDetector()
        self.clustering = VoiceClustering()
    
    async def identify_characters(self, audio_path: str, srt_path: str) -> List[Character]:
        """识别角色"""
        # 1. 音频分段
        # 2. 特征提取
        # 3. 聚类分析
        # 4. 性别识别
        # 5. 角色分类
        pass
    
    async def extract_voice_features(self, audio_segment: str) -> VoiceFeatures:
        """提取音色特征"""
        pass
```

### 4.6 翻译缓存数据库设计
```sql
-- 翻译缓存表
CREATE TABLE translation_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text_hash VARCHAR(64) NOT NULL,
    original_text TEXT NOT NULL,
    translated_text TEXT NOT NULL,
    source_lang VARCHAR(10) NOT NULL,
    target_lang VARCHAR(10) NOT NULL,
    model_used VARCHAR(50),
    quality_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    UNIQUE(text_hash, source_lang, target_lang)
);

-- 翻译检查点表
CREATE TABLE translation_checkpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    srt_path VARCHAR(500) NOT NULL,
    progress_data TEXT NOT NULL,  -- JSON格式
    current_position INTEGER DEFAULT 0,
    total_chunks INTEGER DEFAULT 0,
    translated_chunks TEXT,         -- JSON格式
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(srt_path)
);

-- 翻译任务表
CREATE TABLE translation_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id VARCHAR(64) UNIQUE NOT NULL,
    srt_path VARCHAR(500) NOT NULL,
    source_lang VARCHAR(10) NOT NULL,
    target_lang VARCHAR(10) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    total_chunks INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

### 4.7 声音克隆模块
```python
# voice_cloning_service.py
class VoiceCloningService:
    def __init__(self):
        self.local_models = {
            'f5_tts': F5TTSModel(),      # 本地F5-TTS模型
        }
        self.cloud_services = {
            'minimax': MiniMaxAudioService()  # MiniMax Audio API
        }
        self.voice_processor = VoiceProcessor()
        self.quality_analyzer = VoiceQualityAnalyzer()
        self.cache_manager = VoiceCacheManager()
    
    async def clone_voice(self, character_id: str, audio_samples: List[str], service: str) -> VoiceCloneResult:
        """克隆声音 - 根据用户选择的服务"""
        if service == 'f5_tts':
            return await self._clone_with_local(character_id, audio_samples)
        elif service == 'minimax':
            return await self._clone_with_cloud(character_id, audio_samples)
        else:
            raise ValueError(f"不支持的声音克隆服务: {service}")
    
    async def _clone_with_local(self, character_id: str, audio_samples: List[str]) -> VoiceCloneResult:
        """使用本地F5-TTS克隆声音"""
        try:
            # 1. 音频预处理
            processed_audio = await self.voice_processor.preprocess_audio(audio_samples)
            
            # 2. 音质评估
            quality_result = await self.quality_analyzer.analyze_audio_quality(processed_audio)
            if not quality_result.is_suitable:
                raise VoiceQualityError(f"音频质量不达标: {quality_result.reason}")
            
            # 3. 检查本地缓存
            cache_key = self._generate_voice_cache_key(character_id, processed_audio)
            cached_model = await self.cache_manager.get_cached_model(cache_key)
            if cached_model:
                return VoiceCloneResult(
                    character_id=character_id,
                    model_path=cached_model,
                    quality_score=quality_result.score,
                    is_cached=True
                )
            
            # 4. 使用F5-TTS训练声音模型
            model_path = await self._train_f5_tts_model(character_id, processed_audio)
            
            # 5. 质量验证
            validation_result = await self._validate_voice_model(model_path, character_id)
            
            # 6. 缓存模型
            await self.cache_manager.save_model_cache(cache_key, model_path)
            
            return VoiceCloneResult(
                character_id=character_id,
                model_path=model_path,
                quality_score=validation_result.score,
                training_time=validation_result.training_time
            )
            
        except Exception as e:
            logger.error(f"本地声音克隆失败: {e}")
            raise VoiceCloningError(f"本地声音克隆失败: {e}")
    
    async def _clone_with_cloud(self, character_id: str, audio_samples: List[str]) -> VoiceCloneResult:
        """使用云端MiniMax克隆声音"""
        try:
            # 1. 音频预处理
            processed_audio = await self.voice_processor.preprocess_audio(audio_samples)
            
            # 2. 音质评估
            quality_result = await self.quality_analyzer.analyze_audio_quality(processed_audio)
            if not quality_result.is_suitable:
                raise VoiceQualityError(f"音频质量不达标: {quality_result.reason}")
            
            # 3. 调用MiniMax API
            minimax_service = self.cloud_services['minimax']
            result = await minimax_service.voice_clone(processed_audio, character_id)
            
            return VoiceCloneResult(
                character_id=character_id,
                model_path=result.model_path,
                quality_score=result.quality_score,
                training_time=result.training_time,
                is_cloud=True
            )
            
        except Exception as e:
            logger.error(f"云端声音克隆失败: {e}")
            raise VoiceCloningError(f"云端声音克隆失败: {e}")
    
    async def synthesize(self, text: str, character_id: str, service: str) -> str:
        """语音合成 - 根据选择的服务"""
        if service == 'f5_tts':
            return await self._synthesize_with_local(text, character_id)
        elif service == 'minimax':
            return await self._synthesize_with_cloud(text, character_id)
        else:
            raise ValueError(f"不支持的声音合成服务: {service}")
    
    def get_available_services(self) -> Dict[str, Dict[str, str]]:
        """获取可用声音克隆服务"""
        return {
            'f5_tts': {
                'name': 'F5-TTS',
                'type': 'local',
                'description': '本地零样本声音克隆，无需大量训练数据',
                'requires_gpu': True,
                'training_time': '5-10分钟',
                'quality': '高'
            },
            'minimax': {
                'name': 'MiniMax Audio',
                'type': 'cloud',
                'description': '云端企业级声音克隆服务，质量稳定',
                'requires_api_key': True,
                'training_time': '1-3分钟',
                'quality': '专业级'
            }
        }
    
    async def _train_f5_tts_model(self, character_id: str, audio_samples: List[str]) -> str:
        """使用F5-TTS训练声音模型"""
        try:
            # 1. 准备训练数据
            training_data = await self._prepare_training_data(audio_samples)
            
            # 2. 配置F5-TTS训练参数
            config = F5TTSConfig(
                speaker_id=character_id,
                training_steps=1000,    # 适配快速训练
                learning_rate=1e-4,
                batch_size=4,
                save_dir=f"models/voice_clones/{character_id}"
            )
            
            # 3. 执行训练
            f5_model = self.local_models['f5_tts']
            model_path = await f5_model.train(
                training_data=training_data,
                config=config
            )
            
            return model_path
            
        except Exception as e:
            logger.error(f"F5-TTS训练失败: {e}")
            raise VoiceCloningError(f"声音模型训练失败: {e}")
    
    async def _synthesize_with_local(self, text: str, character_id: str) -> str:
        """使用本地F5-TTS合成语音"""
        try:
            # 1. 加载角色模型
            model_path = f"models/voice_clones/{character_id}/model.pt"
            if not os.path.exists(model_path):
                raise ModelNotFoundError(f"未找到角色声音模型: {character_id}")
            
            # 2. 文本预处理
            processed_text = await self.voice_processor.preprocess_text(text)
            
            # 3. F5-TTS语音合成
            f5_model = self.local_models['f5_tts']
            audio_path = await f5_model.synthesize(
                text=processed_text,
                speaker_id=character_id,
                model_path=model_path
            )
            
            # 4. 音频后处理
            final_audio = await self.voice_processor.postprocess_audio(audio_path)
            
            return final_audio
            
        except Exception as e:
            logger.error(f"本地语音合成失败: {e}")
            # 降级到云端方案
            return await self._synthesize_with_cloud(text, character_id)
    
    async def _synthesize_with_cloud(self, text: str, character_id: str) -> str:
        """使用MiniMax Audio API合成语音"""
        try:
            # 1. 获取角色声音特征
            voice_features = await self._get_character_voice_features(character_id)
            
            # 2. 调用MiniMax Audio API
            minimax_service = self.cloud_services['minimax']
            audio_path = await minimax_service.tts(
                text=text,
                voice_id=voice_features.voice_id,
                voice_prompt=voice_features.prompt_text,
                speed=1.0,
                volume=0.8
            )
            
            return audio_path
            
        except Exception as e:
            logger.error(f"云端语音合成失败: {e}")
            raise VoiceSynthesisError(f"语音合成失败: {e}")
    
    async def _fallback_to_cloud_service(self, character_id: str, audio_samples: List[str]) -> VoiceCloneResult:
        """降级到云端声音克隆服务"""
        try:
            # 使用MiniMax Audio的声音复刻功能
            minimax_service = self.cloud_services['minimax']
            voice_clone_result = await minimax_service.voice_clone(
                audio_samples=audio_samples,
                character_name=character_id
            )
            
            return VoiceCloneResult(
                character_id=character_id,
                model_path=None,  # 云端模型，无本地路径
                voice_id=voice_clone_result.voice_id,
                quality_score=voice_clone_result.quality_score,
                is_cloud_based=True
            )
            
        except Exception as e:
            logger.error(f"云端声音克隆也失败: {e}")
            raise VoiceCloningError(f"声音克隆失败，请检查音频质量或重试: {e}")
```

## 5. 声音克隆技术方案详解

### 5.1 F5-TTS本地部署方案

#### 5.1.1 F5-TTS技术特点
- **零样本声音克隆**：仅需少量音频样本即可高质量克隆声音
- **多语言支持**：支持中文、英文等多种语言的语音合成
- **情感表达**：能够保留原声音的情感特征和语调
- **高质量输出**：生成自然流畅的语音，接近真人水平
- **GPU加速**：支持CUDA加速，充分利用5090显卡性能

#### 5.1.2 F5-TTS本地部署架构
```python
# f5_tts_service.py
class F5TTSModel:
    def __init__(self):
        self.model_path = "models/f5_tts"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.is_loaded = False
    
    async def load_model(self):
        """加载F5-TTS模型"""
        if not self.is_loaded:
            try:
                # 从Hugging Face加载模型
                self.model = F5TTSForConditionalGeneration.from_pretrained(
                    "SWivid/F5-TTS"
                ).to(self.device)
                
                # 加载语音编码器
                self.speaker_encoder = SpeakerEncoder.from_pretrained(
                    "SWivid/F5-TTS-Speaker-Encoder"
                ).to(self.device)
                
                self.is_loaded = True
                logger.info("F5-TTS模型加载成功")
                
            except Exception as e:
                logger.error(f"F5-TTS模型加载失败: {e}")
                raise ModelLoadError(f"F5-TTS模型加载失败: {e}")
    
    async def train(self, training_data: List[AudioSample], config: F5TTSConfig) -> str:
        """快速训练声音模型"""
        await self.load_model()
        
        try:
            # 1. 音频特征提取
            speaker_embeddings = []
            for sample in training_data:
                embedding = await self._extract_speaker_embedding(sample.audio_path)
                speaker_embeddings.append(embedding)
            
            # 2. 计算平均说话人嵌入
            avg_embedding = torch.mean(torch.stack(speaker_embeddings), dim=0)
            
            # 3. 快速适配训练
            optimizer = torch.optim.AdamW(self.model.parameters(), lr=config.learning_rate)
            
            for step in range(config.training_steps):
                # 使用少量数据进行快速适配
                loss = await self._training_step(training_data, avg_embedding)
                optimizer.step()
                
                if step % 100 == 0:
                    logger.info(f"训练进度: {step}/{config.training_steps}, Loss: {loss:.4f}")
            
            # 4. 保存适配后的模型
            model_save_path = os.path.join(config.save_dir, "adapter_model.pt")
            torch.save({
                'model_state_dict': self.model.state_dict(),
                'speaker_embedding': avg_embedding,
                'config': config.__dict__
            }, model_save_path)
            
            return model_save_path
            
        except Exception as e:
            logger.error(f"F5-TTS训练失败: {e}")
            raise TrainingError(f"训练失败: {e}")
    
    async def synthesize(self, text: str, speaker_id: str, model_path: str) -> str:
        """语音合成"""
        await self.load_model()
        
        try:
            # 1. 加载说话人特定模型
            checkpoint = torch.load(model_path, map_location=self.device)
            speaker_embedding = checkpoint['speaker_embedding']
            
            # 2. 文本预处理
            input_ids = self._tokenize_text(text)
            
            # 3. 生成语音
            with torch.no_grad():
                # 生成梅尔频谱图
                mel_spectrogram = self.model.generate(
                    input_ids=input_ids,
                    speaker_embedding=speaker_embedding,
                    temperature=0.7,
                    top_p=0.9
                )
                
                # 转换为音频波形
                audio_waveform = self._mel_to_audio(mel_spectrogram)
            
            # 4. 保存音频
            output_path = f"temp/audio/{speaker_id}_{int(time.time())}.wav"
            self._save_audio(audio_waveform, output_path)
            
            return output_path
            
        except Exception as e:
            logger.error(f"F5-TTS合成失败: {e}")
            raise SynthesisError(f"语音合成失败: {e}")
```

#### 5.1.3 F5-TTS性能优化策略
```python
# f5_tts_optimizer.py
class F5TTSOptimizer:
    def __init__(self):
        self.model_config = F5TTSConfig()
        self.gpu_manager = GPUMemoryManager()
    
    async def optimize_for_gpu(self):
        """GPU性能优化"""
        # 1. 启用半精度训练
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        
        # 2. 显存优化
        if torch.cuda.is_available():
            # 启用梯度检查点
            self.model.gradient_checkpointing_enable()
            
            # 使用内存高效注意力
            self.model.config.use_memory_efficient_attention = True
            
            # 显存分配策略
            self.gpu_manager.set_memory_allocation_strategy('dynamic')
    
    async def batch_synthesis(self, texts: List[str], speaker_id: str) -> List[str]:
        """批量语音合成"""
        # 1. 文本分组
        text_batches = self._group_texts_by_length(texts, batch_size=8)
        
        # 2. 并行处理
        tasks = []
        for batch in text_batches:
            task = self._synthesize_batch(batch, speaker_id)
            tasks.append(task)
        
        # 3. 执行批量合成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return self._process_results(results)
    
    async def cache_management(self):
        """缓存管理"""
        # 1. 模型缓存
        self.model_cache = LRUCache(maxsize=5)
        
        # 2. 说话人嵌入缓存
        self.embedding_cache = TTLCache(maxsize=100, ttl=3600)
        
        # 3. 音频结果缓存
        self.audio_cache = DiskCache(cache_dir="cache/audio")
```

### 5.2 MiniMax Audio云端方案

#### 5.2.1 MiniMax Audio技术特点
- **高质量声音克隆**：支持1:1声音复刻，质量优秀
- **快速处理**：云端API响应快速，无需本地计算资源
- **稳定可靠**：企业级服务，稳定性高
- **多场景适用**：支持多种应用场景的声音合成
- **简单易用**：API接口简单，集成方便

#### 5.2.2 MiniMax Audio API集成
```python
# minimax_audio_service.py
class MiniMaxAudioService:
    def __init__(self):
        self.api_key = os.getenv("MINIMAX_API_KEY")
        self.base_url = "https://api.minimax.chat/v1"
        self.http_client = AsyncHTTPClient()
        self.rate_limiter = RateLimiter(calls_per_minute=60)
    
    async def voice_clone(self, audio_samples: List[str], character_name: str) -> VoiceCloneResult:
        """声音克隆API"""
        await self.rate_limiter.acquire()
        
        try:
            # 1. 上传音频样本
            upload_urls = []
            for sample_path in audio_samples:
                upload_url = await self._upload_audio_sample(sample_path)
                upload_urls.append(upload_url)
            
            # 2. 创建声音克隆任务
            clone_request = {
                "character_name": character_name,
                "audio_samples": upload_urls,
                "quality": "high",
                "language": "zh"
            }
            
            response = await self.http_client.post(
                f"{self.base_url}/voice_clone",
                json=clone_request,
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                return VoiceCloneResult(
                    character_id=character_name,
                    voice_id=result["voice_id"],
                    quality_score=result["quality_score"],
                    is_cloud_based=True
                )
            else:
                raise APIError(f"声音克隆失败: {response.status_code}")
                
        except Exception as e:
            logger.error(f"MiniMax声音克隆失败: {e}")
            raise
    
    async def tts(self, text: str, voice_id: str, voice_prompt: str = None, 
                 speed: float = 1.0, volume: float = 0.8) -> str:
        """文本转语音API"""
        await self.rate_limiter.acquire()
        
        try:
            tts_request = {
                "text": text,
                "voice_id": voice_id,
                "speed": speed,
                "volume": volume,
                "emotion": "natural"
            }
            
            if voice_prompt:
                tts_request["voice_prompt"] = voice_prompt
            
            response = await self.http_client.post(
                f"{self.base_url}/tts",
                json=tts_request,
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                # 保存音频文件
                audio_data = response.content
                output_path = f"temp/audio/minimax_{int(time.time())}.wav"
                
                with open(output_path, 'wb') as f:
                    f.write(audio_data)
                
                return output_path
            else:
                raise APIError(f"TTS合成失败: {response.status_code}")
                
        except Exception as e:
            logger.error(f"MiniMax TTS失败: {e}")
            raise
    
    async def _upload_audio_sample(self, audio_path: str) -> str:
        """上传音频样本"""
        with open(audio_path, 'rb') as f:
            files = {'file': f}
            response = await self.http_client.post(
                f"{self.base_url}/upload_audio",
                files=files,
                headers=self._get_headers()
            )
            
        if response.status_code == 200:
            result = response.json()
            return result["url"]
        else:
            raise APIError(f"音频上传失败: {response.status_code}")
```

#### 5.2.3 MiniMax Audio容错和降级策略
```python
# minimax_fallback.py
class MiniMaxFallbackStrategy:
    def __init__(self):
        self.retry_policy = RetryPolicy(
            max_retries=3,
            backoff_factor=2,
            retryable_exceptions=[TimeoutError, ConnectionError]
        )
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=300
        )
    
    async def safe_voice_clone(self, audio_samples: List[str], character_name: str) -> VoiceCloneResult:
        """安全的声音克隆（带容错）"""
        try:
            # 1. 检查熔断器状态
            if self.circuit_breaker.is_open():
                raise CircuitBreakerOpenError("MiniMax服务暂时不可用")
            
            # 2. 带重试的API调用
            result = await self.retry_policy.execute(
                lambda: self.minimax_service.voice_clone(audio_samples, character_name)
            )
            
            # 3. 成功则重置熔断器
            self.circuit_breaker.on_success()
            
            return result
            
        except Exception as e:
            # 4. 失败则记录熔断器
            self.circuit_breaker.on_failure()
            raise
    
    async def safe_tts(self, text: str, voice_id: str, **kwargs) -> str:
        """安全的TTS合成（带容错）"""
        try:
            if self.circuit_breaker.is_open():
                raise CircuitBreakerOpenError("MiniMax服务暂时不可用")
            
            result = await self.retry_policy.execute(
                lambda: self.minimax_service.tts(text, voice_id, **kwargs)
            )
            
            self.circuit_breaker.on_success()
            return result
            
        except Exception as e:
            self.circuit_breaker.on_failure()
            raise
```

### 5.3 用户选择策略

#### 5.3.1 服务选择接口
```python
# service_selection.py
class VoiceCloningSelectionService:
    def __init__(self):
        self.voice_service = VoiceCloningService()
    
    def get_available_services(self) -> Dict[str, Dict[str, str]]:
        """获取可用声音克隆服务"""
        return self.voice_service.get_available_services()
    
    def validate_service_selection(self, service: str) -> bool:
        """验证服务选择是否有效"""
        return service in self.voice_service.get_available_services()
    
    def get_service_requirements(self, service: str) -> Dict[str, Any]:
        """获取服务配置要求"""
        services = self.voice_service.get_available_services()
        if service in services:
            return services[service]
        return {}
    
    async def recommend_service(self, user_preferences: Dict[str, Any]) -> str:
        """根据用户偏好推荐服务（可选）"""
        # 根据用户硬件配置、网络状况、质量要求等给出建议
        if user_preferences.get('prefer_local', False):
            return 'f5_tts'
        elif user_preferences.get('prefer_cloud', False):
            return 'minimax'
        else:
            # 默认推荐本地方案
            return 'f5_tts'
```

#### 5.3.2 质量评估和对比
```python
# quality_comparison.py
class VoiceQualityComparator:
    def __init__(self):
        self.evaluator = VoiceQualityEvaluator()
    
    async def compare_voice_quality(self, original_audio: str, 
                                   local_result: str, cloud_result: str) -> QualityReport:
        """对比本地和云端声音质量"""
        try:
            # 1. 评估本地结果
            local_quality = await self.evaluator.evaluate(
                reference_audio=original_audio,
                synthesized_audio=local_result,
                metrics=["mos", "similarity", "articulation"]
            )
            
            # 2. 评估云端结果
            cloud_quality = await self.evaluator.evaluate(
                reference_audio=original_audio,
                synthesized_audio=cloud_result,
                metrics=["mos", "similarity", "articulation"]
            )
            
            # 3. 生成对比报告
            report = QualityReport(
                local_score=local_quality.overall_score,
                cloud_score=cloud_quality.overall_score,
                local_metrics=local_quality.detailed_metrics,
                cloud_metrics=cloud_quality.detailed_metrics,
                recommendation=self._make_recommendation(local_quality, cloud_quality)
            )
            
            return report
            
        except Exception as e:
            logger.error(f"质量对比失败: {e}")
            raise
    
    def _make_recommendation(self, local: QualityMetrics, cloud: QualityMetrics) -> str:
        """给出使用建议"""
        if local.overall_score >= cloud.overall_score:
            return "建议使用本地F5-TTS方案"
        else:
            return "建议使用云端MiniMax方案"
```

### 5.4 声音克隆数据模型

#### 5.4.1 数据结构定义
```python
# voice_models.py
class VoiceCloneResult(BaseModel):
    character_id: str
    model_path: Optional[str] = None  # 本地模型路径
    voice_id: Optional[str] = None    # 云端声音ID
    quality_score: float
    training_time: Optional[float] = None
    is_cached: bool = False
    is_cloud_based: bool = False
    created_at: datetime = datetime.now()

class AudioQuality(BaseModel):
    score: float
    is_suitable: bool
    reason: Optional[str] = None
    details: Dict[str, Any] = {}

class F5TTSConfig(BaseModel):
    speaker_id: str
    training_steps: int = 1000
    learning_rate: float = 1e-4
    batch_size: int = 4
    save_dir: str
    temperature: float = 0.7
    top_p: float = 0.9
    audio_sample_rate: int = 22050
    audio_duration: int = 10  # 单个样本最大时长

class QualityReport(BaseModel):
    local_score: float
    cloud_score: float
    local_metrics: Dict[str, float]
    cloud_metrics: Dict[str, float]
    recommendation: str
    created_at: datetime = datetime.now()
```

### 5.5 声音克隆性能优化

#### 5.5.1 GPU显存优化
```python
# gpu_optimization.py
class GPUMemoryManager:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.allocated_memory = 0
        self.memory_threshold = 0.8  # 使用阈值
    
    async def optimize_memory_usage(self):
        """优化显存使用"""
        if torch.cuda.is_available():
            # 1. 清空缓存
            torch.cuda.empty_cache()
            
            # 2. 设置内存分配策略
            torch.cuda.set_per_process_memory_fraction(0.8)
            
            # 3. 启用内存池
            if hasattr(torch.cuda, 'memory_pool'):
                torch.cuda.memory_pool.empty_cache()
    
    async def manage_model_loading(self, model_name: str):
        """管理模型加载"""
        # 1. 检查当前显存使用
        current_memory = torch.cuda.memory_allocated() / 1024**3  # GB
        total_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        
        # 2. 如果显存不足，卸载其他模型
        if current_memory / total_memory > self.memory_threshold:
            await self._unload_unused_models()
        
        # 3. 加载模型
        await self._load_model_with_memory_check(model_name)
    
    async def batch_processing_optimization(self, batch_size: int) -> int:
        """批量处理优化"""
        if not torch.cuda.is_available():
            return batch_size
        
        # 根据显存动态调整批次大小
        available_memory = torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated()
        estimated_batch_memory = batch_size * 100 * 1024**2  # 估计每个批次需要100MB
        
        if available_memory < estimated_batch_memory:
            optimized_batch_size = max(1, batch_size // 2)
            logger.info(f"调整批次大小: {batch_size} -> {optimized_batch_size}")
            return optimized_batch_size
        
        return batch_size
```

## 6. 数据库设计

### 6.1 核心表结构 (SQLite)
```sql
-- 媒体文件表
CREATE TABLE media_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename VARCHAR(255) NOT NULL,
    original_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(20) NOT NULL, -- 'video' or 'audio'
    duration INTEGER, -- 秒
    resolution VARCHAR(50), -- 视频分辨率
    sample_rate INTEGER, -- 音频采样率
    channels INTEGER, -- 音频声道数
    file_size INTEGER,
    format VARCHAR(10),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 音频轨道表（仅视频文件使用）
CREATE TABLE audio_tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    media_id INTEGER REFERENCES media_files(id),
    file_path VARCHAR(500) NOT NULL,
    duration INTEGER,
    sample_rate INTEGER,
    channels INTEGER,
    format VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 字幕表
CREATE TABLE subtitles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    media_id INTEGER REFERENCES media_files(id),
    language VARCHAR(10) NOT NULL,
    content TEXT NOT NULL, -- SRT格式
    source_type VARCHAR(20), -- 'original' or 'translated'
    model_used VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 角色表
CREATE TABLE characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    media_id INTEGER REFERENCES media_files(id),
    name VARCHAR(100),
    gender VARCHAR(10),
    character_type VARCHAR(20),
    total_duration INTEGER, -- 秒
    appearance_count INTEGER DEFAULT 0,
    voice_features TEXT, -- JSON格式存储音色特征
    model_path VARCHAR(500), -- 本地声音克隆模型路径
    cloud_voice_id VARCHAR(100), -- 云端声音ID
    clone_quality_score REAL, -- 声音克隆质量评分
    clone_method VARCHAR(20), -- 克隆方法: 'f5_tts', 'minimax'
    is_cloud_based BOOLEAN DEFAULT FALSE, -- 是否使用云端模型
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 角色对话表
CREATE TABLE character_dialogues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER REFERENCES characters(id),
    subtitle_id INTEGER REFERENCES subtitles(id),
    start_time REAL NOT NULL,
    end_time REAL NOT NULL,
    confidence REAL,
    audio_segment_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 声音克隆任务表
CREATE TABLE voice_clone_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER REFERENCES characters(id),
    task_id VARCHAR(64) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, failed
    clone_method VARCHAR(20), -- f5_tts, minimax
    audio_samples TEXT, -- JSON格式存储音频样本路径
    model_path VARCHAR(500), -- 本地模型路径
    cloud_voice_id VARCHAR(100), -- 云端声音ID
    quality_score REAL,
    error_message TEXT,
    training_time REAL, -- 训练时长（秒）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- 声音合成任务表
CREATE TABLE voice_synthesis_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER REFERENCES characters(id),
    subtitle_id INTEGER REFERENCES subtitles(id),
    task_id VARCHAR(64) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    synthesis_method VARCHAR(20), -- local, cloud
    text TEXT NOT NULL,
    output_path VARCHAR(500),
    duration REAL, -- 音频时长
    quality_score REAL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- 声音克隆缓存表
CREATE TABLE voice_clone_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER REFERENCES characters(id),
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    model_path VARCHAR(500),
    cloud_voice_id VARCHAR(100),
    quality_score REAL,
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- 声音质量评估表
CREATE TABLE voice_quality_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER REFERENCES characters(id),
    task_type VARCHAR(20), -- clone, synthesis
    method VARCHAR(20), -- f5_tts, minimax
    original_audio_path VARCHAR(500),
    synthesized_audio_path VARCHAR(500),
    metrics TEXT, -- JSON格式存储质量指标
    overall_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 任务队列表
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_type VARCHAR(50) NOT NULL,
    media_id INTEGER REFERENCES media_files(id),
    status VARCHAR(20) DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- 缓存表
CREATE TABLE cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    cache_value TEXT NOT NULL,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 系统配置表
CREATE TABLE system_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5.2 索引设计
```sql
-- 性能优化索引
CREATE INDEX idx_media_files_status ON media_files(status);
CREATE INDEX idx_media_files_created_at ON media_files(created_at);
CREATE INDEX idx_media_files_type ON media_files(file_type);
CREATE INDEX idx_subtitles_media_language ON subtitles(media_id, language);
CREATE INDEX idx_characters_media ON characters(media_id);
CREATE INDEX idx_character_dialogues_character ON character_dialogues(character_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_media ON tasks(media_id);
CREATE INDEX idx_cache_key_expires ON cache(cache_key, expires_at);
```

## 6. API设计

### 6.1 RESTful API结构
```python
# 主要API端点
POST   /api/v1/media/upload               # 上传媒体文件
GET    /api/v1/media/{id}                 # 获取媒体文件信息
GET    /api/v1/media                      # 获取媒体文件列表
DELETE /api/v1/media/{id}                # 删除媒体文件

POST   /api/v1/media/{id}/process        # 开始处理
GET    /api/v1/media/{id}/status         # 获取处理状态
POST   /api/v1/media/{id}/pause          # 暂停处理
POST   /api/v1/media/{id}/resume         # 恢复处理
POST   /api/v1/media/{id}/cancel         # 取消处理

GET    /api/v1/media/{id}/audio          # 获取音频信息
GET    /api/v1/media/{id}/subtitles      # 获取字幕
POST   /api/v1/media/{id}/subtitles      # 上传字幕

GET    /api/v1/media/{id}/characters     # 获取角色列表
GET    /api/v1/characters/{id}            # 获取角色详情
POST   /api/v1/characters/{id}/clone      # 克隆声音
POST   /api/v1/characters/{id}/synthesize # 语音合成

GET    /api/v1/models/speech-recognition  # 获取语音识别模型
GET    /api/v1/models/translation        # 获取翻译模型
POST   /api/v1/models/test               # 测试模型连接

GET    /api/v1/settings                   # 获取设置
POST   /api/v1/settings                   # 更新设置
GET    /api/v1/system/status              # 获取系统状态
```

### 6.2 WebSocket事件
```python
# 实时通信事件
@websocket.on('connect')
async def handle_connect(websocket):
    """客户端连接"""
    pass

@websocket.on('video_progress')
async def handle_video_progress(websocket, data):
    """视频处理进度"""
    await websocket.send_json({
        'type': 'progress',
        'video_id': data['video_id'],
        'progress': data['progress'],
        'current_step': data['current_step']
    })

@websocket.on('character_update')
async def handle_character_update(websocket, data):
    """角色识别更新"""
    await websocket.send_json({
        'type': 'character_update',
        'video_id': data['video_id'],
        'characters': data['characters']
    })
```

## 7. 部署方案

### 7.1 桌面应用打包方案
```python
# build.py - 桌面应用打包脚本
import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_desktop_app():
    """构建桌面应用"""
    print("开始构建桌面应用...")
    
    # 1. 安装依赖
    print("安装Python依赖...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # 2. 下载模型文件
    print("下载模型文件...")
    subprocess.run([sys.executable, "scripts/download_models.py"])
    
    # 3. 初始化数据库
    print("初始化数据库...")
    subprocess.run([sys.executable, "scripts/setup_db.py"])
    
    # 4. 使用PyInstaller打包
    print("打包应用...")
    cmd = [
        "pyinstaller",
        "--name=MovieTranslator",
        "--windowed",
        "--onefile",
        "--add-data=data;data",
        "--add-data=resources;resources",
        "--icon=resources/icons/app.ico",
        "--hidden-import=pydub",
        "--hidden-import=librosa",
        "--hidden-import=sense_voice",
        "app/main.py"
    ]
    subprocess.run(cmd)
    
    # 5. 创建安装程序
    print("创建安装程序...")
    create_installer()
    
    print("构建完成!")

def create_installer():
    """创建安装程序 (Inno Setup)"""
    # 生成Inno Setup脚本
    iss_content = """
[Setup]
AppName=Movie Translator
AppVersion=1.0
DefaultDirName={pf}\\Movie Translator
DefaultGroupName=Movie Translator
OutputDir=dist
OutputBaseFilename=MovieTranslator-Setup

[Files]
Source: "dist\\MovieTranslator.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "data\\*"; DestDir: "{app}\\data"; Flags: ignoreversion recursesubdirs
Source: "resources\\*"; DestDir: "{app}\\resources"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\\Movie Translator"; Filename: "{app}\\MovieTranslator.exe"
Name: "{commondesktop}\\Movie Translator"; Filename: "{app}\\MovieTranslator.exe"

[Run]
Filename: "{app}\\MovieTranslator.exe"; Description: "{cm:LaunchProgram,Movie Translator}"; Flags: nowait postinstall skipifsilent
"""
    
    with open("build/setup.iss", "w", encoding="utf-8") as f:
        f.write(iss_content)
    
    # 编译安装程序
    subprocess.run(["iscc", "build/setup.iss"])

if __name__ == "__main__":
    build_desktop_app()
```

### 7.2 应用启动脚本
```python
# run.py - 应用启动脚本
import os
import sys
import subprocess
import threading
import time
from pathlib import Path

def start_backend_server():
    """启动后端服务"""
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    # 启动FastAPI服务器
    cmd = [sys.executable, "main.py", "--host", "127.0.0.1", "--port", "8000"]
    subprocess.run(cmd)

def start_desktop_app():
    """启动桌面应用"""
    app_dir = Path(__file__).parent / "app"
    os.chdir(app_dir)
    
    # 启动桌面应用
    cmd = [sys.executable, "main.py"]
    subprocess.run(cmd)

def main():
    """主函数"""
    print("启动电影翻译系统...")
    
    # 启动后端服务（在单独线程中）
    backend_thread = threading.Thread(target=start_backend_server)
    backend_thread.daemon = True
    backend_thread.start()
    
    # 等待后端服务启动
    time.sleep(3)
    
    # 启动桌面应用
    start_desktop_app()

if __name__ == "__main__":
    main()
```

### 7.3 系统要求检查脚本
```python
# scripts/check_system.py
import platform
import psutil
import GPUtil
import sys

def check_system_requirements():
    """检查系统要求"""
    print("检查系统要求...")
    
    # 操作系统
    print(f"操作系统: {platform.system()} {platform.release()}")
    
    # CPU
    cpu_count = psutil.cpu_count()
    print(f"CPU核心数: {cpu_count}")
    if cpu_count < 4:
        print("警告: CPU核心数建议4核以上")
    
    # 内存
    memory = psutil.virtual_memory()
    print(f"内存: {memory.total // (1024**3)}GB")
    if memory.total < 8 * 1024**3:
        print("警告: 内存建议8GB以上")
    
    # GPU
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = gpus[0]
            print(f"GPU: {gpu.name} ({gpu.memoryTotal}MB)")
        else:
            print("警告: 未检测到GPU，将使用CPU处理（速度较慢）")
    except:
        print("警告: 无法检测GPU信息")
    
    # 磁盘空间
    disk = psutil.disk_usage('/')
    free_space_gb = disk.free // (1024**3)
    print(f"可用磁盘空间: {free_space_gb}GB")
    if free_space_gb < 20:
        print("警告: 可用磁盘空间建议20GB以上")
    
    print("系统要求检查完成!")

if __name__ == "__main__":
    check_system_requirements()
```

## 8. 性能优化策略

### 8.1 数据库优化
- **索引优化**：为常用查询创建合适的索引
- **查询优化**：使用EXPLAIN分析查询性能
- **连接池**：使用数据库连接池减少连接开销
- **读写分离**：主从复制，读写分离
- **分库分表**：大数据量时的水平分片

### 8.2 缓存策略
- **多级缓存**：Redis + 本地缓存
- **缓存预热**：启动时加载热点数据
- **缓存更新**：采用合适的缓存更新策略
- **缓存淘汰**：LRU算法，设置合理的过期时间

### 8.3 异步处理
- **消息队列**：使用Celery处理耗时任务
- **异步IO**：使用async/await提高性能
- **批处理**：批量处理减少IO开销
- **流式处理**：大文件流式处理
- **串行处理**：一次只处理一个文件，确保系统稳定性

### 8.4 SenseVoice本地部署优化
- **GPU加速**：充分利用5090显卡的24GB显存
- **模型优化**：使用TensorRT加速推理，FP16精度
- **批处理**：支持多音频片段并行处理
- **显存管理**：模型预加载，避免重复加载开销
- **缓存机制**：相似音频复用识别结果

### 8.5 资源优化
- **内存管理**：及时释放不再使用的资源
- **GPU优化**：合理使用GPU加速
- **文件清理**：定期清理临时文件
- **监控告警**：实时监控系统资源使用情况

### 8.6 百度语音API集成优化
- **智能切换**：本地处理失败时自动切换百度API
- **限流控制**：合理控制API调用频率，避免超额
- **成本监控**：实时统计API调用成本
- **容错机制**：网络异常时的重试和降级策略
- **质量评估**：对比本地和云端识别质量，动态选择

### 8.7 翻译性能优化策略
- **智能分段**：基于语义完整性进行文本分段，保持上下文连贯性
- **并发控制**：合理控制并发翻译请求数，避免API限流
- **缓存命中**：哈希比对快速识别重复内容，减少重复翻译
- **断点续传**：定期保存翻译进度，支持大文件中断恢复
- **增量翻译**：仅翻译新增或修改的内容，提高效率
- **批处理优化**：将小文本块合并处理，减少API调用次数
- **内存管理**：流式处理大文件，避免内存溢出

## 9. 安全考虑

### 9.1 数据安全
- **输入验证**：严格验证用户输入
- **SQL注入**：使用参数化查询
- **文件上传**：限制文件类型和大小
- **数据加密**：敏感数据加密存储

### 9.2 访问控制
- **身份认证**：JWT令牌认证
- **权限控制**：基于角色的访问控制
- **API限流**：防止API滥用
- **CORS配置**：合理的跨域策略

### 9.3 系统安全
- **容器安全**：最小权限原则
- **网络安全**：防火墙配置
- **日志审计**：完整的操作日志
- **漏洞扫描**：定期安全扫描

## 10. 成本控制模块

### 10.1 成本监控架构
```python
# cost_control.py
class CostControlManager:
    def __init__(self):
        self.budget_manager = BudgetManager()
        self.usage_tracker = UsageTracker()
        self.cost_analyzer = CostAnalyzer()
        self.alert_manager = AlertManager()
        self.fallback_manager = FallbackManager()
    
    async def monitor_api_usage(self):
        """监控API使用情况"""
        # 1. 实时监控各API使用量
        # 2. 计算成本
        # 3. 检查预算
        # 4. 触发预警
        pass
    
    async def get_cost_report(self) -> CostReport:
        """获取成本报告"""
        return await self.cost_analyzer.generate_report()
```

### 10.2 API配额管理
```python
# quota_manager.py
class APIQuotaManager:
    def __init__(self):
        self.quotas = {
            'azure_speech': {
                'monthly_limit': 5000,  # 分钟
                'used': 0,
                'cost_per_minute': 0.013,  # $0.8/60分钟
                'reset_date': self._get_next_month_reset()
            },
            'google_speech': {
                'monthly_limit': 60,  # 分钟
                'used': 0,
                'cost_per_minute': 0.01,  # $0.6/分钟
                'reset_date': self._get_next_month_reset()
            },
            'baidu_speech': {
                'daily_limit': 500,  # 次
                'used': 0,
                'cost_per_call': 0.01,
                'reset_date': self._get_next_day_reset()
            },
            'deepseek': {
                'monthly_limit': 1000000,  # 字
                'used': 0,
                'cost_per_1k_chars': 0.002,
                'reset_date': self._get_next_month_reset()
            },
            'glm': {
                'monthly_limit': 500000,  # 字
                'used': 0,
                'cost_per_1k_chars': 0.003,
                'reset_date': self._get_next_month_reset()
            },
            'minimax': {
                'monthly_limit': 1000,  # 次
                'used': 0,
                'cost_per_call': 0.05,
                'reset_date': self._get_next_month_reset()
            }
        }
    
    async def check_quota(self, service: str, requested_units: int) -> QuotaCheckResult:
        """检查配额"""
        quota = self.quotas.get(service)
        if not quota:
            return QuotaCheckResult(allowed=True, reason="Service not configured")
        
        remaining = quota['monthly_limit'] - quota['used']
        if remaining >= requested_units:
            return QuotaCheckResult(allowed=True, remaining=remaining)
        else:
            return QuotaCheckResult(
                allowed=False, 
                reason="Quota exceeded",
                remaining=remaining,
                suggested_alternative=self._get_alternative_service(service)
            )
    
    async def record_usage(self, service: str, units: int):
        """记录使用量"""
        if service in self.quotas:
            self.quotas[service]['used'] += units
            await self._save_usage_to_db(service, units)
            
            # 检查是否需要预警
            await self._check_quota_alert(service)
    
    def get_quota_status(self) -> Dict[str, QuotaStatus]:
        """获取配额状态"""
        status = {}
        for service, quota in self.quotas.items():
            usage_percent = (quota['used'] / quota['monthly_limit']) * 100
            estimated_cost = quota['used'] * quota['cost_per_unit']
            
            status[service] = QuotaStatus(
                service=service,
                used=quota['used'],
                limit=quota['monthly_limit'],
                usage_percent=usage_percent,
                estimated_cost=estimated_cost,
                days_until_reset=self._days_until_reset(quota['reset_date'])
            )
        
        return status
    
    async def _check_quota_alert(self, service: str):
        """检查配额预警"""
        quota = self.quotas[service]
        usage_percent = (quota['used'] / quota['monthly_limit']) * 100
        
        # 80%预警
        if usage_percent >= 80:
            await self.alert_manager.send_quota_alert(
                service=service,
                usage_percent=usage_percent,
                remaining=quota['monthly_limit'] - quota['used']
            )
        
        # 100%预警
        if usage_percent >= 100:
            await self.alert_manager.send_quota_exceeded_alert(service)
```

### 10.3 预算管理
```python
# budget_manager.py
class BudgetManager:
    def __init__(self):
        self.monthly_budget = 50.0  # 默认月度预算$50
        self.alert_thresholds = [0.8, 0.9, 1.0]  # 预警阈值
        self.cost_tracker = CostTracker()
    
    async def set_monthly_budget(self, amount: float):
        """设置月度预算"""
        self.monthly_budget = amount
        await self._save_budget_to_db(amount)
    
    async def check_budget_status(self) -> BudgetStatus:
        """检查预算状态"""
        # 1. 获取本月已使用金额
        used_amount = await self.cost_tracker.get_monthly_cost()
        
        # 2. 计算使用百分比
        usage_percent = (used_amount / self.monthly_budget) * 100
        
        # 3. 计算剩余预算
        remaining = self.monthly_budget - used_amount
        
        # 4. 检查是否需要预警
        alert_level = None
        for threshold in self.alert_thresholds:
            if usage_percent >= threshold * 100:
                alert_level = threshold
        
        return BudgetStatus(
            monthly_budget=self.monthly_budget,
            used_amount=used_amount,
            usage_percent=usage_percent,
            remaining=remaining,
            alert_level=alert_level,
            days_until_month_end=self._days_until_month_end()
        )
    
    async def enforce_budget_limits(self, service: str, estimated_cost: float) -> bool:
        """执行预算限制"""
        budget_status = await self.check_budget_status()
        
        # 如果预算已超限，拒绝使用付费服务
        if budget_status.usage_percent >= 100:
            logger.warning(f"预算已超限，拒绝使用付费服务: {service}")
            return False
        
        # 如果即将超限，检查是否可以使用免费替代方案
        if budget_status.usage_percent >= 90:
            has_free_alternative = await self._has_free_alternative(service)
            if has_free_alternative:
                logger.info(f"即将超限，切换到免费替代方案: {service}")
                return True
            else:
                logger.warning(f"即将超限且无免费替代方案，拒绝使用: {service}")
                return False
        
        return True
```

### 10.4 智能成本优化
```python
# cost_optimizer.py
class CostOptimizer:
    def __init__(self):
        self.quota_manager = APIQuotaManager()
        self.budget_manager = BudgetManager()
        self.performance_analyzer = PerformanceAnalyzer()
    
    async def optimize_service_selection(self, task_type: str, requirements: Dict) -> ServiceSelection:
        """优化服务选择以控制成本"""
        try:
            # 1. 获取可用的服务选项
            available_services = self._get_available_services(task_type)
            
            # 2. 过滤出预算范围内的服务
            affordable_services = []
            for service in available_services:
                if await self._is_service_affordable(service, requirements):
                    affordable_services.append(service)
            
            # 3. 根据成本效益比排序
            ranked_services = await self._rank_services_by_cost_effectiveness(
                affordable_services, requirements
            )
            
            # 4. 选择最优服务
            selected_service = ranked_services[0] if ranked_services else available_services[0]
            
            return ServiceSelection(
                service=selected_service,
                reason=self._get_selection_reason(selected_service, ranked_services),
                estimated_cost=await self._estimate_cost(selected_service, requirements),
                fallback_options=ranked_services[1:3] if len(ranked_services) > 1 else []
            )
            
        except Exception as e:
            logger.error(f"服务选择优化失败: {e}")
            return ServiceSelection(
                service=available_services[0],
                reason="优化失败，使用默认服务",
                estimated_cost=0
            )
    
    async def _is_service_affordable(self, service: ServiceInfo, requirements: Dict) -> bool:
        """检查服务是否在预算范围内"""
        # 1. 检查配额
        quota_check = await self.quota_manager.check_quota(
            service.name, requirements.get('units', 1)
        )
        
        if not quota_check.allowed:
            return False
        
        # 2. 检查预算
        estimated_cost = await self._estimate_service_cost(service, requirements)
        budget_ok = await self.budget_manager.enforce_budget_limits(
            service.name, estimated_cost
        )
        
        return quota_check.allowed and budget_ok
    
    async def _rank_services_by_cost_effectiveness(self, services: List[ServiceInfo], 
                                                  requirements: Dict) -> List[ServiceInfo]:
        """根据成本效益比排序服务"""
        scored_services = []
        
        for service in services:
            # 1. 计算成本分数
            cost_score = await self._calculate_cost_score(service, requirements)
            
            # 2. 计算质量分数
            quality_score = service.quality_score
            
            # 3. 计算成本效益比
            cost_effectiveness = quality_score / cost_score if cost_score > 0 else 0
            
            scored_services.append({
                'service': service,
                'score': cost_effectiveness,
                'cost_score': cost_score,
                'quality_score': quality_score
            })
        
        # 按分数降序排序
        scored_services.sort(key=lambda x: x['score'], reverse=True)
        
        return [item['service'] for item in scored_services]
```

### 10.5 成本分析和报告
```python
# cost_analyzer.py
class CostAnalyzer:
    def __init__(self):
        self.usage_db = UsageDatabase()
        self.cost_calculator = CostCalculator()
    
    async def generate_cost_report(self, period: str = 'monthly') -> CostReport:
        """生成成本报告"""
        try:
            # 1. 获取使用数据
            usage_data = await self.usage_db.get_usage_data(period)
            
            # 2. 计算各项成本
            cost_breakdown = await self._calculate_cost_breakdown(usage_data)
            
            # 3. 分析趋势
            cost_trends = await self._analyze_cost_trends(usage_data)
            
            # 4. 生成优化建议
            recommendations = await self._generate_cost_recommendations(
                cost_breakdown, cost_trends
            )
            
            return CostReport(
                period=period,
                total_cost=sum(item.cost for item in cost_breakdown),
                breakdown=cost_breakdown,
                trends=cost_trends,
                recommendations=recommendations,
                generated_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"生成成本报告失败: {e}")
            raise
    
    async def _calculate_cost_breakdown(self, usage_data: List[UsageRecord]) -> List[CostItem]:
        """计算成本明细"""
        breakdown = []
        
        # 按服务分组
        service_usage = {}
        for record in usage_data:
            if record.service not in service_usage:
                service_usage[record.service] = []
            service_usage[record.service].append(record)
        
        # 计算每个服务的成本
        for service, records in service_usage.items():
            total_units = sum(record.units for record in records)
            cost = await self.cost_calculator.calculate_service_cost(
                service, total_units
            )
            
            breakdown.append(CostItem(
                service=service,
                units=total_units,
                cost=cost,
                percentage=0  # 将在后面计算百分比
            ))
        
        # 计算百分比
        total_cost = sum(item.cost for item in breakdown)
        for item in breakdown:
            item.percentage = (item.cost / total_cost) * 100 if total_cost > 0 else 0
        
        return breakdown
    
    async def _generate_cost_recommendations(self, breakdown: List[CostItem], 
                                          trends: CostTrends) -> List[str]:
        """生成成本优化建议"""
        recommendations = []
        
        # 1. 识别高成本服务
        high_cost_services = [item for item in breakdown if item.percentage > 30]
        if high_cost_services:
            recommendations.append(
                f"高成本服务建议: {', '.join(s.service for s in high_cost_services)} "
                f"占总成本的{sum(s.percentage for s in high_cost_services):.1f}%，建议优化使用频率或寻找替代方案"
            )
        
        # 2. 分析趋势
        if trends.growth_rate > 20:
            recommendations.append(
                f"成本增长较快(月增长率{trends.growth_rate:.1f}%)，建议设置更严格的预算控制"
            )
        
        # 3. 预算建议
        if trends.predicted_next_month > trends.current_month * 1.1:
            recommendations.append(
                f"预测下月成本为${trends.predicted_next_month:.2f}，建议增加预算或优化使用策略"
            )
        
        return recommendations
```

## 11. 监控和运维

### 11.1 监控指标
- **系统指标**：CPU、内存、磁盘、网络
- **应用指标**：API响应时间、错误率、处理队列长度
- **业务指标**：处理任务数、成功率、平均处理时间
- **自定义指标**：模型准确率、资源使用率
- **成本指标**：API使用量、预算使用率、成本趋势

### 11.2 日志管理
- **结构化日志**：JSON格式的结构化日志
- **日志级别**：DEBUG、INFO、WARNING、ERROR
- **日志聚合**：集中化日志收集和分析
- **日志轮转**：定期归档和清理

### 11.3 告警机制
- **阈值告警**：基于指标阈值的告警
- **异常检测**：基于机器学习的异常检测
- **告警通知**：邮件、短信、企业微信等多渠道通知
- **故障自愈**：自动化的故障恢复机制

### 11.4 成本告警
- **配额预警**：API配额使用达到80%时预警
- **预算预警**：月度预算使用达到80%、90%、100%时预警
- **异常成本预警**：单日成本异常突增时预警
- **成本优化建议**：定期发送成本优化建议

## 12. 数据迁移方案

### 12.1 版本升级数据迁移
```python
# data_migration.py
class DataMigrationManager:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.backup_manager = BackupManager()
        self.version_manager = VersionManager()
        self.validator = DataValidator()
    
    async def migrate_to_version(self, target_version: str) -> MigrationResult:
        """迁移到指定版本"""
        try:
            # 1. 检查当前版本
            current_version = await self.version_manager.get_current_version()
            
            # 2. 创建备份
            backup_path = await self.backup_manager.create_full_backup()
            
            # 3. 执行迁移
            migration_steps = self._get_migration_steps(current_version, target_version)
            
            for step in migration_steps:
                await self._execute_migration_step(step)
            
            # 4. 更新版本号
            await self.version_manager.update_version(target_version)
            
            # 5. 验证数据完整性
            validation_result = await self.validator.validate_data_integrity()
            
            return MigrationResult(
                success=True,
                target_version=target_version,
                backup_path=backup_path,
                validation_result=validation_result,
                migration_time=datetime.now()
            )
            
        except Exception as e:
            # 迁移失败，恢复备份
            await self._restore_from_backup(backup_path)
            raise MigrationError(f"迁移失败: {e}")
    
    async def _execute_migration_step(self, step: MigrationStep):
        """执行迁移步骤"""
        logger.info(f"执行迁移步骤: {step.description}")
        
        if step.type == 'schema_change':
            await self._migrate_schema(step)
        elif step.type == 'data_transformation':
            await self._transform_data(step)
        elif step.type == 'index_creation':
            await self._create_indexes(step)
        elif step.type == 'data_cleanup':
            await self._cleanup_data(step)
```

### 12.2 数据库架构迁移
```python
# schema_migration.py
class SchemaMigration:
    def __init__(self):
        self.db = DatabaseConnection()
    
    async def migrate_from_v1_to_v2(self):
        """从v1迁移到v2"""
        # v1 -> v2 的变更：添加声音克隆相关表
        migration_sql = """
        -- 添加声音克隆任务表
        CREATE TABLE IF NOT EXISTS voice_clone_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id INTEGER REFERENCES characters(id),
            task_id VARCHAR(64) UNIQUE NOT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            clone_method VARCHAR(20),
            audio_samples TEXT,
            model_path VARCHAR(500),
            cloud_voice_id VARCHAR(100),
            quality_score REAL,
            error_message TEXT,
            training_time REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            completed_at TIMESTAMP
        );
        
        -- 添加声音合成任务表
        CREATE TABLE IF NOT EXISTS voice_synthesis_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id INTEGER REFERENCES characters(id),
            subtitle_id INTEGER REFERENCES subtitles(id),
            task_id VARCHAR(64) UNIQUE NOT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            synthesis_method VARCHAR(20),
            text TEXT NOT NULL,
            output_path VARCHAR(500),
            duration REAL,
            quality_score REAL,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        );
        
        -- 更新characters表，添加声音克隆相关字段
        ALTER TABLE characters ADD COLUMN model_path VARCHAR(500);
        ALTER TABLE characters ADD COLUMN cloud_voice_id VARCHAR(100);
        ALTER TABLE characters ADD COLUMN clone_quality_score REAL;
        ALTER TABLE characters ADD COLUMN clone_method VARCHAR(20);
        ALTER TABLE characters ADD COLUMN is_cloud_based BOOLEAN DEFAULT FALSE;
        """
        
        await self.db.execute_migration(migration_sql)
    
    async def migrate_from_v2_to_v3(self):
        """从v2迁移到v3"""
        # v2 -> v3 的变更：添加翻译缓存和成本控制
        migration_sql = """
        -- 添加翻译缓存表
        CREATE TABLE IF NOT EXISTS translation_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text_hash VARCHAR(64) NOT NULL,
            original_text TEXT NOT NULL,
            translated_text TEXT NOT NULL,
            source_lang VARCHAR(10) NOT NULL,
            target_lang VARCHAR(10) NOT NULL,
            model_used VARCHAR(50),
            quality_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            access_count INTEGER DEFAULT 0,
            UNIQUE(text_hash, source_lang, target_lang)
        );
        
        -- 添加API使用记录表
        CREATE TABLE IF NOT EXISTS api_usage_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name VARCHAR(50) NOT NULL,
            api_endpoint VARCHAR(100) NOT NULL,
            units_used INTEGER NOT NULL,
            cost_per_unit REAL NOT NULL,
            total_cost REAL NOT NULL,
            request_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            task_id VARCHAR(64),
            user_id VARCHAR(100)
        );
        
        -- 添加预算配置表
        CREATE TABLE IF NOT EXISTS budget_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            monthly_budget REAL NOT NULL,
            alert_threshold_1 REAL DEFAULT 0.8,
            alert_threshold_2 REAL DEFAULT 0.9,
            alert_threshold_3 REAL DEFAULT 1.0,
            currency VARCHAR(10) DEFAULT 'USD',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        await self.db.execute_migration(migration_sql)
```

### 12.3 配置文件迁移
```python
# config_migration.py
class ConfigMigration:
    def __init__(self):
        self.config_path = "config/"
        self.backup_path = "config/backup/"
    
    async def migrate_config_to_v2(self):
        """迁移配置文件到v2版本"""
        try:
            # 1. 备份现有配置
            await self._backup_config_files()
            
            # 2. 迁移主配置文件
            await self._migrate_main_config()
            
            # 3. 迁移模型配置
            await self._migrate_model_config()
            
            # 4. 迁移API配置
            await self._migrate_api_config()
            
            # 5. 验证配置完整性
            await self._validate_config_migration()
            
        except Exception as e:
            await self._restore_config_backup()
            raise ConfigMigrationError(f"配置迁移失败: {e}")
    
    async def _migrate_main_config(self):
        """迁移主配置文件"""
        old_config = await self._load_config("config.yaml")
        
        # 转换为新格式
        new_config = {
            'version': '2.0',
            'app': {
                'name': old_config.get('app_name', 'Movie Translator'),
                'version': old_config.get('version', '2.0.0'),
                'debug': old_config.get('debug', False)
            },
            'database': {
                'type': 'sqlite',
                'path': old_config.get('database_path', 'data/movie_translate.db')
            },
            'cache': {
                'enabled': True,
                'max_size_mb': old_config.get('cache_size', 1024),
                'ttl_days': 30
            },
            'features': {
                'voice_cloning': {
                    'enabled': True,
                    'local_model': 'f5_tts',
                    'cloud_service': 'minimax'
                },
                'cost_control': {
                    'enabled': True,
                    'monthly_budget': 50.0
                }
            }
        }
        
        await self._save_config("config_v2.yaml", new_config)
```

### 12.4 缓存数据迁移
```python
# cache_migration.py
class CacheMigration:
    def __init__(self):
        self.old_cache_dir = "cache/"
        self.new_cache_dir = "cache/v2/"
        self.cache_mapper = CacheMapper()
    
    async def migrate_cache_data(self):
        """迁移缓存数据"""
        try:
            # 1. 扫描旧缓存目录
            old_cache_files = await self._scan_old_cache()
            
            # 2. 转换缓存格式
            for cache_file in old_cache_files:
                await self._migrate_cache_file(cache_file)
            
            # 3. 更新缓存索引
            await self._update_cache_index()
            
            # 4. 清理旧缓存
            await self._cleanup_old_cache()
            
        except Exception as e:
            logger.error(f"缓存迁移失败: {e}")
            raise
    
    async def _migrate_cache_file(self, old_file: str):
        """迁移单个缓存文件"""
        try:
            # 1. 读取旧缓存数据
            old_data = await self._read_old_cache(old_file)
            
            # 2. 转换数据格式
            new_data = await self.cache_mapper.map_cache_data(old_data)
            
            # 3. 保存到新位置
            new_file_path = self._get_new_cache_path(old_file)
            await self._save_new_cache(new_file_path, new_data)
            
            # 4. 更新缓存映射表
            await self._update_cache_mapping(old_file, new_file_path)
            
        except Exception as e:
            logger.warning(f"缓存文件迁移失败: {old_file}, 错误: {e}")
```

### 12.5 模型文件迁移
```python
# model_migration.py
class ModelMigration:
    def __init__(self):
        self.old_model_dir = "models/"
        self.new_model_dir = "models/v2/"
        self.model_downloader = ModelDownloader()
    
    async def migrate_models(self):
        """迁移模型文件"""
        try:
            # 1. 检查现有模型
            existing_models = await self._check_existing_models()
            
            # 2. 下载新模型
            for model_info in existing_models:
                if model_info['needs_update']:
                    await self._download_updated_model(model_info)
            
            # 3. 迁移自定义模型
            await self._migrate_custom_models()
            
            # 4. 清理旧模型
            await self._cleanup_old_models()
            
        except Exception as e:
            logger.error(f"模型迁移失败: {e}")
            raise
    
    async def _download_updated_model(self, model_info: Dict):
        """下载更新的模型"""
        model_name = model_info['name']
        version = model_info['new_version']
        
        logger.info(f"下载更新模型: {model_name} v{version}")
        
        # 创建下载目录
        download_dir = os.path.join(self.new_model_dir, model_name, version)
        os.makedirs(download_dir, exist_ok=True)
        
        # 下载模型文件
        await self.model_downloader.download_model(
            model_name=model_name,
            version=version,
            target_dir=download_dir
        )
        
        # 验证模型完整性
        await self._verify_model_integrity(model_name, version)
```

### 12.6 迁移验证和回滚
```python
# migration_validator.py
class MigrationValidator:
    def __init__(self):
        self.db_validator = DatabaseValidator()
        self.config_validator = ConfigValidator()
        self.cache_validator = CacheValidator()
    
    async def validate_migration(self, migration_result: MigrationResult) -> ValidationResult:
        """验证迁移结果"""
        try:
            # 1. 验证数据库架构
            db_validation = await self.db_validator.validate_schema()
            
            # 2. 验证配置文件
            config_validation = await self.config_validator.validate_config()
            
            # 3. 验证缓存数据
            cache_validation = await self.cache_validator.validate_cache()
            
            # 4. 验证数据完整性
            data_integrity = await self._validate_data_integrity()
            
            # 5. 运行基本功能测试
            functionality_test = await self._run_functionality_tests()
            
            return ValidationResult(
                database_validation=db_validation,
                config_validation=config_validation,
                cache_validation=cache_validation,
                data_integrity=data_integrity,
                functionality_test=functionality_test,
                overall_success=all([
                    db_validation.success,
                    config_validation.success,
                    cache_validation.success,
                    data_integrity.success,
                    functionality_test.success
                ])
            )
            
        except Exception as e:
            logger.error(f"迁移验证失败: {e}")
            return ValidationResult(overall_success=False, error=str(e))
    
    async def rollback_migration(self, migration_result: MigrationResult):
        """回滚迁移"""
        try:
            logger.info("开始回滚迁移...")
            
            # 1. 恢复数据库备份
            await self._restore_database_backup(migration_result.backup_path)
            
            # 2. 恢复配置文件
            await self._restore_config_backup()
            
            # 3. 恢复缓存数据
            await self._restore_cache_backup()
            
            # 4. 恢复模型文件
            await self._restore_model_backup()
            
            # 5. 重置版本号
            await self._reset_version_number()
            
            logger.info("迁移回滚完成")
            
        except Exception as e:
            logger.error(f"迁移回滚失败: {e}")
            raise RollbackError(f"回滚失败: {e}")
```

### 12.7 自动化迁移脚本
```python
# auto_migrate.py
class AutoMigrator:
    def __init__(self):
        self.migration_manager = DataMigrationManager()
        self.validator = MigrationValidator()
        self.notifier = MigrationNotifier()
    
    async def auto_migrate_to_latest(self):
        """自动迁移到最新版本"""
        try:
            # 1. 检查是否有新版本
            latest_version = await self._get_latest_version()
            current_version = await self._get_current_version()
            
            if current_version == latest_version:
                logger.info("当前已是最新版本，无需迁移")
                return
            
            # 2. 发送迁移开始通知
            await self.notifier.send_migration_start_notification(
                current_version, latest_version
            )
            
            # 3. 执行迁移
            migration_result = await self.migration_manager.migrate_to_version(
                latest_version
            )
            
            # 4. 验证迁移结果
            validation_result = await self.validator.validate_migration(
                migration_result
            )
            
            if validation_result.overall_success:
                # 5. 发送迁移成功通知
                await self.notifier.send_migration_success_notification(
                    migration_result, validation_result
                )
                logger.info("迁移成功完成")
            else:
                # 6. 验证失败，执行回滚
                await self.validator.rollback_migration(migration_result)
                await self.notifier.send_migration_failure_notification(
                    migration_result, validation_result
                )
                raise MigrationError("迁移验证失败，已回滚")
                
        except Exception as e:
            await self.notifier.send_migration_error_notification(str(e))
            raise

## 13. 测试方案

### 13.1 测试架构设计
```python
# test_architecture.py
class TestArchitecture:
    def __init__(self):
        self.test_runner = TestRunner()
        self.test_data_manager = TestDataManager()
        self.test_environment = TestEnvironment()
        self.test_reporter = TestReporter()
    
    async def run_full_test_suite(self) -> TestReport:
        """运行完整测试套件"""
        try:
            # 1. 准备测试环境
            await self.test_environment.setup()
            
            # 2. 加载测试数据
            await self.test_data_manager.load_test_data()
            
            # 3. 运行单元测试
            unit_results = await self.test_runner.run_unit_tests()
            
            # 4. 运行集成测试
            integration_results = await self.test_runner.run_integration_tests()
            
            # 5. 运行端到端测试
            e2e_results = await self.test_runner.run_e2e_tests()
            
            # 6. 运行性能测试
            performance_results = await self.test_runner.run_performance_tests()
            
            # 7. 生成测试报告
            test_report = await self.test_reporter.generate_report({
                'unit': unit_results,
                'integration': integration_results,
                'e2e': e2e_results,
                'performance': performance_results
            })
            
            return test_report
            
        except Exception as e:
            logger.error(f"测试套件运行失败: {e}")
            raise
        
        finally:
            # 清理测试环境
            await self.test_environment.cleanup()
```

### 13.2 单元测试方案
```python
# test_unit.py
class UnitTests:
    def __init__(self):
        self.test_cases = [
            'test_audio_processing',
            'test_speech_recognition',
            'test_translation_service',
            'test_character_recognition',
            'test_voice_cloning',
            'test_cache_management',
            'test_cost_control'
        ]
    
    async def test_audio_processing(self):
        """测试音频处理模块"""
        test_cases = [
            ('test_audio_extraction', self._test_audio_extraction),
            ('test_audio_format_conversion', self._test_audio_format_conversion),
            ('test_audio_quality_detection', self._test_audio_quality_detection),
            ('test_audio_enhancement', self._test_audio_enhancement)
        ]
        
        results = []
        for test_name, test_func in test_cases:
            try:
                result = await test_func()
                results.append(TestResult(test_name, success=True))
            except Exception as e:
                results.append(TestResult(test_name, success=False, error=str(e)))
        
        return results
    
    async def test_speech_recognition(self):
        """测试语音识别模块"""
        test_cases = [
            ('test_whisper_transcription', self._test_whisper_transcription),
            ('test_sense_voice_transcription', self._test_sense_voice_transcription),
            ('test_model_routing', self._test_model_routing),
            ('test_cache_hit', self._test_cache_hit),
            ('test_error_handling', self._test_error_handling)
        ]
        
        results = []
        for test_name, test_func in test_cases:
            try:
                result = await test_func()
                results.append(TestResult(test_name, success=True))
            except Exception as e:
                results.append(TestResult(test_name, success=False, error=str(e)))
        
        return results
    
    async def _test_sense_voice_transcription(self):
        """测试SenseVoice转录功能"""
        # 1. 准备测试音频
        test_audio = self.test_data_manager.get_test_audio("chinese_speech.wav")
        
        # 2. 执行转录
        sense_voice_service = SenseVoiceService()
        result = await sense_voice_service.transcribe(test_audio)
        
        # 3. 验证结果
        assert result.text is not None
        assert len(result.text) > 0
        assert result.language == "en"
        assert result.confidence > 0.8
        
        return True
    
    async def _test_cost_control(self):
        """测试成本控制模块"""
        # 1. 设置测试预算
        budget_manager = BudgetManager()
        await budget_manager.set_monthly_budget(10.0)
        
        # 2. 测试预算检查
        can_use = await budget_manager.enforce_budget_limits("deepseek", 5.0)
        assert can_use == True
        
        # 3. 测试预算超限
        can_use = await budget_manager.enforce_budget_limits("deepseek", 15.0)
        assert can_use == False
        
        return True
```

### 13.3 集成测试方案
```python
# test_integration.py
class IntegrationTests:
    def __init__(self):
        self.test_environment = TestEnvironment()
        self.api_client = APIClient()
    
    async def test_full_pipeline(self):
        """测试完整的处理流程"""
        try:
            # 1. 上传测试视频
            test_video = self.test_data_manager.get_test_video("sample.mp4")
            upload_response = await self.api_client.upload_media(test_video)
            media_id = upload_response.media_id
            
            # 2. 启动处理流程
            process_response = await self.api_client.start_processing(media_id)
            
            # 3. 监控处理进度
            while True:
                status = await self.api_client.get_processing_status(media_id)
                if status.status in ["completed", "failed"]:
                    break
                await asyncio.sleep(1)
            
            # 4. 验证处理结果
            assert status.status == "completed"
            
            # 5. 检查生成的文件
            result_files = await self.api_client.get_result_files(media_id)
            assert len(result_files) > 0
            
            return TestResult("full_pipeline", success=True)
            
        except Exception as e:
            return TestResult("full_pipeline", success=False, error=str(e))
    
    async def test_voice_cloning_integration(self):
        """测试声音克隆集成"""
        try:
            # 1. 上传测试音频
            test_audio = self.test_data_manager.get_test_audio("voice_sample.wav")
            
            # 2. 创建角色
            character_data = {
                "name": "TestCharacter",
                "gender": "male",
                "audio_samples": [test_audio]
            }
            
            character = await self.api_client.create_character(character_data)
            
            # 3. 克隆声音
            clone_result = await self.api_client.clone_voice(character.id)
            
            # 4. 验证克隆结果
            assert clone_result.success == True
            assert clone_result.quality_score > 0.7
            
            # 5. 测试语音合成
            synthesis_result = await self.api_client.synthesize_speech(
                text="这是一个测试文本",
                character_id=character.id
            )
            
            assert synthesis_result.audio_path is not None
            assert os.path.exists(synthesis_result.audio_path)
            
            return TestResult("voice_cloning_integration", success=True)
            
        except Exception as e:
            return TestResult("voice_cloning_integration", success=False, error=str(e))
    
    async def test_cost_control_integration(self):
        """测试成本控制集成"""
        try:
            # 1. 设置测试预算
            await self.api_client.set_budget(5.0)
            
            # 2. 执行多个付费操作
            total_cost = 0
            for i in range(10):
                # 模拟API调用
                cost = 0.6
                total_cost += cost
                
                # 检查预算限制
                can_proceed = await self.api_client.check_budget_limit(cost)
                
                if total_cost > 5.0:
                    assert can_proceed == False
                    break
                else:
                    assert can_proceed == True
            
            return TestResult("cost_control_integration", success=True)
            
        except Exception as e:
            return TestResult("cost_control_integration", success=False, error=str(e))
```

### 13.4 性能测试方案
```python
# test_performance.py
class PerformanceTests:
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.benchmark_runner = BenchmarkRunner()
    
    async def test_processing_speed(self):
        """测试处理速度"""
        test_videos = [
            ("short_video.mp4", 60),      # 1分钟视频
            ("medium_video.mp4", 600),    # 10分钟视频
            ("long_video.mp4", 3600)      # 1小时视频
        ]
        
        results = []
        for video_name, duration in test_videos:
            try:
                # 1. 记录开始时间
                start_time = time.time()
                
                # 2. 执行处理
                video_path = self.test_data_manager.get_test_video(video_name)
                result = await self._process_video(video_path)
                
                # 3. 记录结束时间
                end_time = time.time()
                processing_time = end_time - start_time
                
                # 4. 计算性能指标
                speed_ratio = duration / processing_time
                
                # 5. 验证性能要求
                # 要求：1小时视频在45分钟内完成
                expected_max_time = duration * 0.75
                assert processing_time <= expected_max_time
                
                results.append(PerformanceResult(
                    test_name=f"processing_speed_{video_name}",
                    video_duration=duration,
                    processing_time=processing_time,
                    speed_ratio=speed_ratio,
                    success=True
                ))
                
            except Exception as e:
                results.append(PerformanceResult(
                    test_name=f"processing_speed_{video_name}",
                    success=False,
                    error=str(e)
                ))
        
        return results
    
    async def test_memory_usage(self):
        """测试内存使用"""
        try:
            # 1. 记录初始内存
            initial_memory = psutil.virtual_memory().used / 1024**3  # GB
            
            # 2. 处理大文件
            large_video = self.test_data_manager.get_test_video("large_video.mp4")
            await self._process_video(large_video)
            
            # 3. 记录峰值内存
            peak_memory = self.performance_monitor.get_peak_memory_usage()
            
            # 4. 验证内存要求
            # 要求：峰值内存使用不超过6GB
            assert peak_memory <= 6.0
            
            # 5. 检查内存泄漏
            # 等待垃圾回收
            time.sleep(10)
            final_memory = psutil.virtual_memory().used / 1024**3
            
            # 内存增长不应超过100MB
            memory_growth = final_memory - initial_memory
            assert memory_growth <= 0.1
            
            return PerformanceResult(
                test_name="memory_usage",
                initial_memory=initial_memory,
                peak_memory=peak_memory,
                final_memory=final_memory,
                memory_growth=memory_growth,
                success=True
            )
            
        except Exception as e:
            return PerformanceResult(
                test_name="memory_usage",
                success=False,
                error=str(e)
            )
    
    async def test_concurrent_processing(self):
        """测试并发处理能力"""
        try:
            # 1. 准备多个测试文件
            test_files = [
                self.test_data_manager.get_test_video(f"concurrent_test_{i}.mp4")
                for i in range(3)
            ]
            
            # 2. 并发启动处理
            start_time = time.time()
            tasks = []
            for video_file in test_files:
                task = asyncio.create_task(self._process_video(video_file))
                tasks.append(task)
            
            # 3. 等待所有任务完成
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 4. 记录总时间
            total_time = time.time() - start_time
            
            # 5. 验证结果
            success_count = sum(1 for r in results if not isinstance(r, Exception))
            assert success_count == len(test_files)
            
            return PerformanceResult(
                test_name="concurrent_processing",
                total_files=len(test_files),
                success_count=success_count,
                total_time=total_time,
                success=True
            )
            
        except Exception as e:
            return PerformanceResult(
                test_name="concurrent_processing",
                success=False,
                error=str(e)
            )
```

### 13.5 自动化测试框架
```python
# test_framework.py
class AutomatedTestFramework:
    def __init__(self):
        self.test_config = TestConfig()
        self.test_scheduler = TestScheduler()
        self.test_reporter = TestReporter()
        self.notification_service = NotificationService()
    
    async def run_scheduled_tests(self):
        """运行定期测试"""
        try:
            # 1. 检查是否需要运行测试
            if not await self.test_scheduler.should_run_tests():
                return
            
            # 2. 运行完整测试套件
            test_report = await self.run_full_test_suite()
            
            # 3. 分析测试结果
            analysis = await self._analyze_test_results(test_report)
            
            # 4. 发送通知
            if analysis.has_failures:
                await self.notification_service.send_test_failure_notification(
                    test_report, analysis
                )
            else:
                await self.notification_service.send_test_success_notification(test_report)
            
            # 5. 保存测试报告
            await self.test_reporter.save_report(test_report)
            
        except Exception as e:
            await self.notification_service.send_test_error_notification(str(e))
    
    async def run_ci_tests(self, commit_hash: str) -> TestReport:
        """运行CI测试"""
        try:
            # 1. 设置测试环境
            await self._setup_ci_environment(commit_hash)
            
            # 2. 运行核心测试
            core_tests = [
                'unit_tests',
                'integration_tests',
                'critical_performance_tests'
            ]
            
            test_report = await self.run_selected_tests(core_tests)
            
            # 3. 判断是否通过CI
            ci_passed = self._evaluate_ci_results(test_report)
            
            # 4. 更新CI状态
            await self._update_ci_status(commit_hash, ci_passed, test_report)
            
            return test_report
            
        except Exception as e:
            logger.error(f"CI测试失败: {e}")
            raise
    
    async def run_regression_tests(self, version: str) -> TestReport:
        """运行回归测试"""
        try:
            # 1. 加载历史测试结果
            historical_results = await self.test_reporter.load_historical_results()
            
            # 2. 运行回归测试
            regression_report = await self.run_full_test_suite()
            
            # 3. 比较结果
            comparison = await self._compare_test_results(
                historical_results, regression_report
            )
            
            # 4. 识别回归问题
            regressions = self._identify_regressions(comparison)
            
            if regressions:
                await self.notification_service.send_regression_alert(
                    version, regressions
                )
            
            return regression_report
            
        except Exception as e:
            logger.error(f"回归测试失败: {e}")
            raise
```

### 13.6 测试数据管理
```python
# test_data_manager.py
class TestDataManager:
    def __init__(self):
        self.test_data_repo = TestDataRepository()
        self.data_generator = TestDataGenerator()
    
    async def setup_test_data(self):
        """设置测试数据"""
        try:
            # 1. 生成测试视频
            await self.data_generator.generate_test_videos()
            
            # 2. 生成测试音频
            await self.data_generator.generate_test_audio()
            
            # 3. 生成测试字幕
            await self.data_generator.generate_test_subtitles()
            
            # 4. 设置测试数据库
            await self._setup_test_database()
            
            # 5. 验证测试数据完整性
            await self._validate_test_data_integrity()
            
        except Exception as e:
            logger.error(f"测试数据设置失败: {e}")
            raise
    
    async def cleanup_test_data(self):
        """清理测试数据"""
        try:
            # 1. 清理生成的文件
            await self._cleanup_generated_files()
            
            # 2. 重置测试数据库
            await self._reset_test_database()
            
            # 3. 清理缓存
            await self._cleanup_test_cache()
            
        except Exception as e:
            logger.error(f"测试数据清理失败: {e}")
```

### 13.7 测试报告生成
```python
# test_reporter.py
class TestReporter:
    def __init__(self):
        self.report_template = TestReportTemplate()
        self.exporter = TestReportExporter()
    
    async def generate_comprehensive_report(self, test_results: Dict) -> TestReport:
        """生成综合测试报告"""
        try:
            # 1. 分析测试结果
            analysis = await self._analyze_test_results(test_results)
            
            # 2. 生成报告内容
            report_content = await self.report_template.generate_report(
                test_results=test_results,
                analysis=analysis,
                generated_at=datetime.now()
            )
            
            # 3. 导出多种格式
            await self.exporter.export_html_report(report_content)
            await self.exporter.export_json_report(report_content)
            await self.exporter.export_pdf_report(report_content)
            
            return TestReport(
                content=report_content,
                summary=analysis.summary,
                success_rate=analysis.success_rate,
                generated_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"测试报告生成失败: {e}")
            raise
    
    async def _analyze_test_results(self, test_results: Dict) -> TestAnalysis:
        """分析测试结果"""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        errors = []
        
        # 统计各类型测试结果
        for test_type, results in test_results.items():
            for result in results:
                total_tests += 1
                if result.success:
                    passed_tests += 1
                else:
                    failed_tests += 1
                    errors.append({
                        'test_type': test_type,
                        'test_name': result.name,
                        'error': result.error
                    })
        
        # 计算成功率
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # 生成摘要
        summary = f"总测试数: {total_tests}, 通过: {passed_tests}, 失败: {failed_tests}, 成功率: {success_rate:.1f}%"
        
        return TestAnalysis(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            success_rate=success_rate,
            errors=errors,
            summary=summary
        )
```